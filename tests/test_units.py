import itertools

from lucidform import events
from lucidform.checksums import verhoeff_digit, verhoeff_valid
from lucidform.normalize import normalize
from lucidform.readback import prompt, render


def test_verhoeff_catches_all_single_substitutions_and_adjacent_transpositions():
    good = "234567890124"
    assert verhoeff_valid(good)
    for i, d in itertools.product(range(12), "0123456789"):
        if d != good[i]:
            assert not verhoeff_valid(good[:i] + d + good[i + 1:])
    for i in range(11):
        if good[i] != good[i + 1]:
            assert not verhoeff_valid(good[:i] + good[i + 1] + good[i] + good[i + 2:])


def test_verhoeff_generator_roundtrip():
    for b in ("23456789012", "99999999999", "20000000000"):
        assert verhoeff_valid(b + verhoeff_digit(b))


def test_normalization_never_repairs(form):
    a = form.get("aadhaar")
    assert normalize("2345-6789-012", a) == "23456789012"  # short id is not padded
    assert normalize("2345 6789 O124", a) == "23456789O124"  # O is not turned into 0
    assert normalize("+91 98765-43210", form.get("mobile")) == "9876543210"
    assert normalize("१२३", form.get("pincode")) == "123"
    assert normalize("purush", form.get("gender"), form.extra("gender", "aliases")) == "Male"


def test_readback_groups_identifiers(form):
    assert render("234567890124", form.get("aadhaar")).count("…") == 2
    assert render("ABCPK1234F", form.get("pan")).startswith("A, B, C, P, K")
    assert render("05/03/1990", form.get("dob")) == "5th March 1990"
    assert "comma" in render("12, MG Road", form.get("address"))
    assert "क्या यह सही है" in prompt("462026", form.get("pincode"), "hi")


def test_event_log_append_only(tmp_path, monkeypatch):
    log = tmp_path / "e.jsonl"
    monkeypatch.setenv("LUCIDFORM_LOG", str(log))
    events.emit("A", x=1); events.emit("B", y=[1, 2])
    assert [e["kind"] for e in events.read_log(log)] == ["A", "B"]
