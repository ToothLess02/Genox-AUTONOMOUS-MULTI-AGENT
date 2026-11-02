"""
Genox macOS System Automation Tool
Enables direct control over macOS applications, windows, clipboard, and AppleScript automation.
"""

import subprocess
import os
from typing import Optional
from genox.tools.base import registry

@registry.register
def launch_or_focus_app(app_name: str) -> str:
    """Launch or bring an application to the foreground on macOS.
    
    Args:
        app_name: Name of the application (e.g. 'WhatsApp', 'Google Chrome', 'Mail', 'Notes', 'Terminal').
    
    Returns:
        Status message of the launch action.
    """
    clean_name = app_name.strip()
    try:
        # 1. Try macOS open -a
        res = subprocess.run(["open", "-a", clean_name], capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            # Also tell it to activate via AppleScript for guaranteed foreground focus
            subprocess.run(["osascript", "-e", f'tell application "{clean_name}" to activate'], capture_output=True)
            return f"Successfully launched and focused '{clean_name}' in the foreground."
        else:
            return f"Could not open '{clean_name}': {res.stderr.strip()}"
    except Exception as e:
        return f"Error opening '{clean_name}': {str(e)}"

@registry.register
def copy_to_clipboard(text: str) -> str:
    """Copy text directly to the macOS system clipboard.
    
    Args:
        text: The string content to copy to clipboard.
    
    Returns:
        Confirmation message.
    """
    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(text.encode("utf-8"))
        return f"Copied {len(text)} characters to system clipboard: '{text[:80]}...'"
    except Exception as e:
        return f"Error copying to clipboard: {str(e)}"

@registry.register
def read_clipboard() -> str:
    """Read the current content of the macOS system clipboard.
    
    Returns:
        String content of the clipboard.
    """
    try:
        res = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=5)
        content = res.stdout.strip()
        if not content:
            return "Clipboard is currently empty."
        return f"Clipboard Content ({len(content)} chars):\n{content}"
    except Exception as e:
        return f"Error reading clipboard: {str(e)}"

@registry.register
def run_applescript(script: str) -> str:
    """Execute arbitrary AppleScript code for fine-grained macOS application control,
    UI interactions, menu bar automation, and inter-app scripting.
    
    Args:
        script: AppleScript code to execute.
    
    Returns:
        Standard output or error from AppleScript execution.
    """
    try:
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=25)
        if res.returncode == 0:
            out = res.stdout.strip()
            return f"AppleScript executed successfully:\n{out or '(completed with no output)'}"
        else:
            return f"AppleScript Error (code {res.returncode}):\n{res.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: AppleScript execution timed out after 25 seconds."
    except Exception as e:
        return f"AppleScript Exception: {str(e)}"

@registry.register
def simulate_keystroke(key: str, modifiers: str = "") -> str:
    """Simulate key presses and keyboard shortcuts on macOS (e.g. Command+C, Command+V, Command+F, Return).
    
    Args:
        key: The key to press (e.g. 'c', 'v', 'f', 'k', 'return', 'tab', 'escape').
        modifiers: Optional modifier keys separated by comma, e.g. 'command down', 'command down, shift down'.
    
    Returns:
        Status message.
    """
    key_lower = key.strip().lower()
    mod_clause = f" using {{{modifiers}}}" if modifiers.strip() else ""
    
    if key_lower in ("return", "enter"):
        script = f'tell application "System Events" to key code 36{mod_clause}'
    elif key_lower == "tab":
        script = f'tell application "System Events" to key code 48{mod_clause}'
    elif key_lower == "escape":
        script = f'tell application "System Events" to key code 53{mod_clause}'
    elif key_lower == "space":
        script = f'tell application "System Events" to key code 49{mod_clause}'
    elif key_lower == "down":
        script = f'tell application "System Events" to key code 125{mod_clause}'
    elif key_lower == "up":
        script = f'tell application "System Events" to key code 126{mod_clause}'
    else:
        script = f'tell application "System Events" to keystroke "{key}"{mod_clause}'
        
    try:
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            return f"Simulated key press '{key}' with modifiers '{modifiers or 'none'}'."
        else:
            return f"Keystroke notice: {res.stderr.strip()}"
    except Exception as e:
        return f"Keystroke Error: {str(e)}"

@registry.register
def type_text(text: str) -> str:
    """Type or paste a full string of text into the currently active input field on macOS.
    
    Args:
        text: The text string to insert.
        
    Returns:
        Status message.
    """
    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(text.encode("utf-8"))
        res = subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke "v" using {command down}'], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            return f"Successfully typed/pasted text: '{text[:80]}...'"
        else:
            return f"Paste notice: {res.stderr.strip()}"
    except Exception as e:
        return f"Type text error: {str(e)}"

