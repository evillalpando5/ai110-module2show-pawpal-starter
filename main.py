from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

today = date.today()

owner = Owner(owner_id=1, name="Erika", email="erika@email.com")

biscuit = Pet(pet_id=1, owner_id=1, name="Biscuit", species="Dog", age="3", care_notes="Loves morning walks")
mochi   = Pet(pet_id=2, owner_id=1, name="Mochi",   species="Cat", age="2", care_notes="Indoor only")

# Intentional conflict: both tasks share 08:00–09:00
biscuit.add_task(Task(
    task_id=1, pet_id=1,
    title="Morning walk",
    duration=30, priority=1,
    earliest_start="08:00", latest_end="09:00"
))
mochi.add_task(Task(
    task_id=2, pet_id=2,
    title="Feeding",
    duration=20, priority=2,
    earliest_start="08:00", latest_end="09:00"   # same window → will overlap in schedule
))

# Non-conflicting tasks later in the day
mochi.add_task(Task(
    task_id=3, pet_id=2,
    title="Playtime",
    duration=20, priority=3,
    earliest_start="10:00", latest_end="11:00",
    recurrence="daily"
))

owner.add_pet(biscuit)
owner.add_pet(mochi)

scheduler = Scheduler(owner=owner, schedule_date=today, available_hours=4.0)
scheduler.generate_schedule()
scheduler.display_plan()
scheduler.explain_plan()

# --- Conflict detection ---
# Manually inject an overlapping entry to simulate a conflict
scheduler.entries.append({
    "task_id": 99,
    "title": "Vet appointment",
    "start": "08:15 AM",
    "end": "08:45 AM",
    "priority": 1,
    "pet_id": 1,
    "pet_name": "Biscuit",
    "pet_species": "Dog",
    "reasoning": "manually injected to test conflict detection"
})

conflicts = scheduler.detect_conflicts()
if conflicts:
    print("\n--- Schedule Conflicts ---")
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("\n✅ No conflicts detected.")
