from __future__ import annotations

import datetime as dt
from enum import IntEnum


class Weekday(IntEnum):
    """Days of the week as they are represented inside scheduler."""

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4

    def __str__(self) -> str:
        match self:
            case Weekday.MONDAY:
                return "Monday"
            case Weekday.TUESDAY:
                return "Tuesday"
            case Weekday.WEDNESDAY:
                return "Wednesday"
            case Weekday.THURSDAY:
                return "Thursday"
            case Weekday.FRIDAY:
                return "Friday"

    @classmethod
    def from_str(cls, s: str) -> Weekday:
        """Convert a text representation of an Weekday into the corresponding weekday.

        Raises a `ValueError` if `s` is an invalid string.

        `s` can be one of:

        - mon, seg -> Weekday.Monday
        - tue, ter -> Weekday.Tuesday
        - wed, qua -> Weekday.Wednesday
        - thu, qui -> Weekday.Thursday
        - fri, sex -> Weekday.Friday
        """
        match s.strip().lower():
            case "mon" | "seg":
                return Weekday.MONDAY
            case "tue" | "ter":
                return Weekday.TUESDAY
            case "wed" | "qua":
                return Weekday.WEDNESDAY
            case "thu" | "qui":
                return Weekday.THURSDAY
            case "fri" | "sex":
                return Weekday.FRIDAY
            case _:
                raise ValueError(f"Impossible to convert string '{s}' to a weekday.")


class Period(IntEnum):
    """Class periods as they are represented inside the scheduler."""

    MORNING_1 = 0
    MORNING_2 = 1
    AFTERNOON_1 = 2
    AFTERNOON_2 = 3

    def __str__(self) -> str:
        match self:
            case Period.MORNING_1:
                return "8:00 - 9:40"
            case Period.MORNING_2:
                return "10:00 - 11:40"
            case Period.AFTERNOON_1:
                return "14:00 - 15:40"
            case Period.AFTERNOON_2:
                return "16:00 - 17:40"

    @classmethod
    def intersections(cls, start: dt.time, end: dt.time) -> list[Period]:
        """
        Return the list of periods that are intersected by `start` and `end`.

        >>> Period.intersections(dt.time(8, 0), dt.time(9, 0))
        [<Period.MORNING_1: 0>]

        >>> Period.intersections(dt.time(7, 40), dt.time(10, 10))
        [<Period.MORNING_1: 0>, <Period.MORNING_2: 1>]

        >>> Period.intersections(dt.time(13, 0), dt.time(16, 0))
        [<Period.AFTERNOON_1: 2>]

        >>> Period.intersections(dt.time(11, 30), dt.time(12, 30))
        [<Period.MORNING_2: 1>]

        >>> Period.intersections(dt.time(19, 0), dt.time(20, 40))
        []
        """
        if end < start:
            start, end = end, start

        intersections = []
        if start <= dt.time(8, 0) < end or start < dt.time(9, 40) <= end:
            intersections.append(Period.MORNING_1)
        if start <= dt.time(10, 0) < end or start < dt.time(11, 40) <= end:
            intersections.append(Period.MORNING_2)
        if start <= dt.time(14, 0) < end or start < dt.time(15, 40) <= end:
            intersections.append(Period.AFTERNOON_1)
        if start <= dt.time(16, 0) < end or start < dt.time(17, 40) <= end:
            intersections.append(Period.AFTERNOON_2)
        return intersections
