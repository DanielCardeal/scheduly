%*
def weekday/1(weekday id)
*%
weekday(0..5).

%*
def period/1(period id)
*%
period(0..3).

%*
def class/4(
    course id,
    offering group,
    weekday,
    period
)
*%
{ class(Course, Group, W, P): weekday(W), period(P) } == NumClasses :-
    num_classes(Course, NumClasses),
    lecturer(Course, Group, _).


%*
def conflict/6(
    course A id,
    course A group,
    course B id,
    course B group,
    conflict weekday,
    conflict period
)
*%
% Class conflict
conflict(Course1, Group1, Course2, Group2, Weekday, Period) :-
    class(Course1, Group1, Weekday, Period),
    class(Course2, Group2, Weekday, Period),
    Course1 != Course2,
    Course1 > Course2.

% Group conflict
conflict(Course1, Group1, Course2, Group2, Weekday, Period) :-
    class(Course1, Group1, Weekday, Period),
    class(Course2, Group2, Weekday, Period),
    Course1 == Course2,
    Group1 != Group2,
    Group1 > Group2.


%*
Two classes taught by the same teacher cannot be in conflict with eachother,
unless they are jointed.
*%
:- conflict(CourseA, GroupA, CourseB, GroupB),
    lecturer(CourseA, GroupA, Teacher),
    lecturer(CourseB, GroupB, Teacher),
    not joint(CourseA, CourseB).


%*
Classes must respect the lecturer(s)' available times.
*%
:- class(Course, Group, Weekday, Period),
    lecturer(Course, Group, Teacher),
    not available(Teacher, Weekday, Period).

#show class/4.
