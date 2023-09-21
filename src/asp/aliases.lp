%*
def num_classes/2(course id, number of weekly classes)
*%
num_classes(Course, NumClasses) :- course(Course, _, NumClasses, _, _).

%*
def is_double/1(course_id)
*%
is_double(Course) :- course(Course, _, _, _, 1).

%*
def is_undergrad/1(course_id)
*%
is_undergrad(Course) :- course(Course, "grad", _, _, _).

%*
def conflict/4(
    course A id,
    course A group,
    course B id,
    course B group,
)
*%
conflict(CourseA, GroupA, CourseB, GroupB) :- conflict(CourseA, GroupA, CourseB, GroupB, _, _).
