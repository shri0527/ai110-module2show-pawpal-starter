import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Owner setup ---
st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Available minutes today", min_value=10, max_value=480, value=120)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, available_minutes=available_minutes)

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
    st.success(f"Added {pet_name} the {species}!")

if st.session_state.owner.pets:
    st.write("Pets on this account:")
    for p in st.session_state.owner.pets:
        st.markdown(f"- **{p.name}** ({p.species}, age {p.age})")
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
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
            pet_name=pet_choice,
        )
        target_pet = next(p for p in st.session_state.owner.pets if p.name == pet_choice)
        target_pet.add_task(new_task)
        st.success(f"Added task '{task_title}' to {pet_choice}.")

    all_tasks = st.session_state.owner.all_tasks()
    if all_tasks:
        st.write("All tasks:")
        st.table([
            {"pet": t.pet_name, "title": t.title, "duration": t.duration_minutes,
             "priority": t.priority, "category": t.category, "done": t.is_done}
            for t in all_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

# --- Build Schedule ---
st.divider()
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not st.session_state.owner.pets or not st.session_state.owner.all_tasks():
        st.warning("Add at least one pet and one task before generating a schedule.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        schedule = scheduler.build_schedule(date.today())
        if schedule.tasks:
            st.success(f"Schedule for {schedule.date} — total time: {schedule.total_time()} min")
            for task in schedule.tasks:
                reason = schedule.explanations.get(task.id, "")
                st.markdown(
                    f"**[{task.priority.upper()}]** {task.title} for {task.pet_name} "
                    f"({task.duration_minutes} min) — _{reason}_"
                )
        else:
            st.warning("No tasks fit within your available time.")
