import datetime as dt
import re
from dataclasses import dataclass


class ParserException(Exception):
    """Exception raised when an error occurs during the parsing of CSV input files."""


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


@dataclass(frozen=True)
class TeacherData:
    """Information about availability and time preferences of a teacher.

    The teacher ID must be an uniquely identifiable value.
    """

    teacher_id: str
    available_time: set[ScheduleTimeslot]
    preferred_time: set[ScheduleTimeslot]


def time_to_period(time: dt.time) -> int:
    """
    Returns the time period that intersects a given time_input. If the time
    period doesn't match any time periods, returns -1.

    >>> time_to_period(dt.time(7, 40))
    -1
    >>> time_to_period(dt.time(8, 34))
    1
    >>> time_to_period(dt.time(10, 00))
    2
    >>> time_to_period(dt.time(15, 10))
    3
    """
    if dt.time(8, 0) <= time <= dt.time(9, 40):
        return 1
    elif dt.time(10, 0) <= time <= dt.time(11, 40):
        return 2
    elif dt.time(14, 0) <= time <= dt.time(15, 40):
        return 3
    elif dt.time(16, 0) <= time <= dt.time(17, 40):
        return 4
    return -1


def get_teacher_id(teacher_email: str) -> str:
    """Extract a teacher id from their e-mail address.

    The teachers' id is defined by everything before the domain address of their
    e-mails, transformed to lowercase. The function removes both punctuation and
    numbers from the teacher's e-mail, preventing

    >>> get_teacher_id("alan-turing@linux.ime.usp.br")
    alan_turing
    >>> get_teacher_id("AlanTuring22@google.com")
    alanturing
    """
    teacher_email = teacher_email.lower()
    teacher_email = re.sub(r"[0-9.]", "", teacher_email)
    teacher_email = teacher_email.replace("-", "_")
    return teacher_email[: teacher_email.find("@")]
