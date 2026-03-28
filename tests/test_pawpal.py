import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler


def test_task_completion():
    """Calling mark_done() should set is_done to True."""
    task = Task(title="Morning Walk", duration_minutes=30, priority="high", category="walk", pet_name="Buddy")
    assert task.is_done == False
    task.mark_done()
    assert task.is_done == True


def test_task_addition():
    """Adding a task to a Pet should increase its task count by 1."""
    pet = Pet(name="Buddy", species="dog", age=3)
    assert len(pet.tasks) == 0
    task = Task(title="Feed Breakfast", duration_minutes=10, priority="medium", category="feeding", pet_name="Buddy")
    pet.add_task(task)
    assert len(pet.tasks) == 1


def test_sort_by_time_chronological():
    """sort_by_time() should return tasks in ascending HH:MM order, unscheduled last."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="dog", age=3)
    owner.add_pet(pet)

    late  = Task(title="Evening Walk",   duration_minutes=30, priority="low",    category="walk",    pet_name="Buddy", scheduled_time="18:00")
    early = Task(title="Morning Meds",   duration_minutes=10, priority="high",   category="meds",    pet_name="Buddy", scheduled_time="07:30")
    none_ = Task(title="Grooming",       duration_minutes=20, priority="medium", category="grooming",pet_name="Buddy", scheduled_time="")

    for t in (late, early, none_):
        pet.add_task(t)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    assert sorted_tasks[0].scheduled_time == "07:30", "earliest timed task should be first"
    assert sorted_tasks[1].scheduled_time == "18:00", "later timed task should be second"
    assert sorted_tasks[2].scheduled_time == "",      "unscheduled task should be last"


def test_daily_recurrence_spawns_next_day():
    """Marking a daily recurring task done should create a new occurrence for the next day."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Luna", species="cat", age=2)
    owner.add_pet(pet)

    daily_task = Task(
        title="Morning Feed", duration_minutes=10, priority="high",
        category="feeding", pet_name="Luna", recurrence="daily",
    )
    pet.add_task(daily_task)  # goes into pet.recurring_tasks

    scheduler = Scheduler(owner)
    completion_date = date(2026, 3, 28)  # a Saturday
    found = scheduler.mark_task_done(daily_task.id, completion_date=completion_date)

    assert found, "mark_task_done should return True when the task is found"
    assert daily_task.is_done, "the original task should be marked done"

    next_occurrences = [t for t in pet.recurring_tasks i
    f not t.is_done]
    assert len(next_occurrences) == 1, "exactly one new occurrence should be created"
    assert next_occurrences[0].due_date == date(2026, 3, 29), "next occurrence should be the following day"


def test_conflict_detection_same_time():
    """Two tasks starting at the same time should be flagged as a conflict."""
    owner = Owner(name="Alex", available_minutes=300)
    pet = Pet(name="Buddy", species="dog", age=3)
    owner.add_pet(pet)

    task_a = Task(title="Walk",  duration_minutes=30, priority="high",   category="walk",    pet_name="Buddy", scheduled_time="08:00")
    task_b = Task(title="Meds",  duration_minutes=15, priority="high",   category="meds",    pet_name="Buddy", scheduled_time="08:00")

    for t in (task_a, task_b):
        pet.add_task(t)

    scheduler = Scheduler(owner)
    schedule = scheduler.build_schedule(date(2026, 3, 28))

    assert len(schedule.conflicts) == 1, "overlapping tasks at 08:00 should produce one conflict"
    conflict_ids = {schedule.conflicts[0][0].id, schedule.conflicts[0][1].id}
    assert task_a.id in conflict_ids and task_b.id in conflict_ids
