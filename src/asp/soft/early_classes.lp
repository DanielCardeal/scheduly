%*
Avoid scheduling classes in the afternoon.
*%
afternoon_class(Course, Group, W, P) :-
    class(Course, Group, W, P),
    period(P, "afternoon").

:~ afternoon_class(Course, Group, W, P).
[w_early_classes@p_early_classes, Course, Group, W, P]

#show afternoon_class/4.
