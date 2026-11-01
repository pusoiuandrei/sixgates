"""Make the spike modules importable when pytest is run from any directory."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
