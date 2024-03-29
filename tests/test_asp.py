from clingo import Control
from pytest import fail

from ime_usp_class_scheduler.paths import CONSTRAINTS_DIR


def test_syntax() -> None:
    """Test if there are syntatic errors in the ASP files."""
    ctl = Control()
    for path in CONSTRAINTS_DIR.glob("**/*.lp"):
        try:
            ctl.load(str(path))
        except RuntimeError:
            fail(f"syntax error found in {path.name}.")
