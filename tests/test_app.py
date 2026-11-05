from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


def test_dashboard_loads_without_exception(monkeypatch):
    if not (ROOT / "data/processed/earthquakes.csv").exists():
        pytest.skip("dados processados ausentes")
    monkeypatch.chdir(ROOT)
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not at.exception
