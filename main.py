from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

today = date.today()

owner = Owner(owner_id=1, name="Erika", email="erika@email.com")

biscuit = Pet(pet_id=1, owner_id=1, name="Biscuit", species="Dog", age="3", care_notes="Loves morning walks")
mochi = Pet(pet_id=2, owner_id=1, name="Mochi", species="Cat", age="2", care_notes="Indoor only, needs enrichment")

biscuit.add_task(Task(
    task_id=1, pet_id=1,
    title="Morning walk",
    duration=30, priority=1,
    earliest_start="08:00", latest_end="09:00"
))
biscuit.add_task(Task(
    task_id=2, pet_id=1,
    title="Feeding",
    duration=10, priority=2,
    earliest_start="09:00", latest_end="09:30"
))
mochi.add_task(Task(
    task_id=3, pet_id=2,
    title="Playtime",
    duration=20, priority=3,
    earliest_start="10:00", latest_end="11:00",
    recurrence="daily"
))
mochi.add_task(Task(
    task_id=4, pet_id=2,
    title="Brush fur",
    duration=15, priority=4,
    earliest_start="11:00", latest_end="12:00",
    recurrence="weekly"
))

owner.add_pet(biscuit)
owner.add_pet(mochi)

scheduler = Scheduler(owner=owner, schedule_date=today, available_hours=4.0)
scheduler.generate_schedule()
scheduler.display_plan()
scheduler.explain_plan()
