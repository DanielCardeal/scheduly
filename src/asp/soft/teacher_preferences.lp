%*
Avoid scheduling classes in teacher's preferred times.
*%
:~ class(Course, Group, Weekday, Period),
    lecturer(Course, Group, Teacher),
    not preferred(Teacher, Weekday, Period).
    [w_teacher_preferences@p_teacher_preferences, Teacher, Weekday, Period]
