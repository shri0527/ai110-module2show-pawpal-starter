# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
I included 4 classes. They are Owner, Pet, Task, Schedule. For Owner the attributes were tracking their name, preferenes, and availibility. I also included a method to add pets and set the schedule. For Pet I added basic details like their name, age, and notes about the pet. Then I added a methods to manage tasks related to them. Then for Task i included a category, priority, status of the task, and being able to edit the task itself. Lastly for Schedule I included a list of the task, date to be done by, and duration.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Each Task now gets a unique id generated automatically using uuid4. This fixes a bug where remove_task() would delete every task sharing the same title. Now removal, lookups, and schedule explanations all rely on this ID, making them precise and reliable.

priority and species are now typed as Literal["low", "medium", "high"] and Literal["dog", "cat", "other"] respectively. Previously they were plain strings, meaning invalid values like priority="urgent" would silently pass through and potentially break the scheduler logic later. This catches bad input early.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
I considered owner preferences, task priority, and time. The preference constraint was ranked first because a pet's daily feeding or medication is more time-sensitive than a grooming task, even if both are marked high priority. Time is the hard cutoff — it's a physical limit, not a preference — so it acts as the final gate rather than a sorting criterion.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
The scheduler uses a greedy first-fit strategy: it picks tasks in sorted order and adds each one if it fits, skipping any that don't. The tradeoff is that greedy first-fit can leave time on the table. For example, if a 30-minute walk is next in priority but only 25 minutes remain, it gets skipped — even if a 25-minute grooming task lower in priority would have fit perfectly. This tradeoff is reasonable here because pet care tasks aren't interchangeable — you shouldn't swap a high-priority feeding for a lower-priority bath just to maximize minutes used. Respecting priority order matters more than filling every available minute, and greedy first-fit does that simply and predictably.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used AI for all of the above mentioned. The most helpful was refactoring and debugging. I tired to mirror the prompts as close as to the guidelines of the project. I feel like doing that established the requirements well to the AI and kept it moving in the right direction.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
One moment I didnt accept AI suggestion as-is was when doing the filtering logic and implementation. AI kept trying to do the filtering while adding tasks but I had to make sure that it understood that the filtering process only matters after the schedule is built. I think logically that made sense for the user since most users want to filter through their own schedule.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
Task completion (test_task_completion) — verified that calling mark_done() correctly flips is_done from False to True. This was important because marking tasks done is a fundamental action the whole app depends on, and if it silently failed nothing would ever show as complete.

Task routing (test_task_addition) — verified that adding a one-off task to a pet increases pet.tasks by one. This matters because recurring tasks route to a separate list (recurring_tasks), so it was important to confirm the routing logic worked correctly from the start.

Chronological sorting (test_sort_by_time_chronological) — verified that sort_by_time() returns tasks in ascending time order with unscheduled tasks placed at the end. This was important because the whole schedule display depends on tasks appearing in the right order for the owner to follow.

Daily recurrence spawning (test_daily_recurrence_spawns_next_day) — verified that marking a daily recurring task done on a given date automatically creates a new copy with a due date of the next day. This was the most critical test because recurrence is complex logic and a bug here would silently cause recurring tasks to disappear after being completed once.

Conflict detection (test_conflict_detection_same_time) — verified that two tasks scheduled at the exact same time are flagged as a conflict and both task IDs appear in the conflict record. This was important because conflicts are a safety feature — if two pet care tasks overlap, the owner needs to know.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I am fairly confident (4 out of 5) that the core scheduling logic works correctly. The five tests cover the most critical paths — task state, routing, sorting, recurrence, and conflict detection — and writing them caught a real bug in Task.copy() where a duplicate keyword argument was causing a TypeError whenever a recurring task tried to spawn its next occurrence.

If I had more time, the edge cases I would test next are:

A pet with no tasks at all to confirm build_schedule returns an empty schedule without crashing
A weekly recurring task with empty repeat_days to confirm the fallback to +7 days works
Three tasks all at the same time to confirm the conflict detector doesn't miss the third pair
available_minutes = 0 to confirm no tasks are scheduled when there is no time

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I think something that went well was the planning process. I had a clear vision of what I wanted incorprate and was able to do so in timely manner. I also liked the conflict merge idea that I had where the system can automatically fix it.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I think I would take more time on making the website look more attractive. I think that would have added a personal touch made it stand out more. I also wanted to add more features where the user could move around the schedule themselves but I was unable to add that feature.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
One important thing I learned is that AI can help you write code quickly, but it cannot tell you when something feels wrong to the user — that part still requires you. For example, the filtering feature was technically working, but it was placed in the wrong section of the app. The AI put it under "Add a Task" because that was where the task list lived, and logically that made sense. But as the person using the app, I immediately noticed it felt out of place — filtering belongs where you are reviewing your schedule, not where you are creating tasks. That kind of judgment about user experience only came from actually looking at the app and thinking about how a real pet owner would use it.