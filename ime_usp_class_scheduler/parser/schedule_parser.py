import csv
import datetime as dt
import io

from .main import ScheduleTimeslot, TeacherData, get_teacher_id, time_to_period


def generate_full_availability() -> set[ScheduleTimeslot]:
    """Generate a set with all the possible timeslots."""
    return set(
        ScheduleTimeslot(w, p) for w in range(1, 5) for p in range(1, 4))


def get_timeslots(weekday: int, input: str) -> set[ScheduleTimeslot]:
    """Extract timeslots for a given weekday using the time information stored
    in the input string. Only the starting periods are considered.

    Example:

    >>> get_weekday_timeslots(2, "8:00-10:00;14:00-16:00")
    {ScheduleTimeslot(2, 1), ScheduleTimeslot(2, 3)}
    """
    if not input:
        return set()

    preferred_time = set()
    for time_range in input.split(";"):
        start_time = time_range.split("-")[0]
        time = dt.datetime.strptime(start_time, "%H:%M").time()
        period = time_to_period(time)
        preferred_time.add(ScheduleTimeslot(weekday, period))

    return preferred_time


def parse_schedule(schedule_file: io.TextIOWrapper) -> list[TeacherData]:
    """
    Parse a CSV file containing the teachers' schedule and extract the
    corresponding TeacherData.
    """
    teachers = []
    csv_reader = csv.reader(schedule_file)
    # TODO: add check_header function to assert compatibility with the
    # parser
    _ = next(csv_reader)  # remove header
    for row in csv_reader:
        row = [value.strip() for value in row]
        teacher_id = get_teacher_id(row[1])

        preferred_time = set()
        for i in range(2, 7):
            preferred_time = preferred_time.union(get_timeslots(i - 1, row[i]))

        available_time = generate_full_availability()
        for i in range(7, 12):
            available_time -= get_timeslots(i - 6, row[i])

        teachers.append(TeacherData(teacher_id, available_time,
                                    preferred_time))
    return teachers
