import argparse
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from collect import days_arg  # noqa: E402


@pytest.mark.parametrize("v", ["0", "-1", "91", "100000"])
def test_days_out_of_range_rejected(v):
    with pytest.raises(argparse.ArgumentTypeError):
        days_arg(v)


def test_days_valid():
    assert days_arg("3") == 3 and days_arg("90") == 90
