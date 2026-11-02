import ast
import importlib.util
from pathlib import Path
from genox.config import CUSTOM_TOOLS_DIR
from genox.tools.base import registry

@registry.register
def create_new_tool(tool_name: str, description: str, python_code: str) -> str:
    """Dynamically create, test, and register a BRAND NEW Python tool on the fly!
    Use this when you encounter a task that requires a specialized library, API, or algorithm not present in your base tools.
    
    Args:
        tool_name: Valid python function name (e.g. 'convert_audio_format', 'calculate_compound_interest').
        description: Clear explanation of what the tool does and its parameters for future calls.
        python_code: Valid Python code defining the function `tool_name` with type annotations and docstring.
    """
    clean_name = tool_name.strip()
    if not clean_name.isidentifier():
        return f"Error: '{clean_name}' is not a valid Python identifier."

    # Validate AST
    try:
        parsed = ast.parse(python_code)
    except SyntaxError as e:
        return f"Syntax Error in tool code: {str(e)}"

    # Check that function is defined
    has_func = any(isinstance(node, ast.FunctionDef) and node.name == clean_name for node in parsed.body)
    if not has_func:
        return f"Error: The provided code does not define a top-level function named '{clean_name}'."

    # Save to custom tools folder
    file_path = CUSTOM_TOOLS_DIR / f"{clean_name}.py"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(python_code)

        # Dynamic import & registration
        spec = importlib.util.spec_from_file_location(clean_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        func = getattr(module, clean_name, None)
        if not callable(func):
            return f"Error: '{clean_name}' was imported but is not callable."

        registry.register(func)
        return (
            f"Successfully created and registered dynamic tool '{clean_name}'!\n"
            f"Location: {file_path}\n"
            f"The tool is now active and ready for immediate use."
        )

    except Exception as e:
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass
        return f"Error registering new tool '{clean_name}': {str(e)}"

@registry.register
def list_custom_tools() -> str:
    """List all custom tools dynamically created by Genox."""
    custom_files = list(CUSTOM_TOOLS_DIR.glob("*.py"))
    if not custom_files:
        return "No custom dynamic tools created yet."
        
    names = [f.stem for f in custom_files if not f.stem.startswith("_")]
    return f"Active Custom Dynamic Tools ({len(names)}):\n" + "\n".join(f"- {name}" for name in names)
