import importlib.util
from pathlib import Path
from genox.config import CUSTOM_TOOLS_DIR
from genox.tools.base import registry, ToolRegistry

# Import built-in tools to register them
from genox.tools import terminal
from genox.tools import file_system
from genox.tools import web_search
from genox.tools import web_scraper
from genox.tools import python_runner
from genox.tools import screen_vision
from genox.tools import memory_tool
from genox.tools import dynamic_tool
from genox.tools import interaction_tool
from genox.tools import macos_automation
from genox.tools import whatsapp_tool
from genox.tools import email_tool

def load_custom_tools():
    """Auto-load any previously generated custom tools on startup."""
    if not CUSTOM_TOOLS_DIR.exists():
        return
        
    for py_file in CUSTOM_TOOLS_DIR.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        try:
            mod_name = py_file.stem
            spec = importlib.util.spec_from_file_location(mod_name, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                func = getattr(module, mod_name, None)
                if callable(func):
                    registry.register(func)
        except Exception as e:
            print(f"Warning: Failed to load custom tool {py_file}: {e}")

# Load dynamic tools on package import
load_custom_tools()

__all__ = ["registry", "ToolRegistry", "load_custom_tools"]
