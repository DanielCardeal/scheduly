%*
Avoid scheduling classes in the afternoon.
*%
afternoon_class(Course, Group, Weekday, Period) :-
    class(Course, Group, Weekday, Period),
    part_of_day(P, "afternoon").

:~ afternoon_class(Course, Group, Weekday, Period).
[w_early_classes@p_early_classes, Course, Group, Weekday, Period]

#show afternoon_class/4.
