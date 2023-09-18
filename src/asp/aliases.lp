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
