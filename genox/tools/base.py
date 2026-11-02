from typing import Callable, Dict, List, Any
import inspect

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._descriptions: Dict[str, str] = {}

    def register(self, func: Callable) -> Callable:
        name = func.__name__
        self._tools[name] = func
        self._descriptions[name] = inspect.getdoc(func) or "No description provided."
        return func

    def unregister(self, name: str):
        if name in self._tools:
            del self._tools[name]
            del self._descriptions[name]

    def get_tool(self, name: str) -> Callable:
        return self._tools.get(name)

    def get_all_tools(self) -> List[Callable]:
        return list(self._tools.values())

    def get_tool_metadata(self) -> List[Dict[str, Any]]:
        metadata = []
        for name, func in self._tools.items():
            sig = inspect.signature(func)
            doc = inspect.getdoc(func) or ""
            metadata.append({
                "name": name,
                "description": doc.split("\n")[0] if doc else "No description",
                "full_doc": doc,
                "parameters": [
                    {
                        "name": param_name,
                        "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                        "default": str(param.default) if param.default != inspect.Parameter.empty else None,
                        "required": param.default == inspect.Parameter.empty
                    }
                    for param_name, param in sig.parameters.items()
                ]
            })
        return metadata

# Global tool registry
registry = ToolRegistry()
