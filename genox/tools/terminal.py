import subprocess
import os
import shlex
from genox.config import WORKSPACE_DIR
from genox.tools.base import registry

DANGEROUS_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    ":(){ :|:& };:",
    "mkfs",
    "dd if=/dev/zero",
    "> /dev/sda",
]

@registry.register
def bash_executor(command: str) -> str:
    """Execute a bash/zsh shell command on macOS (e.g. running scripts, brew, curl, system profiler, listing processes).
    Args:
        command: The shell command to run.
    Returns:
        The stdout, stderr, and exit status code.
    """
    cmd_clean = command.strip()
    if not cmd_clean:
        return "Error: Command cannot be empty."

    for danger in DANGEROUS_PATTERNS:
        if danger in cmd_clean:
            return f"Blocked: Command contains forbidden dangerous pattern '{danger}'."

    try:
        # Run command within workspace by default
        result = subprocess.run(
            cmd_clean,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(WORKSPACE_DIR),
            executable="/bin/zsh"
        )
        
        output_parts = []
        if result.stdout:
            stdout_str = result.stdout.strip()
            if len(stdout_str) > 5000:
                stdout_str = stdout_str[:5000] + f"\n... [Truncated {len(result.stdout) - 5000} chars]"
            output_parts.append(f"STDOUT:\n{stdout_str}")
            
        if result.stderr:
            stderr_str = result.stderr.strip()
            if len(stderr_str) > 2000:
                stderr_str = stderr_str[:2000] + f"\n... [Truncated]"
            output_parts.append(f"STDERR:\n{stderr_str}")
            
        output_parts.append(f"EXIT CODE: {result.returncode}")
        return "\n\n".join(output_parts) if output_parts else "Command executed with no output (Exit Code: 0)."

    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 60 seconds."
    except Exception as e:
        return f"Execution Error: {str(e)}"
