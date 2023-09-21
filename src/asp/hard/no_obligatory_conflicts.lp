%*
Obligatory courses should not conflict.
*%
:- conflict(CourseA, GroupA, CourseB, GroupB),
    is_obligatory(CourseA),
    is_obligatory(CourseB).
