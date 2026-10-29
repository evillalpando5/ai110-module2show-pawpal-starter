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
    due_date: date | None = None  # None means "always due" (legacy); set on auto-generated recurrences

    def edit_task(self, **kwargs) -> None:
        """Update any task field by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_completed(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self, new_task_id: int, completed_on: date) -> "Task | None":
        """Return a fresh incomplete copy of this task scheduled for its next recurrence date.

        The new task's due_date is set to completed_on + 1 day (daily) or + 7 days (weekly),
        so is_due_today() will match it on exactly that future date. Returns None for
        non-recurring tasks (recurrence not in "daily" or "weekly").
        """
        if self.recurrence == "daily":
            next_due = completed_on + timedelta(days=1)
        elif self.recurrence == "weekly":
            next_due = completed_on + timedelta(weeks=1)
        else:
            return None
        return Task(
            task_id=new_task_id,
            pet_id=self.pet_id,
            title=self.title,
            duration=self.duration,
            priority=self.priority,
            earliest_start=self.earliest_start,
            latest_end=self.latest_end,
            recurrence=self.recurrence,
            completed=False,
            due_date=next_due,
        )

    def fits_in_window(self) -> bool:
        """Returns True if duration fits between earliest_start and latest_end."""
        start = _parse_time(self.earliest_start)
        end = _parse_time(self.latest_end)
        window_minutes = (end - start).seconds // 60
        return self.duration <= window_minutes

    def is_due_today(self, today: date, last_completed: date | None = None) -> bool:
        """Returns True if task should appear on today's schedule."""
        if self.due_date is not None:
            return self.due_date == today
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

    def complete_task(self, task_id: int, completed_on: date) -> "Task | None":
        """Mark a task done and automatically queue its next occurrence if it recurs.

        The replacement task gets an id one higher than the current maximum in this pet's
        task list and is appended (not inserted), so existing order is preserved. Returns
        the newly created Task, or None if the task doesn't recur or wasn't found.
        """
        task = self.get_task(task_id)
        if task is None:
            return None
        task.mark_completed()
        new_task_id = max(t.task_id for t in self.tasks) + 1
        next_task = task.next_occurrence(new_task_id, completed_on)
        if next_task:
            self.tasks.append(next_task)
        return next_task

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
        for task in tasks:
            if not self.check_constraints(task, minutes_remaining):
                continue
            pet = self._pet_for_task(task)
            task_start = datetime(
                self.schedule_date.year,
                self.schedule_date.month,
                self.schedule_date.day,
                int(task.earliest_start.split(":")[0]),
                int(task.earliest_start.split(":")[1]),
            )
            end_time = task_start + timedelta(minutes=task.duration)
            self.entries.append({
                "task_id": task.task_id,
                "title": task.title,
                "start": task_start.strftime("%I:%M %p"),
                "end": end_time.strftime("%I:%M %p"),
                "priority": task.priority,
                "pet_id": task.pet_id,
                "pet_name": pet.name if pet else "Unknown",
                "pet_species": pet.species if pet else "",
                "reasoning": f"Priority {task.priority}, fits in {task.duration}min window"
            })
            minutes_remaining -= task.duration

    def check_constraints(self, task: Task, minutes_remaining: float) -> bool:
        """Return True if the task fits its time window and the day's remaining time."""
        return task.fits_in_window() and task.duration <= minutes_remaining

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority ascending (1 = highest)."""
        return sorted(tasks, key=lambda t: t.priority)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted chronologically by earliest_start.

        Zero-padded "HH:MM" strings sort correctly with plain string comparison
        (lexicographic order matches chronological order), so no time parsing is needed.
        The original list is not modified.
        """
        return sorted(tasks, key=lambda t: t.earliest_start)

    def filter_by_completion(self, tasks: list[Task], completed: bool = False) -> list[Task]:
        """Return tasks filtered by their completed flag.

        Defaults to completed=False (pending tasks) since that is the common scheduling case.
        Pass completed=True to retrieve a history of finished tasks.
        """
        return [t for t in tasks if t.completed == completed]

    def detect_conflicts(self) -> list[str]:
        """Check all scheduled entries for overlapping time slots and return human-readable warnings.

        Uses the standard interval overlap test: two ranges [a_start, a_end) and [b_start, b_end)
        overlap when a_start < b_end AND b_start < a_end. Each pair is checked once (O(n²)).
        Conflicts across different pets are flagged the same as same-pet conflicts.
        Returns an empty list when no overlaps are found.
        """
        warnings = []
        for i, a in enumerate(self.entries):
            for b in self.entries[i + 1:]:
                a_start = datetime.strptime(a["start"], "%I:%M %p")
                a_end   = datetime.strptime(a["end"],   "%I:%M %p")
                b_start = datetime.strptime(b["start"], "%I:%M %p")
                b_end   = datetime.strptime(b["end"],   "%I:%M %p")
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"⚠️  Conflict: '{a['title']}' ({a['start']}–{a['end']}, {a['pet_name']}) "
                        f"overlaps with '{b['title']}' ({b['start']}–{b['end']}, {b['pet_name']})"
                    )
        return warnings

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
