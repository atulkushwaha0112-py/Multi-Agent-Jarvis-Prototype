"""
todocheck.py — argument-based to-do functions (no input() calls).

Designed to be imported by the LangGraph agent tools.
Fuzzy text matching used for complete/delete so voice input works naturally.
CLI main() preserved under __name__ guard for standalone use.
"""

import json
import os
import base64
import subprocess
from datetime import datetime
from difflib import SequenceMatcher

# Always resolved relative to this file — not CWD
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")


# ──────────────────────────────────────────────────────────────
# Persistence helpers
# ──────────────────────────────────────────────────────────────

# ── Win32 file I/O via ctypes ─────────────────────────────────────────────
# Python's file descriptor (FD) table is corrupted by pyaudio/sounddevice.
# Windows HANDLEs are a completely separate mechanism — unaffected by FD bugs.

import ctypes
import ctypes.wintypes as _wt

_k32 = ctypes.windll.kernel32
_k32.CreateFileW.argtypes  = [_wt.LPCWSTR, _wt.DWORD, _wt.DWORD,
                               ctypes.c_void_p, _wt.DWORD, _wt.DWORD, ctypes.c_void_p]
_k32.CreateFileW.restype   = ctypes.c_void_p
_k32.WriteFile.argtypes    = [ctypes.c_void_p, ctypes.c_char_p,
                               _wt.DWORD, ctypes.POINTER(_wt.DWORD), ctypes.c_void_p]
_k32.ReadFile.argtypes     = [ctypes.c_void_p, ctypes.c_char_p,
                               _wt.DWORD, ctypes.POINTER(_wt.DWORD), ctypes.c_void_p]
_k32.GetFileSize.argtypes  = [ctypes.c_void_p, ctypes.c_void_p]
_k32.GetFileSize.restype   = _wt.DWORD
_k32.CloseHandle.argtypes  = [ctypes.c_void_p]

_INVALID_HANDLE = ctypes.c_void_p(-1).value
_GENERIC_READ   = 0x80000000
_GENERIC_WRITE  = 0x40000000
_FILE_SHARE_RW  = 0x00000003
_OPEN_EXISTING  = 3
_CREATE_ALWAYS  = 2
_FILE_NORMAL    = 0x80


def _win32_read(path: str) -> bytes:
    """Read a file using Win32 HANDLE (bypasses Python FD table)."""
    h = _k32.CreateFileW(path, _GENERIC_READ, _FILE_SHARE_RW, None,
                         _OPEN_EXISTING, _FILE_NORMAL, None)
    if h == _INVALID_HANDLE:
        raise OSError(f"Cannot open {path}: Win32 error {_k32.GetLastError()}")
    try:
        size = _k32.GetFileSize(h, None)
        buf  = ctypes.create_string_buffer(size)
        read = _wt.DWORD(0)
        _k32.ReadFile(h, buf, size, ctypes.byref(read), None)
        return buf.raw[:read.value]
    finally:
        _k32.CloseHandle(h)


def _win32_write(path: str, data: bytes) -> None:
    """Write a file using Win32 HANDLE (bypasses Python FD table)."""
    h = _k32.CreateFileW(path, _GENERIC_WRITE, _FILE_SHARE_RW, None,
                         _CREATE_ALWAYS, _FILE_NORMAL, None)
    if h == _INVALID_HANDLE:
        raise OSError(f"Cannot create {path}: Win32 error {_k32.GetLastError()}")
    try:
        written = _wt.DWORD(0)
        _k32.WriteFile(h, data, len(data), ctypes.byref(written), None)
        _k32.FlushFileBuffers(h)
    finally:
        _k32.CloseHandle(h)


# ──────────────────────────────────────────────────────────────
# Persistence helpers
# ──────────────────────────────────────────────────────────────

