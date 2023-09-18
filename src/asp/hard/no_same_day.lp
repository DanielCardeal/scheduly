%*
Classes from non-double courses must be scheduled in separate days.
*%
:- class(Course, Group, Weekday, Period1),
    class(Course, Group, Weekday, Period2),
    not is_double(Course),
    Period1 != Period2.
