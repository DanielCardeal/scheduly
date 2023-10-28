# Model

This page lists and explains all of the predicates and values used within the project.

## Values

+ course id (symbol | number): a symbol that **uniquely** identifies a course offered by the institute. 

  > Example values: mac0110, mac5770, mae0217, 4310145

+ teacher id (symbol): a symbol that **uniquely** identifies one of the teachers of the department. 

  > Example values: turing, ada_lovelace, gracehopper

+ day (number $\in [1,5]$): a day of the week.

  > Example values: 1 (Monday), 2 (Tuesday), 5 (Friday)

+ period (number $\in [1,4]$): timeslots available for each day. In IME-USP, particularly:

  + 1 => classes from 8 to 9:40 AM
  + 2 => classes from 10 to 11:40 AM
  + 3 => classes from 2 to 3:40 PM
  + 4 => classes from 4 to 6:40 PM

## Predicates

### Timetable information

+ `weekday/1(weekday id)`

  Registers a weekday that is available for scheduling classes.

+ `period/1(period id)`

  Register a period that is available for scheduling classes.

+ `part_of_day/2(period id, part of the day)`

  Indicate what part of the day (mourning, afternoon, night) a period is
  part of.

### Courses' information


+ `num_classes/2(course id, number of weekly classes)`

  Number of classes of a course.

+ `is_double/1(course id)`
  
  Identifies courses with double classes, aka, courses with classes that occupy
  two consecutive periods in the same day.

+ `is_undergrad/1(course id)`
  
  Identifies undergrad courses.

+ `is_obligatory(course id)`

  General information about a course in the educational institution. An ideal
  period of 0 is equivalent to no ideal period.

+ `joint/3(course A id, course B id, offering group)`

  Indicates that a given offering of course A and course B should be scheduled
  in the same classroom and at the same time.

+ `schedule_on/3(course id, offering group, part of the day)`
  
  Allow an offering of a course to be scheduled in a given part of the day.
  Courses can be allowed to be scheduled in more than one given part of the day.

### Curricula information

+ `curriculum/3(curriculum id, course id, is required)`

  Assign a `course` as part of a `curriculum`. The course can be optionally
  marked as 'required', indicating that a student must take this course to
  complete the curriculum.

### Teachers' information

+ `available/3(teacher id, weekday, period)`

  Indicates which day/period a teacher is available to teach.

+ `preferred/3(teacher id, weekday, period)`

  Indicates preferred lecture day/period of a teacher

### Offerings' information

+ `class/5(course id, offering group, weekday, period, fixed?)`

  Schedule a class of a given course to a weekday. Fixed is 1 if the class was
  manually scheduled by the user, or 0 if it was scheduled automatically by the
  scheduler.

+ `lecturer/3(course id, offering group, teacher id)`

  Assign `teacher` as the lecturer of `course` in this given semester. Note that
  there could be multiple instances for a same course/offering group, which
  means more than one teacher is assigned to the same class.

+ `primary_lecturer/3(course id, offering group, teacher id)`

  Mark a teacher as the primary teacher for a course. The primary teacher for a
  course is the teacher with the lowest availability between all the lecturers
  of a class.

+ `conflict/6(first course id, first course group, second course group, second course group, weekday, period)`

  Register schedule conflicts between two different courses or two different
  offerings of the same course. Conflicts occur when two classes occur in the
  same period and weekday. Note that `jointed` classes don't count as
  conflicting to the scheduler.

  > NOTE: `conflict` is symmetric, which means there are always two `conflict`
  > predicates for each pair of conflicting classes in a schedule.

### Aliases

This predicates don't add information about the model, but they facilitate
writing rules in a more concise manner. 

+ `teacher/1(teacher id)`

  A teacher in the scheduler. Teacher information is extracted from `lecturer`
  clauses.

+ `availability/2(teacher id, number of available teaching periods)`

  Count the number of available teaching days for a given teacher.

+ `conflict/4(course A id, course A group, course B id, course B group)`

  Shorter version of `conflict` that ignores the time of conflict.

+ `_conflict/6(course A id, course A group, course B id, course B group, conflict weekday, conflict period)`

  Ordered (non symmetric) version of `conflict`. Useful whenever creating rules
  that should be counted only once per conflict (such as `avoid_all_conflicts`).

+ `_joint/2(course A id, course B id)`

  Ordered (non symmetric) version of `joint`. Useful whenever is necessary to
  access one instance of a jointed classes pair.

+ `true = 1`: truthy constant (same as `int(True)` in Python)

+ `false = 0`: truthy constant (same as `int(False)` in Python)
