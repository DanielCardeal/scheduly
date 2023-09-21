from ime_usp_class_scheduler.model.data import (
    CourseData,
    CurriculaCoursesData,
    CurriculaData,
    JointClassData,
    ScheduleTimeslot,
    TeacherData,
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
            {ScheduleTimeslot(2, 1), ScheduleTimeslot(4, 2)},
        ),
        WorkloadData("mac0499", "nina", "BCC", set()),
        WorkloadData("mac0101", "leliane", "BCC", {ScheduleTimeslot(2, 3)}),
        WorkloadData(
            "mac0321",
            "ddm",
            "Poli EC - PCS 2",
            {ScheduleTimeslot(5, 1), ScheduleTimeslot(5, 2)},
        ),
        WorkloadData(
            "mac0113",
            "pmiranda",
            "FEA 1",
            {
                ScheduleTimeslot(3, 1),
                ScheduleTimeslot(5, 1),
                ScheduleTimeslot(5, 2),
            },
        ),
        WorkloadData("mac2166", "fujita", "Poli Web C", {ScheduleTimeslot(5, 4)}),
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
            generate_full_availability()
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
            generate_full_availability()
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
