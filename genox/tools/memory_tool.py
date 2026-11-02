from genox.tools.base import registry
from genox.brain.memory import memory

@registry.register
def save_memory_fact(key: str, value: str, category: str = "general") -> str:
    """Save an important fact, user preference, credential hint, or project setting into long-term memory.
    Args:
        key: Short identifier (e.g. 'user_favorite_language', 'project_deploy_url').
        value: The detailed information to remember.
        category: 'user_profile', 'project', 'preference', or 'general'.
    """
    res = memory.save_memory(key=key, value=value, category=category)
    return res

@registry.register
def recall_memory_facts(query: str = "") -> str:
    """Recall stored memories or facts matching a topic or keyword.
    Args:
        query: Keyword to search in memories (e.g. 'language', 'deploy', or empty string for all).
    """
    facts = memory.recall_memory(query=query)
    if not facts:
        return f"No memories found matching '{query}'."
    
    output = [f"=== Recalled Memories ({len(facts)} items) ==="]
    for item in facts:
        output.append(f"• [{item.get('category', 'general').upper()}] {item['key']}: {item['value']}")
    return "\n".join(output)
