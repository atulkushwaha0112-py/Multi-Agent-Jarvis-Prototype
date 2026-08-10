"""
Simple Command-Line To-Do App
Features: add, view, complete, and delete tasks (each with a date).
Data is saved to 'todos.json' in the same folder so tasks persist
between runs.
"""

import json
import os
from datetime import datetime

DATA_FILE = "todos.json"


def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(tasks):
    task = input("Enter task description: ").strip()
    date_str = input("Enter date (YYYY-MM-DD) [leave blank for today]: ").strip()

    if not date_str:
        date_str = datetime.today().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Task not added.")
            return

    tasks.append({"task": task, "date": date_str, "done": False})
    save_tasks(tasks)
    print(f"Added: '{task}' on {date_str}")


def view_tasks(tasks):
    if not tasks:
        print("\nNo tasks yet!\n")
        return

    print("\nYour Tasks:")
    print("-" * 40)
    for i, t in enumerate(tasks, start=1):
        status = "✔ Done" if t["done"] else "◻ Pending"
        print(f"{i}. [{status}] {t['task']}  (Due: {t['date']})")
    print("-" * 40 + "\n")


def complete_task(tasks):
    view_tasks(tasks)
    if not tasks:
        return
    try:
        idx = int(input("Enter task number to mark as done: ")) - 1
        if 0 <= idx < len(tasks):
            tasks[idx]["done"] = True
            save_tasks(tasks)
            print("Task marked as done!")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")


def delete_task(tasks):
    view_tasks(tasks)
    if not tasks:
        return
    try:
        idx = int(input("Enter task number to delete: ")) - 1
        if 0 <= idx < len(tasks):
            removed = tasks.pop(idx)
            save_tasks(tasks)
            print(f"Deleted: '{removed['task']}'")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")


def main():
    tasks = load_tasks()

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

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main()