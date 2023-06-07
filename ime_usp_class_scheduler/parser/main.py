from dataclasses import dataclass


@dataclass(frozen=True)
class ScheduleTimeslot:
    """Represents a timeslot on the schedule."""

    weekday: int
    period: int


@dataclass(frozen=True)
class CourseData:
    """Information about a course that should be scheduled by the class scheduler.

    Course and teacher ID's should be uniquely identifiable values.

    The list of fixed classes can be empty, which has the semantic meaning that
    all classes of the course should be schedule by the scheduler. If, for
    example, only half of the classes of course are fixed, the scheduler will
    find adequate schedule periods for the remaining, not fixed, classes.
    """

    course_id: str
    fixed_classes: set[ScheduleTimeslot]
    group: str
    teacher_id: str
