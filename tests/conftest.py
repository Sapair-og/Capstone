import datetime as dt
from pathlib import Path

import pytest
import yaml

from lucidform import events
from lucidform.spec import load_overlay

CORPORA = Path(__file__).parent / "corpora"
TODAY = dt.date(2026, 9, 28)


@pytest.fixture(scope="session")
def form():
    return load_overlay()


@pytest.fixture(autouse=True)
def _clean_events():
    events.clear_memory()
    yield


def corpus(name):
    return yaml.safe_load((CORPORA / name).read_text(encoding="utf-8"))["cases"]
