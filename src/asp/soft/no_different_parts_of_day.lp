%*
Classes from a course should be scheduled on the same period of the day.
*%
different_parts_of_day(Course, Group) :-
    class(Course, Group, _, P1),
    class(Course, Group, _, P2),
    part_of_day(P1, PartOfDay1),
    part_of_day(P2, PartOfDay2),
    P1 <= P2, % don't count duplicates
    PartOfDay1 != PartOfDay2.

:~ different_parts_of_day(Course, Group).
[w_no_different_parts_of_day@p_no_different_parts_of_day, Course, Group]

#show different_parts_of_day/2.
