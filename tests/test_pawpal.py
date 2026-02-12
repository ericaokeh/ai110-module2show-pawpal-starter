"""
Unit tests for PawPal+ System
Tests core functionality of the pet care scheduling system
"""

import unittest
from datetime import date
from pawpal_system import Owner, Pet, Task, DailySchedule, Scheduler


class TestTaskCompletion(unittest.TestCase):
    """Test task completion functionality."""

    def test_mark_complete_changes_status(self):
        """Verify that calling mark_complete() actually changes the task's status."""
        # Create a task (initially incomplete)
        task = Task(
            name="Feed cat",
            category="feeding",
            duration=10,
            priority=5,
            frequency="daily"
        )

        # Verify initial state
        self.assertFalse(task.is_completed(), "Task should start as incomplete")
        self.assertFalse(task.completed, "Task.completed should be False initially")

        # Mark as complete
        task.mark_complete()

        # Verify completion
        self.assertTrue(task.is_completed(), "Task should be completed after mark_complete()")
        self.assertTrue(task.completed, "Task.completed should be True after mark_complete()")

    def test_mark_incomplete_resets_status(self):
        """Verify that mark_incomplete() resets a completed task."""
        # Create and complete a task
        task = Task("Walk dog", "walk", 30, 5)
        task.mark_complete()

        # Verify it's completed
        self.assertTrue(task.is_completed())

        # Reset to incomplete
        task.mark_incomplete()

        # Verify it's incomplete again
        self.assertFalse(task.is_completed(), "Task should be incomplete after mark_incomplete()")


class TestDailyScheduleTaskAddition(unittest.TestCase):
    """Test adding tasks to a daily schedule."""

    def setUp(self):
        """Set up common test fixtures."""
        self.owner = Owner("Alice", available_hours_per_day=4)
        self.pet = Pet("Buddy", "Dog", 5)
        self.schedule = DailySchedule(date.today(), self.owner, self.pet)

    def test_adding_task_increases_task_count(self):
        """Verify that adding a task to a DailySchedule increases the task count."""
        # Create a task
        task = Task("Morning walk", "walk", 30, 5)

        # Verify initial state
        initial_count = len(self.schedule.scheduled_tasks)
        self.assertEqual(initial_count, 0, "Schedule should start with 0 tasks")

        # Add task
        result = self.schedule.add_task(task, "morning")

        # Verify task was added
        self.assertTrue(result, "add_task() should return True on success")
        self.assertEqual(
            len(self.schedule.scheduled_tasks),
            initial_count + 1,
            "Task count should increase by 1 after adding a task"
        )

    def test_adding_task_updates_total_duration(self):
        """Verify that adding a task updates the total duration."""
        # Create tasks
        task1 = Task("Feed dog", "feeding", 10, 5)  # 10 minutes = 0.167 hours
        task2 = Task("Walk dog", "walk", 30, 4)     # 30 minutes = 0.5 hours

        # Initial duration should be 0
        self.assertEqual(self.schedule.get_total_duration(), 0.0)

        # Add first task
        self.schedule.add_task(task1, "morning")
        self.assertAlmostEqual(
            self.schedule.get_total_duration(),
            10/60.0,
            places=2,
            msg="Total duration should be 0.17 hours after adding 10-minute task"
        )

        # Add second task
        self.schedule.add_task(task2, "afternoon")
        expected_total = (10 + 30) / 60.0  # 40 minutes = 0.667 hours
        self.assertAlmostEqual(
            self.schedule.get_total_duration(),
            expected_total,
            places=2,
            msg="Total duration should be 0.67 hours after adding both tasks"
        )

    def test_removing_task_decreases_count(self):
        """Verify that removing a task decreases the task count."""
        # Add some tasks
        task1 = Task("Morning walk", "walk", 30, 5)
        task2 = Task("Evening walk", "walk", 30, 4)

        self.schedule.add_task(task1, "morning")
        self.schedule.add_task(task2, "evening")

        # Verify we have 2 tasks
        self.assertEqual(len(self.schedule.scheduled_tasks), 2)

        # Remove one task
        result = self.schedule.remove_task(task1)

        # Verify removal
        self.assertTrue(result, "remove_task() should return True on success")
        self.assertEqual(
            len(self.schedule.scheduled_tasks),
            1,
            "Task count should decrease by 1 after removing a task"
        )


class TestSchedulerFiltersCompletedTasks(unittest.TestCase):
    """Test that scheduler correctly filters completed tasks."""

    def test_scheduler_excludes_completed_tasks_by_default(self):
        """Verify that generate_plan() excludes completed tasks by default."""
        owner = Owner("Bob", available_hours_per_day=3)
        pet = Pet("Max", "Dog", 3)

        # Create tasks
        task1 = Task("Feed dog", "feeding", 10, 5, frequency="daily")
        task2 = Task("Walk dog", "walk", 30, 5, frequency="daily")
        task3 = Task("Brush dog", "grooming", 15, 3, frequency="daily")

        # Mark one as completed
        task1.mark_complete()

        # Create scheduler
        tasks = [task1, task2, task3]
        scheduler = Scheduler(owner, pet, tasks)

        # Generate plan (should exclude completed tasks by default)
        schedule = scheduler.generate_plan()

        # Verify only incomplete tasks are scheduled
        scheduled_task_objects = [task for time, task in schedule.scheduled_tasks]

        self.assertNotIn(task1, scheduled_task_objects, "Completed task should not be in schedule")
        self.assertIn(task2, scheduled_task_objects, "Incomplete task should be in schedule")
        self.assertIn(task3, scheduled_task_objects, "Incomplete task should be in schedule")
        self.assertEqual(len(scheduled_task_objects), 2, "Should have 2 incomplete tasks scheduled")


