import datetime as dt

from ime_usp_class_scheduler.model import CourseData, ScheduleTimeslot, TeacherData
from ime_usp_class_scheduler.model.parsers.required import (
    _generate_full_availability,
    _get_teacher_id,
    _time_to_period,
    ime_parse_schedule,
    ime_parse_workload,
)


def test_time_to_period():
    assert _time_to_period(dt.time(7, 40)) == -1
    assert _time_to_period(dt.time(8, 34)) == 1
    assert _time_to_period(dt.time(10, 00)) == 2
    assert _time_to_period(dt.time(15, 10)) == 3
    assert _time_to_period(dt.time(19, 00)) == -1


def test_get_teacher_id():
    assert _get_teacher_id("alan-turing@linux.ime.usp.br") == "alan_turing"
    assert _get_teacher_id("13alan-turing@ime.usp.br") == "alan_turing"
    assert _get_teacher_id("AlanTuring22@google.com") == "alanturing"


def test_parse_workload():
    TEST_FILE = "tests/data/test_workload.csv"
    expected = [
        CourseData(
            "mac0329",
            {ScheduleTimeslot(2, 1), ScheduleTimeslot(4, 2)},
            "BCC",
            "nina",
        ),
        CourseData("mac0499", set(), "BCC", "nina"),
        CourseData("mac0101", {ScheduleTimeslot(2, 3)}, "BCC", "leliane"),
        CourseData(
            "mac0321",
            {ScheduleTimeslot(5, 1), ScheduleTimeslot(5, 2)},
            "Poli EC - PCS 2",
            "ddm",
        ),
        CourseData(
            "mac0113",
            {
                ScheduleTimeslot(3, 1),
                ScheduleTimeslot(5, 1),
                ScheduleTimeslot(5, 2),
            },
            "FEA 1",
            "pmiranda",
        ),
        CourseData("mac2166", {ScheduleTimeslot(5, 4)}, "Poli Web C", "fujita"),
        CourseData("mac0113", set(), "FEA 1", "hirata"),
        CourseData("mac0320", set(), "BCC", "yoshiko"),
        CourseData("mac5770", set(), "BCC_POS", "yoshiko"),
        CourseData("mac0327", set(), "BCC", "mksilva"),
    ]
    with open(TEST_FILE) as workload_file:
        assert ime_parse_workload(workload_file) == expected


def test_parse_schedule():
    TEST_FILE = "tests/data/test_schedule.csv"
    expected = [
        TeacherData(
            "pmiranda",
            _generate_full_availability()
            - {
                # Monday
                ScheduleTimeslot(1, 1),
                ScheduleTimeslot(1, 2),
                # Thursday
                ScheduleTimeslot(4, 3),
            },
            preferred_time={
                # Wednesday
                ScheduleTimeslot(3, 1),
                ScheduleTimeslot(3, 2),
                ScheduleTimeslot(3, 3),
                ScheduleTimeslot(3, 4),
                # Thursday
                ScheduleTimeslot(4, 1),
                ScheduleTimeslot(4, 2),
                # Friday
                ScheduleTimeslot(5, 1),
                ScheduleTimeslot(5, 2),
                ScheduleTimeslot(5, 3),
                ScheduleTimeslot(5, 4),
            },
        ),
        TeacherData(
            "egbirgin",
            _generate_full_availability()
            - {
                # Monday
                ScheduleTimeslot(1, 3),
                ScheduleTimeslot(1, 4),
                # Tuesday
                ScheduleTimeslot(2, 3),
                ScheduleTimeslot(2, 4),
                # Wednesday
                ScheduleTimeslot(3, 3),
                ScheduleTimeslot(3, 4),
                # Thursday
                ScheduleTimeslot(4, 3),
                ScheduleTimeslot(4, 4),
                # Friday
                ScheduleTimeslot(5, 1),
                ScheduleTimeslot(5, 2),
                ScheduleTimeslot(5, 3),
                ScheduleTimeslot(5, 4),
            },
            preferred_time={
                # Tuesday
                ScheduleTimeslot(2, 1),
                ScheduleTimeslot(2, 2),
                # Thursday
                ScheduleTimeslot(4, 1),
                ScheduleTimeslot(4, 2),
            },
        ),
        TeacherData(
            "rt",
            _generate_full_availability()
            - {
                # Monday
                ScheduleTimeslot(1, 1),
                # Tuesday
                ScheduleTimeslot(2, 1),
                # Wednesday
                ScheduleTimeslot(3, 1),
                # Thursday
                ScheduleTimeslot(4, 1),
                # Friday
                ScheduleTimeslot(5, 1),
                ScheduleTimeslot(5, 2),
                ScheduleTimeslot(5, 3),
                ScheduleTimeslot(5, 4),
            },
            preferred_time={
                # Monday
                ScheduleTimeslot(1, 2),
                ScheduleTimeslot(1, 3),
                ScheduleTimeslot(1, 4),
                # Tuesday
                ScheduleTimeslot(2, 2),
                ScheduleTimeslot(2, 3),
                ScheduleTimeslot(2, 4),
                # Wednesday
                ScheduleTimeslot(3, 2),
                ScheduleTimeslot(3, 3),
                ScheduleTimeslot(3, 4),
                # Thursday
                ScheduleTimeslot(4, 2),
                ScheduleTimeslot(4, 3),
                ScheduleTimeslot(4, 4),
            },
        ),
    ]
    with open(TEST_FILE) as schedule_file:
        assert ime_parse_schedule(schedule_file) == expected
