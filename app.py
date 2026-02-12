import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, PRIORITY_MIN, PRIORITY_MAX


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize session state vault
if "owner" not in st.session_state:
    st.session_state.owner = None

if "pet" not in st.session_state:
    st.session_state.pet = None

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Header
st.title("🐾 PawPal+ Pet Care Scheduler")
st.markdown("Plan your pet's daily care tasks with smart scheduling and priority management.")

# Sidebar for owner and pet setup
with st.sidebar:
    st.header("Setup")

    # Owner section
    st.subheader("👤 Owner Information")
    owner_name = st.text_input("Owner name", value="Jordan", key="owner_name_input")
    available_hours = st.number_input(
        "Available hours per day",
        min_value=0.0,
        max_value=24.0,
        value=4.0,
        step=0.5,
        key="owner_hours_input"
    )

    if st.button("Create/Update Owner", key="create_owner_btn"):
        try:
            st.session_state.owner = Owner(owner_name, available_hours)
            st.success(f"✓ Owner {owner_name} created!")
        except ValueError as e:
            st.error(f"Error: {e}")

    if st.session_state.owner:
        st.info(f"Current: {st.session_state.owner}")

    st.divider()

    # Pet section
    st.subheader("🐾 Pet Information")

    if st.session_state.owner:
        pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
        species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"], key="species_input")
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=3, key="age_input")
        special_needs_text = st.text_area(
            "Special needs (one per line)",
            placeholder="e.g., anxiety medication\nsenior care\ndietary restrictions",
            key="special_needs_input"
        )

        if st.button("Create/Update Pet", key="create_pet_btn"):
            # Parse special needs
            special_needs = [need.strip() for need in special_needs_text.split("\n") if need.strip()]
            st.session_state.pet = Pet(pet_name, species, age, special_needs)
            st.success(f"✓ Pet {pet_name} created!")

        if st.session_state.pet:
            st.info(f"Current: {st.session_state.pet}")
    else:
        st.warning("Create an owner first!")

