import streamlit as st
from datetime import date, datetime
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

    st.caption("Set the time window for this task:")
    col4a, col4b, col4c = st.columns(3)
    with col4a:
        start_hour = st.selectbox("Start hour", list(range(1, 13)), index=7, key="start_h")
    with col4b:
        start_min = st.selectbox("Start minute", ["00", "15", "30", "45"], key="start_m")
    with col4c:
        start_ampm = st.selectbox("Start", ["AM", "PM"], key="start_ampm")

    col5a, col5b, col5c = st.columns(3)
    with col5a:
        end_hour = st.selectbox("End hour", list(range(1, 13)), index=9, key="end_h")
    with col5b:
        end_min = st.selectbox("End minute", ["00", "15", "30", "45"], key="end_m")
    with col5c:
        end_ampm = st.selectbox("End", ["AM", "PM"], key="end_ampm")

    def _to_24h(hour, minute, ampm):
        h = int(hour) % 12 + (12 if ampm == "PM" else 0)
        return f"{h:02d}:{minute}"

    earliest_start = _to_24h(start_hour, start_min, start_ampm)
    latest_end     = _to_24h(end_hour,   end_min,   end_ampm)

    st.caption(f"Window: {start_hour}:{start_min} {start_ampm} → {end_hour}:{end_min} {end_ampm}")

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
        all_pet_tasks = owner.get_all_tasks()
        # Use Scheduler to sort tasks chronologically for display
        _display_scheduler = Scheduler(owner=owner, schedule_date=date.today(), available_hours=24.0)
        sorted_tasks = _display_scheduler.sort_by_time(all_pet_tasks)
        pending = _display_scheduler.filter_by_completion(sorted_tasks, completed=False)
        done    = _display_scheduler.filter_by_completion(sorted_tasks, completed=True)

        st.write("**Current tasks (sorted by start time):**")
        pet_lookup = {p.pet_id: p for p in owner.pets}
        for t in sorted_tasks:
            pet = pet_lookup.get(t.pet_id)
            start_ampm = datetime.strptime(t.earliest_start, "%H:%M").strftime("%I:%M %p")
            status = "✅" if t.completed else "🔲"
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.write(
                    f"{status} **{t.title}** — {pet.name if pet else '?'} | "
                    f"{start_ampm} | {t.duration} min | Priority {t.priority} | {t.recurrence}"
                )
            with col_btn:
                if not t.completed:
                    if st.button("Done", key=f"complete_{t.task_id}"):
                        pet.complete_task(task_id=t.task_id, completed_on=date.today())
                        st.rerun()

        col_p, col_d = st.columns(2)
        col_p.metric("Pending", len(pending))
        col_d.metric("Completed", len(done))

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
            st.warning("No tasks could be scheduled — check that task durations fit within their time windows.")
        else:
            st.success(f"Schedule generated for {date.today().strftime('%A, %B %d %Y')}!")

            # --- Conflict warnings (shown before the schedule) ---
            conflicts = scheduler.detect_conflicts()
            if conflicts:
                st.error(f"⚠️ {len(conflicts)} scheduling conflict(s) detected — review before your day starts:")
                for warning in conflicts:
                    # Extract the two task names for a friendlier message
                    st.warning(warning)
                st.caption("Tip: adjust a task's start time or duration to resolve overlaps.")

            # --- Schedule table grouped by pet ---
            task_duration = {t.task_id: t.duration for p in owner.pets for t in p.tasks}
            seen_pets = []
            for entry in scheduler.entries:
                if entry["pet_id"] not in seen_pets:
                    seen_pets.append(entry["pet_id"])
                    st.markdown(f"**{entry['pet_name']} ({entry['pet_species']})**")
                    pet_entries = [e for e in scheduler.entries if e["pet_id"] == entry["pet_id"]]
                    st.table([
                        {
                            "Time": f"{e['start']} – {e['end']}",
                            "Task": e["title"],
                            "Duration": f"{task_duration.get(e['task_id'], '?')} min",
                            "Priority": f"★ {e['priority']}",
                        }
                        for e in pet_entries
                    ])

            with st.expander("Why was each task scheduled?"):
                for entry in scheduler.entries:
                    st.write(f"**{entry['title']}** → {entry['reasoning']}")
