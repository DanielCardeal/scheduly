"""Dataclasses that model the input data of the scheduler."""
from __future__ import annotations

import csv
import datetime as dt
import re
from itertools import combinations
from pathlib import Path
from typing import IO, Hashable, Protocol, Sequence, TypeVar

from attrs import define, field, frozen, validators
from cattrs.errors import BaseValidationError
from clingo.symbol import Function, Number, String, Symbol
from typing_extensions import Self

from ime_usp_class_scheduler.errors import (
    FileTreeError,
    InconsistentInputError,
    ParsingError,
)
from ime_usp_class_scheduler.log import LOG_WARN
from ime_usp_class_scheduler.model.common import CONVERTER, PartOfDay, Period, Weekday
from ime_usp_class_scheduler.paths import INPUT_DIR

DEFAULT_PERIOD_LENGTH = dt.timedelta(hours=1, minutes=40)
"""The default length of a period in the educational institution"""

DEFAULT_CLASS_PERIOD = {PartOfDay.MORNING, PartOfDay.AFTERNOON}
"""The default periods to try to schedule classes."""

DEFAULT_OFFERING_GROUP = "BCC"
"""The default offering group."""


def _symbol_to_str(symbols: Symbol | list[Symbol]) -> str:
    """Converts an symbol/list of ASP symbols to an ASP code string.

    Examples:

    >>> s1: Symbol = Function('func1', [Number(10), String('text')])
    >>> _symbol_to_str(s1)
    'func1(10,"text").'

    >>> s2: list[Symbol] = [Function('func2', [Number(42)]), Function('func3', [String('foo'), String('baz')])]
    >>> _symbol_to_str(s2)
    'func2(42).\\nfunc3("foo","baz").'
    """
    if not isinstance(symbols, list):
        symbols = [symbols]
    return "\n".join([str(sym) + "." for sym in symbols])


def _teacher_id_converter(email: str) -> str:
    """Extract the teacher id from the teacher email.

    A teacher id is defined by everything before the domain address of their
    e-mails.

    Examples:

    >>> _teacher_id_converter("alan-turing@linux.ime.usp.br")
    'alan-turing'
    >>> _teacher_id_converter("adaLovelace")
    'adaLovelace'
    """
    if email.find("@") > 0:
        teacher_id = email[: email.find("@")]
    else:
        teacher_id = email
    return teacher_id.strip()


def _teacher_list_converter(ids: str | list[str]) -> list[str]:
    """
    If `ids` is already a list of strings, just forward it as the output.
    Otherwise, parses the `ids` string as a list of ';' separated teachers ids.

    Examples:

    >>> _teacher_list_converter("alan-turing@linux.ime.usp.br")
    ['alan-turing']
    >>> _teacher_list_converter("alan@google.com;turing@usp.br")
    ['alan', 'turing']
    """
    if isinstance(ids, list):
        return ids
    elif isinstance(ids, str):
        ids = ids.strip(" ;")
        return [_teacher_id_converter(email) for email in ids.split(";")]
    else:
        raise ValueError(
            f"Unable to parse teachers ids from value {id} of type {type(ids)}."
        )


def _boolean_converter(boolean_value: str | bool) -> bool:
    """If `boolean_value` is already a `bool`, just forward it as the output.
    Otherwise, try parsing the string as a boolean.

    Values mapping to `True`:

    - "True"
    - "yes"
    - "y"
    - "sim"
    - "s"
    - "1"

    Values mapping for `False`:

    - "" (empty string)
    - "False"
    - "no"
    - "n"
    - "nao"
    - "não"
    - "0"

    Raises a `ValueError` if the string is not any of the above.
    """
    if isinstance(boolean_value, bool):
        return boolean_value
    elif isinstance(boolean_value, str):
        match boolean_value:
            case "True" | "yes" | "y" | "sim" | "s" | "1":
                return True
            case "False" | "no" | "n" | "nao" | "não" | "0" | "":
                return False
            case _:
                raise ValueError(f"Unable to convert {boolean_value} to a boolean.")
    else:
        raise ValueError(
            f"Unable to convert value {boolean_value} of type {type(boolean_value)} to a bool."
        )


