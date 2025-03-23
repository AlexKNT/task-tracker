"""
Tests for the Task Tracker CLI application.
"""

import json
import os
import unittest
from datetime import datetime
from unittest.mock import patch

from task_tracker import Task, TaskRepository, TaskStatus, TaskTrackerCLI


class TestTask(unittest.TestCase):
    """
    Tests for the Task class.
    """
    
    def test_task_initialization(self):
        """Test that a task is correctly initialized with default values."""
        description = "Test task"
        task = Task(description=description)
        
        self.assertIsNotNone(task.task_id)
        self.assertEqual(task.description, description)
        self.assertEqual(task.status, TaskStatus.TODO)
        self.assertIsNotNone(task.created_at)
        self.assertEqual(task.created_at, task.updated_at)
    
    def test_task_to_dict(self):
        """Test that task is correctly converted to a dictionary."""
        task = Task(
            description="Test task",
            task_id="123",
            created_at="2023-01-01T12:00:00",
            updated_at="2023-01-01T12:00:00"
        )
        
        task_dict = task.to_dict()
        
        self.assertEqual(task_dict["id"], "123")
        self.assertEqual(task_dict["description"], "Test task")
        self.assertEqual(task_dict["status"], "todo")
        self.assertEqual(task_dict["createdAt"], "2023-01-01T12:00:00")
        self.assertEqual(task_dict["updatedAt"], "2023-01-01T12:00:00")
    
    def test_task_from_dict(self):
        """Test that a task is correctly created from a dictionary."""
        task_dict = {
            "id": "123",
            "description": "Test task",
            "status": "in-progress",
            "createdAt": "2023-01-01T12:00:00",
            "updatedAt": "2023-01-01T13:00:00"
        }
        
        task = Task.from_dict(task_dict)
        
        self.assertEqual(task.task_id, "123")
        self.assertEqual(task.description, "Test task")
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
        self.assertEqual(task.created_at, "2023-01-01T12:00:00")
        self.assertEqual(task.updated_at, "2023-01-01T13:00:00")
    
    def test_task_update(self):
        """Test that a task is correctly updated."""
        task = Task(
            description="Initial description",
            task_id="123",
            created_at="2023-01-01T12:00:00",
            updated_at="2023-01-01T12:00:00"
        )
        
        with patch('task_tracker.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.fromisoformat("2023-01-01T14:00:00")
            task.update(description="Updated description", status=TaskStatus.IN_PROGRESS)
        
        self.assertEqual(task.description, "Updated description")
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
        self.assertEqual(task.updated_at, "2023-01-01T14:00:00")
        self.assertEqual(task.created_at, "2023-01-01T12:00:00")  # Should remain unchanged


class TestTaskRepository(unittest.TestCase):
    """
    Tests for the TaskRepository class.
    """
    
    def setUp(self):
        """Set up a test repository with a temporary file."""
        self.test_file = "test_tasks.json"
        self.repository = TaskRepository(self.test_file)
    
    def tearDown(self):
        """Clean up by removing the test file."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_ensure_file_exists(self):
        """Test that the file is created if it doesn't exist."""
        self.assertTrue(os.path.exists(self.test_file))
        
        with open(self.test_file, 'r') as file:
            data = json.load(file)
            self.assertEqual(data, [])
    
    def test_add_task(self):
        """Test adding a task to the repository."""
        task = self.repository.add_task("Test task")
        
        self.assertIsNotNone(task.task_id)
        self.assertEqual(task.description, "Test task")
        
        # Verify task was saved to file
        tasks = self.repository.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].description, "Test task")
    
    def test_get_all_tasks(self):
        """Test retrieving all tasks from the repository."""
        self.repository.add_task("Task 1")
        self.repository.add_task("Task 2")
        
        tasks = self.repository.get_all_tasks()
        
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].description, "Task 1")
        self.assertEqual(tasks[1].description, "Task 2")
    
    def test_get_tasks_by_status(self):
        """Test retrieving tasks filtered by status."""
        task1 = self.repository.add_task("Task 1")
        task2 = self.repository.add_task("Task 2")
        self.repository.update_task(task1.task_id, status=TaskStatus.IN_PROGRESS)
        
        todo_tasks = self.repository.get_tasks_by_status(TaskStatus.TODO)
        in_progress_tasks = self.repository.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        done_tasks = self.repository.get_tasks_by_status(TaskStatus.DONE)
        
        self.assertEqual(len(todo_tasks), 1)
        self.assertEqual(todo_tasks[0].description, "Task 2")
        self.assertEqual(len(in_progress_tasks), 1)
        self.assertEqual(in_progress_tasks[0].description, "Task 1")
        self.assertEqual(len(done_tasks), 0)
    
    def test_get_task_by_id(self):
        """Test retrieving a task by ID."""
        task = self.repository.add_task("Test task")
        
        found_task = self.repository.get_task_by_id(task.task_id)
        not_found_task = self.repository.get_task_by_id("non-existent-id")
        
        self.assertIsNotNone(found_task)
        self.assertEqual(found_task.description, "Test task")
        self.assertIsNone(not_found_task)
    
    def test_update_task(self):
        """Test updating a task."""
        task = self.repository.add_task("Initial description")
        
        updated_task = self.repository.update_task(
            task.task_id,
            description="Updated description",
            status=TaskStatus.IN_PROGRESS
        )
        
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task.description, "Updated description")
        self.assertEqual(updated_task.status, TaskStatus.IN_PROGRESS)
        
        # Verify changes were saved
        tasks = self.repository.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].description, "Updated description")
        self.assertEqual(tasks[0].status, TaskStatus.IN_PROGRESS)
    
    def test_delete_task(self):
        """Test deleting a task."""
        task = self.repository.add_task("Test task")
        
        success = self.repository.delete_task(task.task_id)
        
        self.assertTrue(success)
        self.assertEqual(len(self.repository.get_all_tasks()), 0)
        
        # Try deleting non-existent task
        success = self.repository.delete_task("non-existent-id")
        self.assertFalse(success)


