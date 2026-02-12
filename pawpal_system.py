"""
PawPal+ System - Pet Care Scheduling System
Class skeleton based on UML design
"""

from datetime import date as datetime_date, timedelta


# Constants for task priority
PRIORITY_MIN = 1
PRIORITY_MAX = 5


class Owner:
    """Represents a pet owner with available time and preferences."""

    def __init__(self, name, available_hours_per_day):
        """Initialize an Owner with name and available hours per day."""
        if available_hours_per_day < 0 or available_hours_per_day > 24:
            raise ValueError("Available hours must be between 0 and 24")
        self.name = name
        self.available_hours_per_day = float(available_hours_per_day)
        self.preferences = {}

    def get_available_time(self):
        """Return the available hours per day as a float."""
        return self.available_hours_per_day

    def update_preferences(self, preferences):
        """Update the owner's preferences."""
        if isinstance(preferences, dict):
            self.preferences.update(preferences)
        else:
            raise TypeError("Preferences must be a dictionary")

    def __str__(self):
        """Return a string representation of the Owner."""
        return f"Owner: {self.name} (Available: {self.available_hours_per_day} hrs/day)"


class Pet:
    """Represents a pet with basic information and special needs."""

    def __init__(self, name, species, age, special_needs=None):
        """Initialize a Pet with name, species, age, and optional special needs."""
        self.name = name
        self.species = species
        self.age = age
        self.special_needs = special_needs if special_needs is not None else []

    def get_info(self):
        """Return a dictionary containing pet information."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "special_needs": self.special_needs
        }

    def __str__(self):
        """Return a string representation of the Pet."""
        needs = f" (Special needs: {', '.join(self.special_needs)})" if self.special_needs else ""
        return f"{self.name} - {self.species}, {self.age} years old{needs}"


class Task:
    """Represents a pet care task with duration, priority, and other details."""

    def __init__(self, name, category, duration, priority, preferred_time=None, notes="", frequency="once", completed=False, due_date=None):
        """Initialize a Task with name, category, duration (in minutes), and priority.

        Args:
            name: Task name
            category: Category (e.g., 'walk', 'feeding', 'medication', 'grooming', 'enrichment')
            duration: Duration in minutes (must be positive)
            priority: Priority level (1-5, where 5 is highest priority)
            preferred_time: Optional preferred time of day (e.g., 'morning', 'afternoon', 'evening')
            notes: Optional notes about the task
            frequency: How often task occurs (e.g., 'once', 'daily', 'weekly', 'monthly')
            completed: Whether the task has been completed (default False)
            due_date: Optional due date (date object). If None, defaults to today for recurring tasks
        """
        if duration <= 0:
            raise ValueError("Duration must be positive")
        if not (PRIORITY_MIN <= priority <= PRIORITY_MAX):
            raise ValueError(f"Priority must be between {PRIORITY_MIN} and {PRIORITY_MAX}")

        self.name = name
        self.category = category
        self.duration = int(duration)  # in minutes
        self.priority = int(priority)
        self.preferred_time = preferred_time
        self.notes = notes
        self.frequency = frequency
        self.completed = completed

        # Set due date - default to today if not specified and task is recurring
        if due_date is None and frequency in ["daily", "weekly", "monthly"]:
            self.due_date = datetime_date.today()
        else:
            self.due_date = due_date

    def get_duration_hours(self):
        """Return the task duration in hours as a float."""
        return self.duration / 60.0

    def set_priority(self, priority):
        """Set the priority of the task."""
        if not (PRIORITY_MIN <= priority <= PRIORITY_MAX):
            raise ValueError(f"Priority must be between {PRIORITY_MIN} and {PRIORITY_MAX}")
        self.priority = int(priority)

    def mark_complete(self):
        """Mark the task as completed."""
        self.completed = True

    def mark_incomplete(self):
        """Mark the task as incomplete."""
        self.completed = False

    def is_completed(self):
        """Return whether the task is completed."""
        return self.completed

    def __str__(self):
        """Return a string representation of the Task."""
        time_info = f" [{self.preferred_time}]" if self.preferred_time else ""
        status = "✓" if self.completed else "○"
        freq_info = f" ({self.frequency})" if self.frequency != "once" else ""
        due_info = f" Due: {self.due_date}" if self.due_date else ""
        return f"{status} {self.name} ({self.category}) - {self.duration}min, Priority: {self.priority}{time_info}{freq_info}{due_info}"

    def __lt__(self, other):
        """Compare tasks for sorting (less than).

        Higher priority tasks are "less than" lower priority tasks (for descending sort).
        If priorities are equal, shorter tasks come first.
        """
        if not isinstance(other, Task):
            return NotImplemented
        if self.priority != other.priority:
            return self.priority > other.priority  # Higher priority comes first
        return self.duration < other.duration  # Shorter duration comes first

    def __eq__(self, other):
        """Compare tasks for equality.

        Note: Completion status is not included in equality check,
        as the same task definition can be completed or incomplete.
        """
        if not isinstance(other, Task):
            return NotImplemented
        return (self.name == other.name and
                self.category == other.category and
                self.duration == other.duration and
                self.priority == other.priority and
                self.frequency == other.frequency)


class DailySchedule:
    """Represents a daily schedule for a pet owner and their pet."""

    def __init__(self, schedule_date, owner, pet):
        """Initialize a DailySchedule for a specific date, owner, and pet.

        Args:
            schedule_date: The date for this schedule (date object or None for today)
            owner: Owner object
            pet: Pet object
        """
        self.date = schedule_date if schedule_date else datetime_date.today()
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks = []  # List of (time_str, task) tuples
        self.total_duration = 0.0  # Total hours
        self.explanation = ""

    def add_task(self, task, time=None):
        """Add a task to the schedule at a specific time. Returns True if successful.

        Args:
            task: Task object to add
            time: Optional time string (e.g., '9:00 AM', 'morning'). If None, uses preferred_time or 'Unscheduled'

        Returns:
            True if task was added successfully
        """
        if time is None:
            time = task.preferred_time if task.preferred_time else "Unscheduled"

        self.scheduled_tasks.append((time, task))
        self.total_duration += task.get_duration_hours()
        return True

    def remove_task(self, task):
        """Remove a task from the schedule."""
        # Find and remove the task from scheduled_tasks
        for i, (time, scheduled_task) in enumerate(self.scheduled_tasks):
            if scheduled_task == task:
                self.scheduled_tasks.pop(i)
                self.total_duration -= task.get_duration_hours()
                return True
        return False

    def get_total_duration(self):
        """Return the total duration of all scheduled tasks in hours."""
        return self.total_duration

    def is_feasible(self):
        """Check if the schedule is feasible within available time. Returns bool."""
        return self.total_duration <= self.owner.get_available_time()

    def display_schedule(self):
        """Return a formatted string displaying the schedule."""
        lines = [
            f"Daily Schedule for {self.pet.name} - {self.date}",
            f"Owner: {self.owner.name} (Available: {self.owner.get_available_time()} hours)",
            f"Total scheduled: {self.total_duration:.2f} hours",
            f"Feasible: {'Yes' if self.is_feasible() else 'No - exceeds available time!'}",
            "",
            "Tasks:"
        ]

        if not self.scheduled_tasks:
            lines.append("  No tasks scheduled")
        else:
            for time, task in self.scheduled_tasks:
                lines.append(f"  {time}: {task}")

        return "\n".join(lines)

    def get_explanation(self):
        """Return an explanation of the schedule."""
        return self.explanation

    def __str__(self):
        """Return a string representation of the DailySchedule."""
        status = "✓ Feasible" if self.is_feasible() else "✗ Over capacity"
        return f"Schedule ({self.date}): {len(self.scheduled_tasks)} tasks, {self.total_duration:.1f}hrs [{status}]"


class Scheduler:
    """Generates and optimizes daily schedules for pet care tasks."""

    def __init__(self, owner, pet, tasks):
        """Initialize a Scheduler with an owner, pet, and list of tasks.

        Args:
            owner: Owner object
            pet: Pet object
            tasks: List of Task objects to schedule
        """
        self.owner = owner
        self.pet = pet
        self.tasks = tasks if tasks else []
        self.explanation_log = []

    def generate_plan(self, schedule_date=None, include_completed=False):
        """Generate a daily schedule plan. Returns a DailySchedule object.

        Args:
            schedule_date: Optional date for the schedule (defaults to today)
            include_completed: If False (default), only schedule incomplete tasks

        Returns:
            DailySchedule object with optimized task schedule
        """
        # Clear previous explanations
        self.explanation_log = []
        self._log_explanation(f"Generating schedule for {self.pet.name}")
        self._log_explanation(f"Owner has {self.owner.get_available_time()} hours available")

        # Filter tasks based on completion status
        tasks_to_schedule = self.tasks if include_completed else self.get_incomplete_tasks()
        completed_count = len(self.tasks) - len(tasks_to_schedule)

        self._log_explanation(f"Total tasks: {len(self.tasks)} ({completed_count} completed, {len(tasks_to_schedule)} to schedule)")

        # Step 1: Prioritize tasks
        sorted_tasks = self.prioritize_tasks(tasks_to_schedule)

        # Step 2: Fit to time constraints
        selected_tasks = self.fit_to_time_constraint(sorted_tasks)

        # Step 3: Optimize ordering
        optimized_tasks = self.optimize_schedule(selected_tasks)

        # Step 4: Detect conflicts
        conflicts = self.detect_conflicts(optimized_tasks)
        if conflicts:
            self._log_explanation("\n⚠️  SCHEDULING CONFLICTS DETECTED:")
            for warning in conflicts:
                self._log_explanation(warning)
        else:
            self._log_explanation("✓ No scheduling conflicts detected")

        # Step 5: Create schedule
        schedule = DailySchedule(schedule_date, self.owner, self.pet)
        for task in optimized_tasks:
            schedule.add_task(task)

        # Add explanation to schedule
        schedule.explanation = self.explain_reasoning()

        return schedule

    def get_incomplete_tasks(self):
        """Get all incomplete tasks.

        Returns:
            List of tasks where completed=False
        """
        return [task for task in self.tasks if not task.is_completed()]

    def get_tasks_by_frequency(self, frequency):
        """Get all tasks with a specific frequency.

        Args:
            frequency: The frequency to filter by (e.g., 'daily', 'weekly')

        Returns:
            List of tasks matching the frequency
        """
        return [task for task in self.tasks if task.frequency == frequency]

    def get_tasks_by_category(self, category):
        """Filter tasks by category.

        Args:
            category: The category to filter by (e.g., 'walk', 'feeding', 'medication')

        Returns:
            List of tasks matching the category
        """
        return [task for task in self.tasks if task.category == category]

    def get_tasks_by_completion(self, completed=False):
        """Filter tasks by completion status.

        Args:
            completed: If True, return completed tasks. If False, return incomplete tasks.

        Returns:
            List of tasks matching the completion status
        """
        return [task for task in self.tasks if task.is_completed() == completed]

    def get_completed_tasks(self):
        """Get all completed tasks.

        Returns:
            List of completed tasks
        """
        return self.get_tasks_by_completion(completed=True)

    def complete_task(self, task):
        """Mark a task as complete and create a new instance for recurring tasks.

        For tasks with frequency 'daily', 'weekly', or 'monthly', automatically
        creates a new incomplete instance for the next occurrence with an updated due date.

        Args:
            task: Task object to mark as complete

        Returns:
            The newly created task if recurring, otherwise None
        """
        # Mark the original task as complete
        task.mark_complete()

        # Check if this is a recurring task that should generate a new instance
        if task.frequency in ["daily", "weekly", "monthly"]:
            # Calculate next due date based on frequency
            current_due = task.due_date if task.due_date else datetime_date.today()

            if task.frequency == "daily":
                next_due = current_due + timedelta(days=1)
            elif task.frequency == "weekly":
                next_due = current_due + timedelta(weeks=1)
            elif task.frequency == "monthly":
                # Approximate monthly as 30 days
                next_due = current_due + timedelta(days=30)

            # Create a new instance for the next occurrence
            new_task = Task(
                name=task.name,
                category=task.category,
                duration=task.duration,
                priority=task.priority,
                preferred_time=task.preferred_time,
                notes=task.notes,
                frequency=task.frequency,
                completed=False,  # New task starts as incomplete
                due_date=next_due
            )

            # Add the new task to the scheduler's task list
            self.tasks.append(new_task)

            return new_task

        return None

    def prioritize_tasks(self, tasks_to_sort=None):
        """Prioritize and sort tasks. Returns a list of prioritized tasks.

        Tasks are sorted by:
        1. Priority (higher first)
        2. Duration (shorter first for same priority)

        Args:
            tasks_to_sort: Optional list of tasks to sort. If None, uses all tasks.
        """
        if tasks_to_sort is None:
            tasks_to_sort = self.tasks

        sorted_tasks = sorted(tasks_to_sort)  # Uses Task.__lt__
        self._log_explanation(f"Sorted {len(sorted_tasks)} tasks by priority and duration")

        if sorted_tasks:
            top_task = sorted_tasks[0]
            self._log_explanation(f"Highest priority: {top_task.name} (Priority {top_task.priority})")

        return sorted_tasks

    def fit_to_time_constraint(self, sorted_tasks):
        """Fit tasks to time constraints. Returns a list of selected tasks.

        Implements a greedy algorithm: select highest priority tasks
        until time constraint is reached.

        Args:
            sorted_tasks: List of tasks already sorted by priority

        Returns:
            List of tasks that fit within available time
        """
        selected = []
        total_hours = 0.0
        available = self.owner.get_available_time()

        for task in sorted_tasks:
            task_hours = task.get_duration_hours()
            if total_hours + task_hours <= available:
                selected.append(task)
                total_hours += task_hours
                self._log_explanation(f"✓ Included: {task.name} ({task_hours:.2f}h)")
            else:
                self._log_explanation(f"✗ Skipped: {task.name} (would exceed time limit)")

        self._log_explanation(f"Selected {len(selected)}/{len(sorted_tasks)} tasks ({total_hours:.2f}/{available:.2f} hours)")

        return selected

    def optimize_schedule(self, selected_tasks):
        """Optimize the order of selected tasks. Returns a list of optimized tasks.

        Sorts tasks by preferred time (morning → afternoon → evening),
        then by priority within each time slot.

        Args:
            selected_tasks: List of tasks that fit time constraints

        Returns:
            List of tasks in optimized order
        """
        # Define time order for sorting
        time_order = {"morning": 1, "afternoon": 2, "evening": 3, None: 4, "": 4}

        # Sort by time first, then by priority (descending), then by duration (ascending)
        optimized = sorted(
            selected_tasks,
            key=lambda task: (
                time_order.get(task.preferred_time, 4),  # Sort by time period
                -task.priority,                           # Then by priority (higher first)
                task.duration                             # Then by duration (shorter first)
            )
        )

        self._log_explanation(f"Optimized order: grouped by time (morning → afternoon → evening), then by priority")

        return optimized

    def explain_reasoning(self):
        """Return an explanation of the scheduling reasoning as a string."""
        return "\n".join(self.explanation_log)

    def _log_explanation(self, message):
        """Add a message to the explanation log (private helper method)."""
        self.explanation_log.append(message)

    def detect_conflicts(self, tasks_to_check=None):
        """Detect potential scheduling conflicts between tasks.

        A lightweight conflict detection strategy that checks if tasks with the same
        preferred time period might overlap. Returns warnings rather than raising exceptions.

        Args:
            tasks_to_check: Optional list of tasks to check. If None, checks all incomplete tasks.

        Returns:
            List of warning messages (strings) describing conflicts. Empty list if no conflicts.
        """
        if tasks_to_check is None:
            tasks_to_check = self.get_incomplete_tasks()

        warnings = []

        # Constants for typical period lengths (in hours)
        PERIOD_LENGTHS = {
            "morning": 4.0,
            "afternoon": 4.0,
            "evening": 4.0,
            "unscheduled": 24.0
        }

        # Group tasks by their preferred time period
        time_groups = {}
        for task in tasks_to_check:
            time_period = task.preferred_time if task.preferred_time else "unscheduled"
            if time_period not in time_groups:
                time_groups[time_period] = []
            time_groups[time_period].append(task)

        # Check each time period for potential conflicts
        for time_period, tasks in time_groups.items():
            if len(tasks) <= 1:
                continue  # No conflicts possible with 0-1 tasks

            # Calculate total duration and get task names once
            total_hours = sum(task.duration for task in tasks) / 60.0
            period_length = PERIOD_LENGTHS.get(time_period, 24.0)
            task_names = ", ".join(task.name for task in tasks)

            if total_hours > period_length:
                warnings.append(
                    f"⚠️  Conflict in {time_period}: {len(tasks)} tasks ({total_hours:.1f}h total) "
                    f"may exceed typical {period_length}h period - {task_names}"
                )
            elif len(tasks) > 3 and time_period != "unscheduled":
                # Warn if many tasks in same period (even if duration fits)
                warnings.append(
                    f"⚠️  Notice: {len(tasks)} tasks scheduled for {time_period} - "
                    f"consider spreading across periods: {task_names}"
                )

        return warnings
