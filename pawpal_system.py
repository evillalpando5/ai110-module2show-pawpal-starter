from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


def _parse_time(t: str) -> datetime:
    return datetime.strptime(t, "%H:%M")


@dataclass
class Task:
    task_id: int
    pet_id: int
    title: str
    duration: int        # minutes
    priority: int        # 1 (highest) to 5 (lowest)
    earliest_start: str  # "HH:MM"
    latest_end: str      # "HH:MM"
    recurrence: str = "daily"   # "daily" or "weekly"
    completed: bool = False

    def edit_task(self, **kwargs) -> None:
        """Update any task field by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_completed(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def fits_in_window(self) -> bool:
        """Returns True if duration fits between earliest_start and latest_end."""
        start = _parse_time(self.earliest_start)
        end = _parse_time(self.latest_end)
        window_minutes = (end - start).seconds // 60
        return self.duration <= window_minutes

    def is_due_today(self, today: date, last_completed: date | None = None) -> bool:
        """Returns True if task should appear on today's schedule."""
        if self.recurrence == "daily":
            return True
        if self.recurrence == "weekly":
            return last_completed is None or (today - last_completed).days >= 7
        return False


@dataclass
class Pet:
    pet_id: int
    owner_id: int
    name: str
    species: str
    age: str
    care_notes: str
    tasks: list[Task] = field(default_factory=list)

    def edit_pet_info(self, **kwargs) -> None:
        """Update any pet field by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def add_task(self, task: Task) -> None:
        """Append a task and stamp it with this pet's id."""
        task.pet_id = self.pet_id
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove the task with the given id from this pet's list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_task(self, task_id: int) -> Task | None:
        """Return the task matching task_id, or None if not found."""
        return next((t for t in self.tasks if t.task_id == task_id), None)

    def due_tasks(self, today: date) -> list[Task]:
        """Return incomplete tasks that are due on the given date."""
        return [t for t in self.tasks if not t.completed and t.is_due_today(today)]


@dataclass
class Owner:
    owner_id: int
    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Append a pet and stamp it with this owner's id."""
        pet.owner_id = self.owner_id
        self.pets.append(pet)

    def edit_owner_info(self, **kwargs) -> None:
        """Update any owner field by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_pet(self, pet_id: int) -> Pet | None:
        """Return the pet matching pet_id, or None if not found."""
        return next((p for p in self.pets if p.pet_id == pet_id), None)

    def get_all_tasks(self, today: date | None = None) -> list[Task]:
        """Returns every task across all pets, optionally filtered to those due today."""
        if today:
            return [t for p in self.pets for t in p.due_tasks(today)]
        return [t for p in self.pets for t in p.tasks]


@dataclass
class Scheduler:
    owner: Owner
    schedule_date: date
    available_hours: float
    entries: list[dict] = field(default_factory=list)

    def _pet_for_task(self, task: Task) -> Pet:
        """Look up the pet that owns a given task."""
        return self.owner.get_pet(task.pet_id)

    def generate_schedule(self) -> None:
        """Build the day's schedule from all due tasks across every pet."""
        self.entries = []
        tasks = self.prioritize_tasks(self.owner.get_all_tasks(self.schedule_date))
        minutes_remaining = self.available_hours * 60
        current_time = datetime(
            self.schedule_date.year,
            self.schedule_date.month,
            self.schedule_date.day, 8, 0
        )
        for task in tasks:
            if not self.check_constraints(task, minutes_remaining):
                continue
            pet = self._pet_for_task(task)
            end_time = current_time + timedelta(minutes=task.duration)
            self.entries.append({
                "task_id": task.task_id,
                "title": task.title,
                "start": current_time.strftime("%I:%M %p"),
                "end": end_time.strftime("%I:%M %p"),
                "priority": task.priority,
                "pet_id": task.pet_id,
                "pet_name": pet.name if pet else "Unknown",
                "pet_species": pet.species if pet else "",
                "reasoning": f"Priority {task.priority}, fits in {task.duration}min window"
            })
            minutes_remaining -= task.duration
            current_time = end_time

    def check_constraints(self, task: Task, minutes_remaining: float) -> bool:
        """Return True if the task fits its time window and the day's remaining time."""
        return task.fits_in_window() and task.duration <= minutes_remaining

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority ascending (1 = highest)."""
        return sorted(tasks, key=lambda t: t.priority)

    def display_plan(self) -> None:
        """Print the day's schedule grouped by pet with AM/PM times."""
        date_str = self.schedule_date.strftime("%A, %B %d %Y")
        bar = "=" * 60
        print(f"\n{bar}")
        print(f"  Daily Plan for {self.owner.name} — {date_str}")
        print(bar)

        # group entries by pet
        seen_pets = []
        pets_order = []
        for e in self.entries:
            if e["pet_id"] not in seen_pets:
                seen_pets.append(e["pet_id"])
                pets_order.append((e["pet_id"], e["pet_name"], e["pet_species"]))

        for pet_id, pet_name, pet_species in pets_order:
            print(f"\n  {pet_name} ({pet_species})")
            print("  " + "─" * 44)
            pet_entries = [e for e in self.entries if e["pet_id"] == pet_id]
            for e in pet_entries:
                title = e["title"].ljust(22)
                print(f"  {e['start']} – {e['end']}   {title} ★ Priority {e['priority']}")

        print(f"\n{bar}")

    def explain_plan(self) -> None:
        """Print the reasoning behind each scheduled task."""
        bar = "=" * 60
        print(f"  Reasoning")
        print("  " + "─" * 44)
        for e in self.entries:
            title = e["title"].ljust(16)
            print(f"  {title} → {e['reasoning']}")
        print(bar)
