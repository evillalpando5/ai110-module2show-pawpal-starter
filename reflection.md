# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
The UML design should have an owner class, pet class, tasks, and a schedule to display and arrange these classes. The owner should have a pet and a pet can have mutliple tasks associated to it. The schedule should be created based on duration of the task and the priority.

- What classes did you include, and what responsibilities did you assign to each?
I included 6 classes. Owner, pet, task, dailyschedule, scheduleentry, and schedulegenerator. The owner class has owner details and a pet. The pet cass contains details about the pet and can have care tasks attached to it. The schedule generator creates a daily schedule which is made of schedule entries. The schedule entries references a task and has a 

**b. Design changes**

- Did your design change during implementation?
Yes it did there was missing relationships and missing attibutes. There was no link between an owner and their scheduler and tasks did not have a pet either as well as task had no reoccurance value.

- If yes, describe at least one change and why you made it.
The UML had no link between an owner and their schedule. The app needed to display a specific owner's daily plan so I made the change to add owner to scheduler.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
The scheduler considered time as long as the duration was feasible during start and end times and it also considered priority.
- How did you decide which constraints mattered most?
I decided which constraints mattered most based on which were most restricting for example time is the more restricting then if you have the time you can go based on priority and preference is the least restricting but I did not implement that one.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
Back-to-back tasks are not flagged.
The time tested was a_start < b_end and b_start < a_end uses strict <, so a task ending at exactly 08:30 and one starting at exactly 08:30 passes. That's usually correct (no actual overlap), but if a pet needs travel time between tasks it would be a false negative.

- Why is that tradeoff reasonable for this scenario?
This is a reasonable tradeoff because if the tasks were involving the same pet then maybe there is less time needed between tasks. Factoring this in would also add another varibale because depending on owner and location of tasks you'll need a different amount of time between different tasks. The owner could take this into account when scheduling tasks and not scheudling them back to back. Maybe for future improvements then a warning message could be displayed like hey you might be cutting it close with task a and task b.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used claude for design brainstorming both at the UML design stage, coding, and testing stage. I also had to look at methods to see if they could be refactored in a more readable way as well as help debug along the way. For example tasks were being scheduled outside the start and end times because the logic was only checking the duration of the task was avaliable between start and end times.

- What kinds of prompts or questions were most helpful?
The prompts that were most helpful to me were ones in which I had claude brainstorm ideas then I reviewed and asked more questions if necessary. After understanding the logic I allowed claude to implement the ideas I agreed with. The questions to have it explain the changes it made in simple terms was helpful because you could easy understand the main idea quickly.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
When debugging the issue of tasks being schedule outside the start/end times, claude suggested just skipping the task if job overlapped. This was clearly not how PawPal is supposed to handle these cases. I did not accept this change and it suprised me because I had mentioned before that error messages should display for conflicting tasks.
- How did you evaluate or verify what the AI suggested?
I evaluated what claude suggested by thinking about the main focus of how PawPal should function, sometimes claude wanted to do extra functions which were not required nor helpful in any way to the main core functionality of PawPal. Having a clear idea of how you would like your project to work and understanding the changes at every step helps you weigh whether suggestions are actually valuable or not.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested tasks being sorted by time, sorted by priority, new tasks being rengeragted for reoccuring tasks both daily and weekly, tasks being completed arre handled correctly, conflicting tasks being caught, a task ending at the same time another start not being a conflict, and a pet with no tasks does not crash the program and returns a empty tasks array.
- Why were these tests important?
These tests are important because the help test both the happy cases and edge cases like zero tasks. It is easy for a program to work when the test cases are happy cases but a program is really tested when it encounters edge cases and is able to handle them well by displaying proper messages and things like that.

**b. Confidence**

- How confident are you that your scheduler works correctly?
It works okay. The duration of the tasks being possible within the avilable hours isn't working and it would be more helpful if the scheduler showed dates as well maybe for the whole week. 
- What edge cases would you test next if you had more time?
If I had more time I would test weekly tasks conflicting in a way, I would test duration of time not being enough for the tasks. I would test all tasks conflicting. I would test a large amount of tasks with same prioity.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
 I am most satisfied with the conflicting tasks message feature because it ties all the functions together the pets, tasks, and scheduling. I also ran into some issues but was able to debug it and display the message which was rewarding.
 
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would improve the scheduler view to include dates and I would have total tasks duration and available time be considered. I would provide a warning message for back to back tasks like hey you might be cutting it close with task a and task b.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
With each project I am getting a better understanding of the flow. Thw flow of how a program should be coded and I am learning how to keep up with items and functions. To remember to test so you find bugs early and your changes do not break anything. I am also understanding how efficient it is to have AI explain concepts and you can keep asking questions until you fully understand it.