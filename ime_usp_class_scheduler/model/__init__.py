from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScheduleTimeslot:
    """Represents a timeslot on the schedule."""

    weekday: int
    period: int


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class TeacherData:
    """Information about availability and time preferences of a teacher.

    The teacher ID must be an uniquely identifiable value.
    """

    teacher_id: str
    available_time: set[ScheduleTimeslot]
    preferred_time: set[ScheduleTimeslot]
