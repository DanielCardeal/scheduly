import csv
import datetime as dt
import io
import re

from ime_usp_class_scheduler.model import CourseData, ScheduleTimeslot, TeacherData


class ParserException(Exception):
    """Exception raised when an error occurs during the parsing of CSV input files."""


def _generate_full_availability() -> set[ScheduleTimeslot]:
    """Generate a set with all the possible timeslots."""
    return set(ScheduleTimeslot(w, p) for w in range(1, 5) for p in range(1, 4))


def _get_timeslots(weekday: int, input: str) -> set[ScheduleTimeslot]:
    """Extract timeslots for a given weekday using the time information stored
    in the input string. Only the starting periods are considered.

    Example:

    >>> _get_timeslots(2, "8:00-10:00;14:00-16:00")
    {ScheduleTimeslot(weekday=2, period=1), ScheduleTimeslot(weekday=2, period=3)}
    """
    if not input:
        return set()

    preferred_time = set()
    for time_range in input.split(";"):
        start_time = time_range.split("-")[0]
        time = dt.datetime.strptime(start_time, "%H:%M").time()
        period = _time_to_period(time)
        preferred_time.add(ScheduleTimeslot(weekday, period))

    return preferred_time


def _time_to_period(time: dt.time) -> int:
    """
    Returns the time period that intersects a given time_input. If the time
    period doesn't match any time periods, returns -1.

    >>> _time_to_period(dt.time(7, 40))
    -1
    >>> _time_to_period(dt.time(8, 34))
    1
    >>> _time_to_period(dt.time(10, 00))
    2
    >>> _time_to_period(dt.time(15, 10))
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


def _get_teacher_id(teacher_email: str) -> str:
    """Extract a teacher id from their e-mail address.

    The teachers' id is defined by everything before the domain address of their
    e-mails, transformed to lowercase. The function removes both punctuation and
    numbers from the teacher's e-mail, preventing

    >>> _get_teacher_id("alan-turing@linux.ime.usp.br")
    'alan_turing'
    >>> _get_teacher_id("AlanTuring22@google.com")
    'alanturing'
    """
    teacher_email = teacher_email.lower()
    teacher_email = re.sub(r"[0-9.]", "", teacher_email)
    teacher_email = teacher_email.replace("-", "_")
    return teacher_email[: teacher_email.find("@")]


def _get_fixed_classes(fixed_classes_input: str) -> set[ScheduleTimeslot]:
    """Extract the fixed classes of a course from the input string.

    Examples of valid fixed classes inputs:

    + 3a 08:00-09:40 5a 10:00-11:40

        2 fixed classes on the week, one on Tuesdays from 8:00 to 9:40 and
        one on Thursdays from 10:00 to 11:40.

    + 6a 12:00-13:00

        One fixed classe on the week, on Friday from 12:00 to 13:00

    + 2a 16:00 4a 7:40-10:00

        Two fixed classes on the week, one on Mondays from 16:00 to 17:40 (IME
        classes have 1:40 hour classes), and the other on Wednesday from 7:40 to
        10:00.
    """
    # Captures the triplet [weekday, class start time, class end time (if present)]
    FIXED_CLASS_REGEX = r"([2-6])a ([0-2][0-9]:[0-5][0-9])(-[0-2][0-9]:[0-5][0-9])?"
    fixed_classes = set()
    for weekday, start_time, end_time in re.findall(
        FIXED_CLASS_REGEX, fixed_classes_input
    ):
        # TODO: parse correctly Saturday and Sunday
        weekday = int(weekday) - 1  # weekdays on the scheduler are repr. [1-7]
        periods = set()

        start_time = dt.datetime.strptime(start_time, "%H:%M")
        start_period = _time_to_period(start_time.time())
        if start_period != -1:
            periods.add(start_period)

        if end_time:
            end_time = end_time[1:]  # remove '-' prefix
            end_time = dt.datetime.strptime(end_time, "%H:%M")
        else:
            end_time = start_time + dt.timedelta(hours=1, minutes=40)

        end_period = _time_to_period(end_time.time())
        if end_period != -1:
            periods.add(end_period)

        for period in periods:
            fixed_classes.add(ScheduleTimeslot(weekday, period))
    return fixed_classes


def ime_parse_workload(workload_file: io.TextIOWrapper) -> list[CourseData]:
    """
    Parse a CSV file containing the semester workload and extract the
    corresponding CourseData.
    """
    courses = []
    csv_reader = csv.reader(workload_file)
    _ = next(csv_reader)  # remove header
    for row in csv_reader:
        row = [value.strip() for value in row]
        fixed_classes = _get_fixed_classes(row[5])
        teacher_id = _get_teacher_id(row[7])
        for course_id in row[0].split("/"):
            course_id = course_id.lower()
            if row[2]:
                group = row[2]
            elif course_id[3] != "0":
                group = "BCC_POS"
            else:
                group = "BCC"
            courses.append(CourseData(course_id, fixed_classes, group, teacher_id))
    return courses


def ime_parse_schedule(schedule_file: io.TextIOWrapper) -> list[TeacherData]:
    """
    Parse a CSV file containing the teachers' schedule and extract the
    corresponding TeacherData.
    """
    teachers = []
    csv_reader = csv.reader(schedule_file)
    _ = next(csv_reader)  # remove header
    for row in csv_reader:
        row = [value.strip() for value in row]
        teacher_id = _get_teacher_id(row[1])

        preferred_time: set[ScheduleTimeslot] = set()
        for i in range(2, 7):
            preferred_time = preferred_time.union(_get_timeslots(i - 1, row[i]))

        available_time = _generate_full_availability()
        for i in range(7, 12):
            available_time -= _get_timeslots(i - 6, row[i])

        teachers.append(TeacherData(teacher_id, available_time, preferred_time))
    return teachers
