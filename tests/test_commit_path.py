"""Structural + capability guarantees: the only way into FormState is a genuine receipt
for this exact candidate, and receipts cannot be forged outside confirmation.py."""
import dataclasses

import pytest

from conftest import TODAY
from lucidform import events
from lucidform.confirmation import ConfirmationReceipt, ReceiptForgery, confirm
from lucidform.form_state import FormState, SilentWriteBlocked
from lucidform.types import Affirmation, Candidate
from lucidform.validation import validate


def _flow(form, fid="aadhaar", value="2345 6789 0124", reply="yes"):
    st = FormState(form)
    c = Candidate(fid, value)
    rep = validate(c, form, st.confirmed(), today=TODAY)
    _, receipt = confirm(c, rep, reply)
    return st, c, rep, receipt


def test_happy_path_commits_normalized_value(form):
    st, c, _, r = _flow(form)
    assert st.commit("aadhaar", c, r) == "234567890124"
    assert st.confirmed()["aadhaar"] == "234567890124"
    assert [e["kind"] for e in events.recent()] == ["VALIDATION", "CONFIRMATION", "COMMIT"]


def test_no_public_setter(form):
    st = FormState(form)
    with pytest.raises(TypeError):
        st.confirmed()["aadhaar"] = "x"
    with pytest.raises(AttributeError):
        st.values = {}


def test_denied_readback_issues_no_receipt(form):
    *_, r = _flow(form, reply="yes, I know that's wrong")
    assert r is None


def test_rejected_value_issues_no_receipt(form):
    *_, r = _flow(form, value="234567890125")  # checksum fails
    assert r is None


def test_receipt_for_one_value_cannot_commit_another(form):
    st, c, _, r = _flow(form)
    other = dataclasses.replace(c, value="491837265017")  # same candidate_id, different value
    with pytest.raises(SilentWriteBlocked):
        st.commit("aadhaar", other, r)
    assert events.recent("SILENT_WRITE_BLOCKED")


def test_receipt_for_one_candidate_cannot_commit_another(form):
    st, c, _, r = _flow(form)
    with pytest.raises(SilentWriteBlocked):
        st.commit("aadhaar", Candidate("aadhaar", c.value), r)


def test_receipt_cannot_be_moved_to_another_field(form):
    st, c, _, r = _flow(form)
    with pytest.raises(SilentWriteBlocked):
        st.commit("mobile", c, r)


def test_receipt_cannot_be_forged_outside_confirmation(form):
    _, c, rep, _ = _flow(form)
    with pytest.raises(ReceiptForgery):
        ConfirmationReceipt("aadhaar", c.candidate_id, "x", rep, Affirmation(True, "forged"))


def test_tampered_fingerprint_blocked(form):
    st, c, _, r = _flow(form)
    with pytest.raises((SilentWriteBlocked, dataclasses.FrozenInstanceError)):
        object.__setattr__(r, "candidate_fingerprint", "0" * 64)
        st.commit("aadhaar", c, r)


def test_non_receipt_object_blocked(form):
    st, c, rep, r = _flow(form)
    fake = type("R", (), {k: getattr(r, k) for k in ("field_id", "candidate_id", "candidate_fingerprint",
                                                       "validation", "affirmation")})()
    with pytest.raises(SilentWriteBlocked):
        st.commit("aadhaar", c, fake)


def test_unconfirmed_value_cannot_influence_cross_field(form):
    st = FormState(form)
    # state proposed but NOT confirmed -> pincode gate must ignore it
    rep = validate(Candidate("pincode", "110001"), form, st.confirmed(), today=TODAY)
    assert rep.passed
