"""
Report Content Part 2: Chapter 3 (Methodology) and Chapter 4 (System Design & Architecture).
"""

CHAPTER_3 = {
    "title": "CHAPTER 3: METHODOLOGY AND ARCHITECTURAL FRAMEWORK",
    "sections": [
        {
            "heading": "3.1 Core Design Philosophy: The Hybrid Dual-Path Paradigm",
            "content": (
                "The central architectural philosophy of GENOX is founded on the recognition that computational desktop interactions exhibit "
                "a bimodal distribution of complexity:\n\n"
                "1. **Deterministic High-Frequency Intents (~80% of daily interactions):** Routine operations—such as multi-platform web searching "
                "(YouTube, Amazon, Google, Spotify, Reddit, GitHub), launching native macOS applications, querying hardware telemetry (battery status, CPU usage, "
                "memory pressure), volume control, and direct messaging—are syntactically predictable and structurally deterministic. Forcing these operations "
                "through an LLM reasoning loop is computationally wasteful, financially costly, and unnecessarily slow.\n\n"
                "2. **Cognitive Open-Ended Intents (~20% of interactions):** Complex problem-solving tasks—such as automated code synthesis, error debugging, "
                "multi-application workflow chaining, web content scraping and synthesis, research paper summarization, and contextual email drafting—require "
                "dynamic reasoning, semantic deduction, and autonomous tool calling.\n\n"
                "To optimize across both operating regimes, GENOX introduces a **Hybrid Dual-Path Architecture**. Incoming user prompts are first evaluated by a "
                "deterministic, regex-compiled **Lightning Fast-Path Engine** executing in under 50 microseconds. If an intent matches a known operational pattern, "
                "it is immediately dispatched to local operating system subprocesses, bypassing the LLM entirely. If no deterministic match is found, the prompt is "
                "promoted to the **Cognitive Multi-Agent Pipeline**, which orchestrates an autonomous ReAct loop powered by the Google Gemini foundation model."
            )
        },
        {
            "heading": "3.2 Mathematical Formulation of Dual-Path Routing",
            "content": (
                "Let a user request be represented as an utterance string $U \\in \\mathcal{U}$. We define an intent classification and routing function $\\mathcal{R}(U)$:\n\n"
                "$$\\mathcal{R}(U) = \\begin{cases} \\mathcal{T}_{fast}(U), & \\text{if } \\exists p_i \\in \\mathcal{P} \\text{ such that } \\text{match}(p_i, \\text{Norm}(U)) \\neq \\emptyset \\\\ \\mathcal{A}_{LLM}(U), & \\text{otherwise} \\end{cases}$$\n\n"
                "where $\\mathcal{P} = \\{p_1, p_2, \\dots, p_K\\}$ represents the set of compiled regular expression intent patterns, $\\text{Norm}(U)$ denotes the "
                "phonetic wake-word normalization function, $\\mathcal{T}_{fast}$ is the deterministic local execution handler, and $\\mathcal{A}_{LLM}$ is the "
                "autonomous ReAct agent loop.\n\n"
                "The total system execution latency $L_{total}(U)$ is formulated as:\n\n"
                "$$L_{total}(U) = \\mathbb{I}_{fast}(U) \\cdot \\left( t_{norm} + t_{match} + t_{exec} \\right) + (1 - \\mathbb{I}_{fast}(U)) \\cdot \\left( t_{ws} + t_{prompt} + \\sum_{s=1}^{S} (t_{infer}^{(s)} + t_{tool}^{(s)}) \\right)$$\n\n"
                "where $\\mathbb{I}_{fast}(U) \\in \\{0, 1\\}$ is an indicator variable indicating whether $U$ matched the fast path, $t_{norm} + t_{match} \\le 0.05\\text{ ms}$, "
                "$t_{exec} \\le 45\\text{ ms}$, $t_{ws}$ is WebSocket transport latency (~5 ms), $S$ is the number of ReAct reasoning steps, $t_{infer}$ is the Gemini API "
                "inference latency (~450 ms), and $t_{tool}$ is tool execution time.\n\n"
                "By optimizing the decision boundary $\\mathcal{R}(U)$, GENOX minimizes the expected cost objective function:\n\n"
                "$$\\min_{\\mathcal{P}} \\mathbb{E}_{U \\sim \\mathcal{D}} \\left[ C_{API}(U) + \\lambda \\cdot L_{total}(U) \\right]$$\n\n"
                "where $C_{API}$ is monetary cost and $\\lambda$ is the latency penalty weight factor. Under the zero-cost free-tier deployment, $C_{API}(U) = 0$, "
                "and the optimization maximizes throughput while strictly respecting rate-limit boundaries."
            )
        },
        {
            "heading": "3.3 The Patient Listening Turn-Taking State Machine",
            "content": (
                "A pervasive limitation of existing voice assistants is premature turn completion: users who pause momentarily to formulate a complex instruction "
                "are abruptly cut off by standard Voice Activity Detection (VAD) algorithms. GENOX solves this through a dedicated **Patient Listening State Machine**.\n\n"
                "The acoustic engine operates across four formal states:\n"
                "1. **IDLE_WAITING:** The Web Speech API continuously listens to microphone audio streams. Incoming speech transcripts are evaluated against a "
                "40-variant phonetic dictionary of the wake word 'Genox'. The parser checks across up to 10 alternative acoustic candidate hypotheses (`maxAlternatives = 10`), "
                "accounting for common phonetic mis-transcriptions (e.g., 'Geox', 'Janov', 'Zenox', 'The knocks', 'Linux', 'Can ox').\n\n"
                "2. **WAKE_ACKNOWLEDGED:** Upon detecting a valid phonetic match, the system transitions immediately to WAKE_ACKNOWLEDGED. It emits a brief, pleasant verbal "
                "acknowledgment ('Yes') via the Web Speech Synthesis API, visually flashes the holographic particle AI Core into an active pulsing state, and enters the listening window.\n\n"
                "3. **PATIENT_LISTENING:** The system opens a dynamic speech accumulation buffer. A continuous 5-second silence hysteresis timer is initialized:\n\n"
                "$$T_{silence} = t_{now} - t_{last\\_speech}$$\n\n"
                "As the user speaks, intermediate transcript fragments are concatenated into the persistent buffer, and $t_{last\\_speech}$ is continuously updated, resetting the timer. "
                "If the user utters an additional wake phrase (e.g., re-addressing 'Genox' mid-sentence), the state machine strips the redundant wake word and resets the timer without breaking the turn.\n\n"
                "4. **TASK_DISPATCH:** Only when $T_{silence} \\ge 5.0\\text{ seconds}$ does the system conclude that the user has completed their thought. GENOX emits a verbal "
                "confirmation ('OK') via speech synthesis, locks the accumulated text buffer, strips all leading/trailing phonetic wake words, and transmits the clean command payload "
                "to the Dual-Path Router."
            )
        },
        {
            "heading": "3.4 Multi-Agent Specialized Cognitive Squad",
            "content": (
                "When a prompt is routed to the Cognitive Multi-Agent Pipeline, GENOX activates an orchestrated squad of **6 Specialized Sub-Agents**, "
                "each maintaining distinct operational boundaries, system prompts, and tool authorizations:\n\n"
                "• **Agent 1: Coding & Software Specialist:** Authorized to generate Python, JavaScript, and shell scripts; execute sandboxed code inside `/workspace`; "
                "inspect standard output and standard error streams; and iteratively repair runtime exceptions.\n\n"
                "• **Agent 2: Research & Web Intelligence Specialist:** Equipped with DuckDuckGo Search, Wikipedia query APIs, and BeautifulSoup web scrapers to browse "
                "live web documentation, extract raw text, resolve URLs, and synthesize academic literature.\n\n"
                "• **Agent 3: Browser & Web Actuation Specialist:** Manages web browser lifecycles, opens prefilled compose interfaces (Gmail, Web WhatsApp, SaaS platforms), "
                "and formats URL parameter schemes for instant web navigation.\n\n"
                "• **Agent 4: Operating System & Hardware Controller:** Directly interacts with host macOS / Linux kernel utilities to query battery telemetry, CPU utilization, "
                "RAM allocation, disk space, and manage native desktop applications via AppleScript and system daemons.\n\n"
                "• **Agent 5: Vision & Screen Perception Specialist:** Captures high-resolution full-screen or window-specific screenshots (`screencapture`), inspects on-screen "
                "visual state, and provides spatial grounding for desktop interactions.\n\n"
                "• **Agent 6: Memory & User Profile Curator:** Manages long-term episodic and semantic memory in SQLite (`genox_memory.db`), indexing user preferences, "
                "past task trajectories, and factual key-value relationships."
            )
        },
        {
            "heading": "3.5 Human-in-the-Loop (HITL) Multi-Stage Verification Protocol",
            "content": (
                "Autonomous desktop agents with shell and GUI execution privileges introduce substantial operational risks if left completely unconstrained. "
                "A misplaced keystroke or unintended script execution could result in data loss, unauthorized emails, or accidental purchases.\n\n"
                "GENOX resolves this through a formal **Risk-Classified Human-in-the-Loop (HITL) Verification Protocol**:\n\n"
                "• **Green Class (Autonomous Execution):** Non-destructive, read-only, or local operations—such as querying hardware stats, reading local files, "
                "opening browser search URLs, extracting email addresses from text, calculating math, or checking WhatsApp chat windows—execute with 100% autonomy and maximum speed.\n\n"
                "• **Amber Class (Interactive Verification):** Actions that generate external artifacts or prepare communications—such as drafting an email, staging a file overwrite, "
                "or selecting a recipient—require the agent to present an interactive confirmation card in the web HUD (`ask_user_confirmation`) displaying the exact recipient, "
                "subject line, and message body. The agent halts its execution loop and yields control to the user until explicit verification is provided.\n\n"
                "• **Red Class (System Alteration & Dispatch):** Irreversible actions—such as sending an email to an external server, dispatching an automated message, "
                "deleting workspace files, or running root-level shell commands—trigger native operating system modal dialogs using AppleScript (`display dialog`) with "
                "'Confirm' and 'Cancel' buttons. If the user cancels, the tool immediately aborts and returns an explicit UserCancelledException to the agent."
            )
        },
        {
            "heading": "3.6 Zero-Cost Enterprise-Grade Cognitive Integration",
            "content": (
                "To achieve sustainable, free-tier deployment without sacrificing reasoning capabilities, GENOX integrates with Google AI Studio's Gemini API "
                "(`gemini-2.5-flash` / `gemini-3.1-flash-lite`). The system implements four key optimization strategies:\n\n"
                "1. **Reflection Budget Elimination (`thinking_budget=0`):** By setting the internal thinking budget to zero, the model bypasses multi-thousand-token "
                "internal self-reflection cycles for function-calling tasks, reducing latency from 6.5s to 450ms while drastically conserving token quotas.\n\n"
                "2. **Type-Safe Automatic Function Calling (AFC):** Tool definitions are automatically synthesized from native Python type hints and docstrings into "
                "Google GenAI FunctionDeclarations, guaranteeing valid JSON parameter schemas without manual boilerplate.\n\n"
                "3. **Dynamic Memory Ingestion:** Stored user memories from SQLite are injected as concise markdown bullet points directly into the dynamic system prompt, "
                "avoiding expensive vector search lookups for common user preferences.\n\n"
                "4. **Graceful Network Degradation:** If network connectivity drops or DNS resolution fails (`[Errno 8] nodename nor servname provided`), the system catches "
                "the exception, activates local fallback diagnostics, and surfaces an actionable amber warning banner on the HUD instead of crashing."
            )
        }
    ]
}

