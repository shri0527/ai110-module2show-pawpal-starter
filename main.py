from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
owner = Owner(name="Alex", available_minutes=120, preferences=["feeding", "walk"])

# Create pets
buddy = Pet(name="Buddy", species="dog", age=3, notes="Loves morning walks")
whiskers = Pet(name="Whiskers", species="cat", age=5, notes="Indoor cat, needs daily meds")

# Add tasks to Buddy
buddy.add_task(Task(title="Morning Walk", duration_minutes=30, priority="high", category="walk", pet_name="Buddy"))
buddy.add_task(Task(title="Feed Breakfast", duration_minutes=10, priority="high", category="feeding", pet_name="Buddy"))
buddy.add_task(Task(title="Brush Coat", duration_minutes=15, priority="low", category="grooming", pet_name="Buddy"))

# Add tasks to Whiskers
whiskers.add_task(Task(title="Give Medication", duration_minutes=5, priority="high", category="meds", pet_name="Whiskers"))
whiskers.add_task(Task(title="Feed Dinner", duration_minutes=10, priority="medium", category="feeding", pet_name="Whiskers"))
whiskers.add_task(Task(title="Playtime", duration_minutes=20, priority="low", category="play", pet_name="Whiskers"))

# Add pets to owner
owner.add_pet(buddy)
owner.add_pet(whiskers)

# Build today's schedule
scheduler = Scheduler(owner)
schedule = scheduler.build_schedule(date.today())

# Print Today's Schedule
print("=" * 50)
print(f"  TODAY'S SCHEDULE — {schedule.date.strftime('%A, %B %d %Y')}")
print(f"  Owner: {schedule.owner_name}")
print("=" * 50)

for task in schedule.tasks:
    status = "[DONE]" if task.is_done else "[ ]"
    reason = schedule.explanations.get(task.id, "")
    print(f"\n  {status} {task.title}")
    print(f"       Pet      : {task.pet_name}")
    print(f"       Category : {task.category}")
    print(f"       Priority : {task.priority.upper()}")
    print(f"       Duration : {task.duration_minutes} min")
    if reason:
        print(f"       Note     : {reason}")

print("\n" + "=" * 50)
print(f"  Total scheduled time : {schedule.total_time()} min")
print(f"  Available time       : {owner.available_minutes} min")
print("=" * 50)
