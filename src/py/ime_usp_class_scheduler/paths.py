from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
"""Absolute path to the root of the project."""

CONSTRAINTS_DIR = ROOT_DIR.joinpath("asp/")
"""Absolute path to the ASP files directory."""

HARD_CONSTRAINTS_DIR = CONSTRAINTS_DIR.joinpath("hard/")
"""Absolute path to the hard constraints directory."""

SOFT_CONSTRAINTS_DIR = CONSTRAINTS_DIR.joinpath("soft/")
"""Absolute path to the soft constraints directory."""

CONFIG_DIR = ROOT_DIR.joinpath("config/")
"""Absolute path to the configuration directory."""

INPUT_DIR = CONFIG_DIR.joinpath("inputs/")
"""Absolute path to the input data directory."""

PRESETS_DIR = CONFIG_DIR.joinpath("presets/")
"""Absolute path to the presets directory."""
