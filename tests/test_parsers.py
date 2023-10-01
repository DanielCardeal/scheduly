from ime_usp_class_scheduler.model.data import (
    CourseData,
    CurriculaCoursesData,
    CurriculaData,
    JointClassData,
    Period,
    ScheduleTimeslot,
    TeacherData,
    Weekday,
    WorkloadData,
    generate_full_availability,
)
from ime_usp_class_scheduler.parser import (
    ime_parse_schedule,
    ime_parse_workload,
    parse_courses,
    parse_curricula,
    parse_joint,
)


def test_parse_workload() -> None:
    TEST_FILE = "tests/data/test_workload.csv"
    expected = [
        WorkloadData(
            "mac0329",
            "nina",
            "BCC",
            {
                ScheduleTimeslot(Weekday(1), Period(0)),
                ScheduleTimeslot(Weekday(3), Period(1)),
            },
        ),
        WorkloadData("mac0499", "nina", "BCC", set()),
        WorkloadData(
            "mac0101", "leliane", "BCC", {ScheduleTimeslot(Weekday(1), Period(2))}
        ),
        WorkloadData(
            "mac0321",
            "ddm",
            "Poli EC - PCS 2",
            {
                ScheduleTimeslot(Weekday(4), Period(0)),
                ScheduleTimeslot(Weekday(4), Period(1)),
            },
        ),
        WorkloadData(
            "mac0113",
            "pmiranda",
            "FEA 1",
            {
                ScheduleTimeslot(Weekday(2), Period(0)),
                ScheduleTimeslot(Weekday(4), Period(0)),
                ScheduleTimeslot(Weekday(4), Period(1)),
            },
        ),
        WorkloadData(
            "mac2166", "fujita", "Poli Web C", {ScheduleTimeslot(Weekday(4), Period(3))}
        ),
        WorkloadData("mac0113", "hirata", "FEA 1", set()),
        WorkloadData("mac0320", "yoshiko", "BCC", set()),
        WorkloadData("mac5770", "yoshiko", "BCC_POS", set()),
        WorkloadData("mac0327", "mksilva", "BCC", set()),
    ]
    with open(TEST_FILE) as workload_file:
        assert ime_parse_workload(workload_file) == expected


def test_parse_schedule() -> None:
    TEST_FILE = "tests/data/test_schedule.csv"
    expected = [
        TeacherData(
            "pmiranda",
            generate_full_availability()
            - {
                # Monday
                ScheduleTimeslot(Weekday(0), Period(0)),
                ScheduleTimeslot(Weekday(0), Period(1)),
                # Thursday
                ScheduleTimeslot(Weekday(3), Period(2)),
            },
            preferred_time={
                # Wednesday
                ScheduleTimeslot(Weekday(2), Period(0)),
                ScheduleTimeslot(Weekday(2), Period(1)),
                ScheduleTimeslot(Weekday(2), Period(2)),
                ScheduleTimeslot(Weekday(2), Period(3)),
                # Thursday
                ScheduleTimeslot(Weekday(3), Period(0)),
                ScheduleTimeslot(Weekday(3), Period(1)),
                # Friday
                ScheduleTimeslot(Weekday(4), Period(0)),
                ScheduleTimeslot(Weekday(4), Period(1)),
                ScheduleTimeslot(Weekday(4), Period(2)),
                ScheduleTimeslot(Weekday(4), Period(3)),
            },
        ),
        TeacherData(
            "egbirgin",
            generate_full_availability()
            - {
                # Monday
                ScheduleTimeslot(Weekday(0), Period(2)),
                ScheduleTimeslot(Weekday(0), Period(3)),
                # Tuesday
                ScheduleTimeslot(Weekday(1), Period(2)),
                ScheduleTimeslot(Weekday(1), Period(3)),
                # Wednesday
                ScheduleTimeslot(Weekday(2), Period(2)),
                ScheduleTimeslot(Weekday(2), Period(3)),
                # Thursday
                ScheduleTimeslot(Weekday(3), Period(2)),
                ScheduleTimeslot(Weekday(3), Period(3)),
                # Friday
                ScheduleTimeslot(Weekday(4), Period(0)),
                ScheduleTimeslot(Weekday(4), Period(1)),
                ScheduleTimeslot(Weekday(4), Period(2)),
                ScheduleTimeslot(Weekday(4), Period(3)),
            },
            preferred_time={
                # Tuesday
                ScheduleTimeslot(Weekday(1), Period(0)),
                ScheduleTimeslot(Weekday(1), Period(1)),
                # Thursday
                ScheduleTimeslot(Weekday(3), Period(0)),
                ScheduleTimeslot(Weekday(3), Period(1)),
            },
        ),
        TeacherData(
            "rt",
            generate_full_availability()
            - {
                # Monday
                ScheduleTimeslot(Weekday(0), Period(0)),
                # Tuesday
                ScheduleTimeslot(Weekday(1), Period(0)),
                # Wednesday
                ScheduleTimeslot(Weekday(2), Period(0)),
                # Thursday
                ScheduleTimeslot(Weekday(3), Period(0)),
                # Friday
                ScheduleTimeslot(Weekday(4), Period(0)),
                ScheduleTimeslot(Weekday(4), Period(1)),
                ScheduleTimeslot(Weekday(4), Period(2)),
                ScheduleTimeslot(Weekday(4), Period(3)),
            },
            preferred_time={
                # Monday
                ScheduleTimeslot(Weekday(0), Period(1)),
                ScheduleTimeslot(Weekday(0), Period(2)),
                ScheduleTimeslot(Weekday(0), Period(3)),
                # Tuesday
                ScheduleTimeslot(Weekday(1), Period(1)),
                ScheduleTimeslot(Weekday(1), Period(2)),
                ScheduleTimeslot(Weekday(1), Period(3)),
                # Wednesday
                ScheduleTimeslot(Weekday(2), Period(1)),
                ScheduleTimeslot(Weekday(2), Period(2)),
                ScheduleTimeslot(Weekday(2), Period(3)),
                # Thursday
                ScheduleTimeslot(Weekday(3), Period(1)),
                ScheduleTimeslot(Weekday(3), Period(2)),
                ScheduleTimeslot(Weekday(3), Period(3)),
            },
        ),
    ]
    with open(TEST_FILE) as schedule_file:
        assert ime_parse_schedule(schedule_file) == expected


def test_parse_curricula() -> None:
    CURRICULA_FILE = "tests/data/test_curricula.csv"
    COMPONENTS_FILE = "tests/data/test_curricula_components.csv"
    expected = [
        CurriculaData(
            "data_science",
            "BCC",
            {
                CurriculaCoursesData("MACXXXX", True),
                CurriculaCoursesData("MACYYYY", False),
            },
        ),
        CurriculaData("statistics", "BCC", {CurriculaCoursesData("MACYYYY", True)}),
    ]
    with open(CURRICULA_FILE) as cur_f, open(COMPONENTS_FILE) as comp_f:
        assert parse_curricula(cur_f, comp_f) == expected


def test_parse_courses() -> None:
    TEST_FILE = "tests/data/test_courses.csv"
    expected = [
        CourseData("MACXXXX", 2, False, "BCC", 1),
        CourseData("MACYYYY", 4, True, "POS", -1),
    ]
    with open(TEST_FILE) as f:
        assert parse_courses(f) == expected


def test_parse_joint() -> None:
    JOINT_FILE = "tests/data/test_joint.csv"
    expected = [JointClassData("MACXXXX", "MACYYYY")]
    with open(JOINT_FILE) as f:
        assert parse_joint(f) == expected
