%*
def weekday/1(weekday id)
*%
weekday(0..5).

%*
def period/1(period id)
*%
period(0..5).

%*
def part_of_day(period id, part of the day)
*%
part_of_day(0, "morning").
part_of_day(1, "morning").
part_of_day(2, "afternoon").
part_of_day(3, "afternoon").
part_of_day(4, "night").
part_of_day(5, "night").

%*
Ensures joint/2 is symmetric
*%
joint(CourseB, CourseA) :- joint(CourseA, CourseB).

%*
def primary_lecturer(course id, group id, teacher id)
*%
primary_lecturer(Course, Group, Teacher) :-
    lecturer(Course, Group, Teacher),
    availability(Teacher, N),
    N = #min { OtherN: lecturer(Course, Group, OtherTeacher),  availability(OtherTeacher, OtherN)}.

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
conflict(CourseA, GroupA, CourseB, GroupB, Weekday, Period) :-
    class(CourseA, GroupA, Weekday, Period),
    class(CourseB, GroupB, Weekday, Period),
    not joint(CourseA, CourseB),
    CourseA != CourseB.

% Group conflict
conflict(CourseA, GroupA, CourseB, GroupB, Weekday, Period) :-
    class(CourseA, GroupA, Weekday, Period),
    class(CourseB, GroupB, Weekday, Period),
    not joint(CourseA, CourseB),
    CourseA == CourseB,
    GroupA != GroupB.

%*
Two classes taught by the same teacher cannot be in conflict with eachother,
unless they are jointed.
*%
:- not joint(CourseA, CourseB),
    lecturer(CourseA, GroupA, Teacher),
    lecturer(CourseB, GroupB, Teacher),
    conflict(CourseA, GroupA, CourseB, GroupB).

%*
Classes should be scheduled in the correct parts of the day
*%
:- class(Course, Group, _, Period),
    part_of_day(Period, PartOfDay),
    not schedule_on(Course, Group, PartOfDay).

%*
Classes must respect the lecturer(s)' available times.
*%
:- class(Course, Group, Weekday, Period),
    lecturer(Course, Group, Teacher),
    not available(Teacher, Weekday, Period).

%*
Classes from double courses must be schedule one after another in the same
day.
*%
% Different days of the week
:- class(Course, Group, Weekday1, _),
    class(Course, Group, Weekday2, _),
    is_double(Course),
    Weekday1 != Weekday2.

% Ensure double classes are scheduled in consecutive periods
:- class(Course, Group, _, Period1),
    class(Course, Group, _, Period2),
    is_double(Course),
    Period2 != Period1,
    |Period2 - Period1| != 1.


#show class/4.
