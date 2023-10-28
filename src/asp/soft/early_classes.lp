%*
Prefer to schedule classes in the morning.
*%
non_morning_class(Course, Group, Weekday, Period) :-
    class(Course, Group, Weekday, Period, false),
    part_of_day(P, PartOfDay),
    PartOfDay != "morning".

:~ non_morning_class(Course, Group, Weekday, Period).
[w_early_classes@p_early_classes, Course, Group, Weekday, Period]

#show non_morning_class/4.
