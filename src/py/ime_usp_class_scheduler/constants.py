from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

CONSTRAINTS_DIR = ROOT_DIR.joinpath("asp/")
HARD_CONSTRAINTS_DIR = CONSTRAINTS_DIR.joinpath("hard/")
SOFT_CONSTRAINTS_DIR = CONSTRAINTS_DIR.joinpath("soft/")

CONFIG_DIR = ROOT_DIR.joinpath("config/")

INPUT_DIR = CONFIG_DIR.joinpath("inputs/")
PRESETS_DIR = CONFIG_DIR.joinpath("presets/")
