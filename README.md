# ⚡ GENOX — Autonomous Omni-Agent

> **A Universal Autonomous AI Agent with local OS control, web research, code execution, screen perception, long-term memory, and hands-free voice wake activation.**

---

## 🌟 Key Features

1. **Autonomous ReAct Action Loop**:
   - Decomposes complex human instructions into sequential sub-tasks.
   - Observes tool results and self-corrects code or arguments automatically if an error occurs.
2. **The Universal Tools (Hands & Eyes)**:
   - 🖥️ **Bash & System Terminal**: Executes shell commands, launches apps, monitors processes, checks Mac hardware.
   - 📁 **File System Engine**: Reads, creates, patches, and searches any file in the workspace or system.
   - 🌐 **Free Web Search**: Zero-cost, instant live web searches via DuckDuckGo (no API key needed).
   - 📄 **Web Scraper & Reader**: Fetches and extracts clean article text from any URL.
   - 🐍 **Live Python Sandbox**: Writes and executes Python scripts in an isolated subprocess with automatic traceback debugging.
   - 👁️ **Screen Vision**: Captures screenshots of your screen and inspects images/diagrams.
   - 🧠 **Persistent Episodic Memory**: SQLite-backed memory bank for remembering facts, preferences, and user profile across sessions.
   - 🧩 **Meta-Tooling (Self-Extension)**: If you ask Genox to do something it doesn't know how to do, it can write a new Python tool for itself, register it live, and execute it!
3. **Futuristic Genox Command Center**:
   - Glassmorphic dark cyber interface with real-time thought streaming.
   - **Hands-Free "Genox" Wake Word Engine (like Siri)**: Say *"Hey Genox"* or *"Genox"* to wake the agent, hear the chime, and give your command completely hands-free!
   - 3D Holographic AI Core & Reactive Cybernetic Talking Avatar.
   - Voice Input (Speech-to-Text) & Genox Voice Output (Text-to-Speech).
   - Live Workspace File Manager with instant file viewer.
   - Capabilities & Tool Matrix.
4. **Interactive CLI Companion**:
   - Fast, keyboard-friendly terminal interface with Rich formatting.

---

## 🔑 Getting Your Free Google AI Studio Key

Genox is powered by Google's flagship **Gemini 2.5 Flash** model, which has a **100% free tier** with **no credit card required**:

1. Open [aistudio.google.com](https://aistudio.google.com/).
2. Sign in with any standard Google / Gmail account.
3. Click **"Get API key"** ➔ **"Create API key"**.
4. Copy your key and either:
   - Paste it into the `.env` file (`GEMINI_API_KEY=your_key_here`)
   - OR click the **CONFIG** button in the Web Dashboard to save it directly from the UI.

---

## 🚀 Quick Start

### 1. Launch the Web Dashboard
```bash
./genox.sh
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

### 2. Launch the Terminal CLI
```bash
./genox.sh --cli
```

---

## 🛠️ Project Structure

```
Genox/
├── genox/
│   ├── brain/
│   │   ├── agent.py          # Autonomous ReAct execution loop
│   │   └── memory.py         # Persistent SQLite memory store
│   ├── tools/
│   │   ├── terminal.py       # Safe zsh/bash execution
│   │   ├── file_system.py    # File read/write/search
│   │   ├── web_search.py     # Live DuckDuckGo search
│   │   ├── web_scraper.py    # Webpage article reader
│   │   ├── python_runner.py  # Python sandbox execution
│   │   ├── screen_vision.py  # Mac screenshot & image inspection
│   │   ├── memory_tool.py    # Memory recall & storage
│   │   ├── dynamic_tool.py   # Self-extension / meta-tool creator
│   │   └── custom/           # Hot-loaded agent-created tools
│   ├── server/
│   │   └── app.py            # FastAPI + WebSocket server
│   ├── config.py             # App configurations & system prompts
│   └── cli.py                # Rich terminal companion
├── web/                      # Genox Glassmorphic Command Center
│   ├── index.html            # Main dashboard UI
│   ├── css/style.css         # Glassmorphism & cyber-accent design
│   └── js/app.js             # Real-time WebSocket & voice logic
├── workspace/                # Agent's active sandbox for files & outputs
├── run.py                    # Unified entrypoint
└── genox.sh                  # One-click launch script
```
