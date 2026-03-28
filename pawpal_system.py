from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal
import uuid


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    category: str          # e.g. "feeding", "walk", "meds", "grooming"
    pet_name: str          # which pet this task belongs to
    scheduled_time: str = ""   # "HH:MM" format, e.g. "08:00" — empty means unscheduled
    recurrence: Literal["none", "daily", "weekly"] = "none"
    repeat_days: list[str] = field(default_factory=list)  # e.g. ["Mon", "Wed"] for weekly
    is_done: bool = False
    due_date: date | None = None  # next occurrence date for recurring tasks
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_done(self):
        """Mark this task as completed."""
        self.is_done = True

    def edit(
        self,
        title: str = None,
        duration_minutes: int = None,
        priority: Literal["low", "medium", "high"] = None,
        category: str = None,
        scheduled_time: str = None,
        is_done: bool = None,
    ):
        """Update any subset of this task's fields in place."""
        if title is not None:
            self.title = title
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = priority
        if category is not None:
            self.category = category
        if scheduled_time is not None:
            self.scheduled_time = scheduled_time
        if is_done is not None:
            self.is_done = is_done

    def _start_minutes(self) -> int | None:
        """Convert scheduled_time 'HH:MM' to minutes since midnight, or None if unscheduled."""
        if not self.scheduled_time:
            return None
        h, m = self.scheduled_time.split(":")
        return int(h) * 60 + int(m)

    def _end_minutes(self) -> int | None:
        """Return the minute-of-day when this task ends, or None if unscheduled."""
        start = self._start_minutes()
        if start is None:
            return None
        return start + self.duration_minutes

    def copy(self, **overrides) -> "Task":
        """Return a new Task with the same fields, with any overrides applied."""
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            pet_name=self.pet_name,
            scheduled_time=self.scheduled_time,
            recurrence=self.recurrence,
            repeat_days=list(self.repeat_days),
            due_date=self.due_date,
            **overrides,
        )


