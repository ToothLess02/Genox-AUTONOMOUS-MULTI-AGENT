import subprocess
import sys
import tempfile
import os
from pathlib import Path
from genox.config import WORKSPACE_DIR, BASE_DIR
from genox.tools.base import registry

# Path to our venv python
VENV_PYTHON = str(BASE_DIR / ".venv" / "bin" / "python3")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

@registry.register
def execute_python(code: str, timeout: int = 40) -> str:
    """Execute Python code in an isolated subprocess within the workspace.
    Useful for data processing, calculations, file transformations, creating charts, or running tests.
    Args:
        code: The Python code to execute.
        timeout: Execution timeout in seconds (default 40).
    """
    code_clean = code.strip()
    if not code_clean:
        return "Error: Python code cannot be empty."

    # Write code to a temporary script in workspace
    temp_script = WORKSPACE_DIR / f"_temp_run_{os.getpid()}.py"
    try:
        with open(temp_script, "w", encoding="utf-8") as f:
            f.write(code_clean)

        result = subprocess.run(
            [VENV_PYTHON, str(temp_script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(WORKSPACE_DIR)
        )

        output_parts = []
        if result.stdout:
            stdout_str = result.stdout.strip()
            if len(stdout_str) > 6000:
                stdout_str = stdout_str[:6000] + f"\n... [Truncated {len(result.stdout) - 6000} chars]"
            output_parts.append(f"STDOUT:\n{stdout_str}")
            
        if result.stderr:
            stderr_str = result.stderr.strip()
            if len(stderr_str) > 3000:
                stderr_str = stderr_str[:3000] + "\n... [Truncated]"
            output_parts.append(f"STDERR / TRACEBACK:\n{stderr_str}")

        if result.returncode != 0:
            output_parts.append(f"FAILED (Exit Code {result.returncode})")
        else:
            output_parts.append("SUCCESS (Exit Code 0)")

        return "\n\n".join(output_parts) if output_parts else "Code executed successfully with no output."

    except subprocess.TimeoutExpired:
        return f"TimeoutError: Python execution exceeded {timeout} seconds limit."
    except Exception as e:
        return f"Execution Error: {str(e)}"
    finally:
        if temp_script.exists():
            try:
                temp_script.unlink()
            except Exception:
                pass
