%*
Avoid scheduling classes in teacher's preferred times.
*%
not_at_teacher_preferred(Course, Group, Teacher, W, P) :-
    class(Course, Group, W, P, false),
    lecturer(Course, Group, Teacher),
    not preferred(Teacher, W, P).

:~ not_at_teacher_preferred(Course, Group, Teacher, W, P).
[w_teacher_preferences@p_teacher_preferences, Course, Group, Teacher, W, P]

#show not_at_teacher_preferred/5.
