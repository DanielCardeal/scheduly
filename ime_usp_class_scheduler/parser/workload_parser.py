import csv
import datetime as dt
import io
import re

from ime_usp_class_scheduler.parser import CourseData, ScheduleTimeslot

from .main import get_teacher_id, time_to_period


def get_fixed_classes(fixed_classes_input: str) -> list[ScheduleTimeslot]:
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
    for (weekday, start_time, end_time) in re.findall(FIXED_CLASS_REGEX,
                                                      fixed_classes_input):
        weekday = int(weekday) - 1  # weekdays on the scheduler are repr. [1-5]
        periods = set()

        start_time = dt.datetime.strptime(start_time, "%H:%M")
        start_period = time_to_period(start_time.time())
        if start_period != -1:
            periods.add(start_period)

        if end_time:
            end_time = end_time[1:]  # remove '-' prefix
            end_time = dt.datetime.strptime(end_time, "%H:%M")
        else:
            end_time = start_time + dt.timedelta(hours=1, minutes=40)

        end_period = time_to_period(end_time.time())
        if end_period != -1:
            periods.add(end_period)

        for period in periods:
            fixed_classes.add(ScheduleTimeslot(weekday, period))
    return fixed_classes


def parse_workload(workload_file: io.TextIOWrapper) -> list[CourseData]:
    """
    Parse a CSV file containing the semester workload and extract the
    corresponding CourseData.
    """
    courses = []
    csv_reader = csv.reader(workload_file)
    # TODO: add check_header function to assert compatibility with the
    # parser
    _ = next(csv_reader)  # remove header
    for row in csv_reader:
        row = [value.strip() for value in row]
        fixed_classes = get_fixed_classes(row[5])
        teacher_id = get_teacher_id(row[7])
        for course_id in row[0].split("/"):
            course_id = course_id.lower()
            if row[2]:
                group = row[2]
            elif course_id[3] != "0":
                group = "BCC_POS"
            else:
                group = "BCC"
            courses.append(
                CourseData(course_id, fixed_classes, group, teacher_id))
    return courses
