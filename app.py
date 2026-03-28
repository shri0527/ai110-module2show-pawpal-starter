import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}

# --- Owner setup ---
st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Available minutes today", min_value=10, max_value=480, value=120)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, available_minutes=available_minutes)
else:
    st.session_state.owner.available_minutes = available_minutes
    st.session_state.owner.name = owner_name

if "schedule" not in st.session_state:
    st.session_state.schedule = None

# --- Add a Pet ---
st.divider()
st.subheader("Add a Pet")

with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age", min_value=0, max_value=30, value=2)
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    new_pet = Pet(name=pet_name, species=species, age=age)
    st.session_state.owner.add_pet(new_pet)
    st.session_state.schedule = None
    st.success(f"Added {pet_name} the {species}!")

# --- Pet list + Remove ---
if st.session_state.owner.pets:
    st.write("Pets on this account:")
    for p in st.session_state.owner.pets:
        col_info, col_btn = st.columns([5, 1])
        with col_info:
            st.markdown(f"- **{p.name}** ({p.species}, age {p.age})")
        with col_btn:
            if st.button("Remove", key=f"remove_pet_{p.name}"):
                st.session_state.owner.pets = [
                    pet for pet in st.session_state.owner.pets if pet.name != p.name
                ]
                st.session_state.schedule = None
                st.rerun()
else:
    st.info("No pets yet. Add one above.")

# --- Add a Task ---
st.divider()
st.subheader("Add a Task")

