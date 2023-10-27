"""Common dataclasses/functions used throughout the models."""
from __future__ import annotations

import datetime as dt
from enum import IntEnum

from cattrs import Converter

CONVERTER = Converter(prefer_attrib_converters=True)
"""The default converter used while parsing."""


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
    NIGHT_1 = 4
    NIGHT_2 = 5

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
            case Period.NIGHT_1:
                return "19:20 - 21:00"
            case Period.NIGHT_2:
                return "21:10 - 22:50"

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

        >>> Period.intersections(dt.time(19, 0), dt.time(21, 40))
        [<Period.NIGHT_1: 4>, <Period.NIGHT_2: 5>]
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
        if start <= dt.time(19, 20) < end or start < dt.time(21, 0) <= end:
            intersections.append(Period.NIGHT_1)
        if start <= dt.time(21, 10) < end or start < dt.time(22, 50) <= end:
            intersections.append(Period.NIGHT_2)
        return intersections


class PartOfDay(IntEnum):
    """Parts of the day that courses can be scheduled."""

    MORNING = 0
    AFTERNOON = 1
    NIGHT = 2

    def __str__(self) -> str:
        """Convert parts of the day into strings."""
        match self:
            case PartOfDay.MORNING:
                return "morning"
            case PartOfDay.AFTERNOON:
                return "afternoon"
            case PartOfDay.NIGHT:
                return "night"

    @classmethod
    def from_str(cls, input: str) -> set[PartOfDay]:
        """Convert a text representation of a part of the day into a set of PartOfDay.

        Value mappings for `MORNING`:

        - "morning"
        - "manhã"
        - "manha"
        - "M"

        Value mappings for `AFTERNOON`:

        - "afternoon"
        - "tarde"
        - "T"
        - "A"

        Value mappings for `NIGHT`:

        - "night"
        - "noite"
        - "N"

        Special case: value mappings for both morning and afternoon:

        - "integral"
        - "I"

        Raises a `ValueError` if the string is not any of the above.
        """
        match input.strip().lower():
            case "morning" | "manhã" | "manha" | "m":
                return {cls.MORNING}
            case "afternoon" | "tarde" | "t" | "a":
                return {cls.AFTERNOON}
            case "night" | "noite" | "n":
                return {cls.NIGHT}
            case "integral" | "i":
                return {cls.MORNING, cls.AFTERNOON}
            case _:
                raise ValueError(f"invalid part of the day: {input}.")
