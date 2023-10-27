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
Ensures joint/3 is symmetric
*%
joint(CourseB, CourseA, OfferingGroup) :- joint(CourseA, CourseB, OfferingGroup).

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
    not joint(Course, _, Group),
    num_classes(Course, NumClasses),
    lecturer(Course, Group, Teacher).

% Schedule jointed classes
{ class(CourseA, Group, W, P): available(Teacher, W, P) } == NumClasses :-
    joint(CourseA, CourseB, Group),
    num_classes(CourseA, NumClasses),
    lecturer(CourseA, Group, _).

class(CourseB, OfferingGroup, W, P) :-
    joint(CourseA, CourseB, OfferingGroup),
    lecturer(CourseB, OfferingGroup, _),
    class(CourseA, OfferingGroup, W, P).

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
% Group conflict
conflict(CourseA, GroupA, CourseB, GroupB, Weekday, Period) :-
    class(CourseA, GroupA, Weekday, Period),
    class(CourseB, GroupB, Weekday, Period),
    GroupA != GroupB.

% Class conflict
conflict(CourseA, Group, CourseB, Group, Weekday, Period) :-
    class(CourseA, Group, Weekday, Period),
    class(CourseB, Group, Weekday, Period),
    CourseA != CourseB,
    not joint(CourseA, CourseB, Group).

%*
Two classes taught by the same teacher shouldn't conflict.
*%
:- conflict(CourseA, GroupA, CourseB, GroupB),
    lecturer(CourseA, GroupA, Teacher),
    lecturer(CourseB, GroupB, Teacher).

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
