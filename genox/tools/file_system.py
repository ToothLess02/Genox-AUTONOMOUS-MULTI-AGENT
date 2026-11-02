import os
from pathlib import Path
from typing import Optional
from genox.config import WORKSPACE_DIR
from genox.tools.base import registry

def _resolve_path(filepath: str) -> Path:
    p = Path(filepath)
    if not p.is_absolute():
        p = WORKSPACE_DIR / p
    return p.resolve()

@registry.register
def read_file(filepath: str, max_lines: int = 400) -> str:
    """Read the contents of a file on the local filesystem.
    Args:
        filepath: Relative to workspace or absolute path.
        max_lines: Maximum number of lines to return.
    """
    path = _resolve_path(filepath)
    if not path.exists():
        return f"Error: File '{path}' does not exist."
    if path.is_dir():
        return f"Error: '{path}' is a directory, not a file."
    
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        
        truncated = len(lines) > max_lines
        content = "".join(lines[:max_lines])
        result = f"=== File: {path.name} ({len(lines)} total lines) ===\n{content}"
        if truncated:
            result += f"\n... [Truncated: showing first {max_lines} of {len(lines)} lines]"
        return result
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"

@registry.register
def write_file(filepath: str, content: str) -> str:
    """Create or overwrite a file with the given content.
    Args:
        filepath: Relative to workspace or absolute path.
        content: The text content to write into the file.
    """
    path = _resolve_path(filepath)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{path}'."
    except Exception as e:
        return f"Error writing file '{path}': {str(e)}"

@registry.register
def list_files(directory: str = ".") -> str:
    """List files and subdirectories within a directory.
    Args:
        directory: Directory path (defaults to workspace).
    """
    path = _resolve_path(directory)
    if not path.exists():
        return f"Error: Directory '{path}' does not exist."
    if not path.is_dir():
        return f"Error: '{path}' is a file, not a directory."
        
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        if not items:
            return f"Directory '{path}' is empty."
            
        output = [f"Contents of {path}:"]
        for item in items[:100]:
            prefix = "[DIR] " if item.is_dir() else "[FILE]"
            size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
            output.append(f"  {prefix} {item.name}{size}")
            
        if len(items) > 100:
            output.append(f"  ... and {len(items) - 100} more items.")
        return "\n".join(output)
    except Exception as e:
        return f"Error listing directory '{path}': {str(e)}"

@registry.register
def search_files(query: str, directory: str = ".") -> str:
    """Search for files matching a pattern or containing specific text.
    Args:
        query: Name pattern (e.g. '*.py') or text string to search for.
        directory: Directory to search inside.
    """
    path = _resolve_path(directory)
    if not path.exists() or not path.is_dir():
        return f"Error: Invalid directory '{path}'."
        
    matches = []
    try:
        for p in path.rglob("*"):
            if p.is_file() and (query.lower() in p.name.lower()):
                matches.append(str(p.relative_to(path)))
                if len(matches) >= 50:
                    break
                    
        if not matches:
            return f"No files matching '{query}' found in '{path}'."
        return f"Found {len(matches)} matching files:\n" + "\n".join(f"- {m}" for m in matches)
    except Exception as e:
        return f"Error searching files: {str(e)}"
