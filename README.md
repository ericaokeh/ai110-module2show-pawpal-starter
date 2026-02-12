# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

PawPal+ is a production-ready pet care scheduling system with advanced algorithmic capabilities and a professional Streamlit UI.

### Core Scheduling Algorithms

#### **1. Priority-Based Task Sorting**
- **Algorithm**: Two-level sorting using custom `__lt__()` comparison
  - **Primary sort**: Priority (5 = highest → 1 = lowest)
  - **Secondary sort**: Duration (shortest → longest)
- **Implementation**: `Task.__lt__()` and `Scheduler.prioritize_tasks()`
- **Use case**: Ensures high-priority, quick tasks get scheduled first
- **Complexity**: O(n log n) using Python's Timsort

#### **2. Greedy Time Constraint Fitting**
- **Algorithm**: Greedy selection to maximize task completion
  - Iterates through sorted tasks (high priority first)
  - Adds task if it fits within remaining available time
  - Stops when time budget is exhausted
- **Implementation**: `Scheduler.fit_to_time_constraint()`
- **Use case**: Fits maximum number of high-priority tasks into owner's available hours
- **Complexity**: O(n) linear scan through sorted tasks

#### **3. Time Period Optimization**
- **Algorithm**: Multi-key sorting for chronological grouping
  - Groups tasks by time period: morning → afternoon → evening → unscheduled
  - Within each period, sorts by priority (high → low)
  - Within same priority, sorts by duration (short → long)
- **Implementation**: `Scheduler.optimize_schedule()`
- **Use case**: Creates realistic daily schedule that flows naturally through the day
- **Complexity**: O(n log n) sorting with composite key

#### **4. Conflict Detection Strategy**
- **Algorithm**: Lightweight warning system with two detection rules
  - **Rule 1**: Time period overflow - warns if tasks exceed typical period length (4 hours)
  - **Rule 2**: Task clustering - warns if >3 tasks scheduled in same period