# Main content area
if st.session_state.owner and st.session_state.pet:
    # Task management section
    st.header("📋 Manage Tasks")

    # Add task form
    with st.expander("➕ Add New Task", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            task_name = st.text_input("Task name", value="Morning walk", key="task_name_input")
            category = st.selectbox(
                "Category",
                ["walk", "feeding", "medication", "grooming", "enrichment", "cleaning"],
                key="category_input"
            )
            duration = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=240,
                value=30,
                key="duration_input"
            )

        with col2:
            priority = st.slider(
                "Priority (5 = highest)",
                PRIORITY_MIN,
                PRIORITY_MAX,
                3,
                key="priority_input"
            )
            preferred_time = st.selectbox(
                "Preferred time",
                ["", "morning", "afternoon", "evening"],
                key="preferred_time_input"
            )
            frequency = st.selectbox(
                "Frequency",
                ["once", "daily", "weekly", "monthly"],
                index=1,
                key="frequency_input"
            )

        notes = st.text_area("Notes (optional)", key="notes_input")

        if st.button("Add Task", type="primary", key="add_task_btn"):
            try:
                new_task = Task(
                    task_name,
                    category,
                    duration,
                    priority,
                    preferred_time if preferred_time else None,
                    notes,
                    frequency
                )
                st.session_state.tasks.append(new_task)
                st.success(f"✓ Task '{task_name}' added!")
                st.rerun()
            except ValueError as e:
                st.error(f"Error: {e}")

    # Display current tasks
    if st.session_state.tasks:
        st.subheader(f"Current Tasks ({len(st.session_state.tasks)})")

        for i, task in enumerate(st.session_state.tasks):
            col1, col2, col3 = st.columns([6, 2, 1])

            with col1:
                st.markdown(f"**{i+1}.** {task}")

            with col2:
                if st.button(
                    "✓ Complete" if not task.is_completed() else "↺ Undo",
                    key=f"toggle_task_{i}"
                ):
                    if task.is_completed():
                        task.mark_incomplete()
                    else:
                        # Use scheduler to complete task (handles recurring tasks)
                        scheduler = Scheduler(
                            st.session_state.owner,
                            st.session_state.pet,
                            st.session_state.tasks
                        )
                        new_task = scheduler.complete_task(task)

                        # Update session state with the scheduler's task list (includes new recurring task)
                        st.session_state.tasks = scheduler.tasks

                        # Show notification if a new recurring task was created
                        if new_task:
                            st.toast(f"✓ Task completed! New instance due: {new_task.due_date}")
                    st.rerun()

            with col3:
                if st.button("🗑️", key=f"delete_task_{i}"):
                    st.session_state.tasks.pop(i)
                    st.rerun()

        # Clear all tasks button
        if st.button("Clear All Tasks", key="clear_all_btn"):
            st.session_state.tasks = []
            st.rerun()
    else:
        st.info("No tasks yet. Add one above!")

    st.divider()

    # Generate schedule section
    st.header("📅 Generate Schedule")

    if st.session_state.tasks:
        # Show task summary
        incomplete_tasks = [t for t in st.session_state.tasks if not t.is_completed()]
        completed_tasks = [t for t in st.session_state.tasks if t.is_completed()]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tasks", len(st.session_state.tasks))
        with col2:
            st.metric("Incomplete", len(incomplete_tasks))
        with col3:
            st.metric("Completed", len(completed_tasks))

        # Generate button
        if st.button("🚀 Generate Optimized Schedule", type="primary", key="generate_schedule_btn"):
            try:
                # Create scheduler
                scheduler = Scheduler(
                    st.session_state.owner,
                    st.session_state.pet,
                    st.session_state.tasks
                )

                # Generate schedule (excludes completed tasks by default)
                schedule = scheduler.generate_plan()

                # Display schedule
                st.success("✓ Schedule generated successfully!")

                # Schedule summary
                st.subheader("📊 Schedule Summary")
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Tasks Scheduled", len(schedule.scheduled_tasks))
                    st.metric("Total Duration", f"{schedule.get_total_duration():.2f} hours")

                with col2:
                    st.metric("Available Time", f"{st.session_state.owner.get_available_time()} hours")
                    if schedule.is_feasible():
                        st.success("✓ Schedule is feasible!")
                    else:
                        st.error("✗ Schedule exceeds available time!")

                # Display full schedule
                st.subheader("🗓️ Daily Schedule")
                st.code(schedule.display_schedule(), language=None)

                # Show explanation
                with st.expander("💡 Scheduling Explanation", expanded=True):
                    st.text(schedule.get_explanation())

            except Exception as e:
                st.error(f"Error generating schedule: {e}")
    else:
        st.warning("Add at least one task to generate a schedule!")

else:
    # Show setup instructions if owner/pet not created
    st.info("👈 Please create an owner and pet in the sidebar to get started!")

    with st.expander("ℹ️ About PawPal+"):
        st.markdown("""
        **PawPal+** is a smart pet care scheduling assistant that helps you:

        - 📝 Track all your pet care tasks (walks, feeding, medication, etc.)
        - ⏰ Manage time constraints and priorities
        - 🎯 Generate optimized daily schedules
        - 💬 Understand scheduling decisions with clear explanations
        - 🔄 Auto-create recurring tasks when you complete daily/weekly/monthly tasks

        **How to use:**
        1. Create an owner profile in the sidebar
        2. Add your pet's information
        3. Add care tasks with durations and priorities
        4. Mark recurring tasks complete to auto-create the next occurrence
        5. Generate an optimized schedule!

        **Recurring Tasks:**
        - Daily tasks → New instance created for tomorrow
        - Weekly tasks → New instance created for next week
        - Monthly tasks → New instance created for next month
        """)