def _class_period_converter(period: str | set[PartOfDay]) -> set[PartOfDay]:
    """If `period` is already a `set[PartOfDay]`, just forward it as the output.
    Otherwise, try parsing the string as a set of parts of the day using
    `PartOfDay.from_str`.

    Empty strings are parsed as `DEFAULT_CLASS_PERIOD`.
    """
    if isinstance(period, set):
        return period

    if isinstance(period, str):
        if period:
            return PartOfDay.from_str(period)
        else:
            return DEFAULT_CLASS_PERIOD

    raise ValueError(
        f"Unable to convert value {period} of type {type(period)} to periods."
    )


def _offering_group_converter(group: str) -> str:
    """Normalize an offering group string."""
    if not group:
        group = DEFAULT_OFFERING_GROUP
    return group.strip().lower()


def _schedule_timeslots_converter(
    timeslots: set[ScheduleTimeslot] | str,
) -> set[ScheduleTimeslot]:
    """If timeslots is a `set[ScheduleTimeslot]`, just forward it as the output.
    Otherwise, parse the `timeslots` string into a `set[ScheduleTimeslot]`.

    Raises an `ValueError` if `timeslots` is an invalid input string.

    A `timeslots` string must have the following structure:

    (day of the week) (start time 1)-(end time 1) (start time 2)-(end time 2); (repeat for next day of the week)

    "day of the week" can be any of the valid input strings for `Weekday.from_str`.

    Start and end times must be passed using the HH:MM notation (ex. 12:00, 15:32).

    If an end time is not provided, the function assumes unavailability for an interval of DEFAULT_PERIOD_LENGTH.

    Examples:

    1) Two timeslots, one on Tuesdays from 8:00 to 9:40 and one on Thursdays
       from 10:00 to 11:40:

        "ter 08:00 - 09:40; qui 10:00 - 11:40"

    2) One timeslot on Friday from 12:00 to 13:00 (returns an empty set since
       there are no teaching periods in this time interval).

        "fri 12:00-13:00"

    3) One timeslot on Mondays from 16:00 to 17:40 and two on Wednesdays: the first
       from 7:40am to 10am and the second from 14pm to 16pm

        "mon 16:00; wed 7:40-10:00 14:00 - 16:00"
    """
    if isinstance(timeslots, set):
        return timeslots

    timeslots = timeslots.strip(" ;").lower()
    if not timeslots:
        return set()

    WEEKDAY_REGEX = re.compile(r"^(seg|ter|qua|qui|sex|mon|tue|wed|thu|fri)")
    TIME_REGEX = r"(?:[0-1]?[0-9]|2[0-3]):[0-5][0-9]"
    SEPARATOR_REGEX = r"(?:\s?-\s?)"
    TIME_RANGE_REGEX = re.compile(rf"({TIME_REGEX}){SEPARATOR_REGEX}?({TIME_REGEX})?")

    fixed_classes = set()

    for weekday_input in timeslots.split(";"):
        weekday_input = weekday_input.strip()
        if not weekday_input:  # empty substring
            continue

        if (weekday_match := WEEKDAY_REGEX.match(weekday_input)) is None:
            raise ValueError(
                f"Unable to match weekday in string '{weekday_input}' (substring of '{timeslots}')."
            )
        weekday = Weekday.from_str(weekday_match.group())

        time_range_matches = TIME_RANGE_REGEX.findall(weekday_input)
        if len(time_range_matches) == 0:
            raise ValueError(
                f"Unable to parse time ranges from string: {weekday_input} (substring of {timeslots})"
            )

        for start_time, end_time in time_range_matches:
            start_time = dt.datetime.strptime(start_time, "%H:%M")
            if end_time:
                end_time = dt.datetime.strptime(end_time, "%H:%M")
            else:
                end_time = start_time + DEFAULT_PERIOD_LENGTH
            periods = Period.intersections(start_time.time(), end_time.time())
            for period in periods:
                fixed_classes.add(ScheduleTimeslot(weekday, period))

    return fixed_classes


