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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
