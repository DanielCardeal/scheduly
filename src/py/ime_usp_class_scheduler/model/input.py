from __future__ import annotations

import csv
import datetime as dt
import re
from contextlib import ExitStack
from typing import IO, Hashable, Iterable, Optional, Protocol, Sequence, TypeVar

import cattrs
from attrs import asdict, define, field, frozen, validators
from clingo.symbol import Function, Number, String, Symbol
from typing_extensions import Self

from ime_usp_class_scheduler.constants import INPUT_DIR
from ime_usp_class_scheduler.log import LOG_WARN
from ime_usp_class_scheduler.model.common import Period, Weekday

DEFAULT_PERIOD_LENGTH = dt.timedelta(hours=1, minutes=40)
"""The default length of a period in the educational institution"""

CONVERTER = cattrs.Converter(prefer_attrib_converters=True)
"""The default converter used while parsing."""


class ParserException(Exception):
    """Exception raised when an error occurs during the parsing of CSV input files."""


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

    Raises a ParserException if the CSV data doesn't conform to the schema.
    """
    try:
        entries = [data for data in csv.DictReader(csv_data)]
        return [CONVERTER.structure(entry, schema) for entry in entries]
    except cattrs.BaseValidationError as e:
        messages = cattrs.transform_error(e)
        raise ParserException(
            f"Unable to parse CSV input into {schema.__name__}: {messages}."
        )


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
        elif len(courses_id) > 2:
            raise ValueError("Exceded the maximum ammount of course IDs")
        for course_id in courses_id:
            if not course_id:
                raise ValueError("Invalid empty course id")

    teachers_id: list[str] = field(converter=_teacher_list_converter)
    """List of the courses' lecturers unique identifiers."""

    @teachers_id.validator
    def _validate_teachers_id(self, _: str, teachers_id: list[str]) -> None:
        if len(teachers_id) < 1:
            raise ValueError("Expected at least one teacher id.")
        for teacher_id in teachers_id:
            if not teacher_id:
                raise ValueError("Invalid empty teacher id")

    fixed_classes: set[ScheduleTimeslot] = field(
        factory=set,
        converter=_schedule_timeslots_converter,
    )
    """Set of fixed classes of the course offering."""

    course_name: str = ""
    """Course long-form written name."""

    offering_group: str = ""
    """Unique identifier for the course offering group."""

    @property
    def index(self) -> tuple[str, ...]:
        return (*self.courses_id, *self.teachers_id)

    def into_asp(self) -> str:
        """Convert self into lecturer/3 and class/5 ASP predicates."""
        lecturers = []
        fixed_classes = []

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
                    ],
                )
                for t in self.fixed_classes
            ]

        joint_str = ""
        if len(self.courses_id) == 2:
            joint_str = _symbol_to_str(
                Function(
                    "joint",
                    [String(self.courses_id[0]), String(self.courses_id[1])],
                )
            )

        lecturers_str = _symbol_to_str(lecturers)
        fixed_classes_str = "\n".join([f":- not {fixed}." for fixed in fixed_classes])
        return "\n".join((lecturers_str, fixed_classes_str, joint_str))


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
    workloads: list[WorkloadData]
    curriculums: list[CurriculumData]

    def into_str(self) -> str:
        """Converts an InputDataset into an ASP code string."""
        instance_params: Sequence[Sequence[AspInput]] = (
            self.courses,
            self.schedules,
            self.workloads,
            self.curriculums,
        )
        result = "\n".join(el.into_asp() for param in instance_params for el in param)
        return result

    def validate_and_normalize(self) -> None:
        """Check the consistency of the dataset, fixing inconsistencies whenever
        it is possible.

        If a severe inconsistency is found, raises a ParserException. Light
        inconsistencies are reported as warnings.
        """
        # Check if inputs have repeated indexes
        named_params: Sequence[tuple[str, Sequence[AspInput]]] = [
            ("courses", self.courses),
            ("schedules", self.schedules),
            ("workloads", self.workloads),
            ("curriculums", self.curriculums),
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
                raise ParserException(
                    f"Found the following repeated values while parsing {input_type}:\n{repeated}"
                )

        for workload in self.workloads:
            # Check if data of a course to be scheduled is missing
            for course_id in workload.courses_id:
                if not [c for c in self.courses if c.course_id == course_id]:
                    raise ParserException(
                        f"Missing course information for course with id {course_id}."
                    )

            # Warns about teachers without availability data
            for teacher_id in workload.teachers_id:
                if not [t for t in self.schedules if t.teacher_id == teacher_id]:
                    LOG_WARN(
                        f"No availability for teacher '{teacher_id}', using full availability."
                    )

    @classmethod
    def from_default_files(cls) -> Self:
        """Creates an InputDataset from the default input files (placed at INPUT_DIR)."""
        try:
            with ExitStack() as stack:

                def open_input(basename: str) -> IO[str]:
                    path = INPUT_DIR.joinpath(basename).with_suffix(".csv")
                    return stack.enter_context(open(path, "rU"))

                courses_file = open_input("courses")
                schedules_file = open_input("schedules")
                workloads_file = open_input("workloads")
                curriculum_file = open_input("curriculum")

                courses = _csv_to_schema(courses_file, CourseData)
                schedules = _csv_to_schema(schedules_file, TeacherScheduleData)
                workloads = _csv_to_schema(workloads_file, WorkloadData)
                curriculum = _csv_to_schema(curriculum_file, CurriculumData)

            return cls(courses, schedules, workloads, curriculum)
        except (FileNotFoundError, PermissionError, OSError) as e:
            raise ParserException(
                f"Unable to load input file {e.filename}: {e.__class__.__name__}"
            )
