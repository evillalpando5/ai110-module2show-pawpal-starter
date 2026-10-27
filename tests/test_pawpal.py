from pawpal_system import Pet, Task


def make_task(task_id=1, pet_id=1):
    return Task(
        task_id=task_id, pet_id=pet_id,
        title="Test task",
        duration=20, priority=2,
        earliest_start="08:00", latest_end="10:00"
    )


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
