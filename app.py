import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Session state initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_id=1, name="", email="")
if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

owner = st.session_state.owner

# --- Header ---
st.title("🐾 PawPal+")
st.caption("A daily pet care planner.")
st.divider()

# --- Owner info ---
st.subheader("Owner Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value=owner.name)
with col2:
    owner_email = st.text_input("Your email", value=owner.email)

if st.button("Save owner info"):
    owner.edit_owner_info(name=owner_name, email=owner_email)
    st.success(f"Saved! Welcome, {owner.name}.")

st.divider()

# --- Add a pet ---
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name")
with col2:
    species = st.selectbox("Species", ["Dog", "Cat", "Other"])
with col3:
    age = st.text_input("Age", value="1")
care_notes = st.text_input("Care notes (optional)")

if st.button("Add pet"):
    if pet_name:
        new_pet = Pet(
            pet_id=st.session_state.next_pet_id,
            owner_id=owner.owner_id,
            name=pet_name,
            species=species,
            age=age,
            care_notes=care_notes
        )
        owner.add_pet(new_pet)
        st.session_state.next_pet_id += 1
        st.success(f"{pet_name} added!")
    else:
        st.warning("Please enter a pet name.")

if owner.pets:
    st.write("**Your pets:**")
    for p in owner.pets:
        st.write(f"- {p.name} ({p.species}, age {p.age})")

st.divider()

# --- Add a task ---
st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    pet_options = {p.name: p for p in owner.pets}
    selected_pet_name = st.selectbox("Assign to pet", list(pet_options.keys()))

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.number_input("Priority (1=high, 5=low)", min_value=1, max_value=5, value=2)

    col4, col5 = st.columns(2)
    with col4:
        earliest_start = st.text_input("Earliest start (HH:MM)", value="08:00")
    with col5:
        latest_end = st.text_input("Latest end (HH:MM)", value="10:00")

    recurrence = st.selectbox("Recurrence", ["daily", "weekly"])

    if st.button("Add task"):
        new_task = Task(
            task_id=st.session_state.next_task_id,
            pet_id=0,
            title=task_title,
            duration=int(duration),
            priority=int(priority),
            earliest_start=earliest_start,
            latest_end=latest_end,
            recurrence=recurrence
        )
        pet_options[selected_pet_name].add_task(new_task)
        st.session_state.next_task_id += 1
        st.success(f"Task '{task_title}' added to {selected_pet_name}!")

    if any(p.tasks for p in owner.pets):
        st.write("**Current tasks:**")
        for p in owner.pets:
            for t in p.tasks:
                status = "✅" if t.completed else "🔲"
                st.write(f"{status} **{p.name}** — {t.title} ({t.duration}min, priority {t.priority})")

st.divider()

# --- Generate schedule ---
st.subheader("Generate Today's Schedule")
available_hours = st.slider("Available hours today", min_value=1.0, max_value=12.0, value=4.0, step=0.5)

if st.button("Generate schedule"):
    all_tasks = owner.get_all_tasks(today=date.today())
    if not all_tasks:
        st.warning("No tasks due today. Add some tasks first.")
    else:
        scheduler = Scheduler(
            owner=owner,
            schedule_date=date.today(),
            available_hours=available_hours
        )
        scheduler.generate_schedule()

        if not scheduler.entries:
            st.warning("No tasks could be scheduled — check that task durations fit their time windows.")
        else:
            st.success(f"Schedule generated for {date.today().strftime('%A, %B %d %Y')}!")
            seen_pets = []
            for entry in scheduler.entries:
                if entry["pet_id"] not in seen_pets:
                    seen_pets.append(entry["pet_id"])
                    st.markdown(f"**{entry['pet_name']} ({entry['pet_species']})**")
                st.write(f"  {entry['start']} – {entry['end']}  |  {entry['title']}  |  ★ Priority {entry['priority']}")

            with st.expander("Reasoning"):
                for entry in scheduler.entries:
                    st.write(f"**{entry['title']}** → {entry['reasoning']}")
