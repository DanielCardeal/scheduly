%*
def weekday/1(weekday id)
*%
weekday(0..5).

%*
def period/1(period id)
*%
period(0..3).

%*
Ensures joint/2 is symmetric
*%
joint(CourseB, CourseA) :- joint(CourseA, CourseB).

%*
def class/4(
    course id,
    offering group,
    weekday,
    period
)
*%
% Schedule non-jointed classes
{ class(Course, Group, W, P): available(Teacher, W, P) } == NumClasses :-
    not joint(Course, _),
    num_classes(Course, NumClasses),
    lecturer(Course, Group, Teacher).

% Schedule jointed classes
{ class(CourseA, GroupA, W, P): available(Teacher, W, P) } == NumClasses :-
    joint(CourseA, CourseB),
    num_classes(CourseA, NumClasses),
    lecturer(CourseA, GroupA, _).

class(CourseB, GroupB, W, P) :-
    joint(CourseA, CourseB),
    lecturer(CourseB, GroupB, _),
    class(CourseA, _, W, P).


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
    not joint(Course1, Course2),
    Course1 != Course2,
    Course1 > Course2.

% Group conflict
conflict(Course1, Group1, Course2, Group2, Weekday, Period) :-
    class(Course1, Group1, Weekday, Period),
    class(Course2, Group2, Weekday, Period),
    not joint(Course1, Course2),
    Course1 == Course2,
    Group1 > Group2.


%*
Two classes taught by the same teacher cannot be in conflict with eachother,
unless they are jointed.
*%
:- not joint(CourseA, CourseB),
    lecturer(CourseA, GroupA, Teacher),
    lecturer(CourseB, GroupB, Teacher),
    conflict(CourseA, GroupA, CourseB, GroupB).

%*
Classes must respect the lecturer(s)' available times.
*%
:- class(Course, Group, Weekday, Period),
    lecturer(Course, Group, Teacher),
    not available(Teacher, Weekday, Period).

#show class/4.
#show joint/2.
#show conflict/6.
