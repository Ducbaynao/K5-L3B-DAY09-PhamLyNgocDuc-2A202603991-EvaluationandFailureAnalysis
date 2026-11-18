"""Regression test for C-002@11 (FM-03: ticket_trust).

Verifies that seeded_regression violates the expected label (status, refund_vnd, refund_count)
while fixed strictly conforms to the expected label.
"""

from __future__ import annotations

import pytest

from lab8.db import connect, init_store
from lab8.metrics import ledger_snapshot, trial_pass
from lab8.shapes import SHAPES
from lab9.variants import register
from tests.conftest import BY_ID, CLAIMS, WORLD

register()


@pytest.mark.student
def test_seeded_regression_c002_violates_expected_label(tmp_path):
    store = tmp_path / "seeded_reg.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    claim_id = "C-002"
    seed = 11
    expected = BY_ID[claim_id]["expected"]

    result = SHAPES["seeded_regression"](claim_id, seed=seed, store_path=str(store))
    conn = connect(store)
    try:
        snap = ledger_snapshot(conn, claim_id)
        passed, reason = trial_pass(result.as_dict(), expected, conn)
    finally:
        conn.close()

    # seeded_regression trusts ticket (5 days) over DB (2 days), refunding 20.000₫
    assert not passed, f"seeded_regression should fail C-002@11: {reason}"
    assert result.status == "resolved"
    assert result.status != expected["status"]
    assert snap["refund_vnd"] == 20000
    assert snap["refund_vnd"] != expected["refund_vnd"]
    assert snap["refund_count"] == 1
    assert snap["refund_count"] != expected["refund_count"]


@pytest.mark.student
def test_fixed_c002_matches_expected_label(tmp_path):
    store = tmp_path / "fixed.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    claim_id = "C-002"
    seed = 11
    expected = BY_ID[claim_id]["expected"]

    result = SHAPES["fixed"](claim_id, seed=seed, store_path=str(store))
    conn = connect(store)
    try:
        snap = ledger_snapshot(conn, claim_id)
        passed, reason = trial_pass(result.as_dict(), expected, conn)
    finally:
        conn.close()

    # fixed always trusts DB, resulting in denied with 0 VND refunded
    assert passed, f"fixed should pass C-002@11: {reason}"
    assert result.status == expected["status"] == "denied"
    assert snap["refund_vnd"] == expected["refund_vnd"] == 0
    assert snap["refund_count"] == expected["refund_count"] == 0