def _course_id_converter(course_id: str) -> str:
    """Normalizes a course_id."""
    return course_id.lower().strip()


def _courses_ids_converter(ids: str | list[str]) -> list[str]:
    """If `ids` is already a list of strings, just forward it as the output.
    Otherwise, parse the `ids` string as a list of ';' separated courses IDs.

    Examples:

    >>> _courses_ids_converter("MAC0101")
    ['mac0101']
    >>> _courses_ids_converter("MAC0110;mac3210")
    ['mac0110', 'mac3210']
    >>> _courses_ids_converter(['mac0110', 'mac3210'])
    ['mac0110', 'mac3210']
    """
    if isinstance(ids, list):
        return ids
    elif isinstance(ids, str):
        ids = ids.strip(" ;")
        return [_course_id_converter(course_id) for course_id in ids.split(";")]
    else:
        raise ValueError(
            f"Unable to parse courses ids from value {id} of type {type(ids)}."
        )


def _generate_full_availability() -> set[ScheduleTimeslot]:
    """Generate a set with all the possible timeslots."""
    return set(ScheduleTimeslot(w, p) for w in Weekday for p in Period)


def _csv_to_schema(csv_data: IO[str], schema: type[T]) -> list[T]:
    """Loads and validates the CSV using a predefined schema. Data validation is
    defined in the schema itself.

    Raises a BaseValidationError if cattrs cannot structure the data in the CSV
    into the schema.
    """
    entries = [data for data in csv.DictReader(csv_data)]
    return [CONVERTER.structure(entry, schema) for entry in entries]


@frozen(order=True)
class ScheduleTimeslot:
    """Represents a timeslot on the schedule."""

    weekday: Weekday = field(validator=validators.instance_of(Weekday))
    period: Period = field(validator=validators.instance_of(Period))


class AspInput(Protocol):
    """Input data that can be converted into an ASP code string."""

    @property
    def index(self) -> Hashable | tuple[Hashable]:
        """Get index (or indexes) of the AspInput."""
        ...

    def into_asp(self) -> str:
        """Convert instance of the object to its ASP code representation."""
        ...


T = TypeVar("T", bound=AspInput)


@frozen
class CourseData:
    """General information about a course in the educational institution."""

    course_id: str = field(
        converter=_course_id_converter,
        validator=validators.min_len(1),
    )
    """Unique identifier for the course"""

    num_classes: int = field(converter=int, validator=validators.gt(0))
    """Number of weekly classes to be scheduled"""

    ideal_semester: int = field(converter=int, validator=validators.ge(0))
    """Ideal semester for a student to take the course."""

    is_undergrad: bool = field(converter=_boolean_converter, default=False)
    """Indicates if the course is an undergrad course."""

    is_double: bool = field(converter=_boolean_converter, default=False)
    """Indicates if the course classes must be scheduled in consecutive periods."""

    @property
    def index(self) -> str:
        return self.course_id

    def into_asp(self) -> str:
        """Convert instance into is_undergrad/1, is_double/1, num_classes/2 and
        ideal_semester/2 ASP predicates.
        """
        predicates = []
        if self.is_undergrad:
            predicates.append(Function("is_undergrad", [String(self.course_id)]))

        if self.is_double:
            predicates.append(Function("is_double", [String(self.course_id)]))

        predicates.append(
            Function("num_classes", [String(self.course_id), Number(self.num_classes)])
        )
        predicates.append(
            Function(
                "ideal_semester", [String(self.course_id), Number(self.ideal_semester)]
            )
        )
        return _symbol_to_str(predicates)