- **Implementation**: `Scheduler.detect_conflicts()`
- **Approach**: Non-blocking warnings (returns list of strings, doesn't raise exceptions)
- **Use case**: Guides users to balance schedules without preventing schedule generation
- **Complexity**: O(n) single pass grouping by time period

#### **5. Recurring Task Management**
- **Algorithm**: Factory pattern for task regeneration
  - Marks original task as complete
  - Creates new Task instance with updated due date based on frequency:
    - Daily: `due_date + 1 day`
    - Weekly: `due_date + 7 days`
    - Monthly: `due_date + 30 days`
  - Preserves all task attributes (name, category, duration, priority, etc.)
- **Implementation**: `Scheduler.complete_task()`
- **Use case**: Automates recurring task lifecycle for daily pet care routines
- **Pattern**: Factory pattern - creates new objects rather than modifying existing ones

### Data Management Features

#### **Task Filtering**
- Filter by **category**: walk, feeding, medication, grooming, enrichment, cleaning
- Filter by **completion status**: incomplete, completed, all
- Filter by **frequency**: once, daily, weekly, monthly
- **Methods**: `get_tasks_by_category()`, `get_tasks_by_completion()`, `get_tasks_by_frequency()`

#### **Task State Management**
- Track completion status with `mark_complete()` / `mark_incomplete()`
- Query completion state with `is_completed()`
- Separate incomplete/completed tasks for focused scheduling

#### **Schedule Analytics**
- Total time required for incomplete tasks
- Task distribution by category, frequency, and time period
- Feasibility checks (scheduled duration ≤ available time)

### User Interface Features

#### **Streamlit Web App**
- **Owner & Pet Setup**: Configure owner availability and pet information
- **Task Management**: Add, edit, complete, and delete tasks
- **Interactive Filtering**:
  - Filter by category, status, frequency
  - Sort by priority, duration, or time period
  - Real-time task count and preview
- **Visual Schedule Display**:
  - Grouped by time period (morning/afternoon/evening)
  - Metrics dashboard with task counts and time calculations
  - Color-coded conflict warnings with actionable suggestions
- **Analytics Dashboard**:
  - Task breakdown by category, frequency, and time period
  - Time distribution visualization
  - Completion tracking

#### **Conflict Warning System**
- **Error-level warnings** (red) for time overflows
- **Warning-level notifications** (yellow) for heavy schedules
- **Actionable recommendations**: 5 specific strategies to resolve conflicts
- **User-friendly explanations**: Plain language describing what conflicts mean

### Advanced Behaviors

#### **Automatic Task Regeneration**
- Completing a daily task creates tomorrow's instance
- Completing a weekly task creates next week's instance
- Completing a monthly task creates next month's instance
- One-time tasks do NOT regenerate

#### **Intelligent Schedule Explanation**
- Logs each scheduling decision (filtering, sorting, fitting, optimizing)
- Explains which tasks were included/excluded and why
- Displays reasoning in expandable UI panel

#### **Edge Case Handling**
- Gracefully handles empty task lists
- Manages owners with zero available hours
- Handles tasks exceeding available time (excludes but doesn't error)
- Supports tasks with identical priorities and durations

### Architecture & Design

#### **Design Patterns**
- **Factory Pattern**: `Scheduler.complete_task()` creates new Task instances
- **Strategy Pattern**: Multiple sorting strategies (priority, duration, time period)
- **Template Method**: `generate_plan()` orchestrates scheduling pipeline
- **Observer-like Pattern**: `_log_explanation()` tracks scheduling decisions

#### **Object-Oriented Principles**
- **Separation of Concerns**: Owner, Pet, Task, DailySchedule, Scheduler classes
- **Single Responsibility**: Each class has one clear purpose
- **Encapsulation**: Private helper methods (e.g., `_log_explanation()`)
- **Composition**: DailySchedule contains Tasks; Scheduler uses Owner, Pet, and Tasks

#### **Code Quality**
- **Type hints** in method signatures for clarity
- **Docstrings** for all public methods
- **Input validation** with descriptive error messages
- **Immutability considerations**: Task equality based on definition, not state

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

PawPal+ includes intelligent algorithmic features:

**Sorting & Filtering**
- Tasks sort by priority (1-5) and organize by time period (morning → afternoon → evening)
- Filter tasks by category (walk, feeding, medication), completion status, or frequency (daily/weekly/monthly)

**Recurring Tasks**
- Completing a recurring task automatically creates the next instance with the correct due date
- Daily tasks renew for tomorrow, weekly for next week (+7 days), monthly for next month (+30 days)

**Conflict Detection**
- Lightweight warnings detect when too many tasks are scheduled in one time period
- Checks if total duration exceeds ~4 hours per period or if more than 3 tasks overlap
- Non-blocking approach: warnings guide but don't prevent schedule generation

## Testing PawPal+

The PawPal+ system includes a comprehensive test suite with **31 tests** covering core scheduling behaviors, edge cases, and boundary conditions.

### Running Tests

```bash
# Run all tests with pytest (recommended)
python -m pytest

# Run tests with verbose output
python -m pytest tests/test_pawpal.py -v

# Alternative: Run with unittest
python -m unittest tests.test_pawpal -v
```

### Test Coverage

The test suite validates the following key behaviors:

**Sorting Correctness (7 tests)**
- Tasks sorted by priority (highest first), then duration (shortest first)
- Time period grouping (morning → afternoon → evening)
- Edge cases: empty lists, single tasks, identical tasks

**Recurrence Logic (5 tests)**
- Daily tasks regenerate for tomorrow (+1 day)
- Weekly tasks regenerate for next week (+7 days)
- Monthly tasks regenerate for next month (+30 days)
- One-time tasks do NOT regenerate
- New recurring instances preserve all original attributes

**Conflict Detection (6 tests)**
- Detects when tasks exceed time period capacity (>4 hours)
- Warns when too many tasks (>3) scheduled in same period
- Correctly handles well-distributed schedules
- Excludes completed tasks from conflict checks

**Edge Cases & Boundary Conditions (7 tests)**
- Pet with no tasks
- Owner with zero available hours
- Task duration exactly equals available time
- Two tasks at exact same time
- All tasks already completed
- Single task exceeds all available time

**Additional Tests (6 tests)**
- Task completion status management
- Daily schedule task addition/removal
- Filtering completed vs incomplete tasks

### Confidence Level

** 5/5 High Confidence** 

All 31 tests pass successfully, providing robust coverage of:
- Happy paths (everything works as expected)
- Edge cases (unusual but valid scenarios)
- Boundary conditions (limits and thresholds)
- Error handling (invalid inputs and constraints)

The system is production-ready with reliable scheduling logic, proper conflict detection, and accurate recurring task management.

**Running the Project**
```bash
# CLI demo (shows conflict detection)
python main.py

# Streamlit app
streamlit run app.py

# Run tests
python -m pytest
```

## 📸 Demo

<a href="/course_images/ai110/PawSchedule.png" target="_blank"><img src='/course_images/ai110/PawSchedule.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>