class TestRecurringTasks(unittest.TestCase):
    """Test recurring task functionality."""

    def setUp(self):
        """Set up common test fixtures."""
        self.owner = Owner("Jordan", available_hours_per_day=4)
        self.pet = Pet("Luna", "Cat", 2)

    def test_daily_task_creates_new_instance(self):
        """Verify that completing a daily task creates a new instance for tomorrow."""
        task = Task("Feed breakfast", "feeding", 10, 5, frequency="daily")
        scheduler = Scheduler(self.owner, self.pet, [task])

        # Complete the task
        new_task = scheduler.complete_task(task)

        # Verify new instance was created
        self.assertIsNotNone(new_task, "Completing daily task should create new instance")
        self.assertEqual(len(scheduler.tasks), 2, "Should have 2 tasks after completing daily task")

        # Verify original task is completed
        self.assertTrue(task.is_completed(), "Original task should be completed")

        # Verify new task is incomplete
        self.assertFalse(new_task.is_completed(), "New task should be incomplete")

        # Verify new task has correct due date (tomorrow)
        self.assertIsNotNone(new_task.due_date, "New task should have a due date")
        expected_due = date.today() + __import__('datetime').timedelta(days=1)
        self.assertEqual(new_task.due_date, expected_due, "Daily task should be due tomorrow")

    def test_weekly_task_creates_new_instance(self):
        """Verify that completing a weekly task creates a new instance for next week."""
        task = Task("Weekly grooming", "grooming", 30, 3, frequency="weekly")
        scheduler = Scheduler(self.owner, self.pet, [task])

        # Complete the task
        new_task = scheduler.complete_task(task)

        # Verify new instance was created
        self.assertIsNotNone(new_task, "Completing weekly task should create new instance")
        self.assertEqual(len(scheduler.tasks), 2, "Should have 2 tasks after completing weekly task")

        # Verify new task has correct due date (next week)
        expected_due = date.today() + __import__('datetime').timedelta(weeks=1)
        self.assertEqual(new_task.due_date, expected_due, "Weekly task should be due next week")

    def test_monthly_task_creates_new_instance(self):
        """Verify that completing a monthly task creates a new instance for next month."""
        task = Task("Monthly vet visit", "medical", 60, 4, frequency="monthly")
        scheduler = Scheduler(self.owner, self.pet, [task])

        # Complete the task
        new_task = scheduler.complete_task(task)

        # Verify new instance was created
        self.assertIsNotNone(new_task, "Completing monthly task should create new instance")
        self.assertEqual(len(scheduler.tasks), 2, "Should have 2 tasks after completing monthly task")

        # Verify new task has correct due date (30 days from now)
        expected_due = date.today() + __import__('datetime').timedelta(days=30)
        self.assertEqual(new_task.due_date, expected_due, "Monthly task should be due in 30 days")

    def test_one_time_task_does_not_create_new_instance(self):
        """Verify that completing a one-time task does NOT create a new instance."""
        task = Task("One-time nail trim", "grooming", 15, 3, frequency="once")
        scheduler = Scheduler(self.owner, self.pet, [task])

        # Complete the task
        new_task = scheduler.complete_task(task)

        # Verify NO new instance was created
        self.assertIsNone(new_task, "One-time task should NOT create new instance")
        self.assertEqual(len(scheduler.tasks), 1, "Should still have only 1 task")
        self.assertTrue(task.is_completed(), "Original task should be completed")

    def test_new_recurring_task_has_same_attributes(self):
        """Verify that new recurring task instance has same attributes as original."""
        original = Task(
            "Morning walk",
            "walk",
            30,
            5,
            preferred_time="morning",
            notes="Important walk",
            frequency="daily"
        )
        scheduler = Scheduler(self.owner, self.pet, [original])

        # Complete the task
        new_task = scheduler.complete_task(original)

        # Verify new task has same attributes (except completion status and due date)
        self.assertEqual(new_task.name, original.name)
        self.assertEqual(new_task.category, original.category)
        self.assertEqual(new_task.duration, original.duration)
        self.assertEqual(new_task.priority, original.priority)
        self.assertEqual(new_task.preferred_time, original.preferred_time)
        self.assertEqual(new_task.notes, original.notes)
        self.assertEqual(new_task.frequency, original.frequency)
        self.assertFalse(new_task.is_completed(), "New task should be incomplete")
        self.assertNotEqual(new_task.due_date, original.due_date, "New task should have different due date")