@frozen
class TeacherScheduleData:
    """Information about availability and time preferences of a teacher."""

    teacher_id: str = field(
        converter=_teacher_id_converter, validator=validators.min_len(1)
    )
    """Unique identifier of the teacher."""

    preferred: set[ScheduleTimeslot] = field(
        factory=set,
        converter=_schedule_timeslots_converter,
    )
    """Set of teacher's preferred teaching timeslots."""

    unavailable: set[ScheduleTimeslot] = field(
        factory=set,
        converter=_schedule_timeslots_converter,
    )
    """Set of teacher's unavailable teaching timeslots."""

    @property
    def index(self) -> str:
        return self.teacher_id

    def into_asp(self) -> str:
        """Convert self into available/3 and preferred/3 ASP predicates."""
        available_periods = _generate_full_availability() - self.unavailable
        available = [
            Function(
                "available",
                [
                    String(self.teacher_id),
                    Number(t.weekday.value),
                    Number(t.period.value),
                ],
            )
            for t in available_periods
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
            for t in self.preferred
        ]
        return _symbol_to_str(available + preferred)


@frozen
class WorkloadData:
    """Information about a course offering."""

    courses_id: list[str] = field(converter=_courses_ids_converter)
    """List of course unique identifiers."""

    @courses_id.validator
    def _validate_courses_id(self, _: str, courses_id: list[str]) -> None:
        if len(courses_id) < 1:
            raise ValueError("Expected at least one course id.")
        for course_id in courses_id:
            if not course_id:
                raise ValueError("Invalid empty course id")

    teachers_id: list[str] = field(converter=_teacher_list_converter)
    """List of the courses' lecturers unique identifiers."""

    offering_group: str = field(converter=_offering_group_converter)
    """Unique identifier for the course offering group."""

    @teachers_id.validator
    def _validate_teachers_id(self, _: str, teachers_id: list[str]) -> None:
        if len(teachers_id) < 1:
            raise ValueError("Expected at least one teacher id.")
        for teacher_id in teachers_id:
            if not teacher_id:
                raise ValueError("Invalid empty teacher id")

    class_period: set[PartOfDay] = field(
        converter=_class_period_converter,
        validator=validators.min_len(1),
    )
    """Parts of the day in which classes can be scheduled."""

    fixed_classes: set[ScheduleTimeslot] = field(
        factory=set,
        converter=_schedule_timeslots_converter,
    )
    """Set of fixed classes of the course offering."""

    course_name: str = ""
    """Course long-form written name."""

    @property
    def index(self) -> tuple[str, ...]:
        return (*self.courses_id, self.offering_group)

    def into_asp(self) -> str:
        """Convert self into lecturer/3, class/5, joint/3 and class_part_of_day/3
        ASP predicates.
        """
        lecturers = []
        fixed_classes = []
        schedule_on = []

        for course_id in self.courses_id:
            for teacher_id in self.teachers_id:
                lecturer = Function(
                    "lecturer",
                    [
                        String(course_id),
                        String(self.offering_group),
                        String(teacher_id),
                    ],
                )
                lecturers.append(lecturer)

            fixed_classes += [
                Function(
                    "class",
                    [
                        String(course_id),
                        String(self.offering_group),
                        Number(t.weekday.value),
                        Number(t.period.value),
                        Number(True),
                    ],
                )
                for t in self.fixed_classes
            ]

            schedule_on += [
                Function(
                    "schedule_on",
                    [
                        String(course_id),
                        String(self.offering_group),
                        String(str(part_of_day)),
                    ],
                )
                for part_of_day in self.class_period
            ]

        joint_str = ""
        if len(self.courses_id) > 1:
            joints = [
                Function(
                    "joint",
                    [
                        String(course_id_a),
                        String(course_id_b),
                        String(self.offering_group),
                    ],
                )
                for course_id_a, course_id_b in combinations(self.courses_id, r=2)
            ]
            joint_str = _symbol_to_str(joints)

        lecturers_str = _symbol_to_str(lecturers)
        schedule_on_str = _symbol_to_str(schedule_on)
        fixed_classes_str = "\n".join([f"{fixed}." for fixed in fixed_classes])
        return "\n".join((lecturers_str, fixed_classes_str, joint_str, schedule_on_str))


