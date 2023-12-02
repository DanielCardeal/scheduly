% WARNING: Changes in the base model are possibly destructive and should be
% carrefully considered.

#const monday = 0.
#const tuesday = 1.
#const wednesday = 2.
#const thursday = 3.
#const friday = 4.

%*
def weekday/1(weekday id)
*%
weekday(0..4).

% Horários letivos
#const morning1 = 0.
#const morning2 = 1.
#const afternoon1 = 2.
#const afternoon2 = 3.
#const night1 = 4.
#const night2 = 5.

%*
def period/1(period id)
*%
period(morning1..night2).

%*
def part_of_day(period id, part of the day)
*%
partofday(morning1..morning2, morning).
partofday(afternoon1..afternoon2, afternoon).
partofday(night1..night2, night).

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
def class/5(
    course id,
    offering group,
    weekday,
    period,
    fixed?
)
*%
{ class(Course, Group, W, P, false): available(Teacher, W, P) } :-
    primary_lecturer(Course, Group, Teacher).

% Add additional predicates for jointed classes
class(CourseB, Group, W, P, Fixed) :-
    joint(CourseA, CourseB, Group),
    class(CourseA, Group, W, P, Fixed).

%*
The number of weekly classes of an offered course must be respected.
*%
:- { class(Course, Group, W, P, _) } != NumClasses,
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
% Group conflict
conflict(CourseA, GroupA, CourseB, GroupB, Weekday, Period) :-
    class(CourseA, GroupA, Weekday, Period, _),
    class(CourseB, GroupB, Weekday, Period, _),
    GroupA != GroupB.

% Class conflict
conflict(CourseA, Group, CourseB, Group, Weekday, Period) :-
    class(CourseA, Group, Weekday, Period, _),
    class(CourseB, Group, Weekday, Period, _),
    CourseA != CourseB,
    not joint(CourseA, CourseB, Group).

%*
Two classes taught by the same teacher shouldn't conflict.
*%
:- conflict(CourseA, GroupA, CourseB, GroupB),
    lecturer(CourseA, GroupA, Teacher),
    lecturer(CourseB, GroupB, Teacher).

%*
Classes should be scheduled in the correct parts of the day, unless
they are fixed
*%
:- class(Course, Group, _, Period, false),
    part_of_day(Period, PartOfDay),
    not schedule_on(Course, Group, PartOfDay).

%*
Classes must respect the lecturer(s)' available times, unless they
are fixed.
*%
:- class(Course, Group, Weekday, Period, false),
    lecturer(Course, Group, Teacher),
    not available(Teacher, Weekday, Period).

%*
Classes from double courses must be schedule one after another in the same
day, unless they are fixed.
*%
% Different days of the week
:- class(Course, Group, Weekday1, _, false),
    class(Course, Group, Weekday2, _, _),
    is_double(Course),
    Weekday1 != Weekday2.

% Ensure double classes are scheduled in consecutive periods, unless they are
% fixed.
:- class(Course, Group, _, Period1, false),
    class(Course, Group, _, Period2, _),
    is_double(Course),
    Period2 != Period1,
    |Period2 - Period1| != 1.

#show class/5.
