# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design consists of the classes Owner, Pet, Task, DailySchedule, and Scheduler, and they have the responsibilities of:

Managing pet care scheduling through five specialized components. The Owner class stores owner information and available time constraints, while the Pet class holds pet details and special needs. The Task class represents individual care activities with priority, duration, completion status, and frequency tracking. The DailySchedule class organizes selected tasks into a timed plan and validates feasibility, while the Scheduler class serves as the "brain" that prioritizes tasks, fits them to time constraints using a greedy algorithm, and generates optimized daily schedules with explanations.



**b. Design changes**

Yes, The PawPal+ scheduler uses time period grouping (morning/afternoon/evening) instead of exact time slot conflict detection. This means it checks if tasks exceed a typical 4-hour period rather than detecting actual overlapping time windows. The tradeoff prioritizes simplicity and flexibility—users select "morning" from a dropdown instead of specifying exact start times, which matches how pet owners naturally think about their schedules. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers three main constraints: (1) **available time** - the owner's daily hours available for pet care, (2) **task priority** - urgency from 1-5 where 5 is highest (medication, feeding), and (3) **preferred time periods** - morning/afternoon/evening preferences for each task. I decided priority mattered most for safety reasons (missing medication could harm the pet), followed by time constraints (unrealistic schedules are useless), and finally preferences (nice to have but flexible). The greedy algorithm selects highest-priority tasks first until the time budget is exhausted.

**b. Tradeoffs**

My scheduler uses time period grouping (morning/afternoon/evening) instead of exact time slot conflict detection. This means it checks if total task duration exceeds ~4 hours per period rather than detecting actual overlapping time windows (like 9:00-9:30 AM conflicts). This tradeoff is reasonable because pet owners think in periods ("I'll walk the dog in the morning") not exact minutes, it requires less user input (dropdown vs. time pickers), and maintains O(n) complexity instead of O(n²). While some edge-case conflicts may be missed, the simpler approach matches how users naturally plan their day and keeps schedules flexible enough to adapt to real life.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools (Claude) throughout the entire development process: (1) **Design phase** - generating the initial class skeleton from UML concepts, (2) **Implementation** - implementing sorting algorithms, recurring task logic, and conflict detection with explanations of Python idioms like lambda functions and timedelta, (3) **Testing** - creating comprehensive unit tests that verify all major features, and (4) **Refactoring** - analyzing the detect_conflicts() method for potential simplifications while maintaining readability. The most helpful prompts were specific and context-aware, like "implement a method that filters tasks by completion status" or "how could this algorithm be simplified for better readability or performance?"

**b. Judgment and verification**

When analyzing the detect_conflicts() algorithm, AI suggested a more "Pythonic" version using defaultdict and comprehensions that would reduce the code from 51 lines to 32 lines. However, I chose to keep a hybrid approach - extracting constants and calculating task_names once (DRY principle) but maintaining explicit dictionary management. I evaluated this by considering the educational context (this is a learning project where readability matters more than brevity) and verified that both versions had the same O(n) complexity. The "simpler" version wasn't actually simpler for beginners to understand, so I prioritized clarity over conciseness.

---

## 4. Testing and Verification

**a. What you tested**

I created 17 unit tests organized into four test suites: (1) **Task completion** - verifying mark_complete() and mark_incomplete() change status correctly, (2) **DailySchedule operations** - testing add_task(), remove_task(), and duration tracking, (3) **Recurring tasks** - ensuring daily/weekly/monthly tasks auto-create new instances with correct due dates, and (4) **Conflict detection** - validating warnings for overloaded periods, well-distributed schedules, and completed task handling. These tests were important because they verify the core scheduling logic works independently of the UI - I can trust my backend before connecting it to Streamlit.

**b. Confidence**

I'm highly confident (90%+) that the scheduler works correctly for typical use cases. All 17 tests pass, the main.py demo successfully demonstrates sorting/filtering/conflict detection, and the Streamlit app correctly integrates all features with toast notifications for recurring tasks. If I had more time, I would test edge cases like: (1) tasks with 0-minute duration, (2) scheduling with 0 available hours, (3) conflicts when all tasks are in the same period, (4) recurring tasks completed multiple times in succession, and (5) very large task lists (100+ tasks) to verify O(n) performance holds.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the recurring task system - it demonstrates thoughtful design that anticipates user needs. When a user completes a daily task like "morning walk," the system automatically creates tomorrow's instance with the correct due date, ensuring continuous care without manual re-entry. This required careful integration between the Task, Scheduler, and Streamlit UI layers, and the result feels genuinely helpful rather than just technically correct. The toast notifications showing "New instance due: 2026-02-13" provide immediate feedback that builds user confidence.

**b. What you would improve**

If I had another iteration, I would add actual time-based scheduling (9:00 AM - 10:00 AM) as an *optional* feature alongside the current period-based system. Users could choose flexibility (select "morning") or precision (specify "9:00 AM") depending on the task. This hybrid approach would preserve simplicity for routine tasks while enabling exact scheduling for appointments like vet visits. I would also implement a "suggest better distribution" feature that recommends moving tasks between periods when conflicts are detected, rather than just warning about them.

**c. Key takeaway**

The most important thing I learned is that **the best algorithm isn't always the most sophisticated one** - it's the one that matches user needs and mental models. When analyzing the conflict detection algorithm, the "Pythonic" version was technically cleaner but harder to understand. Similarly, exact time-slot detection would be more precise but doesn't match how pet owners think about their day. Working with AI taught me to evaluate suggestions not just for correctness, but for appropriateness - asking "does this serve the user?" rather than just "does this work?" Good system design requires balancing technical elegance with human usability.
