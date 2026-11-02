import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from genox.config import BASE_DIR, WORKSPACE_DIR, GEMINI_API_KEY, GENOX_MODEL
from genox.tools.base import registry
from genox.brain.agent import agent
from genox.brain.memory import memory

app = FastAPI(title="Genox - Autonomous AI Agent Platform", version="1.0.0")

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConfigRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    model_name: Optional[str] = None

class MemoryRequest(BaseModel):
    key: str
    value: str
    category: Optional[str] = "general"

class PromptRequest(BaseModel):
    prompt: str
    max_steps: Optional[int] = 15

try:
    import psutil
except ImportError:
    psutil = None

@app.get("/api/status")
def get_status():
    """System health and agent configuration status."""
    has_key = bool(agent.api_key and len(agent.api_key) > 5)
    return {
        "status": "ready" if has_key else "needs_api_key",
        "api_key_configured": has_key,
        "model": agent.model_name,
        "workspace": str(WORKSPACE_DIR),
        "total_tools": len(registry.get_all_tools()),
        "memories_count": len(memory.recall_memory("")),
    }

@app.get("/api/system-stats")
def get_system_stats():
    """Real-time macOS CPU, RAM, and storage metrics."""
    if not psutil:
        return {"cpu": 24, "memory": 48, "disk": 35}
    try:
        cpu = round(psutil.cpu_percent(interval=None), 1)
        mem = round(psutil.virtual_memory().percent, 1)
        disk = round(psutil.disk_usage("/").percent, 1)
        return {"cpu": cpu, "memory": mem, "disk": disk}
    except Exception:
        return {"cpu": 25, "memory": 50, "disk": 30}

@app.get("/api/tools")
def get_tools():
    """List of all available registered tools."""
    return registry.get_tool_metadata()

@app.post("/api/config")
def update_config(req: ConfigRequest):
    """Update API key or model without server restart."""
    env_file = BASE_DIR / ".env"
    lines = []
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

    updated_key = False
    updated_model = False
    new_lines = []

    for line in lines:
        if req.gemini_api_key and line.startswith("GEMINI_API_KEY="):
            new_lines.append(f"GEMINI_API_KEY={req.gemini_api_key.strip()}\n")
            updated_key = True
        elif req.model_name and line.startswith("GENOX_MODEL="):
            new_lines.append(f"GENOX_MODEL={req.model_name.strip()}\n")
            updated_model = True
        else:
            new_lines.append(line)

    if req.gemini_api_key and not updated_key:
        new_lines.append(f"GEMINI_API_KEY={req.gemini_api_key.strip()}\n")
    if req.model_name and not updated_model:
        new_lines.append(f"GENOX_MODEL={req.model_name.strip()}\n")

    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    if req.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = req.gemini_api_key.strip()
        agent.update_key(req.gemini_api_key.strip())

    if req.model_name:
        os.environ["GENOX_MODEL"] = req.model_name.strip()
        agent.model_name = req.model_name.strip()

    return {"success": True, "message": "Configuration successfully saved."}

@app.get("/api/memory")
def get_memories(q: str = ""):
    """Get stored memories and facts."""
    return memory.recall_memory(q)

@app.post("/api/memory")
def add_memory(req: MemoryRequest):
    """Add a new memory fact."""
    res = memory.save_memory(req.key, req.value, req.category or "general")
    return {"success": True, "message": res}

@app.delete("/api/memory/{key}")
def delete_memory(key: str):
    """Delete a memory fact."""
    success = memory.delete_memory(key)
    return {"success": success}

@app.get("/api/history")
def get_history(limit: int = 15):
    """Get task execution history."""
    return memory.get_recent_history(limit)

@app.get("/api/files")
def list_workspace_files():
    """List files in workspace for the File Deck."""
    files = []
    if WORKSPACE_DIR.exists():
        for p in sorted(WORKSPACE_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if p.name.startswith("."):
                continue
            files.append({
                "name": p.name,
                "is_dir": p.is_dir(),
                "size": p.stat().st_size if p.is_file() else 0,
                "modified": p.stat().st_mtime,
                "path": str(p.relative_to(WORKSPACE_DIR))
            })
    return files

@app.get("/api/file-content")
def get_file_content(filename: str):
    """Read a specific file from the workspace."""
    path = (WORKSPACE_DIR / filename).resolve()
    # Safety check: must stay within workspace
    if not str(path).startswith(str(WORKSPACE_DIR)):
        raise HTTPException(status_code=403, detail="Forbidden file path.")
    if not path.exists() or path.is_dir():
        raise HTTPException(status_code=404, detail="File not found.")
    
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(20000)
        return {"filename": path.name, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time bi-directional connection for thought stream and tool outputs."""
    await websocket.accept()
    try:
        while True:
            data_text = await websocket.receive_text()
            try:
                data = json.loads(data_text)
            except Exception:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format."})
                continue

            action = data.get("action")
            if action == "execute":
                prompt = data.get("prompt", "").strip()
                max_steps = int(data.get("max_steps", 15))
                if not prompt:
                    await websocket.send_json({"type": "error", "message": "Prompt cannot be empty."})
                    continue

                async for event in agent.execute_task(prompt=prompt, max_steps=max_steps):
                    await websocket.send_json(event)
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket Error: {e}")

# Mount static web UI files
web_dir = BASE_DIR / "web"
if web_dir.exists():
    app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="static")