def load_tasks() -> list:
    """Load task list from todos.json via Win32 HANDLE; returns [] if missing."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        return json.loads(_win32_read(DATA_FILE).decode("utf-8"))
    except Exception:
        return []


def save_tasks(tasks: list) -> None:
    """Persist task list to todos.json via Win32 HANDLE."""
    _win32_write(DATA_FILE, json.dumps(tasks, indent=2).encode("utf-8"))


# ──────────────────────────────────────────────────────────────
# Core operations — argument-based, return strings
# ──────────────────────────────────────────────────────────────

def _resolve_date(date_str: str) -> str | None:
    """
    Convert any reasonable date string to YYYY-MM-DD.
    Accepts: 'today', 'tomorrow', 'monday', 'Aug 15', '2026-08-15', etc.
    Returns None if the string cannot be parsed.
    """
    s = date_str.strip().lower()

    # Fast-path common words
    if s in ("today", "now"):
        return datetime.today().strftime("%Y-%m-%d")
    if s == "tomorrow":
        from datetime import timedelta
        return (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Try strict YYYY-MM-DD first
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return date_str.strip()
    except ValueError:
        pass

    # Try weekday names
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if s in weekdays:
        from datetime import timedelta
        today = datetime.today()
        target = weekdays.index(s)
        days_ahead = (target - today.weekday()) % 7 or 7
        return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # Try dateutil for everything else ('Aug 15', 'August 15 2026', etc.)
    try:
        from dateutil import parser as dateutil_parser
        parsed = dateutil_parser.parse(date_str, default=datetime.today())
        return parsed.strftime("%Y-%m-%d")
    except Exception:
        pass

    return None


def add_task(description: str, date_str: str = "") -> str:
    """
    Add a new task.

    Parameters
    ----------
    description : str
        Task text.
    date_str : str, optional
        Due date in YYYY-MM-DD format.  Defaults to today.

    Returns
    -------
    str  — confirmation or error message.
    """
    description = description.strip()
    if not description:
        return "Task description cannot be empty."

    if not date_str:
        date_str = datetime.today().strftime("%Y-%m-%d")
    else:
        date_str = _resolve_date(date_str)
        if date_str is None:
            return "Couldn't parse that date — try saying 'today', 'tomorrow', or a date like August 15."

    tasks = load_tasks()
    tasks.append({"task": description, "date": date_str, "done": False})
    save_tasks(tasks)
    return f"Added task: '{description}' due {date_str}."


def view_tasks() -> str:
    """
    Return a formatted string listing all tasks with their status.
    Returns a helpful message if there are no tasks.
    """
    tasks = load_tasks()
    if not tasks:
        return "You have no tasks yet."

    lines = ["Your tasks:"]
    for i, t in enumerate(tasks, start=1):
        status = "✔" if t["done"] else "◻"
        lines.append(f"  {i}. [{status}] {t['task']}  (Due: {t['date']})")
    return "\n".join(lines)


def _fuzzy_find(query: str, tasks: list) -> int:
    """
    Return the index of the task whose text best matches `query`.
    Uses SequenceMatcher ratio; returns -1 if no tasks.
    """
    if not tasks:
        return -1
    query_lower = query.lower()
    best_idx, best_score = 0, 0.0
    for i, t in enumerate(tasks):
        score = SequenceMatcher(None, query_lower, t["task"].lower()).ratio()
        if score > best_score:
            best_score, best_idx = score, i
    return best_idx


def complete_task(query: str) -> str:
    """
    Mark the task that best matches `query` as done.

    Parameters
    ----------
    query : str  — partial or full task description spoken by the user.

    Returns
    -------
    str — confirmation or error message.
    """
    tasks = load_tasks()
    idx = _fuzzy_find(query, tasks)
    if idx == -1:
        return "No tasks found."
    if tasks[idx]["done"]:
        return f"Task '{tasks[idx]['task']}' is already marked done."
    tasks[idx]["done"] = True
    save_tasks(tasks)
    return f"Marked done: '{tasks[idx]['task']}'."


def delete_task(query: str) -> str:
    """
    Delete the task that best matches `query`.

    Parameters
    ----------
    query : str  — partial or full task description spoken by the user.

    Returns
    -------
    str — confirmation or error message.
    """
    tasks = load_tasks()
    idx = _fuzzy_find(query, tasks)
    if idx == -1:
        return "No tasks found."
    removed = tasks.pop(idx)
    save_tasks(tasks)
    return f"Deleted task: '{removed['task']}'."


# ──────────────────────────────────────────────────────────────
# CLI (unchanged semantics, preserved for standalone use)
# ──────────────────────────────────────────────────────────────

def _cli_add(tasks):
    desc = input("Enter task description: ").strip()
    date_str = input("Enter date (YYYY-MM-DD) [leave blank for today]: ").strip()
    print(add_task(desc, date_str))


def _cli_complete(tasks):
    print(view_tasks())
    query = input("Enter task name/keywords to mark done: ").strip()
    print(complete_task(query))


def _cli_delete(tasks):
    print(view_tasks())
    query = input("Enter task name/keywords to delete: ").strip()
    print(delete_task(query))


def main():
    menu = """
=== TO-DO APP ===
1. Add task
2. View tasks
3. Mark task as done
4. Delete task
5. Exit
"""
    while True:
        print(menu)
        choice = input("Choose an option (1-5): ").strip()
        tasks = load_tasks()

        if choice == "1":
            _cli_add(tasks)
        elif choice == "2":
            print(view_tasks())
        elif choice == "3":
            _cli_complete(tasks)
        elif choice == "4":
            _cli_delete(tasks)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main()