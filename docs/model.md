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

### Courses' information

+ `course/5(course id, course group, number of weekly classes, ideal period, is double)`

  General information about a course in the educational institution.  

+ `joint/2(course A id, course B id)`

  Indicates that `course A` and `course B` should be offered in the same
  classroom and at the same time.

### Curricula information

+ `curriculum/2(curriculum id, curriculum group)`

  Represents a curriculum in the institution. 

+ `curriculum_component/3(curriculum id, course id, is required)`

  Assign a `course` as part of a `curriculum`. The component can be optionally
  marked as 'required', indicating that a student must take this course to
  complete the curriculum.

### Teachers' information

+ `teacher/1(teacher id)`

  Identifies a teacher in the scheduler

+ `available/3(teacher id, weekday, period)`

  Indicates which day/period a teacher is available to teach.

+ `preferred/3(teacher id, weekday, period)`

  Indicates preferred lecture day/period of a teacher

### Offerings' information

+ `lecturer/3(course id, offering group, teacher id)`

  Assign `teacher` as the lecturer of `course` in this given semester. Note that
  there could be multiple instances for a same course/offering group, which
  means more than one teacher is assigned to the same class.

+ `class/4(course id, offering group, weekday, period)`

  Schedule a class of a given course to a weekday

+ `conflict/6(first course id, first course group, second course group, second course group, weekday, period)`

  Register schedule conflicts between two different courses or two different offerings of the same course. Conflicts occur when two classes occur in the same period and weekday.
  
### Aliases

This predicates don't add information about the model, but they facilitate
writing rules in a more concise manner. 

+ `num_classes/2(course id, number of weekly classes)`
+ `is_double/1(course id)`
+ `is_undergrad/1(course id)`
+ `is_obligatory(course id)`
+ `conflict/4(course A id, course A group, course B id, course B group)`