class TestConflictDetection(unittest.TestCase):
    """Test scheduling conflict detection."""

    def setUp(self):
        """Set up common test fixtures."""
        self.owner = Owner("Alex", available_hours_per_day=6)
        self.pet = Pet("Buddy", "Dog", 5)

    def test_no_conflicts_with_well_distributed_tasks(self):
        """Verify that well-distributed tasks produce no conflict warnings."""
        tasks = [
            Task("Morning walk", "walk", 30, 5, preferred_time="morning"),
            Task("Breakfast", "feeding", 10, 5, preferred_time="morning"),
            Task("Afternoon walk", "walk", 30, 4, preferred_time="afternoon"),
            Task("Dinner", "feeding", 10, 5, preferred_time="evening"),
        ]
        scheduler = Scheduler(self.owner, self.pet, tasks)

        conflicts = scheduler.detect_conflicts()

        self.assertEqual(len(conflicts), 0, "Well-distributed tasks should have no conflicts")

    def test_conflict_when_too_many_tasks_in_period(self):
        """Verify that >3 tasks in same period generates a warning."""
        tasks = [
            Task("Task 1", "walk", 30, 5, preferred_time="morning"),
            Task("Task 2", "feeding", 30, 5, preferred_time="morning"),
            Task("Task 3", "medication", 30, 5, preferred_time="morning"),
            Task("Task 4", "grooming", 30, 4, preferred_time="morning"),
            Task("Task 5", "enrichment", 30, 3, preferred_time="morning"),
        ]
        scheduler = Scheduler(self.owner, self.pet, tasks)

        conflicts = scheduler.detect_conflicts()

        self.assertGreater(len(conflicts), 0, "5 tasks in morning should generate conflict warning")
        self.assertTrue(
            any("morning" in warning.lower() for warning in conflicts),
            "Warning should mention 'morning' time period"
        )

    def test_conflict_when_duration_exceeds_period(self):
        """Verify that tasks exceeding period duration generate a warning."""
        tasks = [
            # Total: 300 minutes (5 hours) - exceeds 4-hour morning period
            Task("Long walk", "walk", 120, 5, preferred_time="morning"),
            Task("Training", "enrichment", 120, 4, preferred_time="morning"),
            Task("Grooming", "grooming", 60, 3, preferred_time="morning"),
        ]
        scheduler = Scheduler(self.owner, self.pet, tasks)

        conflicts = scheduler.detect_conflicts()

        self.assertGreater(len(conflicts), 0, "Tasks exceeding period duration should generate warning")
        self.assertTrue(
            any("exceed" in warning.lower() or "conflict" in warning.lower() for warning in conflicts),
            "Warning should mention conflict or exceeding duration"
        )

    def test_no_conflict_at_exact_period_threshold(self):
        """Verify that tasks exactly at the 4-hour threshold don't trigger warning."""
        tasks = [
            # Total: exactly 240 minutes (4 hours)
            Task("Task 1", "walk", 120, 5, preferred_time="afternoon"),
            Task("Task 2", "enrichment", 120, 4, preferred_time="afternoon"),
        ]
        scheduler = Scheduler(self.owner, self.pet, tasks)

        conflicts = scheduler.detect_conflicts()

        # Should not trigger duration-based warning (exactly at threshold)
        # Might still warn about number of tasks, but not about exceeding duration
        duration_conflicts = [w for w in conflicts if "exceed" in w.lower()]
        self.assertEqual(len(duration_conflicts), 0, "Tasks at exact threshold should not exceed warning")

    def test_conflict_detection_with_completed_tasks(self):
        """Verify that completed tasks are not checked for conflicts by default."""
        tasks = [
            Task("Morning task 1", "walk", 60, 5, preferred_time="morning", completed=True),
            Task("Morning task 2", "feeding", 60, 5, preferred_time="morning", completed=True),
            Task("Morning task 3", "medication", 60, 5, preferred_time="morning", completed=True),
            Task("Morning task 4", "grooming", 60, 4, preferred_time="morning", completed=True),
            # All completed - should not trigger conflicts since we check incomplete by default
        ]
        scheduler = Scheduler(self.owner, self.pet, tasks)

        # Default behavior: only check incomplete tasks
        conflicts = scheduler.detect_conflicts()

        self.assertEqual(len(conflicts), 0, "Completed tasks should not generate conflicts by default")

    def test_conflict_detection_returns_list_of_strings(self):
        """Verify that detect_conflicts returns a list of string warnings."""
        tasks = [
            Task("Task 1", "walk", 90, 5, preferred_time="morning"),
            Task("Task 2", "feeding", 90, 5, preferred_time="morning"),
            Task("Task 3", "grooming", 90, 4, preferred_time="morning"),
        ]
        scheduler = Scheduler(self.owner, self.pet, tasks)

        conflicts = scheduler.detect_conflicts()

        self.assertIsInstance(conflicts, list, "detect_conflicts should return a list")
        for conflict in conflicts:
            self.assertIsInstance(conflict, str, "Each conflict should be a string")


if __name__ == "__main__":
    unittest.main()
