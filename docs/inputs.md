# Inputs

As described in the [getting started](docs/getting_started.md) page, there are
four input files that are used to add information into the scheduler: courses,
curriculum, schedules and workload. This docs page describes thoroughly the
structure of each of them, explaining what values are expected in each table.

## Types

Here are some details about some of the types that might appear in the input
tables:

1. String: any text-like value, such as "Computer Science" or "courseABC".

2. Boolean: strings that can be interpreted as `true` or `false`. Examples are:

   - `true` values: yes, sim (pt-BR for yes), Y, True, 1.
   - `false` values: no, não (pt-BR for no), N, False, 0.

3. Number: decimal numbers, such as 10 and 2024.

4. Time range: a text that describes one (or multiple) spans of time. As they
   are more easily grasp in practice, let's look for some examples:

   - "fri 12:00-13:00" → one interval of time on Fridays between 12:00 and
     13:00.

   - "tue 08:00 - 09:40; thu 10:00 - 11:40" → two timespans, one on Tuesdays
     from 8:00 to 9:40 and one on Thursdays from 10:00 to 11:40:

   - "qua 7:00-10:00 14:00-16:00" → two timespans on Wednesdays ("qua" is an
     abbreviation for Wednesday in pt-BR), one from 7 to 10AM and other from 2
     to 4 PM.

5. Time of the day: a text that describes a time of the day (morning, afternnon
   or night). Examples

   - Morning: "M", "morning", "manhã" (pt-BR for morning)
   - Afternoon: "A", "afternoon", "tarde" (pt-BR for afternoon), T
   - Night: "N", "night", "noite" (pt-BR for morning)
   - Integral (morning + afternoon): "I", "integral"

## Inputs

The following sections describe the column names, expected types and meaning
inside the scheduler. Columns with `default` values can be empty.

Extra columns are allowed in any of the tables, but will be ignored by the
scheduler. This can be useful to add organizational information without the need
to create separate tables.

> **IMPORTANT:** Column names should be exactly as described below. Also, all
> columns are required, even if all their values are empty.

### Courses

Used for setting general information about courses in the scheduler.

| Value            | Type                       | Meaning                                                                                  |
| ---------------- | -------------------------- | ---------------------------------------------------------------------------------------- |
| `course_id`      | String (not empty)         | A name that can be used to uniquely identify a course in the scheduler                   |
| `num_classes`    | Number > 0                 | Number of weekly classes of a course. Must be greater than 0.                            |
| `ideal_semester` | Number >= 0                | Which is the ideal semester for students to take the course                              |
| `is_double`      | Boolean (default: `false`) | Are the courses' classes double, i.e., scheduled in consecutive periods on the same day? |
| `is_undergrad`   | Boolean (default: `false`) | Identifies a course as an undergrad course                                               |

### Curriculum

Information about educational curricula in the institution.

| Value          | Type                       | Meaning                                                                    |
| -------------- | -------------------------- | -------------------------------------------------------------------------- |
| `course_id`    | String (not empty)         | A name that can be used to uniquely identify a course in the scheduler     |
| `curricula_id` | String (not empty)         | A name that can be used to uniquely identify a curriculum in the scheduler |
| `is_required`  | Boolean (default: `false`) | Is the course required to complete the curricula?                          |

### Schedules

Information about teachers' availability and preferred teaching periods.

| Value         | Type               | Meaning                                                                                                                                           |
| ------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `teacher_id`  | String (not empty) | A name that can be used to uniquely identify a teacher. If it is an email, the scheduler will use everything prior to the @ as the ID.            |
| `unavailable` | Time range         | Teacher **unavailable** teaching periods. If empty, assumes that the teacher is available to teach in every possible time period.                 |
| `preferred`   | Time range         | Teacher **preferred** teaching periods. If empty, assumes that the teacher makes no distinction between teaching all of theirs available periods. |

### Workload

Course offering information.

| Value            | Type                           | Meaning                                                                                                                                              |
| ---------------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `courses_id`     | String (not empty)             | A comma separated list of strings that can be used to uniquely identify courses.                                                                     |
| `teachers_id`    | String (not empty)             | A comma separated list of strings that can be used to uniquely identify a teacher (if IDs are emails, will trim everything prior to the @ symbol).   |
| `offering_group` | String (not empty)             | A string that uniquely identifies an offering of the course. Classes of the same course but with different offering groups are scheduled separately. |
| `course_name`    | String                         | The name of the course                                                                                                                               |
| `class_period`   | Time of the day (default: "I") | Time of the day to schedule classes of a given course/offering.                                                                                      |
| `fixed_classes`  | Time range                     | Adds fixed classes of the course/offering in the teaching periods that intersect the time range.                                                     |