if not st.session_state.owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    with st.form("add_task_form"):
        pet_choice = st.selectbox("Assign to pet", [p.name for p in st.session_state.owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        category = st.text_input("Category (e.g. walk, feeding, meds)", value="walk")
        scheduled_time = st.text_input("Scheduled time (HH:MM, leave blank if flexible)", value="")
        recurrence = st.selectbox("Repeats", ["none", "daily", "weekly"])
        repeat_days = st.multiselect(
            "Repeat on (weekly only)",
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        )
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
            pet_name=pet_choice,
            scheduled_time=scheduled_time.strip(),
            recurrence=recurrence,
            repeat_days=repeat_days,
        )
        target_pet = next(p for p in st.session_state.owner.pets if p.name == pet_choice)
        target_pet.add_task(new_task)
        st.session_state.schedule = None
        st.success(f"Added task '{task_title}' to {pet_choice}." + (" Repeats " + recurrence + "." if recurrence != "none" else ""))

    # Simple unfiltered task list — all one-off + recurring tasks sorted by time
    all_displayable = sorted(
        st.session_state.owner.all_tasks()
        + [t for pet in st.session_state.owner.pets for t in pet.recurring_tasks],
        key=lambda t: t.scheduled_time or "99:99",
    )

    if all_displayable:
        st.write("All tasks (sorted by time):")
        st.table([
            {
                "Time": t.scheduled_time if t.scheduled_time else "—",
                "Pet": t.pet_name,
                "Task": t.title,
                "Duration": f"{t.duration_minutes} min",
                "Priority": PRIORITY_BADGE[t.priority],
                "Category": t.category,
                "Repeats": t.recurrence if t.recurrence == "none" else (t.recurrence + " " + "/".join(t.repeat_days)),
                "Done": "✓" if t.is_done else "○",
            }
            for t in all_displayable
        ])
    else:
        st.info("No tasks yet. Add one above.")

# --- Build Schedule ---
st.divider()
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    all_owner_tasks = st.session_state.owner.all_tasks() + [
        t for pet in st.session_state.owner.pets for t in pet.recurring_tasks
    ]
    if not st.session_state.owner.pets or not all_owner_tasks:
        st.warning("Add at least one pet and one task before generating a schedule.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        st.session_state.schedule = scheduler.build_schedule(date.today())

schedule = st.session_state.schedule

if schedule is not None:
    if schedule.tasks:
        st.success(
            f"Schedule for **{schedule.date}** — "
            f"{len(schedule.tasks)} task(s) — "
            f"total time: **{schedule.total_time()} min** "
            f"of {st.session_state.owner.available_minutes} min available"
        )

        # --- Filters ---
        filter_cols = st.columns(3)
        with filter_cols[0]:
            pet_names = ["All pets"] + [p.name for p in st.session_state.owner.pets]
            filter_pet = st.selectbox("Filter by pet", pet_names)
        with filter_cols[1]:
            filter_priority = st.selectbox("Filter by priority", ["All", "high", "medium", "low"])
        with filter_cols[2]:
            filter_done = st.selectbox("Filter by status", ["All", "Pending", "Done"])

        filtered_schedule = schedule.tasks
        if filter_pet != "All pets":
            filtered_schedule = [t for t in filtered_schedule if t.pet_name == filter_pet]
        if filter_priority != "All":
            filtered_schedule = [t for t in filtered_schedule if t.priority == filter_priority]
        if filter_done == "Pending":
            filtered_schedule = [t for t in filtered_schedule if not t.is_done]
        elif filter_done == "Done":
            filtered_schedule = [t for t in filtered_schedule if t.is_done]

        if filtered_schedule:
            st.write(f"Showing {len(filtered_schedule)} of {len(schedule.tasks)} scheduled task(s):")
            st.table([
                {
                    "Time": t.scheduled_time if t.scheduled_time else "Flexible",
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": PRIORITY_BADGE[t.priority],
                    "Why included": schedule.explanations.get(t.id, "fits available time"),
                }
                for t in filtered_schedule
            ])
        else:
            st.info("No scheduled tasks match the selected filters.")

        # --- Conflict resolution ---
        if schedule.conflicts:
            st.divider()
            st.markdown("### ⚠️ Scheduling Conflicts")
            st.caption(
                "Fix each conflict below. Auto-fix moves the second task to start right "
                "after the first ends. Or set your own times and click Apply."
            )

            for i, (task_a, task_b) in enumerate(schedule.conflicts):
                end_a_min = task_a._end_minutes()
                end_a_str = f"{end_a_min // 60:02d}:{end_a_min % 60:02d}"

                with st.expander(
                    f"Conflict {i + 1}: '{task_a.title}' ({task_a.scheduled_time}) "
                    f"overlaps '{task_b.title}' ({task_b.scheduled_time})",
                    expanded=True,
                ):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**{task_a.title}**")
                        st.markdown(f"Pet: {task_a.pet_name}")
                        st.markdown(f"🕐 {task_a.scheduled_time} → {end_a_str} ({task_a.duration_minutes} min)")
                    with col_b:
                        st.markdown(f"**{task_b.title}**")
                        st.markdown(f"Pet: {task_b.pet_name}")
                        st.markdown(f"🕐 starts {task_b.scheduled_time} ({task_b.duration_minutes} min)")

                    st.markdown("---")

                    # Option 1 — auto-fix
                    st.markdown(
                        f"**Option 1 — Auto-fix:** Move *{task_b.title}* to {end_a_str} "
                        f"(right after *{task_a.title}* ends)"
                    )
                    if st.button(
                        f"Auto-fix: move '{task_b.title}' → {end_a_str}",
                        key=f"autofix_{task_b.id}_{i}",
                    ):
                        task_b.scheduled_time = end_a_str
                        scheduler = Scheduler(st.session_state.owner)
                        st.session_state.schedule = scheduler.build_schedule(date.today())
                        st.rerun()

                    # Option 2 — manual fix
                    st.markdown("**Option 2 — Set your own times:**")
                    fix_col_a, fix_col_b, fix_col_apply = st.columns([2, 2, 1])
                    with fix_col_a:
                        new_time_a = st.text_input(
                            f"New time for '{task_a.title}'",
                            value=task_a.scheduled_time,
                            key=f"manual_a_{task_a.id}_{i}",
                        )
                    with fix_col_b:
                        new_time_b = st.text_input(
                            f"New time for '{task_b.title}'",
                            value=task_b.scheduled_time,
                            key=f"manual_b_{task_b.id}_{i}",
                        )
                    with fix_col_apply:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Apply", key=f"apply_{task_a.id}_{task_b.id}_{i}"):
                            task_a.scheduled_time = new_time_a.strip()
                            task_b.scheduled_time = new_time_b.strip()
                            scheduler = Scheduler(st.session_state.owner)
                            st.session_state.schedule = scheduler.build_schedule(date.today())
                            st.rerun()

        else:
            st.success("No scheduling conflicts — your plan is clear!")

    else:
        st.warning("No tasks fit within your available time.")

# --- Mark a Task Done ---
st.divider()
st.subheader("Mark a Task Done")

# Include both one-off tasks and recurring tasks
all_tasks = st.session_state.owner.all_tasks() + [
    t for pet in st.session_state.owner.pets for t in pet.recurring_tasks
]
pending = [t for t in all_tasks if not t.is_done]

if not pending:
    st.info("No pending tasks to mark done.")
else:
    task_labels = {f"{t.title} ({t.pet_name})": t for t in pending}
    chosen_label = st.selectbox("Select a completed task", list(task_labels.keys()))

    if st.button("Mark done"):
        chosen_task = task_labels[chosen_label]
        scheduler = Scheduler(st.session_state.owner)
        scheduler.mark_task_done(chosen_task.id)
        st.session_state.schedule = None
        st.success(f"'{chosen_task.title}' marked as done!")
        st.rerun()
