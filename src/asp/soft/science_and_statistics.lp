%*
Avoid conflicting with sciences and statistics courses for courses of ideal
semester greater or equal than 2.
*%
science_conflicts(ScienceC, ObligatoryC, W, P) :-
    conflict(ScienceC, _, ObligatoryC, _, W, P),
    curriculum("sciences", ScienceC, _),
    is_obligatory(ObligatoryC),
    ideal_semester(ObligatoryC, IdealSemester),
    IdealSemester >= 2.

statistic_conflicts(StatisticsC, ObligatoryC, W, P) :-
    conflict(StatisticsC, _, ObligatoryC, _, W, P),
    curriculum("statistics", StatisticsC, _),
    is_obligatory(ObligatoryC),
    ideal_semester(ObligatoryC, IdealSemester),
    IdealSemester >= 2.

:~ science_conflicts(Course, Other, W, P); statistics_conflicts(Course, Other, W, P).
[w_science_and_statistics@p_science_and_statistics, Course, Other, W, P]

#show science_conflicts/4.
#show statistics_conflicts/4.
