%*
def period/1(period id)
*%
period(P) :- period(P, _).

%*
def num_classes/2(course id, number of weekly classes)
*%
num_classes(Course, NumClasses) :- course(Course, _, NumClasses, _, _).

%*
def ideal_period/2(course id, ideal period)
*%
ideal_period(Course, IdealPeriod) :- course(Course, _, _, IdealPeriod, _).

%*
def is_double/1(course_id)
*%
is_double(Course) :- course(Course, _, _, _, 1).

%*
def is_undergrad/1(course_id)
*%
is_undergrad(Course) :- course(Course, "grad", _, _, _).

%*
def is_obligatory/1(course id)
*%
is_obligatory(Course) :- curriculum_component("obligatory", Course, _).

%*
def lecturer/1(teacher id)
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
_joint(CourseA, CourseB) :- joint(CourseA, CourseB), CourseA > CourseB.

%*
availability/2(teacher id, number of available teaching periods)
*%
availability(Teacher, N) :-
    teacher(Teacher),
    N = #count { W, P: available(Teacher, W, P) }.

