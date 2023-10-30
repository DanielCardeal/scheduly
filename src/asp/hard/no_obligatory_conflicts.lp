%*
Obligatory courses of the same ideal semester should not conflict (only for BCC)
*%
:- conflict(CourseA, "bcc", CourseB, "bcc"),
    is_obligatory(CourseA),
    is_obligatory(CourseB),
    ideal_semester(CourseA, IdealSemester),
    ideal_semester(CourseB, IdealSemester),
    IdealSemester > 0.
