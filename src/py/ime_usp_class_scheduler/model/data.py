from __future__ import annotations

from typing import Any, Protocol

from attrs import field, frozen, validators
from clingo.symbol import Function, Number, String, Symbol


class ASPData(Protocol):
    """Protocol of all classes that can be converted to ASP"""

    def to_asp(self) -> list[Symbol]:
        """Convert instance of the object to its ASP symbol representation."""
        ...


@frozen
class CourseData:
    """General information about a course in the educational institution."""

    course_id: str = field(converter=str)
    num_classes: int = field(validator=validators.instance_of(int))
    is_double: bool = field(validator=validators.instance_of(bool))
    group: str = field(converter=str)
    ideal_period: int = field(validator=validators.instance_of(int))

    def to_asp(self) -> list[Symbol]:
        """Convert self into a course/5 ASP predicate."""
        return [
            Function(
                "course",
                [
                    String(self.course_id),
                    String(self.group),
                    Number(self.num_classes),
                    Number(self.ideal_period),
                    Number(self.is_double),
                ],
            )
        ]


@frozen
class TeacherData:
    """Information about availability and time preferences of a teacher."""

    teacher_id: str = field(converter=str)
    available_time: set[ScheduleTimeslot] = field(validator=validators.instance_of(set))
    preferred_time: set[ScheduleTimeslot] = field(validator=validators.instance_of(set))

    def to_asp(self) -> list[Symbol]:
        """Convert self into teacher/1, available/3 and preferred/3 ASP predicates."""
        available = [
            Function(
                "available",
                [String(self.teacher_id), Number(t.weekday), Number(t.period)],
            )
            for t in self.available_time
        ]
        preferred = [
            Function(
                "preferred",
                [String(self.teacher_id), Number(t.weekday), Number(t.period)],
            )
            for t in self.preferred_time
        ]
        return available + preferred


@frozen(order=True)
class ScheduleTimeslot:
    """Represents a timeslot on the schedule."""

    weekday: int = field(validator=validators.instance_of(int))
    period: int = field(validator=validators.instance_of(int))

    @weekday.validator
    def _validate_weekday(self, _: Any, value: int) -> None:
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

    # TODO: implement multiple teachers for one class
    course_id: str = field(converter=str)
    teacher_id: str = field(converter=str)
    offering_group: str = field(converter=str)
    fixed_classes: set[ScheduleTimeslot] = field(validator=validators.instance_of(set))

    def to_asp(self) -> list[Symbol]:
        """Convert self into lecturer/3 and class/5 ASP predicates."""
        lectures = Function(
            "lecturer",
            [
                String(self.course_id),
                String(self.offering_group),
                String(self.teacher_id),
            ],
        )
        fixed = [
            Function(
                "class",
                [
                    String(self.course_id),
                    String(self.offering_group),
                    String(self.teacher_id),
                    Number(t.weekday),
                    Number(t.period),
                ],
            )
            for t in self.fixed_classes
        ]

        return [lectures] + fixed


@frozen
class JointClassData:
    """Indicates that two courses must be scheduled together."""

    course_id_A: str = field(converter=str)
    course_id_B: str = field(converter=str)

    def to_asp(self) -> list[Symbol]:
        "Convert self into a joint/2 ASP predicate."
        return [Function("joint", [String(self.course_id_A), String(self.course_id_B)])]


@frozen
class CurriculaData:
    """Represents a curriculum of the educational institution."""

    curriculum_id: str = field(converter=str)
    group: str = field(converter=str)
    courses: set[CurriculaCoursesData] = field(validator=validators.instance_of(set))

    def to_asp(self) -> list[Symbol]:
        """Convert self into curriculum/3 and curriculum_component/3 ASP predicates."""
        curriculum = Function(
            "curriculum", [String(self.curriculum_id), String(self.group)]
        )
        curriculum_components = [
            Function(
                "curriculum_component",
                [
                    String(self.curriculum_id),
                    String(data.course_id),
                    Number(data.is_required),
                ],
            )
            for data in self.courses
        ]
        return [curriculum] + curriculum_components


@frozen
class CurriculaCoursesData:
    """Stores information about a course that compose a curriculum, to be
    referenced by CurriculaData.
    """

    course_id: str = field(converter=str)
    is_required: bool = field(validator=validators.instance_of(bool))