class TestTaskTrackerCLI(unittest.TestCase):
    """
    Tests for the TaskTrackerCLI class.
    """
    
    def setUp(self):
        """Set up a test CLI with a test repository."""
        self.test_file = "test_tasks.json"
        self.repository = TaskRepository(self.test_file)
        self.cli = TaskTrackerCLI(self.repository)
    
    def tearDown(self):
        """Clean up by removing the test file."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    @patch('builtins.print')
    def test_add_task_command(self, mock_print):
        """Test the add task command."""
        self.cli.execute(["program", "add", "Test", "task"])
        
        tasks = self.repository.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].description, "Test task")
        mock_print.assert_called_with(f"Task added successfully with ID: {tasks[0].task_id}")
    
    @patch('builtins.print')
    def test_update_task_status_command(self, mock_print):
        """Test the update task status command."""
        task = self.repository.add_task("Test task")
        
        self.cli.execute(["program", "update", task.task_id, "--status", "in-progress"])
        
        updated_task = self.repository.get_task_by_id(task.task_id)
        self.assertEqual(updated_task.status, TaskStatus.IN_PROGRESS)
        mock_print.assert_called_with(f"Task '{task.task_id}' status updated to 'in-progress'")
    
    @patch('builtins.print')
    def test_update_task_description_command(self, mock_print):
        """Test the update task description command."""
        task = self.repository.add_task("Initial description")
        
        self.cli.execute(["program", "update", task.task_id, "--description", "Updated", "description"])
        
        updated_task = self.repository.get_task_by_id(task.task_id)
        self.assertEqual(updated_task.description, "Updated description")
        mock_print.assert_called_with(f"Task '{task.task_id}' description updated")
    
    @patch('builtins.print')
    def test_delete_task_command(self, mock_print):
        """Test the delete task command."""
        task = self.repository.add_task("Test task")
        
        self.cli.execute(["program", "delete", task.task_id])
        
        tasks = self.repository.get_all_tasks()
        self.assertEqual(len(tasks), 0)
        mock_print.assert_called_with(f"Task '{task.task_id}' deleted successfully")
    
    @patch('builtins.print')
    def test_list_all_tasks_command(self, mock_print):
        """Test the list all tasks command."""
        self.repository.add_task("Task 1")
        self.repository.add_task("Task 2")
        
        self.cli.execute(["program", "list"])
        
        mock_print.assert_any_call("All Tasks:")
    
    @patch('builtins.print')
    def test_list_filtered_tasks_command(self, mock_print):
        """Test the list filtered tasks command."""
        task1 = self.repository.add_task("Task 1")
        self.repository.add_task("Task 2")
        self.repository.update_task(task1.task_id, status=TaskStatus.DONE)
        
        self.cli.execute(["program", "list", "done"])
        
        mock_print.assert_any_call("Done Tasks:")
        
        # Reset mock
        mock_print.reset_mock()
        
        self.cli.execute(["program", "list", "todo"])
        
        mock_print.assert_any_call("Todo Tasks:")


if __name__ == "__main__":
    unittest.main()