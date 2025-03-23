"""
Task Tracker CLI

A command-line application for tracking and managing tasks.
This application allows users to add, update, delete, and list tasks with different statuses.
"""

import json
import os
import sys
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class TaskStatus(str, Enum):
    """
    Enum representing the possible statuses of a task.
    """
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


class Task:
    """
    Class representing a task in the task tracker.
    
    Attributes:
        task_id (str): Unique identifier for the task.
        description (str): Short description of the task.
        status (TaskStatus): Current status of the task.
        created_at (str): ISO formatted date and time when the task was created.
        updated_at (str): ISO formatted date and time when the task was last updated.
    """
    
    def __init__(
        self,
        description: str,
        status: TaskStatus = TaskStatus.TODO,
        task_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        """
        Initialize a new Task object.
        
        Args:
            description: Short description of the task.
            status: Current status of the task. Defaults to TaskStatus.TODO.
            task_id: Unique identifier for the task. If None, a new UUID will be generated.
            created_at: ISO formatted creation date. If None, current time will be used.
            updated_at: ISO formatted update date. If None, matches created_at.
        """
        self.task_id = task_id if task_id else str(uuid.uuid4())
        self.description = description
        self.status = status
        current_time = datetime.now().isoformat()
        self.created_at = created_at if created_at else current_time
        self.updated_at = updated_at if updated_at else self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary for JSON serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the task.
        """
        return {
            "id": self.task_id,
            "description": self.description,
            "status": self.status.value,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, task_dict: Dict[str, Any]) -> 'Task':
        """
        Create a Task object from a dictionary.
        
        Args:
            task_dict: Dictionary containing task data.
            
        Returns:
            Task: A new Task object.
        """
        return cls(
            description=task_dict["description"],
            status=TaskStatus(task_dict["status"]),
            task_id=task_dict["id"],
            created_at=task_dict["createdAt"],
            updated_at=task_dict["updatedAt"]
        )
    
    def update(self, description: Optional[str] = None, status: Optional[TaskStatus] = None) -> None:
        """
        Update task properties and set updated_at to current time.
        
        Args:
            description: New description if provided.
            status: New status if provided.
        """
        if description is not None:
            self.description = description
        if status is not None:
            self.status = status
        self.updated_at = datetime.now().isoformat()


class TaskRepository:
    """
    Repository class for handling task storage and retrieval.
    """
    
    def __init__(self, file_path: str = "tasks.json"):
        """
        Initialize a TaskRepository with the specified file path.
        
        Args:
            file_path: Path to the JSON file for storing tasks. Defaults to "tasks.json".
        """
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """
        Create the tasks file with an empty list if it doesn't exist.
        """
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                json.dump([], file)
    
    def _load_tasks(self) -> List[Task]:
        """
        Load all tasks from the file.
        
        Returns:
            List[Task]: List of Task objects.
        """
        with open(self.file_path, 'r') as file:
            tasks_data = json.load(file)
        return [Task.from_dict(task_dict) for task_dict in tasks_data]
    
    def _save_tasks(self, tasks: List[Task]) -> None:
        """
        Save tasks to the file.
        
        Args:
            tasks: List of Task objects to save.
        """
        tasks_data = [task.to_dict() for task in tasks]
        with open(self.file_path, 'w') as file:
            json.dump(tasks_data, file, indent=2)
    
    def add_task(self, description: str) -> Task:
        """
        Add a new task to the repository.
        
        Args:
            description: Description of the new task.
            
        Returns:
            Task: The newly created task.
        """
        tasks = self._load_tasks()
        new_task = Task(description=description)
        tasks.append(new_task)
        self._save_tasks(tasks)
        return new_task
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks from the repository.
        
        Returns:
            List[Task]: All stored tasks.
        """
        return self._load_tasks()
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Get tasks filtered by status.
        
        Args:
            status: Status to filter by.
            
        Returns:
            List[Task]: Tasks matching the specified status.
        """
        all_tasks = self._load_tasks()
        return [task for task in all_tasks if task.status == status]
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Find a task by its ID.
        
        Args:
            task_id: ID of the task to find.
            
        Returns:
            Optional[Task]: The found task, or None if not found.
        """
        all_tasks = self._load_tasks()
        for task in all_tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def update_task(self, task_id: str, description: Optional[str] = None, status: Optional[TaskStatus] = None) -> Optional[Task]:
        """
        Update a task by ID.
        
        Args:
            task_id: ID of the task to update.
            description: New description if provided.
            status: New status if provided.
            
        Returns:
            Optional[Task]: The updated task, or None if not found.
        """
        all_tasks = self._load_tasks()
        for task in all_tasks:
            if task.task_id == task_id:
                task.update(description, status)
                self._save_tasks(all_tasks)
                return task
        return None
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: ID of the task to delete.
            
        Returns:
            bool: True if task was deleted, False if not found.
        """
        all_tasks = self._load_tasks()
        initial_count = len(all_tasks)
        filtered_tasks = [task for task in all_tasks if task.task_id != task_id]
        
        if len(filtered_tasks) < initial_count:
            self._save_tasks(filtered_tasks)
            return True
        return False


class TaskTrackerCLI:
    """
    Command-line interface for the Task Tracker application.
    Handles user input and displays results.
    """
    
    def __init__(self, repository: TaskRepository):
        """
        Initialize CLI with a task repository.
        
        Args:
            repository: TaskRepository for data access.
        """
        self.repository = repository
    
    def execute(self, args: List[str]) -> None:
        """
        Execute a command based on command-line arguments.
        
        Args:
            args: Command-line arguments.
        """
        if len(args) < 2:
            self._print_usage()
            return
        
        command = args[1]
        
        try:
            if command == "add":
                if len(args) < 3:
                    print("Error: Missing task description")
                    self._print_usage()
                    return
                description = " ".join(args[2:])
                self._add_task(description)
                
            elif command == "update":
                if len(args) < 4:
                    print("Error: Missing task ID or update information")
                    self._print_usage()
                    return
                task_id = args[2]
                if args[3] == "--status" and len(args) > 4:
                    status_str = args[4]
                    self._update_task_status(task_id, status_str)
                elif args[3] == "--description" and len(args) > 4:
                    description = " ".join(args[4:])
                    self._update_task_description(task_id, description)
                else:
                    print("Error: Invalid update command")
                    self._print_usage()
                
            elif command == "delete":
                if len(args) < 3:
                    print("Error: Missing task ID")
                    self._print_usage()
                    return
                task_id = args[2]
                self._delete_task(task_id)
                
            elif command == "list":
                if len(args) == 2:
                    self._list_all_tasks()
                elif len(args) > 2:
                    status_filter = args[2]
                    self._list_tasks_by_filter(status_filter)
                
            else:
                print(f"Error: Unknown command '{command}'")
                self._print_usage()
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def _print_usage(self) -> None:
        """
        Print usage information.
        """
        print("Task Tracker CLI Usage:")
        print("  python task_tracker.py add <description>             - Add a new task")
        print("  python task_tracker.py update <id> --status <status> - Update task status (todo, in-progress, done)")
        print("  python task_tracker.py update <id> --description <description> - Update task description")
        print("  python task_tracker.py delete <id>                   - Delete a task")
        print("  python task_tracker.py list                          - List all tasks")
        print("  python task_tracker.py list todo                     - List todo tasks")
        print("  python task_tracker.py list in-progress              - List in-progress tasks")
        print("  python task_tracker.py list done                     - List done tasks")
        print("  python task_tracker.py list not-done                 - List tasks that are not done")
    
    def _add_task(self, description: str) -> None:
        """
        Add a new task.
        
        Args:
            description: Description of the task.
        """
        task = self.repository.add_task(description)
        print(f"Task added successfully with ID: {task.task_id}")
    
    def _update_task_status(self, task_id: str, status_str: str) -> None:
        """
        Update a task's status.
        
        Args:
            task_id: ID of the task to update.
            status_str: New status string.
        """
        try:
            status = TaskStatus(status_str)
            task = self.repository.update_task(task_id, status=status)
            if task:
                print(f"Task '{task_id}' status updated to '{status.value}'")
            else:
                print(f"Task with ID '{task_id}' not found")
        except ValueError:
            print(f"Error: Invalid status '{status_str}'. Use 'todo', 'in-progress', or 'done'.")
    
    def _update_task_description(self, task_id: str, description: str) -> None:
        """
        Update a task's description.
        
        Args:
            task_id: ID of the task to update.
            description: New description.
        """
        task = self.repository.update_task(task_id, description=description)
        if task:
            print(f"Task '{task_id}' description updated")
        else:
            print(f"Task with ID '{task_id}' not found")
    
    def _delete_task(self, task_id: str) -> None:
        """
        Delete a task.
        
        Args:
            task_id: ID of the task to delete.
        """
        success = self.repository.delete_task(task_id)
        if success:
            print(f"Task '{task_id}' deleted successfully")
        else:
            print(f"Task with ID '{task_id}' not found")
    
    def _list_all_tasks(self) -> None:
        """
        List all tasks.
        """
        tasks = self.repository.get_all_tasks()
        if not tasks:
            print("No tasks found")
            return
        
        print("All Tasks:")
        self._print_tasks(tasks)
    
    def _list_tasks_by_filter(self, filter_str: str) -> None:
        """
        List tasks by filter criteria.
        
        Args:
            filter_str: Filter string (todo, in-progress, done, not-done).
        """
        tasks = []
        
        if filter_str == "todo":
            tasks = self.repository.get_tasks_by_status(TaskStatus.TODO)
            print("Todo Tasks:")
        elif filter_str == "in-progress":
            tasks = self.repository.get_tasks_by_status(TaskStatus.IN_PROGRESS)
            print("In-Progress Tasks:")
        elif filter_str == "done":
            tasks = self.repository.get_tasks_by_status(TaskStatus.DONE)
            print("Done Tasks:")
        elif filter_str == "not-done":
            todo_tasks = self.repository.get_tasks_by_status(TaskStatus.TODO)
            in_progress_tasks = self.repository.get_tasks_by_status(TaskStatus.IN_PROGRESS)
            tasks = todo_tasks + in_progress_tasks
            print("Not Done Tasks:")
        else:
            print(f"Error: Unknown filter '{filter_str}'")
            return
        
        if not tasks:
            print("No tasks found")
            return
        
        self._print_tasks(tasks)
    
    def _print_tasks(self, tasks: List[Task]) -> None:
        """
        Print a list of tasks in a formatted way.
        
        Args:
            tasks: List of tasks to print.
        """
        for task in tasks:
            created_date = datetime.fromisoformat(task.created_at).strftime("%Y-%m-%d %H:%M")
            updated_date = datetime.fromisoformat(task.updated_at).strftime("%Y-%m-%d %H:%M")
            print(f"ID: {task.task_id}")
            print(f"Description: {task.description}")
            print(f"Status: {task.status.value}")
            print(f"Created: {created_date}")
            print(f"Updated: {updated_date}")
            print("-" * 40)


def main() -> None:
    """
    Main entry point for the Task Tracker CLI application.
    """
    file_path = "tasks.json"
    repository = TaskRepository(file_path)
    cli = TaskTrackerCLI(repository)
    cli.execute(sys.argv)


if __name__ == "__main__":
    main()