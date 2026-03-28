# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

Several enhancements were added to make the scheduler more intelligent and maintainable:

**Recurring task auto-renewal** — When a `daily` or `weekly` task is marked complete, the scheduler automatically creates the next occurrence. Daily tasks get a new due date of today + 1 day (using `timedelta(days=1)`). Weekly tasks scan forward to find the nearest matching repeat day (e.g. Mon/Thu/Sat).

**Conflict detection** — `detect_conflicts()` scans all timed tasks chronologically and flags any pair where one task's end time overlaps the next task's start time. Warnings are printed without crashing the program.

**Single-pass sorting** — Task prioritization was simplified from two sequential sorts into one, using a combined key: owner preference category first, then priority level, then duration. A `prefs` set makes the preference check O(1).

**`Task.copy()`** — A `copy(**overrides)` method was added to `Task` so recurring task templates can be cloned cleanly with targeted field overrides, eliminating repeated field-by-field construction in two separate places.

**Cleaner removal** — `Pet.remove_task()` now returns a boolean, and `Scheduler.remove_task()` uses `any()` to short-circuit on the first successful removal instead of comparing list lengths before and after.

---

## Testing PawPal+

### Running the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Test | What it verifies |
|---|---|
| `test_task_completion` | Calling `mark_done()` sets `is_done` to `True` |
| `test_task_addition` | Adding a task to a `Pet` increases its task count correctly; recurring tasks route to `recurring_tasks`, one-off tasks to `tasks` |
| `test_sort_by_time_chronological` | `sort_by_time()` returns tasks in ascending `HH:MM` order, with unscheduled tasks placed at the end |
| `test_daily_recurrence_spawns_next_day` | Marking a daily recurring task done automatically creates a new occurrence with a `due_date` of the following day |
| `test_conflict_detection_same_time` | Two tasks scheduled at the same time are detected and recorded as a conflict in the schedule |

### Confidence Level

★★★★☆ (4 / 5)

The core scheduling behaviors — priority sorting, time-budget greedy fit, recurring task injection, conflict detection, and task completion — are all implemented and tested. The bug in `Task.copy()` (duplicate keyword argument when passing overrides) was caught and fixed through testing. Confidence is held at 4 rather than 5 because there is currently no interactive UI for marking tasks done, auto-time-assignment does not exist (times must be set manually), and edge cases such as three-way time conflicts and weekly tasks with empty `repeat_days` are identified but not yet covered by tests.

---

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
