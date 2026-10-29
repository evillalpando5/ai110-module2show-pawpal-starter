# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
The UML design should have an owner class, pet class, tasks, and a schedule to display and arrange these classes. The owner should have a pet and a pet can have mutliple tasks associated to it. The schedule should be created based on duration of the task and the priority.

- What classes did you include, and what responsibilities did you assign to each?
I included 6 classes. Owner, pet, task, dailyschedule, scheduleentry, and schedulegenerator. The owner class has owner details and a pet. The pet cass contains details about the pet and can have care tasks attached to it. The schedule generator creates a daily schedule which is made of schedule entries. The schedule entries references a task and has a 

**b. Design changes**

- Did your design change during implementation?
Missing relationships

Owner → DailySchedule: The UML has no link between an owner and their schedule. The app needs to display a specific owner's daily plan, so there should be a direct association.
ScheduleGenerator → Owner/Pet: The generator only references Task and DailySchedule in the UML, but it needs to know which pet's tasks to pull. Right now there's no path from generator → pet → tasks.
Missing attributes

Task has no pet_id or reference back to its parent Pet. Once tasks from multiple pets exist (the README says "add/edit tasks"), you can't tell which task belongs to which pet.
DailySchedule has no pet_id either — if an owner has multiple pets, you can't distinguish schedules.
Task has no recurrence field (daily vs. weekly), which the README's scheduling table explicitly calls out as a feature to handle.
Logic bottlenecks

ScheduleGenerator does everything: constraint checking, prioritization, slot calculation, and schedule creation. If any one of those methods has a bug, the whole plan breaks. Worth splitting checkConstraints and prioritizeTasks out so they can be tested independently — which aligns with the README's emphasis on testing key scheduling behaviors.
DailySchedule.generatePlan() and ScheduleGenerator.generateSchedule() overlap in responsibility. It's unclear which one is the real entry point. You'll want to pick one (probably ScheduleGenerator) and make the other just a display/wrapper.
There's no concept of a time budget (total available hours in a day). Without it, calculateTimeSlots has nothing to bound against, so the plan could schedule more tasks than the day allows.

- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
Back-to-back tasks are not flagged
The test a_start < b_end and b_start < a_end uses strict <, so a task ending at exactly 08:30 and one starting at exactly 08:30 passes. That's usually correct (no actual overlap), but if a pet needs travel time between tasks it would be a false negative.

- Why is that tradeoff reasonable for this scenario?

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