@dataclass
class Pet:
    name: str
    species: Literal["dog", "cat", "other"]
    age: int
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)
    recurring_tasks: list[Task] = field(default_factory=list)  # master list of recurring task templates

    def add_task(self, task: Task):
        """Append a task to this pet's list. Recurring tasks go to recurring_tasks; one-off tasks go to tasks."""
        if task.recurrence != "none":
            self.recurring_tasks.append(task)
        else:
            self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove the task with the given ID from both lists. Returns True if found."""
        before = len(self.tasks) + len(self.recurring_tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.recurring_tasks = [t for t in self.recurring_tasks if t.id != task_id]
        return len(self.tasks) + len(self.recurring_tasks) < before


class Schedule:
    def __init__(self, schedule_date: date, owner_name: str):
        self.date = schedule_date
        self.owner_name = owner_name
        self.tasks: list[Task] = []
        self.explanations: dict[str, str] = {}  # task id -> reason it was chosen
        self.conflicts: list[tuple[Task, Task]] = []  # pairs of overlapping timed tasks

    def filter_tasks(self, pet_name: str = None, done: bool = None) -> list[Task]:
        """Return a filtered view of scheduled tasks, optionally narrowed by pet name and/or completion status."""
        return [
            t for t in self.tasks
            if (pet_name is None or t.pet_name == pet_name)
            and (done is None or t.is_done == done)
        ]

    def display(self):
        """Print all scheduled tasks with their status and selection reason."""
        print(f"Schedule for {self.owner_name} on {self.date}  |  Total time: {self.total_time()} min")
        for task in self.tasks:
            reason = self.explanations.get(task.id, "")
            status = "done" if task.is_done else "pending"
            time_label = f" @ {task.scheduled_time}" if task.scheduled_time else ""
            print(f"  [{task.priority.upper()}] {task.title} for {task.pet_name} ({task.duration_minutes} min){time_label} [{status}] — {reason}")

    def total_time(self) -> int:
        """Return the total duration in minutes of all tasks in this schedule."""
        return sum(t.duration_minutes for t in self.tasks)


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: list[str] = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: list[str] = preferences or []
        self.pets: list[Pet] = []
        self.schedule: Schedule | None = None

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def set_schedule(self, schedule: Schedule):
        """Assign a schedule to this owner."""
        self.schedule = schedule

    def all_tasks(self) -> list[Task]:
        """Returns every one-off task across all pets — useful for the Scheduler."""
        return [task for pet in self.pets for task in pet.tasks]


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
DAY_MAP = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an Owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    # ------------------------------------------------------------------
    # Core schedule-building
    # ------------------------------------------------------------------

    def build_schedule(self, schedule_date: date) -> Schedule:
        """
        Build and return today's schedule in four steps:
        1. Inject copies of recurring tasks that apply today into each pet's one-off task list.
        2. Collect all pending one-off tasks, sort by priority and owner preferences.
        3. Greedily pick tasks that fit within the owner's available_minutes.
        4. Sort the final task list chronologically by scheduled_time, then detect time conflicts.
        Attaches the finished Schedule to the owner and returns it.
        """
        # Step 1 — inject recurring tasks that apply today
        today_name = schedule_date.strftime("%a")  # e.g. "Mon"
        for pet in self.owner.pets:
            for rt in pet.recurring_tasks:
                applies = (
                    rt.recurrence == "daily"
                    or (rt.recurrence == "weekly" and today_name in rt.repeat_days)
                )
                if applies and not rt.is_done:
                    # Add a fresh copy so the master recurring task isn't consumed
                    pet.tasks.append(rt.copy(recurrence="none"))

        # Step 2 — collect and sort pending one-off tasks
        prefs = set(self.owner.preferences)
        pending = [t for t in self.owner.all_tasks() if not t.is_done]
        pending.sort(key=lambda t: (
            0 if t.category in prefs else 1,
            PRIORITY_ORDER[t.priority],
            t.duration_minutes,
        ))

        schedule = Schedule(schedule_date, self.owner.name)
        time_remaining = self.owner.available_minutes

        # Step 3 — greedy fit within available time
        for task in pending:
            if task.duration_minutes <= time_remaining:
                schedule.tasks.append(task)
                schedule.explanations[task.id] = self._explain(task)
                time_remaining -= task.duration_minutes

        # Step 4 — sort chronologically; unscheduled tasks go to the end
        schedule.tasks.sort(key=lambda t: t.scheduled_time or "99:99")

        # Detect and record any time conflicts between timed tasks
        schedule.conflicts = self.detect_conflicts(schedule)

        self.owner.set_schedule(schedule)
        return schedule

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self, schedule: Schedule) -> list[tuple[Task, Task]]:
        """
        Return pairs of tasks whose scheduled time windows overlap.
        Only tasks with a scheduled_time are checked; unscheduled tasks are skipped.
        """
        timed = [t for t in schedule.tasks if t.scheduled_time]
        timed.sort(key=lambda t: t.scheduled_time)

        conflicts = []
        for i in range(len(timed) - 1):
            a = timed[i]
            b = timed[i + 1]
            if a._end_minutes() > b._start_minutes():
                conflicts.append((a, b))
        return conflicts

    # ------------------------------------------------------------------
    # Task queries
    # ------------------------------------------------------------------

    def get_tasks_by_priority(self, priority: Literal["low", "medium", "high"]) -> list[Task]:
        """Return all tasks (across all pets) matching the given priority."""
        return [t for t in self.owner.all_tasks() if t.priority == priority]

    def get_tasks_by_category(self, category: str) -> list[Task]:
        """Return all tasks (across all pets) matching the given category."""
        return [t for t in self.owner.all_tasks() if t.category == category]

    def get_tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks belonging to a specific pet."""
        return [t for t in self.owner.all_tasks() if t.pet_name == pet_name]

    def pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks across all pets."""
        return [t for t in self.owner.all_tasks() if not t.is_done]

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted chronologically by scheduled_time. Unscheduled tasks go to the end."""
        return sorted(self.owner.all_tasks(), key=lambda t: t.scheduled_time if t.scheduled_time else "99:99")

    def filter_tasks(self, pet_name: str = None, done: bool = None) -> list[Task]:
        """Return tasks across all pets, optionally filtered by pet name and/or completion status."""
        result = self.owner.all_tasks()
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if done is not None:
            result = [t for t in result if t.is_done == done]
        return result

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def mark_task_done(self, task_id: str, completion_date: date = None) -> bool:
        """Find a task by ID across all pets (including recurring) and mark it done.
        For daily/weekly recurring tasks, automatically creates the next occurrence.
        Returns True if found."""
        if completion_date is None:
            completion_date = date.today()

        # Search one-off tasks first
        for task in self.owner.all_tasks():
            if task.id == task_id:
                task.mark_done()
                return True

        # Search recurring tasks; spawn next occurrence when marked done
        for pet in self.owner.pets:
            for task in pet.recurring_tasks:
                if task.id == task_id:
                    task.mark_done()
                    self._spawn_next_occurrence(pet, task, completion_date)
                    return True

        return False

    def _spawn_next_occurrence(self, pet: "Pet", completed_task: Task, completion_date: date):
        """Create the next occurrence of a daily or weekly task and add it to the pet."""
        if completed_task.recurrence == "daily":
            next_date = completion_date + timedelta(days=1)
        elif completed_task.recurrence == "weekly":
            next_date = self._next_weekly_date(completion_date, completed_task.repeat_days)
        else:
            return

        pet.recurring_tasks.append(completed_task.copy(due_date=next_date))

    def _next_weekly_date(self, from_date: date, repeat_days: list[str]) -> date:
        """Return the nearest date after from_date that falls on one of the repeat_days."""
        target_weekdays = {DAY_MAP[d] for d in repeat_days if d in DAY_MAP}
        for offset in range(1, 8):
            candidate = from_date + timedelta(days=offset)
            if candidate.weekday() in target_weekdays:
                return candidate
        return from_date + timedelta(days=7)  # fallback

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID from whichever pet owns it. Returns True if found."""
        return any(pet.remove_task(task_id) for pet in self.owner.pets)

    # ------------------------------------------------------------------
    # Summary / reporting
    # ------------------------------------------------------------------

    def summary(self):
        """Print a quick overview of all tasks grouped by pet."""
        print(f"=== PawPal Summary for {self.owner.name} ===")
        print(f"Pets: {len(self.owner.pets)}  |  Available time: {self.owner.available_minutes} min")
        for pet in self.owner.pets:
            done = sum(1 for t in pet.tasks if t.is_done)
            print(f"\n  {pet.name} ({pet.species}, age {pet.age})  —  {done}/{len(pet.tasks)} tasks done")
            for task in pet.tasks:
                status = "✓" if task.is_done else "○"
                print(f"    {status} [{task.priority.upper()}] {task.title} ({task.duration_minutes} min, {task.category})")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _explain(self, task: Task) -> str:
        """Return a human-readable string explaining why a task was included in the schedule."""
        reasons = []
        if task.priority == "high":
            reasons.append("high priority")
        if task.category in self.owner.preferences:
            reasons.append(f"preferred category '{task.category}'")
        return ", ".join(reasons) if reasons else "fits available time"
