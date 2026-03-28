from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
owner = Owner(name="Alex", available_minutes=120, preferences=["feeding", "walk"])

# Create pets
buddy = Pet(name="Buddy", species="dog", age=3, notes="Loves morning walks")
whiskers = Pet(name="Whiskers", species="cat", age=5, notes="Indoor cat, needs daily meds")

# --- One-off tasks added OUT OF ORDER (scrambled times) ---
buddy.add_task(Task(title="Brush Coat",     duration_minutes=15, priority="low",    category="grooming", pet_name="Buddy",    scheduled_time="09:00"))
buddy.add_task(Task(title="Morning Walk",   duration_minutes=30, priority="high",   category="walk",     pet_name="Buddy",    scheduled_time="07:00"))
whiskers.add_task(Task(title="Feed Dinner",     duration_minutes=10, priority="medium", category="feeding", pet_name="Whiskers", scheduled_time="17:00"))
buddy.add_task(Task(title="Feed Breakfast", duration_minutes=10, priority="high",   category="feeding",  pet_name="Buddy",    scheduled_time="07:45"))
whiskers.add_task(Task(title="Give Medication", duration_minutes=5,  priority="high",   category="meds",    pet_name="Whiskers", scheduled_time="08:00"))

# --- Recurring tasks ---
# Daily: Whiskers gets playtime every day
whiskers.add_task(Task(
    title="Playtime", duration_minutes=20, priority="low", category="play",
    pet_name="Whiskers", scheduled_time="18:00",
    recurrence="daily",
))

# Weekly: Buddy gets a bath on Mon/Thu — intentionally overlaps with Brush Coat to demo conflict detection
buddy.add_task(Task(
    title="Bath Time", duration_minutes=25, priority="medium", category="grooming",
    pet_name="Buddy", scheduled_time="09:10",   # overlaps Brush Coat (09:00–09:15)
    recurrence="weekly", repeat_days=["Mon", "Thu", "Sat"],
))

# Add pets to owner
owner.add_pet(buddy)
owner.add_pet(whiskers)

# Build today's schedule
scheduler = Scheduler(owner)
schedule = scheduler.build_schedule(date.today())

# ── TODAY'S SCHEDULE ────────────────────────────────────────────────
print("=" * 52)
print(f"  TODAY'S SCHEDULE — {schedule.date.strftime('%A, %B %d %Y')}")
print(f"  Owner : {schedule.owner_name}")
print("=" * 52)

for pet in owner.pets:
    pet_tasks = schedule.filter_tasks(pet_name=pet.name)
    if not pet_tasks:
        continue
    done_count = sum(1 for t in pet_tasks if t.is_done)
    print(f"\n  {pet.name} ({pet.species})  —  {done_count}/{len(pet_tasks)} done")
    print("  " + "-" * 48)
    for task in pet_tasks:
        status   = "[DONE]" if task.is_done else "[ ]"
        time_str = f"@ {task.scheduled_time}  " if task.scheduled_time else "            "
        reason   = schedule.explanations.get(task.id, "")
        recur    = f"  [{task.recurrence}]" if task.recurrence != "none" else ""
        print(f"    {status} {time_str}{task.title}{recur}")
        print(f"           {task.priority.upper()} priority | {task.duration_minutes} min | {task.category}")
        if reason:
            print(f"           note: {reason}")

# ── CONFLICT WARNINGS ───────────────────────────────────────────────
if schedule.conflicts:
    print("\n" + "=" * 52)
    print("  !! TIME CONFLICTS DETECTED")
    print("=" * 52)
    for a, b in schedule.conflicts:
        print(f"  '{a.title}' ({a.pet_name}, {a.scheduled_time}–{a._end_minutes() // 60:02d}:{a._end_minutes() % 60:02d})")
        print(f"    overlaps with")
        print(f"  '{b.title}' ({b.pet_name}, {b.scheduled_time})")
        print()

# ── SUMMARY ─────────────────────────────────────────────────────────
print("=" * 52)
pending = schedule.filter_tasks(done=False)
print(f"  Total scheduled : {schedule.total_time()} / {owner.available_minutes} min")
print(f"  Pending tasks   : {len(pending)}")
print("=" * 52)

# ── SORT BY TIME DEMO ────────────────────────────────────────────────
print("\n" + "=" * 52)
print("  ALL TASKS SORTED BY TIME (via sort_by_time)")
print("=" * 52)
for task in scheduler.sort_by_time():
    time_str = task.scheduled_time if task.scheduled_time else "unscheduled"
    print(f"  {time_str}  |  {task.pet_name:<10}  |  {task.title}")

# ── FILTER BY PET DEMO ───────────────────────────────────────────────
print("\n" + "=" * 52)
print("  FILTER: Buddy's tasks only (via filter_tasks)")
print("=" * 52)
for task in scheduler.filter_tasks(pet_name="Buddy"):
    status = "[DONE]" if task.is_done else "[ ]"
    print(f"  {status}  {task.scheduled_time or 'unscheduled':<6}  {task.title}")

# ── FILTER BY STATUS DEMO ────────────────────────────────────────────
print("\n" + "=" * 52)
print("  FILTER: All pending (not done) tasks (via filter_tasks)")
print("=" * 52)
for task in scheduler.filter_tasks(done=False):
    print(f"  [ ]  {task.pet_name:<10}  {task.scheduled_time or 'unscheduled':<6}  {task.title}")
