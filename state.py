"""
JARVIS AgentState — shared state passed through every LangGraph node.
"""

from __future__ import annotations

from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Shared state for the JARVIS LangGraph agent.

    Fields
    ------
    messages : list
        Full conversation history (HumanMessage / AIMessage / ToolMessage).
        `add_messages` reducer appends new messages rather than replacing.
    music : str | None
        The query string of the currently playing song, or None.
    last_contact : str | None
        The most recently mentioned WhatsApp contact name.
    pending_confirmation : dict | None
        Stores a pending irreversible action awaiting user "yes/no" confirmation.
        Example: {"action": "send_whatsapp", "name": "Arnav", "message": "Hi!"}
    turn_count : int
        Number of completed voice turns since boot.
    """

    messages: Annotated[list, add_messages]
    music: str | None
    last_contact: str | None
    pending_confirmation: dict | None
    turn_count: int
