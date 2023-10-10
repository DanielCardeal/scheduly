%*
Avoid conflicts between classes of the same curriculum
*%
curriculum_conflict(CourseA, GroupA, CourseB, GroupB, W, P, Curriculum) :-
    _conflict(CourseA, GroupA, CourseB, GroupB, W, P),
    curriculum_component(Curriculum, CourseA, _),
    curriculum_component(Curriculum, CourseB, _).


:~ curriculum_conflict(CourseA, GroupA, CourseB, GroupB, W, P, Curriculum).
[w_no_curriculum_conflicts@p_no_curriculum_conflicts, CourseA, GroupA, CourseB, GroupB, W, P, Curriculum]

#show curriculum_conflict/7.
