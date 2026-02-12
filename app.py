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

    # Display current tasks with filtering and sorting
    if st.session_state.tasks:
        st.subheader(f"Current Tasks ({len(st.session_state.tasks)})")

        # Filtering and sorting controls
        with st.expander("🔍 Filter & Sort Tasks", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                filter_category = st.selectbox(
                    "Filter by category",
                    ["All"] + ["walk", "feeding", "medication", "grooming", "enrichment", "cleaning"],
                    key="filter_category"
                )

            with col2:
                filter_status = st.selectbox(
                    "Filter by status",
                    ["All", "Incomplete", "Completed"],
                    key="filter_status"
                )

            with col3:
                filter_frequency = st.selectbox(
                    "Filter by frequency",
                    ["All", "once", "daily", "weekly", "monthly"],
                    key="filter_frequency"
                )

            sort_by = st.radio(
                "Sort by",
                ["Priority (High→Low)", "Duration (Short→Long)", "Time Period"],
                horizontal=True,
                key="sort_by"
            )

        # Apply filters using Scheduler methods
        scheduler = Scheduler(st.session_state.owner, st.session_state.pet, st.session_state.tasks)

        # Filter tasks
        filtered_tasks = st.session_state.tasks.copy()

        if filter_category != "All":
            filtered_tasks = [t for t in filtered_tasks if t.category == filter_category]

        if filter_status == "Incomplete":
            filtered_tasks = [t for t in filtered_tasks if not t.is_completed()]
        elif filter_status == "Completed":
            filtered_tasks = [t for t in filtered_tasks if t.is_completed()]

        if filter_frequency != "All":
            filtered_tasks = [t for t in filtered_tasks if t.frequency == filter_frequency]

        # Sort tasks using Scheduler's prioritize method
        if sort_by == "Priority (High→Low)":
            scheduler_temp = Scheduler(st.session_state.owner, st.session_state.pet, filtered_tasks)
            filtered_tasks = scheduler_temp.prioritize_tasks()
        elif sort_by == "Duration (Short→Long)":
            filtered_tasks = sorted(filtered_tasks, key=lambda t: t.duration)
        elif sort_by == "Time Period":
            scheduler_temp = Scheduler(st.session_state.owner, st.session_state.pet, filtered_tasks)
            prioritized = scheduler_temp.prioritize_tasks()
            filtered_tasks = scheduler_temp.optimize_schedule(prioritized)

        # Display filtered and sorted tasks
        st.caption(f"Showing {len(filtered_tasks)} of {len(st.session_state.tasks)} tasks")

        if filtered_tasks:
            # Create task data for table display
            task_data = []
            for task in filtered_tasks:
                task_data.append({
                    "Status": "✓" if task.is_completed() else "○",
                    "Task": task.name,
                    "Category": task.category,
                    "Duration": f"{task.duration}min",
                    "Priority": f"{'⭐' * task.priority}",
                    "Time": task.preferred_time or "—",
                    "Frequency": task.frequency
                })

            # Display as table
            st.dataframe(
                task_data,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # Task action buttons
            st.caption("Task Actions:")
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
        else:
            st.info("No tasks match the current filters.")

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
        # Create scheduler for analytics
        scheduler = Scheduler(st.session_state.owner, st.session_state.pet, st.session_state.tasks)

        # Show comprehensive task analytics
        incomplete_tasks = scheduler.get_incomplete_tasks()
        completed_tasks = scheduler.get_completed_tasks()

        # Task summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tasks", len(st.session_state.tasks))
        with col2:
            st.metric("Incomplete", len(incomplete_tasks))
        with col3:
            st.metric("Completed", len(completed_tasks))
        with col4:
            # Calculate total time needed for incomplete tasks
            total_time_needed = sum(t.get_duration_hours() for t in incomplete_tasks)
            st.metric("Time Needed", f"{total_time_needed:.1f}h")

        # Show breakdown by category and frequency
        with st.expander("📊 Task Analytics", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**By Category**")
                categories = {}
                for task in st.session_state.tasks:
                    categories[task.category] = categories.get(task.category, 0) + 1

                for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    st.markdown(f"- {category}: {count}")

            with col2:
                st.markdown("**By Frequency**")
                frequencies = {}
                for task in st.session_state.tasks:
                    frequencies[task.frequency] = frequencies.get(task.frequency, 0) + 1

                for frequency, count in sorted(frequencies.items(), key=lambda x: x[1], reverse=True):
                    st.markdown(f"- {frequency}: {count}")

            # Show time distribution
            st.markdown("**By Time Period**")
            col1, col2, col3, col4 = st.columns(4)
            morning_count = len([t for t in incomplete_tasks if t.preferred_time == "morning"])
            afternoon_count = len([t for t in incomplete_tasks if t.preferred_time == "afternoon"])
            evening_count = len([t for t in incomplete_tasks if t.preferred_time == "evening"])
            flexible_count = len([t for t in incomplete_tasks if not t.preferred_time])

            with col1:
                st.metric("🌅 Morning", morning_count)
            with col2:
                st.metric("☀️ Afternoon", afternoon_count)
            with col3:
                st.metric("🌙 Evening", evening_count)
            with col4:
                st.metric("📌 Flexible", flexible_count)

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

                # Check for conflicts BEFORE displaying success
                conflicts = scheduler.detect_conflicts()

                # Display schedule generation status
                if not conflicts:
                    st.success("✓ Schedule generated successfully with no conflicts!")
                else:
                    st.warning("⚠️ Schedule generated with warnings. Please review conflicts below.")

                # Schedule summary
                st.subheader("📊 Schedule Summary")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Tasks Scheduled", len(schedule.scheduled_tasks))

                with col2:
                    st.metric("Total Duration", f"{schedule.get_total_duration():.2f} hours")

                with col3:
                    st.metric("Available Time", f"{st.session_state.owner.get_available_time()} hours")

                # Feasibility check
                if schedule.is_feasible():
                    st.success("✅ **Schedule is feasible!** All tasks fit within available time.")
                else:
                    st.error("❌ **Schedule exceeds available time!** Some tasks were excluded.")

                # CONFLICT WARNINGS - Display prominently if any exist
                if conflicts:
                    st.divider()
                    st.subheader("⚠️ Scheduling Conflicts Detected")

                    st.markdown("""
                    **What this means:** Some tasks may overlap or compete for the same time period.
                    These are warnings to help you adjust your schedule, not errors that prevent scheduling.
                    """)

                    # Display each conflict as a warning box
                    for conflict in conflicts:
                        # Parse conflict to make it more user-friendly
                        if "exceed" in conflict.lower():
                            st.error(f"🚫 **Time Overflow:** {conflict}")
                            st.caption("💡 **Suggestion:** Spread tasks across different time periods or reduce task durations.")
                        elif "notice" in conflict.lower():
                            st.warning(f"⚠️ **Heavy Schedule:** {conflict}")
                            st.caption("💡 **Suggestion:** Consider moving some tasks to morning/afternoon/evening for better balance.")
                        else:
                            st.warning(f"⚠️ {conflict}")

                    # Provide actionable recommendations
                    with st.expander("💡 How to resolve conflicts", expanded=True):
                        st.markdown("""
                        **Options to fix scheduling conflicts:**

                        1. **Adjust Time Periods**
                           - Move some tasks to less busy time slots (morning → afternoon → evening)
                           - Spread tasks throughout the day instead of clustering

                        2. **Reduce Task Durations**
                           - Shorten walk times or grooming sessions if possible
                           - Combine similar tasks to save time

                        3. **Adjust Priorities**
                           - Lower priority for less critical tasks
                           - High-priority tasks will be scheduled first

                        4. **Increase Available Hours**
                           - Update your available hours per day in the sidebar
                           - Consider delegating some tasks if possible

                        5. **Complete or Remove Tasks**
                           - Mark completed tasks as done
                           - Remove unnecessary or one-time tasks
                        """)

                st.divider()

                # Display schedule breakdown by time period
                st.subheader("🗓️ Daily Schedule")

                # Group tasks by time period
                morning_tasks = [(time, task) for time, task in schedule.scheduled_tasks if task.preferred_time == "morning"]
                afternoon_tasks = [(time, task) for time, task in schedule.scheduled_tasks if task.preferred_time == "afternoon"]
                evening_tasks = [(time, task) for time, task in schedule.scheduled_tasks if task.preferred_time == "evening"]
                unscheduled_tasks = [(time, task) for time, task in schedule.scheduled_tasks if not task.preferred_time]

                # Display by time period with visual separation
                if morning_tasks:
                    st.markdown("**🌅 Morning**")
                    for time, task in morning_tasks:
                        st.markdown(f"- {task}")

                if afternoon_tasks:
                    st.markdown("**☀️ Afternoon**")
                    for time, task in afternoon_tasks:
                        st.markdown(f"- {task}")

                if evening_tasks:
                    st.markdown("**🌙 Evening**")
                    for time, task in evening_tasks:
                        st.markdown(f"- {task}")

                if unscheduled_tasks:
                    st.markdown("**📌 Flexible / Unscheduled**")
                    for time, task in unscheduled_tasks:
                        st.markdown(f"- {task}")

                # Full schedule view
                with st.expander("📋 View Full Schedule Details"):
                    st.code(schedule.display_schedule(), language=None)

                # Show explanation
                with st.expander("💡 Scheduling Explanation", expanded=False):
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
