import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from clean import clean  # noqa: E402


def row(**kw):
    base = dict(id="a", time="2026-01-01T00:00:00.000Z", updated="2026-01-01T01:00:00.000Z",
                latitude=10.0, longitude=20.0, depth=10.0, mag=4.0, magType="ml",
                place="5 km N of Town, Chile", status="reviewed", type="earthquake")
    base.update(kw)
    return base


def test_dedup_keeps_latest_update():
    df = clean(pd.DataFrame([row(mag=3.0), row(mag=3.5, updated="2026-01-02T00:00:00.000Z")]))
    assert len(df) == 1 and df.iloc[0]["mag"] == 3.5


def test_filters_non_earthquakes_and_invalid_values():
    raw = pd.DataFrame([
        row(id="ok"),
        row(id="blast", type="explosion"),
        row(id="lat", latitude=95),
        row(id="lon", longitude=-200),
        row(id="mag", mag=11),
        row(id="nomag", mag=None),
    ])
    assert list(clean(raw)["id"]) == ["ok"]


def test_negative_depth_and_region():
    df = clean(pd.DataFrame([row(depth=-1.5)]))
    assert df.iloc[0]["depth"] == 0
    assert df.iloc[0]["region"] == "Chile"
