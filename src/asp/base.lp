%*
def class/4(
    course id,
    offering group,
    weekday,
    period
)
*%
{ class(Course, Group, Weekday, Period) : lecturer(Course, Group, Teacher), available(Teacher, Weekday, Period) } == NumClasses :-
    num_classes(Course, NumClasses).


%*
def conflict/6(
    first course id,
    first course group,
    second course group,
    second course group,
    weekday,
    period
)
*%
% Class conflict
conflict(Course1, Group1, Course2, Group2, Weekday, Period) :-
    class(Course1, Group1, Weekday, Period),
    class(Course2, Group2, Weekday, Period),
    Course1 != Course2.

% Group conflict
conflict(Course1, Group1, Course2, Group2, Weekday, Period) :-
    class(Course1, Group1, Weekday, Period),
    class(Course2, Group2, Weekday, Period),
    Course1 == Course2, Group1 != Group2.


%*
Two classes taught by the same teacher cannot be in conflict with eachother,
unless they are jointed.
*%
:- conflict(CourseA, GroupA, CourseB, GroupB, _, _),
    lecturer(CourseA, GroupA, Teacher),
    lecturer(CourseB, GroupB, Teacher),
    not joint(CourseA, CourseB).


%*
Classes must respect the lecturer(s)' available times.
*%
:- class(Course, Group, Weekday, Period),
    lecturer(Course, Group, Teacher),
    not available(Teacher, Weekday, Period).