CHAPTER_4 = {
    "title": "CHAPTER 4: SYSTEM DESIGN AND DETAILED ARCHITECTURE",
    "sections": [
        {
            "heading": "4.1 High-Level Architecture Overview",
            "content": (
                "The GENOX system is structured into six modular, loosely coupled architectural tiers:\n\n"
                "1. **Presentation & Perceptual Tier:** The client-side web interface (`web/index.html`, `style.css`, `app.js`) running inside a modern web browser. "
                "It manages the 60 FPS HTML5 Canvas particle AI Core, Web Audio API frequency analyzers, Web Speech API speech recognition and synthesis, and real-time "
                "bidirectional WebSocket communication.\n\n"
                "2. **Gateway & Orchestration Tier:** The asynchronous FastAPI server (`genox/server/app.py`) running on `127.0.0.1:8000`. It manages static file serving, "
                "RESTful configuration endpoints (`/api/status`, `/api/config`, `/api/memory`), and the persistent WebSocket connection (`/ws`) that streams real-time "
                "thought events, tool calls, and observations.\n\n"
                "3. **Routing & Intent Interception Tier:** The Lightning Fast-Path Intent Router (`genox/brain/fast_path.py`), which executes deterministic regex rules "
                "and phonetic string normalization to intercept routine queries in <50ms.\n\n"
                "4. **Cognitive Agent Tier:** The ReAct Agent Brain (`genox/brain/agent.py`), which orchestrates multi-turn automatic function calling with the Google Gemini API, "
                "manages tool registries, and streams execution states.\n\n"
                "5. **Desktop & System Actuation Tier:** The tool execution layer comprising 27 specialized tools spanning macOS native GUI automation (`macos_automation.py`), "
                "WhatsApp Catalyst scripting (`whatsapp_tool.py`), web scraping (`web_scraper.py`), shell execution (`system_tools.py`), and user verification (`user_interaction.py`).\n\n"
                "6. **Persistence & Relational Storage Tier:** The embedded SQLite database (`genox_memory.db`) managed by `genox/brain/memory.py`, providing ACID-compliant "
                "episodic task logging and semantic memory recall."
            )
        },
        {
            "heading": "4.2 Comprehensive Data Flow Diagrams (DFDs)",
            "content": (
                "The flow of data and control across the GENOX system is formalized through hierarchical Data Flow Diagrams:\n\n"
                "• **DFD Level 0 (Context Diagram):** Represents the entire GENOX platform as a single operational boundary interacting with four primary external entities: "
                "the Human Operator (Audio/Voice & Web UI), the Host Operating System (macOS Kernel, System Events, Window Server), Web Platforms (YouTube, Amazon, Google, etc.), "
                "and the Google AI Studio Gemini API.\n\n"
                "• **DFD Level 1 (Subsystem Functional Decomposition):** Decomposes GENOX into five core subsystems:\n"
                "  - Subsystem 1.0: Acoustic Perception & Phonetic Parsing\n"
                "  - Subsystem 2.0: Dual-Path Intent Decision & Routing\n"
                "  - Subsystem 3.0: Deterministic Fast-Path Execution Engine\n"
                "  - Subsystem 4.0: Cognitive ReAct Multi-Agent Squad\n"
                "  - Subsystem 5.0: Relational Memory Matrix & SQLite Persistence\n\n"
                "• **DFD Level 2 (Detailed Process Decompositions):**\n"
                "  - *Process 1.0 (Acoustic Perception):* Captures raw microphone audio, extracts Web Speech transcripts across 10 candidate hypotheses, applies phonetic dictionary "
                "transformations, evaluates the 5-second silence hysteresis, and emits the clean prompt.\n"
                "  - *Process 2.0 (Fast-Path Interception):* Matches normalized prompt against compiled regex dictionaries, extracts structured parameters (platform, query, contact, message), "
                "and dispatches native subprocess calls.\n"
                "  - *Process 4.0 (Cognitive Agent Execution):* Ingests prompt and SQLite memories, dispatches Gemini AFC request, intercepts tool call events, validates arguments, "
                "executes local tool functions, records observations, and streams real-time updates over WebSocket.\n"
                "  - *Process 5.0 (Cross-App Automation):* Reopens target Catalyst application, injects keyboard/mouse HID events via CoreGraphics, accesses system clipboard, and "
                "prompts user confirmation."
            )
        },
        {
            "heading": "4.3 Unified Modeling Language (UML) Behavioral Modeling",
            "content": (
                "The behavioral and structural dynamics of GENOX are modeled through standard UML 2.5 diagrams:\n\n"
                "• **UML Use Case Diagram:** Defines 8 primary system use cases: (1) Voice Wake & Turn-Taking, (2) Multi-Platform Search, (3) Native Application Launching, "
                "(4) Autonomous WhatsApp Messaging, (5) Cross-Application Email Synthesis, (6) Web Research & Summarization, (7) Sandboxed Code Execution, and "
                "(8) Memory Management & Preference Recall. Primary actors include the Human Operator, Operating System Window Server, and External Web Services.\n\n"
                "• **UML Sequence Diagram (Voice Listening & Fast-Path Execution):** Models the precise sequence of asynchronous messages exchanged between the User, Web Microphone, "
                "JavaScript State Machine, Speech Synthesis, FastAPI WebSocket, and Operating System Subprocesses.\n\n"
                "• **UML Sequence Diagram (Cross-App WhatsApp & Email Workflow):** Traces the complex multi-step execution loop: User prompt &rarr; ReAct Agent &rarr; WhatsApp Tool "
                "(reopen window, Cmd+F, CoreGraphics click, AXTextArea focus) &rarr; Email Extractor &rarr; HITL Verification Card &rarr; Gmail Draft Composer &rarr; Verification Dialog.\n\n"
                "• **UML Activity Diagram:** Details the dual-path decision logic: Audio input &rarr; Phonetic evaluation &rarr; Wake validation &rarr; Patient listening accumulation &rarr; "
                "Regex matching &rarr; [Branch A: Fast Path Subprocess | Branch B: ReAct Cognitive Loop] &rarr; HITL Check &rarr; Speech Output & UI Update.\n\n"
                "• **UML State Machine Diagram:** Formulates the 7 formal operating states of GENOX: IDLE, HEARING, WAKING, PATIENT_LISTENING, ROUTING, COGNITIVE_EXECUTION, "
                "and HITL_WAITING."
            )
        },
        {
            "heading": "4.4 Database Design & Relational Memory Architecture",
            "content": (
                "GENOX utilizes an embedded SQLite relational database (`genox_memory.db`) configured in Write-Ahead Logging (WAL) mode for maximum concurrent read performance. "
                "The schema is defined across four normalized tables:\n\n"
                "1. **`memories` Table:** Stores persistent semantic facts and user preferences.\n"
                "   - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)\n"
                "   - `key` (TEXT UNIQUE NOT NULL) — Semantic identifier (e.g., 'user_name', 'favorite_ide')\n"
                "   - `value` (TEXT NOT NULL) — Stored value string\n"
                "   - `category` (TEXT DEFAULT 'general') — Categorical domain ('personal', 'system', 'preferences')\n"
                "   - `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)\n"
                "   - `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)\n\n"
                "2. **`task_history` Table:** Maintains an immutable audit trail of every executed task.\n"
                "   - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)\n"
                "   - `prompt` (TEXT NOT NULL) — Raw user input prompt\n"
                "   - `final_response` (TEXT) — Agent's final synthesis\n"
                "   - `steps` (TEXT) — JSON-serialized execution steps\n"
                "   - `success` (BOOLEAN DEFAULT 1) — Task completion status\n"
                "   - `timestamp` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)\n\n"
                "3. **`task_steps` Table:** Detailed per-step tool execution telemetry.\n"
                "   - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)\n"
                "   - `task_id` (INTEGER REFERENCES task_history(id))\n"
                "   - `step_index` (INTEGER NOT NULL)\n"
                "   - `tool_name` (TEXT NOT NULL)\n"
                "   - `tool_args` (TEXT) — JSON-serialized input arguments\n"
                "   - `tool_output` (TEXT) — Raw observation output\n"
                "   - `duration_ms` (REAL)\n\n"
                "4. **`user_profile` Table:** System settings and configuration telemetry.\n"
                "   - `setting_key` (TEXT PRIMARY KEY)\n"
                "   - `setting_value` (TEXT NOT NULL)\n"
                "   - `last_modified` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
        }
    ]
}

