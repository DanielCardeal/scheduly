%*
Don't schedule double classes in different parts of the day
*%
:- class(Course, Group, _, Period1),
    class(Course, Group, _, Period2),
    is_double(Course),
    Period2 != Period1,
    part_of_day(Period1, PartOfDay1),
    part_of_day(Period2, PartOfDay2),
    PartOfDay1 != PartOfDay2.
