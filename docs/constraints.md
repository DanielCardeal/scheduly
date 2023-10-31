# Constraints

This is a reference page describing in details how constraints work, which rules
are already built into the scheduler and how can you change them into your
institution needs.

To get an overview of how constraints work and how the scheduler uses the
different types of rules to generate search for the best schedule, please refer
to [scheduling 101](docs/scheduling_101.md).

## Hard constraints

`scheduly` provides the following hard constraints by default:

| Name                                                              | Description                                                                                                   |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| [minimum_spacing](src/asp/hard/minimum_spacing.lp)                | Prevents the scheduler to schedule classes of the same course/offering less than `minimum_spacing` days apart |
| [no_obligatory_conflicts](src/as/hard/no_obligatory_conflicts.lp) | Ensures obligatory courses of the same ideal period do not conflict with each other (only for "BCC".          |
| [no_same_day](src/asp/hard/no_same_day.lp)                        | Don't schedule two classes of the same course/offering in the same day.                                       |
| [no_split_double](src/asp/hard/no_split_double.lp)                | Don't allow double classes to be split in different parts of the day.                                         |

## Soft constraints

The default soft constraints are:

| Name                                                                   | Description                                                                                       |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| [avoid_all_conflicts](src/asp/soft/avoid_all_conflicts.lp)             | Avoid all conflicts                                                                               |
| [early_classes](src/asp/soft/early_classes.lp)                         | Penalize scheduling classes in the afternoon/night                                                |
| [maximum_spacing](src/asp/soft/maximum_spacing.lp)                     | Avoid scheduling classes more than `maximum_spacing` days apart                                   |
| [no_curriculum_conflicts](src/asp/soft/no_curriculum_conflicts.lp)     | Avoid conflicts between classes of the same curriculum                                            |
| [no_different_parts_of_day](src/asp/soft/no_different_parts_of_day.lp) | Penalize scheduling classes from a course/offering in different periods of the day                |
| [no_friday_afternoon](src/asp/soft/no_friday_afternoon.lp)             | Don't schedule BCC classes on Friday after lunch                                                  |
| [science_and_statistics](src/asp/soft/science_and_statistics.lp)       | Avoid conflicts between sciences/statistics classes and obligatory classes of ideal semester >= 2 |
| [teacher_preferences](src/asp/soft/teacher_preferences.lp)             | Avoid scheduling classes outside the teachers' preferred teaching periods                         |
