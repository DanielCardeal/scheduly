
%*
Bound the distance of days for classes of the same offering.
*%
#const minimum_spacing = 1.
#const maximum_spacing = 3.

too_little_spacing(Course, Group) :-
    class(Course, Group, W1, _),
    class(Course, Group, W2, _),
    W1 < W2,
    (W2 - W1) < minimum_spacing.

too_much_spacing(Course, Group) :-
    class(Course, Group, W1, _),
    class(Course, Group, W2, _),
    W1 < W2,
    (W2 - W1) > maximum_spacing.

:~ too_little_spacing(Course, Group).
[w_bounded_spacing@p_bounded_spacing, Course, Group]

:~ too_much_spacing(Course, Group).
[w_bounded_spacing@p_bounded_spacing, Course, Group]

#show too_little_spacing/2.
#show too_much_spacing/2.
