"""Make ariadne/code importable and provide a plain runner (pytest is optional)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
