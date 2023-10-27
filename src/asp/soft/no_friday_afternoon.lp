%*
Avoid scheduling BCC undergrad classes after friday morning.
*%
friday_afternoon_class(Course) :-
    class(Course, "bcc", 4, Period),
    is_undergrad(Course),
    part_of_day(Period, PartOfDay),
    PartOfDay != "morning".

:~ friday_afternoon_class(Course, Period).
[w_no_friday_afternoon@p_no_friday_afternoon, Course]
