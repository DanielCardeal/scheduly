%*
Don't schedule classes less than `minimum_spacing` days apart.
*%
#const minimum_spacing = 2.

:- class(Course, Group, W1, _),
    class(Course, Group, W2, _),
    W1 < W2,
    (W2 - W1) < minimum_spacing.
