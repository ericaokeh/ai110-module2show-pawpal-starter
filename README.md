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
