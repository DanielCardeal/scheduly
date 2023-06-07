import datetime as dt

import pytest

from ime_usp_class_scheduler.parser import CourseData, ScheduleTimeslot
from ime_usp_class_scheduler.parser.workload_parser import (
    WorkloadParserException, get_teacher_id, parse_workload, time_to_period)


class TestWorkloadParser:

    def test_time_to_period(self):
        assert time_to_period(dt.time(7, 40)) == -1
        assert time_to_period(dt.time(8, 34)) == 1
        assert time_to_period(dt.time(10, 00)) == 2
        assert time_to_period(dt.time(15, 10)) == 3
        assert time_to_period(dt.time(19, 00)) == -1

    def test_get_teacher_id(self):
        assert get_teacher_id("alan-turing@linux.ime.usp.br") == "alan_turing"
        assert get_teacher_id("AlanTuring22@google.com") == "alanturing22"
        with pytest.raises(WorkloadParserException):
            get_teacher_id("13alan-turing@ime.usp.br")

    def test_parse_workload(self):
        TEST_FILE = "tests/data/test_workload.csv"
        expected = [
            CourseData(
                "mac0329",
                {ScheduleTimeslot(2, 1),
                 ScheduleTimeslot(4, 2)},
                "BCC",
                "nina",
            ),
            CourseData("mac0499", set(), "BCC", "nina"),
            CourseData("mac0101", {ScheduleTimeslot(2, 3)}, "BCC", "leliane"),
            CourseData(
                "mac0321",
                {ScheduleTimeslot(5, 1),
                 ScheduleTimeslot(5, 2)},
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
            CourseData("mac2166", {ScheduleTimeslot(5, 4)}, "Poli Web C",
                       "fujita"),
            CourseData("mac0113", set(), "FEA 1", "hirata"),
            CourseData("mac0320", set(), "BCC", "yoshiko"),
            CourseData("mac5770", set(), "BCC_POS", "yoshiko"),
            CourseData("mac0327", set(), "BCC", "mksilva"),
        ]
        with open(TEST_FILE) as workload_file:
            assert parse_workload(workload_file) == expected
