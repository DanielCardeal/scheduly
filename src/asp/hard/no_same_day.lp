%*
Don't schedule more than one classe of each course in one day, unless it is a
double course.
*%
:- class(Course, Group, Weekday, Period1, false),
    class(Course, Group, Weekday, Period2, _),
    not is_double(Course),
    Period1 != Period2.
