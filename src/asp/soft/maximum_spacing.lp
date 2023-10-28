%*
Avoid scheduling classes more than `maximum_spacing` days apart.
*%
#const maximum_spacing = 3.

too_much_spacing(Course, Group) :-
    class(Course, Group, W1, _, false),
    class(Course, Group, W2, _, _),
    |W2 - W1| > maximum_spacing.

:~ too_much_spacing(Course, Group).
[w_maximum_spacing@p_maximum_spacing, Course, Group]

#show too_much_spacing/2.
