import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
