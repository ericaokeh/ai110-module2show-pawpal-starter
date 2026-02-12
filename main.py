"""
PawPal+ Main Script - Testing Conflict Detection
Demonstrates the scheduling conflict detection with overlapping tasks
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_tasks(tasks, title="Tasks"):
    """Print a list of tasks with numbering."""
    print(f"\n{title}:")
    if not tasks:
        print("  (none)")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task}")


def main():
    print_section("🐾 PawPal+ - Conflict Detection Demo 🐾")

    # Create owner and pet
    owner = Owner("Alex", available_hours_per_day=6)
    pet = Pet("Buddy", "Dog", 5, special_needs=["hip dysplasia"])

    print(f"\n👤 {owner}")
    print(f"🐕 {pet}")

    # SCENARIO 1: Too many tasks in morning period
    print_section("Scenario 1: Overloaded Morning Schedule")

    tasks_scenario1 = [
        # All these tasks scheduled for morning - will cause conflict
        Task("Morning walk", "walk", 60, 5, preferred_time="morning", frequency="daily"),
        Task("Feed breakfast", "feeding", 15, 5, preferred_time="morning", frequency="daily"),
        Task("Medication", "medication", 10, 5, preferred_time="morning", frequency="daily"),
        Task("Training session", "enrichment", 90, 4, preferred_time="morning", frequency="daily"),
        Task("Grooming", "grooming", 45, 3, preferred_time="morning", frequency="daily"),
        # Total morning duration: 220 minutes (3.67 hours) - should trigger warning
    ]

    print_tasks(tasks_scenario1, "Tasks (all scheduled for morning)")

    scheduler1 = Scheduler(owner, pet, tasks_scenario1)
    schedule1 = scheduler1.generate_plan()

    print("\n📅 Generated Schedule:")
    print(schedule1.display_schedule())

    print("\n💡 Explanation (with conflict warnings):")
    print(schedule1.get_explanation())

    # SCENARIO 2: Conflicts across multiple time periods
    print_section("Scenario 2: Multiple Time Period Conflicts")

    tasks_scenario2 = [
        # Morning conflicts (too many tasks)
        Task("Morning walk", "walk", 45, 5, preferred_time="morning", frequency="daily"),
        Task("Breakfast", "feeding", 10, 5, preferred_time="morning", frequency="daily"),
        Task("Meds", "medication", 5, 5, preferred_time="morning", frequency="daily"),
        Task("Play time", "enrichment", 60, 4, preferred_time="morning", frequency="daily"),
        Task("Brush fur", "grooming", 20, 3, preferred_time="morning", frequency="daily"),

        # Afternoon conflicts (exceeds typical period)
        Task("Afternoon walk", "walk", 120, 5, preferred_time="afternoon", frequency="daily"),
        Task("Training", "enrichment", 90, 4, preferred_time="afternoon", frequency="daily"),
        Task("Vet appointment", "medical", 60, 5, preferred_time="afternoon", frequency="weekly"),
        # Afternoon total: 270 min (4.5 hours) - exceeds typical 4-hour period

        # Evening - reasonable
        Task("Dinner", "feeding", 15, 5, preferred_time="evening", frequency="daily"),
        Task("Evening walk", "walk", 30, 4, preferred_time="evening", frequency="daily"),
    ]

    print_tasks(tasks_scenario2, "Tasks (conflicts in morning & afternoon)")

    scheduler2 = Scheduler(owner, pet, tasks_scenario2)
    schedule2 = scheduler2.generate_plan()

    print("\n📅 Generated Schedule:")
    print(schedule2.display_schedule())

    print("\n💡 Explanation (with conflict warnings):")
    print(schedule2.get_explanation())

    # SCENARIO 3: No conflicts (well-balanced schedule)
    print_section("Scenario 3: Well-Balanced Schedule (No Conflicts)")

    tasks_scenario3 = [
        # Morning
        Task("Morning walk", "walk", 30, 5, preferred_time="morning", frequency="daily"),
        Task("Breakfast", "feeding", 10, 5, preferred_time="morning", frequency="daily"),

        # Afternoon
        Task("Afternoon walk", "walk", 30, 4, preferred_time="afternoon", frequency="daily"),
        Task("Play time", "enrichment", 20, 3, preferred_time="afternoon", frequency="daily"),

        # Evening
        Task("Dinner", "feeding", 10, 5, preferred_time="evening", frequency="daily"),
        Task("Evening walk", "walk", 30, 4, preferred_time="evening", frequency="daily"),
    ]

    print_tasks(tasks_scenario3, "Tasks (well-distributed)")

    scheduler3 = Scheduler(owner, pet, tasks_scenario3)
    schedule3 = scheduler3.generate_plan()

    print("\n📅 Generated Schedule:")
    print(schedule3.display_schedule())

    print("\n💡 Explanation (should show no conflicts):")
    print(schedule3.get_explanation())

    # SCENARIO 4: Testing standalone conflict detection
    print_section("Scenario 4: Direct Conflict Detection")

    tasks_scenario4 = [
        Task("Task A", "walk", 90, 5, preferred_time="morning"),
        Task("Task B", "feeding", 60, 5, preferred_time="morning"),
        Task("Task C", "grooming", 90, 4, preferred_time="morning"),
        # Total: 240 minutes (4 hours) for morning - right at the limit
    ]

    print_tasks(tasks_scenario4, "Tasks for conflict check")

    scheduler4 = Scheduler(owner, pet, tasks_scenario4)
    conflicts = scheduler4.detect_conflicts()

    print(f"\n🔍 Conflict Detection Results:")
    if conflicts:
        print(f"   Found {len(conflicts)} warning(s):")
        for warning in conflicts:
            print(f"   {warning}")
    else:
        print("   ✓ No conflicts detected!")

    # Summary
    print_section("📊 Summary")

    print("""
Conflict Detection Strategy:
  ✓ Groups tasks by preferred time period (morning/afternoon/evening)
  ✓ Calculates total duration per time period
  ✓ Warns if total exceeds typical period length (~4 hours)
  ✓ Warns if too many tasks (>3) in same period
  ✓ Returns warnings instead of crashing the program
  ✓ Integrated into schedule generation process

Benefits:
  • Helps pet owners avoid over-scheduling
  • Provides clear warnings about potential conflicts
  • Allows schedule generation to continue (non-blocking)
  • Gives suggestions to spread tasks across periods
    """)

    print("=" * 70)
    print("🎉 Conflict Detection Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
