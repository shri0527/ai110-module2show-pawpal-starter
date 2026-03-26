from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str          # "low", "medium", "high"
    category: str          # e.g. "feeding", "walk", "meds", "grooming"
    is_done: bool = False

    def mark_done(self):
        self.is_done = True

    def edit(self, title: str = None, duration_minutes: int = None, priority: str = None):
        if title is not None:
            self.title = title
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = priority


@dataclass
class Pet:
    name: str
    species: str           # "dog", "cat", "other"
    age: int
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, title: str):
        self.tasks = [t for t in self.tasks if t.title != title]


class Schedule:
    def __init__(self, date: date):
        self.date = date
        self.tasks: list[Task] = []
        self.explanations: dict[str, str] = {}  # task title -> reason it was chosen

    def display(self):
        print(f"Schedule for {self.date}")
        for task in self.tasks:
            reason = self.explanations.get(task.title, "")
            print(f"  [{task.priority.upper()}] {task.title} ({task.duration_minutes} min) — {reason}")

    def total_time(self) -> int:
        return sum(t.duration_minutes for t in self.tasks)


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: list[str] = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: list[str] = preferences or []
        self.pets: list[Pet] = []
        self.schedule: Schedule | None = None

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def set_schedule(self, schedule: Schedule):
        self.schedule = schedule
