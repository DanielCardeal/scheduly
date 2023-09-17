from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

CONFIG_DIR = ROOT_DIR.joinpath("config/")

INPUT_DIR = CONFIG_DIR.joinpath("inputs/")
PRESETS_DIR = CONFIG_DIR.joinpath("presets/")
