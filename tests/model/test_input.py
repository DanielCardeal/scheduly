from io import StringIO
from textwrap import dedent
from typing import TypeVar

import pytest

from ime_usp_class_scheduler.model.common import Period, Weekday
from ime_usp_class_scheduler.model.input import (
    AspInput,
    CourseData,
    CurriculumData,
    ParserException,
    ScheduleTimeslot,
    TeacherScheduleData,
    WorkloadData,
    _boolean_converter,
    _courses_ids_converter,
    _csv_to_schema,
    _schedule_timeslots_converter,
)

T = TypeVar("T", bound=AspInput)


class TestParsers:
    @pytest.mark.parametrize(
        "schema,test_input,output",
        [
            (
                CourseData,
                """\
            course_id,num_classes,ideal_semester,is_undergrad,is_double
            mac111,3,0,y,sim
            mac222,2,3,,não
             """,
                [
                    CourseData(
                        course_id="mac111",
                        num_classes=3,
                        ideal_semester=0,
                        is_undergrad=True,
                        is_double=True,
                    ),
                    CourseData(
                        course_id="mac222",
                        num_classes=2,
                        ideal_semester=3,
                    ),
                ],
            ),
            (
                TeacherScheduleData,
                """\
                teacher_id,preferred,unavailable
                profX,mon 10:00;ter 8:00,wed 10:00-16:00;fri 8:00 - 18:00
                profY,,
                """,
                [
                    TeacherScheduleData(
                        teacher_id="profX",
                        preferred={
                            ScheduleTimeslot(Weekday.MONDAY, Period.MORNING_2),
                            ScheduleTimeslot(Weekday.TUESDAY, Period.MORNING_1),
                        },
                        unavailable={
                            ScheduleTimeslot(Weekday.WEDNESDAY, Period.MORNING_2),
                            ScheduleTimeslot(Weekday.WEDNESDAY, Period.AFTERNOON_1),
                            ScheduleTimeslot(Weekday.FRIDAY, Period.MORNING_1),
                            ScheduleTimeslot(Weekday.FRIDAY, Period.MORNING_2),
                            ScheduleTimeslot(Weekday.FRIDAY, Period.AFTERNOON_1),
                            ScheduleTimeslot(Weekday.FRIDAY, Period.AFTERNOON_2),
                        },
                    ),
                    TeacherScheduleData(
                        teacher_id="profY",
                    ),
                ],
            ),
            (
                WorkloadData,
                """\
                courses_id,course_name,offering_group,fixed_classes,teachers_id
                mac111;mac222,Computer science intro,ime,mon 8:00; wed 14:00,profA@ime.usp.br;profB@google.com
                mac333,,,,profC@yahoo.com
                """,
                [
                    WorkloadData(
                        courses_id=["mac111", "mac222"],
                        teachers_id=["profA", "profB"],
                        fixed_classes={
                            ScheduleTimeslot(Weekday.MONDAY, Period.MORNING_1),
                            ScheduleTimeslot(Weekday.WEDNESDAY, Period.AFTERNOON_1),
                        },
                        course_name="Computer science intro",
                        offering_group="ime",
                    ),
                    WorkloadData(
                        courses_id=["mac333"],
                        teachers_id=["profC"],
                    ),
                ],
            ),
            (
                CurriculumData,
                """\
                course_id,curricula_id,is_required
                mac111,systems,não
                mac111,ai,sim
                mac222,ai,
                """,
                [
                    CurriculumData(
                        course_id="mac111",
                        curricula_id="systems",
                        is_required=False,
                    ),
                    CurriculumData(
                        course_id="mac111",
                        curricula_id="ai",
                        is_required=True,
                    ),
                    CurriculumData(
                        course_id="mac222",
                        curricula_id="ai",
                    ),
                ],
            ),
        ],
    )
    def test_succesfull(
        self, schema: type[T], test_input: str, output: list[T]
    ) -> None:
        """Test if wellformed input CSVs are parsed correctly."""
        test_input = dedent(test_input)
        csv_data = StringIO(test_input)
        assert _csv_to_schema(csv_data, schema) == output

    @pytest.mark.parametrize(
        "schema,test_input",
        [
            (
                # Course data without course id
                CourseData,
                """\
                course_id,num_classes,ideal_semester,is_undergrad,is_double
                ,1,0,y,y
                 """,
            ),
            (
                # Course data with invalid num classes
                CourseData,
                """\
                course_id,num_classes,ideal_semester,is_undergrad,is_double
                mac111,-1,0,,
                 """,
            ),
            (
                # Course data with invalid ideal semester
                CourseData,
                """\
                course_id,num_classes,ideal_semester,is_undergrad,is_double
                mac111,1,-1,,
                 """,
            ),
            (
                # Schedule data without course id
                TeacherScheduleData,
                """\
                teacher_id,preferred,unavailable
                ,mon 8:00,mon 10:00
                """,
            ),
            (
                # Workload data without courses ids
                WorkloadData,
                """\
                courses_id,course_name,offering_group,fixed_classes,teachers_id
                ,,,,profA@ime.usp.br
                """,
            ),
            (
                # Workload data with too much courses ids
                WorkloadData,
                """\
                courses_id,course_name,offering_group,fixed_classes,teachers_id
                mac111;mac222;mac333,,,,profA@ime.usp.br
                """,
            ),
            (
                # Workload data without teachers ids
                WorkloadData,
                """\
                courses_id,course_name,offering_group,fixed_classes,teachers_id
                mac111,,,,
                """,
            ),
            (
                # Curricula data without course id
                CurriculumData,
                """\
                course_id,curricula_id,is_required
                ,systems,
                """,
            ),
            (
                # Curricula data without curricula id
                CurriculumData,
                """\
                course_id,curricula_id,is_required
                mac111,,
                """,
            ),
        ],
    )
    def test_failure(self, schema: type[T], test_input: str) -> None:
        """Tests if exceptions are properly raised when a malformed CSV is given."""
        test_input = dedent(test_input)
        csv_data = StringIO(test_input)
        with pytest.raises(ParserException):
            _csv_to_schema(csv_data, schema)


