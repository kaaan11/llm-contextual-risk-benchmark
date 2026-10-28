"""Phase 7G — E2a fail-closed gate tests.

Covers the E2a behaviour contract without producing real annotation semantics:
rejections use PENDING / PARTIAL / DISAGREEMENT live states and minimal
structural violation vectors. In-memory fixtures that carry a gate_result are
explicitly marked SYNTHETIC_VIOLATION: they attribute nothing to a rater (no
reviewer identity, no timestamp, no history event) and are never persisted.
A positive two-rater path with real human provenance cannot be fabricated here
and stays a reviewer acceptance item; the in-memory two-rating agreement setup
below reuses the suite's established F-06 fixture pattern for gate mechanics.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from apply_phase7g_annotations import (  # noqa: E402
    QCError,
    blind_item_eligible_for_context,
    blind_item_for,
    category_for,
    keep_eligibility,
    keep_gate_blockers,
    record_blind,
    record_context,
    record_decision,
)
from validate_phase7g_review import validate  # noqa: E402

AUDIT = ROOT / "results" / "dataset_audit"
BLIND = AUDIT / "phase7g_blind_review.json"
KEY = AUDIT / "phase7g_blind_key.json"
QC = AUDIT / "phase7g_human_qc.json"

TS = "2026-08-14T18:00:00Z"


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _rid_to_bid(key: dict, rid: str) -> str:
    return next(m["blind_id"] for m in key["mapping"]
                if m["research_item_id"] == rid)


def _live_partial_rid(blind: dict, key: dict) -> str:
    """Research item whose live blind record is PARTIAL_ONE_RATER."""
    partial = next(i for i in blind["items"]
                   if i["annotation_status"] == "PARTIAL_ONE_RATER")
    return next(m["research_item_id"] for m in key["mapping"]
                if m["blind_id"] == partial["blind_id"])


def _slot(**over):
    base = {"reviewer_id": None, "reviewer_role": "r",
            "isolated_prompt_valence_observed": None,
            "reviewer_confidence": None, "reviewer_notes": None,
            "annotated_at": None}
    base.update(over)
    return base


def _stubbed_eligibility():
    """Stub the eligibility sub-dependency to True for wiring tests.

    Returns a mock.patch context manager. The stub yields a boolean tuple
    only — never annotation payloads, identities or timestamps.
    """
    return patch("apply_phase7g_annotations.blind_item_eligible_for_context",
                 return_value=(True, "stubbed for wiring test"))


def _patched_fail_gate():
    """Stub gate recomputation to FAIL for wiring tests (no valence input)."""
    return patch("apply_phase7g_annotations.evaluate_gate",
                 return_value=("FAIL", "ISOLATED_VALENCE_GATE_FAIL"))


def _stage_qc_item(qc: dict, rid: str):
    """Writer input shape: reviews COMPLETE, decision still PENDING."""
    item = next(i for i in qc["items"] if i["research_item_id"] == rid)
    for section in ("context_review", "safety_review", "naturalness_review"):
        item[section]["status"] = "COMPLETE"
    item["safety_review"]["safety_status"] = "PASS"
    item["reviewer_role"] = "r"
    item["review_timestamp"] = TS
    return item


def _approved_qc_item(qc: dict, rid: str):
    """Validator input shape: approved KEEP with consistent counts."""
    item = _stage_qc_item(qc, rid)
    item.update(review_decision="KEEP", researcher_qc=True,
                stimulus_review_status="KEEP")
    qc["counts"].update(keep=1, pending=49, researcher_qc_true=1)
    return item


class ContextEligibilityHelperTests(unittest.TestCase):
    def test_pending_is_refused(self):
        ok, reason = blind_item_eligible_for_context(
            {"annotation_status": "PENDING"})
        self.assertFalse(ok)
        self.assertIn("PENDING", reason)

    def test_partial_one_rater_is_refused(self):
        ok, reason = blind_item_eligible_for_context(
            {"annotation_status": "PARTIAL_ONE_RATER"})
        self.assertFalse(ok)
        self.assertIn("ADJUDICATED", reason)

    def test_unresolved_disagreement_is_refused(self):
        ok, _ = blind_item_eligible_for_context(
            {"annotation_status": "DISAGREEMENT_PENDING_ADJUDICATION"})
        self.assertFalse(ok)

    def test_missing_provenance_is_refused(self):
        item = {"annotation_status": "ADJUDICATED",
                "adjudicated_valence": "V",
                "rater_a": _slot(isolated_prompt_valence_observed="V",
                                 annotated_at=TS),
                "rater_b": _slot(isolated_prompt_valence_observed="V")}
        ok, reason = blind_item_eligible_for_context(item)
        self.assertFalse(ok)
        self.assertIn("provenance", reason)

    def test_role_only_slots_are_not_evidence(self):
        # E2a-R1: a generic reviewer_role alone proves no human identity.
        item = {"annotation_status": "ADJUDICATED",
                "adjudicated_valence": "V",
                "rater_a": _slot(isolated_prompt_valence_observed="V",
                                 annotated_at=TS),
                "rater_b": _slot(isolated_prompt_valence_observed="V",
                                 annotated_at=TS)}
        ok, reason = blind_item_eligible_for_context(item)
        self.assertFalse(ok)
        self.assertIn("reviewer identity", reason)

    def test_same_reviewer_id_is_refused(self):
        item = {"annotation_status": "ADJUDICATED",
                "adjudicated_valence": "V",
                "rater_a": _slot(isolated_prompt_valence_observed="V",
                                 reviewer_id="SYN-SAME", annotated_at=TS),
                "rater_b": _slot(isolated_prompt_valence_observed="V",
                                 reviewer_id="SYN-SAME", annotated_at=TS)}
        ok, reason = blind_item_eligible_for_context(item)
        self.assertFalse(ok)
        self.assertIn("same reviewer_id", reason)

    def test_adjudication_without_rationale_is_refused(self):
        item = {"annotation_status": "ADJUDICATED",
                "adjudicated_valence": "V",
                "adjudicated_by": {"reviewer_id": "SYN-ADJ"},
                "rater_a": _slot(isolated_prompt_valence_observed="V",
                                 reviewer_id="SYN-A", annotated_at=TS),
                "rater_b": _slot(isolated_prompt_valence_observed="W",
                                 reviewer_id="SYN-B", annotated_at=TS)}
        ok, reason = blind_item_eligible_for_context(item)
        self.assertFalse(ok)
        self.assertIn("rationale", reason)

    # NOTE (E2a-R2): no positive-shape test exists here on purpose. An
    # eligible agreement/adjudication record can only be asserted with real
    # human provenance, which agents must not fabricate. The True path of the
    # shared helper stays a reviewer acceptance item.

    def test_unknown_mapping_raises_fail_closed(self):
        blind, key = load(BLIND), load(KEY)
        with self.assertRaises(QCError) as ctx:
            blind_item_for(blind, key, "RI-NOPE-000")
        self.assertIn("unknown research_item_id", str(ctx.exception))


class KeepGateBlockersTests(unittest.TestCase):
    """Full-evidence KEEP bound. Refusal states use genuine incomplete shapes;
    gate-branch wiring uses stubbed eligibility (boolean only) over live-shaped
    records with void placeholders — never human semantics."""

    def test_pending_blocks(self):
        item = {"annotation_status": "PENDING"}
        self.assertIn("blind_isolated_prompt_review",
                      keep_gate_blockers(item, "dual_use_nonnull"))

    def test_partial_and_disagreement_block(self):
        for status in ("PARTIAL_ONE_RATER", "DISAGREEMENT_PENDING_ADJUDICATION"):
            blockers = keep_gate_blockers({"annotation_status": status},
                                          "dual_use_nonnull")
            self.assertTrue(any("two-rater mandate" in b for b in blockers),
                            status)

    def test_empty_slots_with_hand_status_are_refused(self):
        # Counterexample: hand-set ADJUDICATED/PASS on empty slots proves nothing.
        item = {"annotation_status": "ADJUDICATED", "gate_result": "PASS",
                "rater_a": _slot(), "rater_b": _slot()}
        self.assertTrue(keep_gate_blockers(item, "dual_use_nonnull"))

    def test_same_identity_blocks(self):
        item = {"annotation_status": "ADJUDICATED",
                "adjudicated_valence": "SYN",
                "rater_a": _slot(isolated_prompt_valence_observed="SYN-V",
                                 reviewer_id="SYN-SAME", annotated_at=TS),
                "rater_b": _slot(isolated_prompt_valence_observed="SYN-V",
                                 reviewer_id="SYN-SAME", annotated_at=TS)}
        blockers = keep_gate_blockers(item, "dual_use_nonnull")
        self.assertTrue(any("same reviewer_id" in b for b in blockers))

    def test_consistent_fail_blocks_as_never_waived(self):
        blind = {"annotation_status": "ADJUDICATED", "gate_result": "FAIL",
                 "adjudicated_valence": "SYN"}
        with _stubbed_eligibility(), _patched_fail_gate():
            blockers = keep_gate_blockers(blind, "dual_use_nonnull")
        self.assertTrue(any("never waived" in b for b in blockers),
                        blockers)

    def test_missing_unknown_and_mismatched_gates_block(self):
        # Eligibility stubbed True; gate inputs are void placeholders, so the
        # real recomputation runs on semantically empty values.
        cases = {
            "missing": (None, "SYN"),
            "unknown": ("MAYBE", "SYN"),
            "mismatched": ("PASS", "SYN"),
        }
        for name, (gate, adjudicated) in cases.items():
            blind = {"annotation_status": "ADJUDICATED",
                     "gate_result": gate, "adjudicated_valence": adjudicated}
            with _stubbed_eligibility():
                blockers = keep_gate_blockers(blind, "dual_use_nonnull")
            self.assertTrue(blockers, name)
            self.assertFalse(any("never waived" in b for b in blockers), name)

    def test_keep_eligibility_mirrors_writer_bounds(self):
        qc = load(QC)
        item = next(i for i in qc["items"]
                    if i["research_item_id"] == "RI-DU-001")
        blind = {"annotation_status": "PARTIAL_ONE_RATER"}
        eligible, reasons = keep_eligibility(item, blind, "dual_use_nonnull")
        self.assertFalse(eligible)
        self.assertTrue(any("two-rater mandate" in r for r in reasons))
        blind = {"annotation_status": "ADJUDICATED", "gate_result": "FAIL",
                 "adjudicated_valence": "SYN"}
        with _stubbed_eligibility(), _patched_fail_gate():
            eligible, reasons = keep_eligibility(
                item, blind, "dual_use_nonnull")
        self.assertFalse(eligible)
        self.assertTrue(any("never waived" in r for r in reasons))

    # NOTE (E2a-R2): no consistent-PASS assertion exists here on purpose. A
    # passing gate can only be asserted with real human provenance, which
    # stays a reviewer acceptance item.


class LivePartialRefusalTests(unittest.TestCase):
    """The live PARTIAL_ONE_RATER record opens no context (E2a core)."""

    def setUp(self):
        self.blind = load(BLIND)
        self.key = load(KEY)
        self.qc = load(QC)

    def test_live_partial_item_refuses_context(self):
        rid = _live_partial_rid(self.blind, self.key)
        qc, blind = copy.deepcopy(self.qc), copy.deepcopy(self.blind)
        with self.assertRaises(QCError) as ctx:
            record_context(qc, blind, self.key,
                           [{"research_item_id": rid,
                             "context_relevance": {"context_is_material": "true"},
                             "notes": {"context_is_material": "n"}}],
                           None, "researcher_self_review", TS)
        self.assertIn("ADJUDICATED", str(ctx.exception))

    def test_refused_context_changes_nothing(self):
        rid = _live_partial_rid(self.blind, self.key)
        qc, blind = copy.deepcopy(self.qc), copy.deepcopy(self.blind)
        qc_before, blind_before = copy.deepcopy(qc), copy.deepcopy(blind)
        with self.assertRaises(QCError):
            record_context(qc, blind, self.key,
                           [{"research_item_id": rid,
                             "context_relevance": {"context_is_material": "true"},
                             "notes": {"context_is_material": "n"}}],
                           None, "researcher_self_review", TS)
        self.assertEqual(qc, qc_before)
        self.assertEqual(blind, blind_before)

    def test_cli_listing_excludes_live_partial_item(self):
        from scripts.review_context import get_pending_context_items
        rid = _live_partial_rid(self.blind, self.key)
        listed = get_pending_context_items(self.qc, self.blind, self.key)
        self.assertNotIn(rid, [i["research_item_id"] for i in listed])
        for item in listed:
            bitem = blind_item_for(
                self.blind, self.key, item["research_item_id"])
            self.assertTrue(blind_item_eligible_for_context(bitem)[0])


class FailGateTests(unittest.TestCase):
    """Blind gate FAIL refuses KEEP in writer and validator alike."""

    def setUp(self):
        self.blind = load(BLIND)
        self.key = load(KEY)
        self.qc = load(QC)

    def _fail_state(self, rid="RI-DU-005"):
        """Live-shaped blind record with a stored FAIL gate.

        Slots stay null (untouched); only status/gate/adjudicated-marker
        fields are set, and the adjudicated marker is the void placeholder
        "SYN" — never a real valence, identity or timestamp. Eligibility is
        stubbed True by callers where the gate branch is under test.
        """
        qc, blind = copy.deepcopy(self.qc), copy.deepcopy(self.blind)
        bid = _rid_to_bid(self.key, rid)
        bitem = next(i for i in blind["items"] if i["blind_id"] == bid)
        bitem.update(annotation_status="ADJUDICATED", gate_result="FAIL",
                     gate_flag="ISOLATED_VALENCE_GATE_FAIL",
                     adjudicated_valence="SYN")
        _stage_qc_item(qc, rid)
        return qc, blind, rid

    def _fail_state_approved(self, rid="RI-DU-005"):
        qc, blind, rid = self._fail_state(rid)
        _approved_qc_item(qc, rid)
        return qc, blind, rid

    def test_writer_refuses_keep_on_fail_gate(self):
        qc, blind, rid = self._fail_state()
        with _stubbed_eligibility(), _patched_fail_gate():
            with self.assertRaises(QCError) as ctx:
                record_decision(qc, blind, self.key,
                                [{"research_item_id": rid, "decision": "KEEP"}],
                                None, "r", TS)
        self.assertIn("never waived", str(ctx.exception))

    def test_writer_refusal_changes_nothing(self):
        qc, blind, rid = self._fail_state()
        qc_before, blind_before = copy.deepcopy(qc), copy.deepcopy(blind)
        with _stubbed_eligibility(), _patched_fail_gate():
            with self.assertRaises(QCError):
                record_decision(qc, blind, self.key,
                                [{"research_item_id": rid, "decision": "KEEP"}],
                                None, "r", TS)
        self.assertEqual(qc, qc_before)
        self.assertEqual(blind, blind_before)

    def test_validator_flags_keep_on_fail_gate(self):
        qc, blind, rid = self._fail_state_approved()
        with _stubbed_eligibility(), _patched_fail_gate():
            errors = validate(qc, blind, self.key)
        self.assertTrue(any("never waived" in e for e in errors), errors)

    def test_writer_validator_agree_on_blind_states(self):
        # Same bound on both layers for every structural blind state.
        # Writer input keeps the decision PENDING; validator input carries the
        # approved KEEP shape. Gate-branch states stub only the eligibility
        # sub-dependency (boolean); gate mapping stays real except where the
        # branch definition needs a stubbed FAIL recomputation.
        # NOTE: no consistent-PASS success case exists here on purpose — a
        # passing gate can only be asserted with real human provenance.
        ri_du006 = "RI-DU-006"
        refusal_states = [
            "PENDING",
            "PARTIAL_ONE_RATER",
            "DISAGREEMENT",
        ]
        for name in refusal_states:
            qc, blind = copy.deepcopy(self.qc), copy.deepcopy(self.blind)
            bid = _rid_to_bid(self.key, ri_du006)
            bitem = next(i for i in blind["items"] if i["blind_id"] == bid)
            status = ("DISAGREEMENT_PENDING_ADJUDICATION"
                      if name == "DISAGREEMENT" else name)
            bitem.update(annotation_status=status, gate_result=None,
                         gate_flag=None)
            _stage_qc_item(qc, ri_du006)
            with self.assertRaises(QCError, msg=f"writer allows {name}"):
                record_decision(qc, blind, self.key,
                                [{"research_item_id": ri_du006,
                                  "decision": "KEEP"}],
                                None, "r", TS)
            approved = copy.deepcopy(qc)
            _approved_qc_item(approved, ri_du006)
            self.assertTrue(validate(approved, blind, self.key),
                            f"validator misses {name}")
        gate_states = {
            "ADJUDICATED+FAIL": ("FAIL", True),
            "ADJUDICATED+MISSING": (None, False),
            "ADJUDICATED+UNKNOWN": ("MAYBE", False),
            "ADJUDICATED+MISMATCH": ("PASS", False),
        }
        for name, (gate, patch_gate) in gate_states.items():
            qc, blind = copy.deepcopy(self.qc), copy.deepcopy(self.blind)
            bid = _rid_to_bid(self.key, ri_du006)
            bitem = next(i for i in blind["items"] if i["blind_id"] == bid)
            # Void adjudicated marker: structurally non-null so the gate
            # section is reached; semantically empty ("SYN" is not a valence).
            bitem.update(annotation_status="ADJUDICATED",
                         gate_result=gate, gate_flag=None,
                         adjudicated_valence="SYN")
            _stage_qc_item(qc, ri_du006)
            with ExitStack() as stack:
                stack.enter_context(_stubbed_eligibility())
                if patch_gate:
                    stack.enter_context(_patched_fail_gate())
                with self.assertRaises(QCError, msg=f"writer allows {name}"):
                    record_decision(qc, blind, self.key,
                                    [{"research_item_id": ri_du006,
                                      "decision": "KEEP"}],
                                    None, "r", TS)
            approved = copy.deepcopy(qc)
            _approved_qc_item(approved, ri_du006)
            with ExitStack() as stack:
                stack.enter_context(_stubbed_eligibility())
                if patch_gate:
                    stack.enter_context(_patched_fail_gate())
                self.assertTrue(validate(approved, blind, self.key),
                                f"validator misses {name}")

    def test_batch_refusal_is_atomic(self):
        # No ratings are recorded here at all: the first payload (REVISE with
        # notes) would mutate, the second (KEEP on a PENDING blind) refuses.
        blind, qc = copy.deepcopy(self.blind), copy.deepcopy(self.qc)
        qc_before, blind_before = copy.deepcopy(qc), copy.deepcopy(blind)
        with self.assertRaises(QCError):
            record_decision(
                qc, blind, self.key,
                [{"research_item_id": "RI-DU-007", "decision": "REVISE",
                  "notes": "needs rework"},
                 {"research_item_id": "RI-DU-008", "decision": "KEEP"}],
                None, "r", TS)
        self.assertEqual(qc, qc_before)
        self.assertEqual(blind, blind_before)


class DecideWizardEligibilityTests(unittest.TestCase):
    def test_fail_gate_visible_and_ineligible(self):
        from scripts.decide_phase7g import get_pending_decision_items
        qc = load(QC)
        pending = get_pending_decision_items(qc)
        self.assertEqual(len(pending), 50)
        item = next(i for i in qc["items"]
                    if i["research_item_id"] == "RI-DU-001")
        blind = {"annotation_status": "ADJUDICATED", "gate_result": "FAIL",
                 "adjudicated_valence": "SYN"}
        with _stubbed_eligibility(), _patched_fail_gate():
            eligible, reasons = keep_eligibility(
                item, blind, "dual_use_nonnull")
        self.assertFalse(eligible)
        self.assertTrue(any("never waived" in r for r in reasons))
        eligible, _ = keep_eligibility(
            item, {"annotation_status": "PARTIAL_ONE_RATER"},
            "dual_use_nonnull")
        self.assertFalse(eligible)

    def test_same_identity_ineligible_in_cli_bound(self):
        qc = load(QC)
        item = next(i for i in qc["items"]
                    if i["research_item_id"] == "RI-DU-001")
        blind = {"annotation_status": "ADJUDICATED",
                 "adjudicated_valence": "SYN",
                 "rater_a": _slot(isolated_prompt_valence_observed="SYN-V",
                                  reviewer_id="SYN-SAME", annotated_at=TS),
                 "rater_b": _slot(isolated_prompt_valence_observed="SYN-V",
                                  reviewer_id="SYN-SAME", annotated_at=TS)}
        eligible, reasons = keep_eligibility(
            item, blind, "dual_use_nonnull")
        self.assertFalse(eligible)
        self.assertTrue(any("same reviewer_id" in r for r in reasons))


class LoadedStateOrderingTests(unittest.TestCase):
    """Disk-loaded PARTIAL/unresolved + COMPLETE context is flagged (R3)."""

    def setUp(self):
        self.blind = load(BLIND)
        self.key = load(KEY)
        self.qc = load(QC)

    def test_partial_with_complete_context_is_flagged(self):
        rid = _live_partial_rid(self.blind, self.key)
        qc = copy.deepcopy(self.qc)
        item = next(i for i in qc["items"] if i["research_item_id"] == rid)
        item["context_review"]["status"] = "COMPLETE"
        errors = validate(qc, self.blind, self.key)
        self.assertTrue(any("before the blind" in e for e in errors), errors)

    def test_empty_slots_hand_status_refused_everywhere(self):        # Counterexample: hand-set ADJUDICATED/PASS on empty slots proves
        # nothing — writer (context + KEEP) refuses, validator flags, CLI hides.
        from scripts.review_context import get_pending_context_items
        qc, blind = copy.deepcopy(self.qc), copy.deepcopy(self.blind)
        rid = "RI-DU-010"
        bid = _rid_to_bid(self.key, rid)
        bitem = next(i for i in blind["items"] if i["blind_id"] == bid)
        bitem.update(annotation_status="ADJUDICATED", gate_result="PASS",
                     gate_flag=None)
        with self.assertRaises(QCError):
            record_context(copy.deepcopy(qc), blind, self.key,
                           [{"research_item_id": rid,
                             "context_relevance": {"context_is_material": "true"},
                             "notes": {"context_is_material": "n"}}],
                           None, "r", TS)
        _stage_qc_item(qc, rid)
        with self.assertRaises(QCError):
            record_decision(copy.deepcopy(qc), blind, self.key,
                            [{"research_item_id": rid, "decision": "KEEP"}],
                            None, "r", TS)
        approved = copy.deepcopy(qc)
        _approved_qc_item(approved, rid)
        aitem = next(i for i in approved["items"]
                     if i["research_item_id"] == rid)
        aitem["context_review"]["status"] = "COMPLETE"
        self.assertTrue(validate(approved, blind, self.key))
        listed = get_pending_context_items(qc, blind, self.key)
        self.assertNotIn(rid, [i["research_item_id"] for i in listed])

    def test_same_identity_with_complete_context_is_flagged(self):
        qc, blind = copy.deepcopy(self.qc), copy.deepcopy(self.blind)
        rid = "RI-DU-009"
        bid = _rid_to_bid(self.key, rid)
        bitem = next(i for i in blind["items"] if i["blind_id"] == bid)
        # Same synthetic ID on both slots; void placeholder valences carry no
        # human semantics. The record is refused (never eligible).
        bitem.update(
            annotation_status="ADJUDICATED",
            adjudicated_valence="SYN",
            rater_a=_slot(isolated_prompt_valence_observed="SYN-V",
                          reviewer_id="SYN-SAME", annotated_at=TS),
            rater_b=_slot(isolated_prompt_valence_observed="SYN-V",
                          reviewer_id="SYN-SAME", annotated_at=TS))
        item = next(i for i in qc["items"] if i["research_item_id"] == rid)
        item["context_review"]["status"] = "COMPLETE"
        # Writer refuses context on the same-identity record ...
        with self.assertRaises(QCError):
            record_context(copy.deepcopy(qc), blind, self.key,
                           [{"research_item_id": rid,
                             "context_relevance": {"context_is_material": "true"},
                             "notes": {"context_is_material": "n"}}],
                           None, "r", TS)
        # ... and the loaded state is flagged.
        errors = validate(qc, blind, self.key)
        self.assertTrue(any("same reviewer_id" in e for e in errors), errors)


class PhaseCompletionEvidenceTests(unittest.TestCase):
    """Completion needs two-rater evidence per item, whatever the decisions."""

    def setUp(self):
        self.blind = load(BLIND)
        self.key = load(KEY)
        self.qc = load(QC)

    def test_all_adjudicated_empty_slots_with_rejects_still_fails(self):
        # Mandatory counterexample: all 50 blind statuses ADJUDICATED with
        # empty slot evidence, all 50 QC decisions reasoned REJECT,
        # phase_complete=true. No valence, identity or annotation is added to
        # the fixture — slots stay exactly as loaded (null).
        from validate_phase7g_review import validate_blind
        blind = copy.deepcopy(self.blind)
        for item in blind["items"]:
            item["annotation_status"] = "ADJUDICATED"
        qc = copy.deepcopy(self.qc)
        for item in qc["items"]:
            item.update(review_decision="REJECT", researcher_qc=False,
                        stimulus_review_status="REJECT",
                        reviewer_role="r", review_timestamp=TS,
                        decision_notes="out of scope",
                        rejection_reason="out of scope",
                        suitable_for_model_evaluation=False)
        qc["counts"].update(pending=0, keep=0, revise=0, reject=50,
                            researcher_qc_true=0)
        qc["phase_complete"] = True
        qc["status"] = "QC_COMPLETE"
        blind_errors = validate_blind(blind)
        self.assertTrue(any("without complete two-rater evidence" in e
                            for e in blind_errors), blind_errors)
        errors = validate(qc, blind, self.key)
        completion = [e for e in errors if "phase_complete" in e]
        self.assertTrue(completion, errors)
        self.assertTrue(any("two-rater" in e for e in completion), completion)


class Phase7GPostAuditRegressions(unittest.TestCase):
    def test_validate_history_rejects_unknown_research_item_id_and_missing_reinit_fields(self):
        """B7: validate_history in 7G rejects unknown research_item_id and reinit missing backup fields."""
        from validate_phase7g_review import validate_history

        qc = {
            "items": [
                {"research_item_id": "RI-AM-001", "review_decision": "PENDING"}
            ]
        }
        init_line = json.dumps({"event": "qc_log_initialised"})

        # Unknown ID
        bad_decision = json.dumps({
            "event": "review_decision",
            "research_item_id": "RI-UNKNOWN-999",
            "previous_decision": "PENDING",
            "new_decision": "KEEP",
            "timestamp": "2026-08-14T12:00:00Z",
        })
        errors = validate_history([init_line, bad_decision], qc)
        self.assertTrue(any("unknown research_item_id" in e for e in errors), errors)

        # Reinit missing backup_dir or manifest_sha256
        reinit_no_backup = json.dumps({
            "event": "review_reinitialised",
            "manifest_sha256": "abcdef",
        })
        reinit_no_sha = json.dumps({
            "event": "review_reinitialised",
            "backup_dir": "/path/to/backup",
        })
        errors_b = validate_history([init_line, reinit_no_backup], qc)
        self.assertTrue(any("lacks backup_dir" in e for e in errors_b), errors_b)

        errors_s = validate_history([init_line, reinit_no_sha], qc)
        self.assertTrue(any("lacks manifest_sha256" in e for e in errors_s), errors_s)


if __name__ == "__main__":
    unittest.main()
