%*
Classes from double courses must be schedule one after another in the same
day.
*%
% Different days of the week
:- class(Course, Group, Weekday1, _),
    class(Course, Group, Weekday2, _),
    is_double(Course),
    Weekday1 != Weekday2.

% Different
:- class(Course, Group, Weekday, Period1),
    class(Course, Group, Weekday, Period2),
    is_double(Course),
    (Period1 - Period2)**2 != 1.
