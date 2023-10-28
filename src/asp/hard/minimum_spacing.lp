%*
Don't schedule classes less than `minimum_spacing` days apart.
*%
#const minimum_spacing = 2.

:- class(Course, Group, W1, _, false),
    class(Course, Group, W2, _, _),
    not is_double(Course),
    W1 != W2,
    |W1 - W2| < minimum_spacing.
