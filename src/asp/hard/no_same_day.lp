%*
BCC non-double classes must be scheduled in separate days.
*%
:- class(Course, "bcc", Weekday, Period1),
    class(Course, "bcc", Weekday, Period2),
    not is_double(Course),
    Period1 != Period2.
