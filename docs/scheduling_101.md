# Scheduling 101

In this page, you will be learning how to use and configure the scheduler to
your institutional needs.

## Inputs

In order to create a schedule, the program first needs to know what it is
scheduling in the first place. This means that we need to somehow input
information about courses, teachers, classes and so on into the scheduler.

To do that, scheduly uses four input spreadsheets located in `config/inputs`:

1. `courses.csv`: general information about courses in the scheduler, such as a
   course identifier, number of weekly classes, etc. Since this data isn't
   expected to change frequently, we encourage users to reuse the same database
   every iteration of the scheduling process.

> **IMPORTANT** it is strictly required that every course scheduled by the
> scheduler have this information filled in.

2. `curriculum.csv`: data about curricula in the educational institution.
   Curricula helps the scheduler to make intelligent decisions while creating a
   schedule, such as avoid conflicts between classes of the same curricula.

3. `schedules.csv`: data about teacher's time availability and restriction.
   Although not required, providing preferred and unavailable teaching periods
   can greatly improve performance of the scheduler, leading to better schedules
   overall.

4. `workload.csv`: course offering information, such as class lecturers and
   which period classes should be scheduled.

> You can find detailed information about inputs in the
> [inputs page](docs/inputs.md).

With the inputs filled in, we can focus on **configuring the model**.

## Configuring the model

To build a well-structured schedule, the program takes into account multiple
*rules*. This rules, or constraints, come in two distinct, yet complementary,
types:

1. Hard rules: these are rules that describe the structure of a valid schedule
   that can be generated as an output of the program. The prefix **hard**
   indicates that this kind of constraints are set in stone, and no valid
   solution can break these rules.

2. Soft rules: in contrast to the previously described hard rules, these are
   rules that allow the scheduler to **compare** sets of valid schedules and
   pick the best among them. Breaking a soft rule doesn't automatically
   disregard a solution, but rather it penalizes the solution by a certain cost
   (or **weight**).

One can understand the search for a solution in the scheduler to be a 2-step
process where the program first finds sets of valid answers using hard rules,
and then uses weak constraints to rank the valid answers using costs of the soft
rules.

In order to allow users to configure this rules in an organized manner, scheduly
uses the concept of a **preset**. A preset is a [TOML](https://toml.io/en/)
configuration file that lives under the `config/presets` directory and is used
to configure the underlying course scheduler model.

In these files, users can enable/disable constraints, set the **weight** and
**priority** values for soft constraints, and also configure how much resources
are used while during the search for a solution.

As a side note, **weight** and **priority** are special parameters for
fine-tuning the importance of soft constraints in the resulting schedule. While
**weight** defines how bad it is to break a given soft rule (greater the weight,
worse it is to break), **priority** allows for separating soft constraints in
optimization layers.

For example, if there are two rules (A) and (B) with priority 1 and 0
respectively, the scheduler will first optimize results based on rules of the
upmost priority (in this case, A) and pass these results to be optimized by the
next optimization layer (in this case, the constraint B). Again, higher values
indicate greater importance of a rule.

By default, the `default` preset is used, but users can use customized presets
by passing the `-p/--preset` command-line flag.

## Scheduling!

With both inputs and the preset configure, one can simply call:

```bash
scheduly cli -p preset filename without extension
```

To create a schedule.
