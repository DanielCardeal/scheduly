%*
Obligatory courses of the same ideal semester should not conflict.
*%
:- conflict(CourseA, GroupA, CourseB, GroupB),
    is_obligatory(CourseA),
    is_obligatory(CourseB),
    ideal_semester(CourseA, IdealSemester),
    ideal_semester(CourseB, IdealSemester).
