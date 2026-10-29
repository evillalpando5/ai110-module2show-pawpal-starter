from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


def make_task(task_id=1, pet_id=1, priority=2, earliest_start="08:00", latest_end="10:00",
              duration=20, recurrence="daily", title="Test task"):
    return Task(
        task_id=task_id, pet_id=pet_id,
        title=title,
        duration=duration, priority=priority,
        earliest_start=earliest_start, latest_end=latest_end,
        recurrence=recurrence,
    )


def make_owner_with_pet(*tasks):
    owner = Owner(owner_id=1, name="Tester", email="t@test.com")
    pet = Pet(pet_id=1, owner_id=1, name="Biscuit", species="Dog", age="3", care_notes="")
    for t in tasks:
        pet.add_task(t)
    owner.add_pet(pet)
    return owner, pet


# --- Existing tests ---

def test_mark_completed_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_completed()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(pet_id=1, owner_id=1, name="Biscuit", species="Dog", age="3", care_notes="")
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1


# --- Sorting correctness ---

def test_sort_by_time_returns_chronological_order():
    t1 = make_task(task_id=1, earliest_start="10:00", latest_end="11:00")
    t2 = make_task(task_id=2, earliest_start="08:00", latest_end="09:00")
    t3 = make_task(task_id=3, earliest_start="09:00", latest_end="10:00")
    owner, _ = make_owner_with_pet(t1, t2, t3)
    scheduler = Scheduler(owner=owner, schedule_date=date.today(), available_hours=8.0)
    sorted_tasks = scheduler.sort_by_time([t1, t2, t3])
    starts = [t.earliest_start for t in sorted_tasks]
    assert starts == sorted(starts)


def test_prioritize_tasks_orders_by_priority_ascending():
    t_low = make_task(task_id=1, priority=5)
    t_high = make_task(task_id=2, priority=1)
    t_mid = make_task(task_id=3, priority=3)
    owner, _ = make_owner_with_pet(t_low, t_high, t_mid)
    scheduler = Scheduler(owner=owner, schedule_date=date.today(), available_hours=8.0)
    result = scheduler.prioritize_tasks([t_low, t_high, t_mid])
    assert [t.priority for t in result] == [1, 3, 5]


# --- Recurrence logic ---

def test_complete_daily_task_creates_next_day_occurrence():
    today = date.today()
    pet = Pet(pet_id=1, owner_id=1, name="Biscuit", species="Dog", age="3", care_notes="")
    task = make_task(task_id=1, recurrence="daily")
    pet.add_task(task)
    next_task = pet.complete_task(task_id=1, completed_on=today)
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_complete_weekly_task_creates_next_week_occurrence():
    today = date.today()
    pet = Pet(pet_id=1, owner_id=1, name="Biscuit", species="Dog", age="3", care_notes="")
    task = make_task(task_id=1, recurrence="weekly")
    pet.add_task(task)
    next_task = pet.complete_task(task_id=1, completed_on=today)
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_completed_task_excluded_from_due_tasks():
    today = date.today()
    pet = Pet(pet_id=1, owner_id=1, name="Biscuit", species="Dog", age="3", care_notes="")
    task = make_task(task_id=1)
    task.mark_completed()
    pet.add_task(task)
    assert pet.due_tasks(today) == []


# --- Conflict detection ---

def test_detect_conflicts_flags_overlapping_entries():
    owner, _ = make_owner_with_pet()
    scheduler = Scheduler(owner=owner, schedule_date=date.today(), available_hours=4.0)
    scheduler.entries = [
        {"task_id": 1, "title": "Walk",    "start": "08:00 AM", "end": "08:30 AM",
         "priority": 1, "pet_id": 1, "pet_name": "Biscuit", "pet_species": "Dog", "reasoning": ""},
        {"task_id": 2, "title": "Feeding", "start": "08:15 AM", "end": "08:45 AM",
         "priority": 2, "pet_id": 1, "pet_name": "Biscuit", "pet_species": "Dog", "reasoning": ""},
    ]
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Feeding" in conflicts[0]


def test_detect_conflicts_identical_start_times():
    owner, _ = make_owner_with_pet()
    scheduler = Scheduler(owner=owner, schedule_date=date.today(), available_hours=4.0)
    scheduler.entries = [
        {"task_id": 1, "title": "Walk",    "start": "08:00 AM", "end": "08:30 AM",
         "priority": 1, "pet_id": 1, "pet_name": "Biscuit", "pet_species": "Dog", "reasoning": ""},
        {"task_id": 2, "title": "Feeding", "start": "08:00 AM", "end": "08:20 AM",
         "priority": 2, "pet_id": 2, "pet_name": "Mochi",   "pet_species": "Cat", "reasoning": ""},
    ]
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1


def test_back_to_back_tasks_no_conflict():
    owner, _ = make_owner_with_pet()
    scheduler = Scheduler(owner=owner, schedule_date=date.today(), available_hours=4.0)
    scheduler.entries = [
        {"task_id": 1, "title": "Walk",    "start": "08:00 AM", "end": "08:30 AM",
         "priority": 1, "pet_id": 1, "pet_name": "Biscuit", "pet_species": "Dog", "reasoning": ""},
        {"task_id": 2, "title": "Feeding", "start": "08:30 AM", "end": "08:50 AM",
         "priority": 2, "pet_id": 1, "pet_name": "Biscuit", "pet_species": "Dog", "reasoning": ""},
    ]
    conflicts = scheduler.detect_conflicts()
    assert conflicts == []


# --- Pet with no tasks ---

def test_pet_with_no_tasks_generates_empty_schedule():
    owner, _ = make_owner_with_pet()  # pet has no tasks
    scheduler = Scheduler(owner=owner, schedule_date=date.today(), available_hours=4.0)
    scheduler.generate_schedule()
    assert scheduler.entries == []


def test_pet_with_no_tasks_due_tasks_returns_empty():
    pet = Pet(pet_id=1, owner_id=1, name="Biscuit", species="Dog", age="3", care_notes="")
    assert pet.due_tasks(date.today()) == []


# --- Task that doesn't fit its own window ---

def test_task_too_long_for_window_is_excluded():
    # 60-min task in a 30-min window → should not be scheduled
    task = make_task(task_id=1, duration=60, earliest_start="08:00", latest_end="08:30")
    owner, _ = make_owner_with_pet(task)
    scheduler = Scheduler(owner=owner, schedule_date=date.today(), available_hours=4.0)
    scheduler.generate_schedule()
    assert scheduler.entries == []
