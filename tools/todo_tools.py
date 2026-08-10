"""tools/todo_tools.py — To-do management tools for LangGraph."""

from langchain_core.tools import tool
from todocheck import add_task, view_tasks, complete_task, delete_task


@tool
def add_todo_tool(description: str, date: str = "") -> str:
    """
    Add a new to-do task with an optional due date.
    Use when user says 'add task', 'remind me to', 'add to my list'.
    description: what the task is (e.g. 'buy milk').
    date: optional YYYY-MM-DD; defaults to today if blank.
    """
    try:
        return add_task(description=description, date_str=date)
    except Exception as e:
        return f"Could not add task: {e}"


@tool
def view_todos_tool() -> str:
    """
    List all current to-do tasks with status and due dates.
    Use when user asks 'what are my tasks', 'show my list', 'any todos'.
    No arguments needed.
    """
    try:
        return view_tasks()
    except Exception as e:
        return f"Could not load tasks: {e}"


@tool
def complete_todo_tool(query: str) -> str:
    """
    Mark a task done by matching its description (fuzzy text search).
    Use when user says 'mark done', 'complete', 'I finished X'.
    query: partial or full task description.
    """
    try:
        return complete_task(query)
    except Exception as e:
        return f"Could not complete task: {e}"


@tool
def delete_todo_tool(query: str) -> str:
    """
    Delete a task by matching its description (fuzzy text search).
    Use when user says 'delete task', 'remove X from my list'.
    query: partial or full task description.
    """
    try:
        return delete_task(query)
    except Exception as e:
        return f"Could not delete task: {e}"
