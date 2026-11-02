import os
import json
import asyncio
import functools
from typing import AsyncGenerator, Dict, Any, List, Optional
from google import genai
from google.genai import types

from genox.config import GEMINI_API_KEY, GENOX_MODEL, SYSTEM_PROMPT, BASE_DIR
from genox.tools.base import registry
from genox.brain.memory import memory
from genox.brain.fast_path import try_fast_path

class GenoxAgent:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model or os.getenv("GENOX_MODEL", "gemini-3.5-flash").strip()
        self.client = None
        if self.api_key:
            self._init_client()

    def update_key(self, api_key: str):
        """Update API key dynamically at runtime."""
        self.api_key = api_key.strip()
        self._init_client()

    def _init_client(self):
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            print(f"Failed to initialize GenAI Client: {e}")
            self.client = None

    async def execute_task(self, prompt: str, max_steps: int = 15) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a task autonomously using Google GenAI Automatic Function Calling (AFC).
        Yields real-time events for thoughts, tool calls, observations, and final response.
        """
        if not self.api_key:
            yield {
                "type": "error",
                "message": (
                    "No Gemini API Key configured! Please enter your 100% free Google AI Studio key "
                    "in the CONFIG modal (or .env file)."
                )
            }
            return

        if not self.client:
            self._init_client()
            if not self.client:
                yield {"type": "error", "message": "Failed to connect to Google GenAI service."}
                return

        yield {"type": "start", "prompt": prompt}

        # 0. Check Lightning Fast-Path Intent Engine (<50ms execution)
        fast_res = try_fast_path(prompt)
        if fast_res:
            yield {"type": "status", "message": "Executing Lightning Fast-Path Action..."}
            if fast_res.get("url"):
                yield {"type": "open_url", "url": fast_res["url"]}
            yield {
                "type": "tool_call",
                "tool": fast_res["tool"],
                "args": fast_res["args"],
                "url": fast_res.get("url")
            }
            yield {
                "type": "tool_result",
                "tool": fast_res["tool"],
                "output": fast_res["output"]
            }
            yield {
                "type": "final_response",
                "content": fast_res["final_response"]
            }
            memory.log_task(
                prompt=prompt,
                final_response=fast_res["final_response"],
                steps=[{"step": 1, "tool": fast_res["tool"], "args": fast_res["args"], "output": fast_res["output"]}],
                success=True
            )
            yield {"type": "complete", "total_steps": 1}
            return

        # 1. Enrich with stored user memories and facts
        recalled_memories = memory.recall_memory(query="")
        memory_context = ""
        if recalled_memories:
            facts = "\n".join([f"- [{m.get('category','general')}] {m['key']}: {m['value']}" for m in recalled_memories[:12]])
            memory_context = f"\n\nPersistent User Memories & Facts:\n{facts}\n"

        full_system_instruction = SYSTEM_PROMPT + memory_context

        # 2. Build instrumented tools that publish events to an async queue
        loop = asyncio.get_running_loop()
        event_q = asyncio.Queue()
        steps_log: List[Dict[str, Any]] = []

        def on_tool_call(name: str, kwargs: dict):
            event = {
                "type": "tool_call",
                "tool": name,
                "args": kwargs
            }
            steps_log.append({"step": len(steps_log) + 1, "tool": name, "args": kwargs})
            loop.call_soon_threadsafe(event_q.put_nowait, event)

        def on_tool_result(name: str, result: Any):
            output_str = str(result)
            event = {
                "type": "tool_result",
                "tool": name,
                "output": output_str
            }
            if steps_log and steps_log[-1].get("tool") == name:
                steps_log[-1]["output"] = output_str[:1200]
            loop.call_soon_threadsafe(event_q.put_nowait, event)

        instrumented_tools = []
        for tool_fn in registry.get_all_tools():
            tname = tool_fn.__name__
            def make_wrapper(fn=tool_fn, name=tname):
                @functools.wraps(fn)
                def wrapped(**kwargs):
                    on_tool_call(name, kwargs)
                    try:
                        res = fn(**kwargs)
                    except Exception as exc:
                        res = f"Tool Execution Error: {exc}"
                    on_tool_result(name, res)
                    return res
                return wrapped
            instrumented_tools.append(make_wrapper())

        # 3. Model candidate fallback list (optimized for free-tier quota)
        model_candidates = [self.model_name, "gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.1-flash-lite-preview"]
        seen_models = set()
        chosen_model = None
        last_error = None

        def run_chat_sync(model_to_use: str):
            try:
                cfg = types.GenerateContentConfig(
                    tools=instrumented_tools,
                    system_instruction=full_system_instruction,
                    temperature=0.2,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                )
                chat = self.client.chats.create(model=model_to_use, config=cfg)
                return chat.send_message(prompt)
            except Exception:
                # Fallback without thinking_config if unsupported
                cfg = types.GenerateContentConfig(
                    tools=instrumented_tools,
                    system_instruction=full_system_instruction,
                    temperature=0.2,
                )
                chat = self.client.chats.create(model=model_to_use, config=cfg)
                return chat.send_message(prompt)

        final_response_text = ""
        success = False

        for candidate_model in model_candidates:
            if candidate_model in seen_models:
                continue
            seen_models.add(candidate_model)

            try:
                yield {"type": "status", "message": f"Engaging AI Core ({candidate_model.upper()})..."}
                
                # Start chat execution in background thread
                chat_task = asyncio.create_task(asyncio.to_thread(run_chat_sync, candidate_model))

                # Yield events from the queue in real-time as tools execute
                while not chat_task.done() or not event_q.empty():
                    try:
                        event = await asyncio.wait_for(event_q.get(), timeout=0.15)
                        yield event
                    except asyncio.TimeoutError:
                        pass

                resp = await chat_task
                final_response_text = resp.text or "Task execution complete."
                chosen_model = candidate_model
                self.model_name = candidate_model
                success = True
                break

            except Exception as e:
                last_error = e
                print(f"[Genox Agent] Model {candidate_model} failed: {e}. Trying fallback...")
                # Flush remaining events in queue
                while not event_q.empty():
                    yield await event_q.get()

        if success:
            yield {"type": "final_response", "content": final_response_text}
            memory.log_task(prompt=prompt, final_response=final_response_text, steps=steps_log, success=True)
            yield {"type": "complete", "total_steps": len(steps_log)}
        else:
            err_str = str(last_error) if last_error else "Unknown execution error"
            if "nodename nor servname" in err_str or "gaierror" in type(last_error).__name__:
                err_msg = "⚠️ Network Connection Notice: Unable to connect to Google Gemini API (offline or DNS resolution blocked). Please check your internet connectivity."
            else:
                err_msg = f"Agent Runtime Error: {err_str}"
            yield {"type": "error", "message": err_msg}
            memory.log_task(prompt=prompt, final_response=err_msg, steps=steps_log, success=False)

# Global default agent instance
agent = GenoxAgent()