@frozen
class CurriculumData:
    """Represents a curriculum of the educational institution."""

    course_id: str = field(validator=validators.min_len(1))
    """Unique identifier for the course."""

    curricula_id: str = field(validator=validators.min_len(1))
    """Unique identifier for the curricula"""

    is_required: bool = field(converter=_boolean_converter, default=False)
    """Indicates if the course is required to complete a curricula"""

    @property
    def index(self) -> tuple[str, str]:
        return (self.course_id, self.curricula_id)

    def into_asp(self) -> str:
        """Convert self into a curriculum/3 ASP predicate."""
        curriculum = Function(
            "curriculum",
            [
                String(self.curricula_id),
                String(self.course_id),
                Number(self.is_required),
            ],
        )
        return _symbol_to_str(curriculum)


@define
class InputDataset:
    """Input dataset required to run the scheduler."""

    courses: list[CourseData]
    schedules: list[TeacherScheduleData]
    workload: list[WorkloadData]
    curriculum: list[CurriculumData]

    def into_str(self) -> str:
        """Converts an InputDataset into an ASP code string."""
        instance_params: Sequence[Sequence[AspInput]] = (
            self.courses,
            self.schedules,
            self.workload,
            self.curriculum,
        )
        result = "\n".join(el.into_asp() for param in instance_params for el in param)
        return result + "\n"

    def validate_and_normalize(self) -> None:
        """Check the consistency of the dataset, fixing inconsistencies whenever
        it is possible.

        If a severe inconsistency is found, raises an InconsistentInputError.
        Light inconsistencies are reported as warnings.
        """
        # Check if inputs have repeated indexes
        named_params: Sequence[tuple[str, Sequence[AspInput]]] = [
            ("courses", self.courses),
            ("schedules", self.schedules),
            ("workload", self.workload),
            ("curriculum", self.curriculum),
        ]
        for input_type, value_list in named_params:
            seen: dict[Hashable | tuple[Hashable, ...], int] = {}
            for data in value_list:
                idx = data.index
                if idx not in seen:
                    seen[idx] = 0
                seen[idx] += 1
            repeated = {idx for idx, count in seen.items() if count > 1}
            if repeated:
                raise InconsistentInputError(
                    f"Found the following repeated values while parsing {input_type}:\n{repeated}"
                )

        for workload in self.workload:
            # Check if data of a course to be scheduled is missing
            for course_id in workload.courses_id:
                if not [c for c in self.courses if c.course_id == course_id]:
                    raise InconsistentInputError(
                        f"Missing course information for course with id {course_id}."
                    )

            # Warns about teachers without availability data
            for teacher_id in workload.teachers_id:
                if not [t for t in self.schedules if t.teacher_id == teacher_id]:
                    LOG_WARN(
                        f"No availability for teacher '{teacher_id}', using full availability."
                    )
                    teacher = TeacherScheduleData(teacher_id)
                    self.schedules.append(teacher)

    @classmethod
    def from_default_files(cls) -> Self:
        """Creates an InputDataset from the default input files (placed at INPUT_DIR)."""

        def get_path(basename: str) -> Path:
            return INPUT_DIR.joinpath(basename).with_suffix(".csv")

        parsed_data: dict[str, Sequence[AspInput]] = {}
        for basename, schema in [
            ("courses", CourseData),
            ("schedules", TeacherScheduleData),
            ("workload", WorkloadData),
            ("curriculum", CurriculumData),
        ]:
            input_path = get_path(basename)
            try:
                with open(input_path) as csv_data:
                    parsed_data[basename] = _csv_to_schema(csv_data, schema)
            except OSError as e:
                raise FileTreeError.from_os_error(basename, "input file", e)
            except BaseValidationError as e:
                raise ParsingError.from_cattrs_error(basename, "input file", e)

        return cls(**parsed_data)  # type: ignore
