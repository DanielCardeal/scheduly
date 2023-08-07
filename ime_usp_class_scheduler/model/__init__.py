from __future__ import annotations

from attrs import field, frozen, validators


@frozen
class CourseData:
    """General information about a course in the educational institution."""

    course_id: str = field(converter=str)
    num_classes: int = field(validator=validators.instance_of(int))
    is_double: bool = field(validator=validators.instance_of(bool))
    group: str = field(converter=str)
    ideal_period: int = field(validator=validators.instance_of(int))


@frozen
class TeacherData:
    """Information about availability and time preferences of a teacher."""

    teacher_id: str = field(converter=str)
    available_time: set[ScheduleTimeslot] = field(validator=validators.instance_of(set))
    preferred_time: set[ScheduleTimeslot] = field(validator=validators.instance_of(set))


@frozen(order=True)
class ScheduleTimeslot:
    """Represents a timeslot on the schedule."""

    weekday: int = field(validator=validators.instance_of(int))
    period: int = field(validator=validators.instance_of(int))

    @weekday.validator
    def _validate_weekday(self, attribute, value):
        if not 1 <= value <= 7:
            raise ValueError("weekday must be between 1 and 7")


@frozen
class WorkloadData:
    """Information about a course offering, such as the lecturer's ID.

    The list of fixed classes can be empty, which indicates that all classes of
    the course should be schedule by the scheduler. If, for example, only half of
    the classes of course are fixed, the scheduler will find adequate schedule
    periods for the remaining classes.
    """

    course_id: str = field(converter=str)
    teacher_id: str = field(converter=str)
    group: str = field(converter=str)
    fixed_classes: set[ScheduleTimeslot] = field(validator=validators.instance_of(set))


@frozen
class JointClassData:
    """Indicates that two courses must be scheduled together."""

    course_id_A: str = field(converter=str)
    course_id_B: str = field(converter=str)


@frozen
class CurriculaData:
    """Represents a curriculum of the educational institution."""

    curriculum_id: str = field(converter=str)
    group: str = field(converter=str)
    courses: set[CurriculaCoursesData] = field(validator=validators.instance_of(set))


@frozen
class CurriculaCoursesData:
    """Stores information about a course that compose a curriculum, to be
    referenced by CurriculaData.
    """

    course_id: str = field(converter=str)
    is_required: bool = field(validator=validators.instance_of(bool))
