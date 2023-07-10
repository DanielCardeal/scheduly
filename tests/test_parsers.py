import datetime as dt

from ime_usp_class_scheduler.parser import (
    CourseData,
    ScheduleTimeslot,
    TeacherData,
    parse_schedule,
    parse_workload,
)
from ime_usp_class_scheduler.parser.schedule_parser import generate_full_availability
from ime_usp_class_scheduler.parser.workload_parser import (
    get_teacher_id,
    time_to_period,
)


def test_time_to_period():
    assert time_to_period(dt.time(7, 40)) == -1
    assert time_to_period(dt.time(8, 34)) == 1
    assert time_to_period(dt.time(10, 00)) == 2
    assert time_to_period(dt.time(15, 10)) == 3
    assert time_to_period(dt.time(19, 00)) == -1


def test_get_teacher_id():
    assert get_teacher_id("alan-turing@linux.ime.usp.br") == "alan_turing"
    assert get_teacher_id("13alan-turing@ime.usp.br") == "alan_turing"
    assert get_teacher_id("AlanTuring22@google.com") == "alanturing"


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
        assert parse_workload(workload_file) == expected


def test_parse_schedule():
    TEST_FILE = "tests/data/test_schedule.csv"
    expected = [
        TeacherData(
            "pmiranda",
            generate_full_availability()
            - {
                # Segunda
                ScheduleTimeslot(1, 1),
                ScheduleTimeslot(1, 2),
                # Quinta
                ScheduleTimeslot(4, 3),
            },
            preferred_time={
                # Quarta
                ScheduleTimeslot(3, 1),
                ScheduleTimeslot(3, 2),
                ScheduleTimeslot(3, 3),
                ScheduleTimeslot(3, 4),
                # Quinta
                ScheduleTimeslot(4, 1),
                ScheduleTimeslot(4, 2),
                # Sexta
                ScheduleTimeslot(5, 1),
                ScheduleTimeslot(5, 2),
                ScheduleTimeslot(5, 3),
                ScheduleTimeslot(5, 4),
            },
        ),
        TeacherData(
            "egbirgin",
            generate_full_availability()
            - {
                # Segunda
                ScheduleTimeslot(1, 3),
                ScheduleTimeslot(1, 4),
                # Terça
                ScheduleTimeslot(2, 3),
                ScheduleTimeslot(2, 4),
                # Quarta
                ScheduleTimeslot(3, 3),
                ScheduleTimeslot(3, 4),
                # Quinta
                ScheduleTimeslot(4, 3),
                ScheduleTimeslot(4, 4),
                # Sexta
                ScheduleTimeslot(5, 1),
                ScheduleTimeslot(5, 2),
                ScheduleTimeslot(5, 3),
                ScheduleTimeslot(5, 4),
            },
            preferred_time={
                # Terça
                ScheduleTimeslot(2, 1),
                ScheduleTimeslot(2, 2),
                # Quinta
                ScheduleTimeslot(4, 1),
                ScheduleTimeslot(4, 2),
            },
        ),
        TeacherData(
            "rt",
            generate_full_availability()
            - {
                # Segunda
                ScheduleTimeslot(1, 1),
                # Terça
                ScheduleTimeslot(2, 1),
                # Quarta
                ScheduleTimeslot(3, 1),
                # Quinta
                ScheduleTimeslot(4, 1),
                # Sexta
                ScheduleTimeslot(5, 1),
                ScheduleTimeslot(5, 2),
                ScheduleTimeslot(5, 3),
                ScheduleTimeslot(5, 4),
            },
            preferred_time={
                # Segunda
                ScheduleTimeslot(1, 2),
                ScheduleTimeslot(1, 3),
                ScheduleTimeslot(1, 4),
                # Terça
                ScheduleTimeslot(2, 2),
                ScheduleTimeslot(2, 3),
                ScheduleTimeslot(2, 4),
                # Quarta
                ScheduleTimeslot(3, 2),
                ScheduleTimeslot(3, 3),
                ScheduleTimeslot(3, 4),
                # Quinta
                ScheduleTimeslot(4, 2),
                ScheduleTimeslot(4, 3),
                ScheduleTimeslot(4, 4),
            },
        ),
    ]
    with open(TEST_FILE) as schedule_file:
        assert parse_schedule(schedule_file) == expected
