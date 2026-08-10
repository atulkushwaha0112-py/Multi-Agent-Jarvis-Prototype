"""tools/memory_tools.py — Qdrant vector memory tools for LangGraph."""

from langchain_core.tools import tool
from memory import save_memory, search_memory


@tool
def save_memory_tool(text: str) -> str:
    """
    Save a fact or piece of information to long-term memory.
    Deduplicates automatically — will not store the same fact twice.
    Use this when the user says 'remember that', 'save this', 'note that'.
    text: the fact to remember (e.g. "Priya's email is priya@example.com").
    """
    try:
        save_memory(text)
        return f"Remembered: '{text}'"
    except Exception as e:
        return f"Could not save memory: {e}"


@tool
def search_memory_tool(query: str) -> list:
    """
    Search long-term memory for facts related to the query.
    Returns up to 3 matching facts with their relevance scores.
    Use this when the user asks about something they previously told JARVIS.
    query: what to look for (e.g. a contact name, topic, or keyword).
    """
    try:
        results = search_memory(query)
        if not results:
            return [{"text": "Nothing found in memory.", "score": 0.0}]
        return results
    except Exception as e:
        return [{"error": str(e)}]
