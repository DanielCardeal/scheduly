from __future__ import annotations

from enum import Enum
from typing import Protocol

from attrs import field, frozen, validators
from clingo import SymbolType
from clingo.symbol import Function, Number, String, Symbol
from typing_extensions import Self


class IntoASP(Protocol):
    """Objects that can be converted into an ASP code string."""

    def into_asp(self) -> str:
        """Convert instance of the object to its ASP code representation."""
        ...


class FromASP(Protocol):
    """Objects that can be parsed from an ASP symbol."""

    @classmethod
    def from_asp(cls, symbol: Symbol) -> Self:
        ...


class Weekday(Enum):
    """Days of the week as they are represented inside scheduler."""

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4

    def __str__(self) -> str:
        match self:
            case Weekday.MONDAY:
                return "monday"
            case Weekday.TUESDAY:
                return "tuesday"
            case Weekday.WEDNESDAY:
                return "wednesday"
            case Weekday.THURSDAY:
                return "thursday"
            case Weekday.FRIDAY:
                return "friday"


class Period(Enum):
    """Class periods as they are represented inside the scheduler."""

    MORNING_1 = 0
    MORNING_2 = 1
    AFTERNOON_1 = 2
    AFTERNOON_2 = 3

    def __str__(self) -> str:
        match self:
            case Period.MORNING_1:
                return "8:00 - 9:40"
            case Period.MORNING_2:
                return "10:00 - 11:40"
            case Period.AFTERNOON_1:
                return "14:00 - 15:40"
            case Period.AFTERNOON_2:
                return "16:00 - 17:40"


@frozen
class CourseData:
    """General information about a course in the educational institution."""

    course_id: str = field(converter=str)
    num_classes: int = field(validator=validators.instance_of(int))
    is_double: bool = field(validator=validators.instance_of(bool))
    group: str = field(converter=str)
    ideal_period: int = field(validator=validators.instance_of(int))

    def into_asp(self) -> str:
        """Convert self into a course/5 ASP predicate."""
        asp_list = [
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
        return _asp_list_to_str(asp_list)


@frozen
class TeacherData:
    """Information about availability and time preferences of a teacher."""

    teacher_id: str = field(converter=str)
    available_time: set[ScheduleTimeslot] = field(validator=validators.instance_of(set))
    preferred_time: set[ScheduleTimeslot] = field(validator=validators.instance_of(set))

    def into_asp(self) -> str:
        """Convert self into teacher/1, available/3 and preferred/3 ASP predicates."""
        available = [
            Function(
                "available",
                [
                    String(self.teacher_id),
                    Number(t.weekday.value),
                    Number(t.period.value),
                ],
            )
            for t in self.available_time
        ]
        preferred = [
            Function(
                "preferred",
                [
                    String(self.teacher_id),
                    Number(t.weekday.value),
                    Number(t.period.value),
                ],
            )
            for t in self.preferred_time
        ]
        return _asp_list_to_str(available + preferred)


@frozen(order=True)
class ScheduleTimeslot:
    """Represents a timeslot on the schedule."""

    weekday: Weekday = field(validator=validators.instance_of(Weekday))
    period: Period = field(validator=validators.instance_of(Period))


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
    offering_group: str = field(converter=str)
    fixed_classes: set[ScheduleTimeslot] = field(validator=validators.instance_of(set))

    def into_asp(self) -> str:
        """Convert self into lecturer/3 and class/5 ASP predicates."""
        lectures = Function(
            "lecturer",
            [
                String(self.course_id),
                String(self.offering_group),
                String(self.teacher_id),
            ],
        )
        lectures_str = _asp_list_to_str([lectures])

        fixed = [
            Function(
                "class",
                [
                    String(self.course_id),
                    String(self.offering_group),
                    Number(t.weekday.value),
                    Number(t.period.value),
                ],
            )
            for t in self.fixed_classes
        ]
        fixed_str = "\n".join([f":- not {cl}." for cl in fixed])

        return lectures_str + "\n" + fixed_str


@frozen
class JointClassData:
    """Indicates that two courses must be scheduled together."""

    course_id_A: str = field(converter=str)
    course_id_B: str = field(converter=str)

    def into_asp(self) -> str:
        "Convert self into a joint/2 ASP predicate."
        return _asp_list_to_str(
            [Function("joint", [String(self.course_id_A), String(self.course_id_B)])]
        )


@frozen
class CurriculaData:
    """Represents a curriculum of the educational institution."""

    curriculum_id: str = field(converter=str)
    group: str = field(converter=str)
    courses: set[CurriculaCoursesData] = field(validator=validators.instance_of(set))

    def into_asp(self) -> str:
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
        return _asp_list_to_str([curriculum] + curriculum_components)


@frozen
class CurriculaCoursesData:
    """Stores information about a course that compose a curriculum, to be
    referenced by CurriculaData.
    """

    course_id: str = field(converter=str)
    is_required: bool = field(validator=validators.instance_of(bool))


def generate_full_availability() -> set[ScheduleTimeslot]:
    """Generate a set with all the possible timeslots."""
    return set(ScheduleTimeslot(w, p) for w in Weekday for p in Period)


@frozen
class ClassData:
    """Information about a scheduled class in a ASP model."""

    course_id: str
    group: str
    weekday: Weekday
    period: Period

    @classmethod
    def from_asp(cls, symbol: Symbol) -> Self:
        assert (
            symbol.type is SymbolType.Function and symbol.name == "class"
        ), f"Unable to construct ClassData object from the given symbol: {str(symbol)}"
        course_id = symbol.arguments[0].string
        group = symbol.arguments[1].string
        weekday = Weekday(symbol.arguments[2].number)
        period = Period(symbol.arguments[3].number)
        return cls(course_id, group, weekday, period)


@frozen
class ConflictData:
    """Information about conflicting classes in a ASP model."""

    course_id_a: str
    group_id_a: str
    course_id_b: str
    group_id_b: str
    weekday: Weekday
    period: Period

    @classmethod
    def from_asp(cls, symbol: Symbol) -> Self:
        assert (
            symbol.type is SymbolType.Function and symbol.name == "conflict"
        ), f"Unable to construct ConflictData object from the given symbol: {str(symbol)}"
        course_id_a = symbol.arguments[0].string
        group_id_a = symbol.arguments[1].string
        course_id_b = symbol.arguments[2].string
        group_id_b = symbol.arguments[3].string
        weekday = Weekday(symbol.arguments[4].number)
        period = Period(symbol.arguments[5].number)
        return cls(course_id_a, group_id_a, course_id_b, group_id_b, weekday, period)


@frozen
class JointedData:
    """Information about jointed courses in an ASP model."""

    course_id_a: str
    course_id_b: str

    @classmethod
    def from_asp(cls, symbol: Symbol) -> Self:
        assert (
            symbol.type is SymbolType.Function and symbol.name == "jointed"
        ), f"Unable to construct JointedData object from the given symbol: {str(symbol)}"
        course_id_a = symbol.arguments[0].string
        course_id_b = symbol.arguments[1].string
        return cls(course_id_a, course_id_b)


def _asp_list_to_str(asp_list: list[Symbol]) -> str:
    """Converts a list of ASP symbols to an ASP code string."""
    return "\n".join([str(sym) + "." for sym in asp_list])
