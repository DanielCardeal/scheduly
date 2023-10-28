%*
def const true
*%
#const true = 1.

%*
def const false
*%
#const false = 0.

%*
def is_obligatory/1(course id)
*%
is_obligatory(Course) :- curriculum("obligatory", Course, _).

%*
def teacher/1(teacher id)
*%
teacher(Teacher) :- lecturer(_, _, Teacher).

%*
def conflict/4(
    course A id,
    course A group,
    course B id,
    course B group,
)
*%
conflict(CourseA, GroupA, CourseB, GroupB) :- conflict(CourseA, GroupA, CourseB, GroupB, _, _).

%*
def _conflict/6(
    course A id,
    course A group,
    course B id,
    course B group,
    conflict weekday,
    conflict period
)
*%
_conflict(CourseA, GroupA, CourseB, GroupB, Weekday, Period) :-
    conflict(CourseA, GroupA, CourseB, GroupB, Weekday, Period),
    CourseA > CourseB.

%*
def _joint/2(course A id, course B id)
*%
_joint(CourseA, CourseB, Group) :- joint(CourseA, CourseB, Group), CourseA > CourseB.

%*
availability/2(teacher id, number of available teaching periods)
*%
availability(Teacher, N) :-
    teacher(Teacher),
    N = #count { W, P: available(Teacher, W, P) }.

#show _conflict/6.
#show _joint/3.
#show availability/2.