class TestConverters:
    @pytest.mark.parametrize(
        "test_input,output",
        [
            # Empty inputs
            (
                set(),
                set(),
            ),
            (
                "",
                set(),
            ),
            (
                ";;;",
                set(),
            ),
            # Non-empty input
            (
                {ScheduleTimeslot(Weekday.MONDAY, Period.MORNING_1)},
                {ScheduleTimeslot(Weekday.MONDAY, Period.MORNING_1)},
            ),
            (
                "ter 08:00 - 09:40; qui 10:00 - 11:40",
                {
                    ScheduleTimeslot(Weekday.TUESDAY, Period.MORNING_1),
                    ScheduleTimeslot(Weekday.THURSDAY, Period.MORNING_2),
                },
            ),
            (
                "fri 12:00-13:00",
                set(),
            ),
            (
                "mon 16:00; wed 7:40-10:00 14:00 - 16:00",
                {
                    ScheduleTimeslot(Weekday.MONDAY, Period.AFTERNOON_2),
                    ScheduleTimeslot(Weekday.WEDNESDAY, Period.MORNING_1),
                    ScheduleTimeslot(Weekday.WEDNESDAY, Period.AFTERNOON_1),
                },
            ),
        ],
    )
    def test_schedule_timeslots(
        self, test_input: set[ScheduleTimeslot] | str, output: set[ScheduleTimeslot]
    ) -> None:
        """Tests parsing of scheduled timeslots strings."""
        assert _schedule_timeslots_converter(test_input) == output

    @pytest.mark.parametrize(
        "test_input,output",
        [
            # Wellformed
            ("mac0101", ["mac0101"]),
            ("mac0470;mac5856", ["mac0470", "mac5856"]),
            # Bad prefix/suffix
            ("mac0470;mac5856;", ["mac0470", "mac5856"]),
            (";mac0470;mac5856", ["mac0470", "mac5856"]),
            ("mac0470;mac5856;  ", ["mac0470", "mac5856"]),
            # Extra whitespace
            ("   mac0470  ;   mac5856;    ", ["mac0470", "mac5856"]),
        ],
    )
    def test_courses_ids(self, test_input: str, output: list[str]) -> None:
        """Tests parsing of courses id strings."""
        assert _courses_ids_converter(test_input) == output

    @pytest.mark.parametrize(
        "test_input,output",
        [
            (True, True),
            (False, False),
        ]
        + [
            (truthy_string, True)
            for truthy_string in (
                "True",
                "yes",
                "y",
                "sim",
                "s",
                "1",
            )
        ]
        + [
            (falsey_string, False)
            for falsey_string in (
                "",
                "False",
                "no",
                "n",
                "nao",
                "não",
                "0",
            )
        ],
    )
    def test_boolean_converter(self, test_input: bool | str, output: bool) -> None:
        """Tests conversion of boolean strings."""
        assert _boolean_converter(test_input) == output
