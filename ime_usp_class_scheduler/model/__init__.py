from attrs import field, frozen


@frozen(order=True)
class ScheduleTimeslot:
    """Represents a timeslot on the schedule."""

    weekday: int = field(converter=int)
    period: int = field(converter=int)

    @weekday.validator
    def _validate_weekday(self, attribute, value):
        if not 1 <= value <= 7:
            raise ValueError("weekday must be between 1 and 7")


@frozen
class CourseData:
    """Information about a course that should be scheduled by the class scheduler.

    Course and teacher ID's should be uniquely identifiable values.

    The list of fixed classes can be empty, which has the semantic meaning that
    all classes of the course should be schedule by the scheduler. If, for
    example, only half of the classes of course are fixed, the scheduler will
    find adequate schedule periods for the remaining, not fixed, classes.
    """

    course_id: str = field(converter=str)
    teacher_id: str = field(converter=str)
    group: str = field(converter=str)
    fixed_classes: set[ScheduleTimeslot] = field(converter=set)


@frozen
class TeacherData:
    """Information about availability and time preferences of a teacher.

    The teacher ID must be an uniquely identifiable value.
    """

    teacher_id: str = field(converter=str)
    available_time: set[ScheduleTimeslot] = field(converter=set)
    preferred_time: set[ScheduleTimeslot] = field(converter=set)
