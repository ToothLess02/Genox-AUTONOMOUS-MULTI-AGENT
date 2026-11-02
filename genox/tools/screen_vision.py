import subprocess
import os
from pathlib import Path
from PIL import Image
from genox.config import WORKSPACE_DIR
from genox.tools.base import registry

@registry.register
def capture_screen(filename: str = "current_screen.png") -> str:
    """Capture a screenshot of the macOS screen and save it to the workspace.
    Args:
        filename: Name of the saved image file (saved in workspace).
    """
    save_path = WORKSPACE_DIR / filename
    try:
        result = subprocess.run(
            ["screencapture", "-x", str(save_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and save_path.exists() and save_path.stat().st_size > 0:
            # Optimize image size for faster analysis
            try:
                with Image.open(save_path) as img:
                    width, height = img.size
                    if width > 1920:
                        ratio = 1920 / width
                        new_size = (1920, int(height * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                        img.save(save_path, optimize=True, quality=85)
            except Exception:
                pass
            return f"Screenshot successfully captured and saved to '{save_path}' (Resolution: {width}x{height})."
        else:
            return (
                f"Notice: Screen capture could not access the active display ({result.stderr.strip() or 'permission required'}). "
                "If on macOS, ensure Terminal/IDE has 'Screen Recording' permission in System Settings -> Privacy & Security -> Screen Recording. "
                "Alternatively, you can place any image or screenshot file into the workspace directory and ask me to analyze it!"
            )
    except Exception as e:
        return f"Screen Capture Error: {str(e)}"

@registry.register
def inspect_image_info(image_filename: str) -> str:
    """Check metadata and dimensions of an image in the workspace.
    Args:
        image_filename: Name or path of image in workspace.
    """
    path = Path(image_filename)
    if not path.is_absolute():
        path = WORKSPACE_DIR / path
        
    if not path.exists():
        return f"Error: Image '{path.name}' not found in workspace."
        
    try:
        with Image.open(path) as img:
            return f"Image '{path.name}': Format={img.format}, Size={img.size[0]}x{img.size[1]}, Mode={img.mode}, Bytes={path.stat().st_size}"
    except Exception as e:
        return f"Error inspecting image '{path.name}': {str(e)}"
