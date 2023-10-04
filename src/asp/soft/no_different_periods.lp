
%*
Classes from a course should be scheduled on the same period of the day.
*%
different_periods(Course, Group) :-
    class(Course, Group, _, P1), class(Course, Group, _, P2),
    period(P1, P1Name),
    period(P2, P2Name),
    P1Name != P2Name.

:~ different_periods(Course, Group).
[w_no_different_periods@p_no_different_periods, Course, Group]

#show different_periods/2.
