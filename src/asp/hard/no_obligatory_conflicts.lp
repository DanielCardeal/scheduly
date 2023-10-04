%*
Obligatory courses of the same ideal period should not conflict.
*%
:- conflict(CourseA, GroupA, CourseB, GroupB),
    is_obligatory(CourseA),
    is_obligatory(CourseB),
    ideal_period(CourseA, IdealPeriod),
    ideal_period(CourseB, IdealPeriod).
