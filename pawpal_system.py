from dataclasses import dataclass, field
from datetime import date
from typing import Literal
import uuid


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    category: str          # e.g. "feeding", "walk", "meds", "grooming"
    pet_name: str          # which pet this task belongs to
    is_done: bool = False
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
        if is_done is not None:
            self.is_done = is_done


@dataclass
class Pet:
    name: str
    species: Literal["dog", "cat", "other"]
    age: int
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str):
        """Remove the task with the given ID from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.id != task_id]


class Schedule:
    def __init__(self, schedule_date: date, owner_name: str):
        self.date = schedule_date
        self.owner_name = owner_name
        self.tasks: list[Task] = []
        self.explanations: dict[str, str] = {}  # task id -> reason it was chosen

    def display(self):
        """Print all scheduled tasks with their status and selection reason."""
        print(f"Schedule for {self.owner_name} on {self.date}  |  Total time: {self.total_time()} min")
        for task in self.tasks:
            reason = self.explanations.get(task.id, "")
            status = "done" if task.is_done else "pending"
            print(f"  [{task.priority.upper()}] {task.title} for {task.pet_name} ({task.duration_minutes} min) [{status}] — {reason}")

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
        """Returns every task across all pets — useful for the Scheduler."""
        return [task for pet in self.pets for task in pet.tasks]


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an Owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    # ------------------------------------------------------------------
    # Core schedule-building
    # ------------------------------------------------------------------

    def build_schedule(self, schedule_date: date) -> Schedule:
        """Build and return a priority-sorted schedule that fits within the owner's available time."""
        pending = [t for t in self.owner.all_tasks() if not t.is_done]

        # Sort: priority first, then shorter tasks first as a tiebreaker
        pending.sort(key=lambda t: (PRIORITY_ORDER[t.priority], t.duration_minutes))

        # Apply owner category preferences: preferred categories jump to the front
        if self.owner.preferences:
            pending.sort(key=lambda t: (
                0 if t.category in self.owner.preferences else 1,
                PRIORITY_ORDER[t.priority],
                t.duration_minutes,
            ))

        schedule = Schedule(schedule_date, self.owner.name)
        time_remaining = self.owner.available_minutes

        for task in pending:
            if task.duration_minutes <= time_remaining:
                schedule.tasks.append(task)
                schedule.explanations[task.id] = self._explain(task)
                time_remaining -= task.duration_minutes

        self.owner.set_schedule(schedule)
        return schedule

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

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def mark_task_done(self, task_id: str) -> bool:
        """Find a task by ID across all pets and mark it done. Returns True if found."""
        for task in self.owner.all_tasks():
            if task.id == task_id:
                task.mark_done()
                return True
        return False

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID from whichever pet owns it. Returns True if found."""
        for pet in self.owner.pets:
            before = len(pet.tasks)
            pet.remove_task(task_id)
            if len(pet.tasks) < before:
                return True
        return False

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
