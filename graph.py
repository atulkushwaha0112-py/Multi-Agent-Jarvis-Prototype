"""
graph.py — LangGraph StateGraph for JARVIS.

Architecture:
    START → agent → (tools_condition) → tools → agent → END
                                     ↘ END (no tool call)

The agent node uses ChatMistralAI with all tools bound.
The ToolNode auto-dispatches tool calls returned by the LLM.
"""
import sys
sys.dont_write_bytecode = True  # never load stale .pyc files

import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage

from state import AgentState
from tools import ALL_TOOLS

load_dotenv()



SYSTEM_PROMPT = """You are JARVIS, a voice assistant. Follow these rules strictly:

0. 

1. REPLY IN ONE SHORT SENTENCE. No markdown, no lists, no long explanations.
   Your words become speech — keep it brief and natural.

2. WHATSAPP RULES — CRITICAL:
   - User says "send"/"message"/"tell" → call send_whatsapp_tool ONLY. Never call read first.
   - User says "read"/"check messages"/"what did X say" → call read_whatsapp_tool ONLY.
   - These are SEPARATE actions. Never mix them.

3. CONFIRMATION BEFORE IRREVERSIBLE ACTIONS:
   - Before send_whatsapp_tool or send_email_tool, ask: "Send it?" 
   - Only call the tool after user says yes/send it/go ahead.
   - For read, todo, memory, music — no confirmation needed, just do it.

4. TOOL RESULTS: Summarise in ONE spoken sentence. No JSON, no raw data.

5. ERRORS: Just say what went wrong in plain English.
"""


# ──────────────────────────────────────────────────────────────
# LLM + tool binding
# ──────────────────────────────────────────────────────────────

llm = ChatMistralAI(
    model="mistral-small-latest",   # higher rate limits than large; fine for voice
    api_key=os.getenv("MISTRAL_API_KEY"),
    temperature=0.3,
    max_retries=6,                   # auto-retry 429 with exponential backoff
)

llm_with_tools = llm.bind_tools(ALL_TOOLS)


# ──────────────────────────────────────────────────────────────
# Nodes
# ──────────────────────────────────────────────────────────────

def agent_node(state: AgentState) -> dict:
    """
    Prepend the system prompt, call the LLM (with tools bound),
    and return the new assistant message + updated turn_count.
    """
    system_msg = SystemMessage(content=SYSTEM_PROMPT)
    messages_with_system = [system_msg] + list(state["messages"])

    import time
    time.sleep(0.5)  # small pause to stay within Mistral free-tier rate limits
    response = llm_with_tools.invoke(messages_with_system)

    return {
        "messages": [response],
        "turn_count": state.get("turn_count", 0) + 1,
    }


tool_node = ToolNode(ALL_TOOLS)


# ──────────────────────────────────────────────────────────────
# Graph construction
# ──────────────────────────────────────────────────────────────

graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges("agent", tools_condition)
graph_builder.add_edge("tools", "agent")

app = graph_builder.compile()
