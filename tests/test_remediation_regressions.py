"""Remediation regression tests (pre_eval campaign).

Covers: F-06 two-rater gate enforcement, F-03 roll-up derivation consistency,
F-08 denominator accounting + duplicate detection + append guard, F-10 frozen
config preflight, and protected-invariant checks for the R1 clarification.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from apply_phase7g_annotations import (  # noqa: E402
    QCError, record_blind, record_adjudication, record_context, record_decision,
)
from validate_phase7g_review import validate, validate_blind, validate_summary  # noqa: E402
from benchmark.errors import LoggingError  # noqa: E402
from benchmark.logging import JsonlResponseLogger  # noqa: E402
from benchmark.metrics import calculate_metrics  # noqa: E402
from benchmark.preflight import PreflightError, assert_run_config_frozen  # noqa: E402
from benchmark.metadata import ExperimentMetadata  # noqa: E402
from benchmark.types import ModelSpec  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


AUDIT = ROOT / "results" / "dataset_audit"
BLIND = AUDIT / "phase7g_blind_review.json"
KEY = AUDIT / "phase7g_blind_key.json"
QC = AUDIT / "phase7g_human_qc.json"
SUMMARY = AUDIT / "phase7g_quality_summary.json"
HISTORY = AUDIT / "phase7g_review_history.jsonl"
TS = "2026-08-14T22:00:00Z"


def _rid_to_bid(key: dict, rid: str) -> str:
    return next(m["blind_id"] for m in key["mapping"] if m["research_item_id"] == rid)


def _two_rater_agree(blind: dict, key: dict, rid: str = "RI-DU-001",
                     valence: str = "ambiguous_dual_use") -> None:
    bid = _rid_to_bid(key, rid)
    for rater, rid_ in (("rater_a", "RATER-A-ID"), ("rater_b", "RATER-B-ID")):
        record_blind(blind, key, [{"blind_id": bid, "rater": rater,
                                   "valence": valence, "confidence": "high"}],
                     rid_, None, TS)


class TwoRaterGateTests(unittest.TestCase):
    """F-06: one rating can never complete an item; gates require ADJUDICATED."""

    def setUp(self):
        self.blind = load(BLIND)
        self.key = load(KEY)
        self.qc = load(QC)

    def _context_complete(self, qc, blind, rid="RI-DU-001"):
        record_context(qc, blind, self.key, [{
            "research_item_id": rid,
            "context_relevance": {"context_is_material": "true"},
            "notes": {"context_is_material": "ok"},
            "naturalness": "high",
            "safety_status": "PASS",
        }], "REV", "researcher_self_review", TS)

    def test_one_rater_cannot_reach_keep(self):
        # E2a fail-closed gate: a single rating opens neither context nor KEEP.
        qc = copy.deepcopy(self.qc)
        blind = copy.deepcopy(self.blind)
        bid = _rid_to_bid(self.key, "RI-DU-001")
        record_blind(blind, self.key,
                     [{"blind_id": bid, "rater": "rater_a",
                       "valence": "ambiguous_dual_use", "confidence": "high"}],
                     "ONLY-RATER", "role", TS)
        with self.assertRaises(QCError) as ctx:
            self._context_complete(qc, blind)
        self.assertIn("ADJUDICATED", str(ctx.exception))
        with self.assertRaises(QCError) as ctx:
            record_decision(qc, blind, self.key,
                            [{"research_item_id": "RI-DU-001", "decision": "KEEP"}],
                            "DECIDER", None, TS)
        self.assertIn("two-rater mandate", str(ctx.exception))

    def test_same_reviewer_id_on_both_slots_refused(self):
        blind = copy.deepcopy(self.blind)
        bid = _rid_to_bid(self.key, "RI-DU-002")
        record_blind(blind, self.key, [{"blind_id": bid, "rater": "rater_a",
                                        "valence": "ambiguous_dual_use",
                                        "confidence": "high"}], "SAME-ID", None, TS)
        with self.assertRaises(QCError) as ctx:
            record_blind(blind, self.key, [{"blind_id": bid, "rater": "rater_b",
                                            "valence": "ambiguous_dual_use",
                                            "confidence": "high"}], "SAME-ID", None, TS)
        self.assertIn("independent raters", str(ctx.exception))

    def test_disagreement_blocks_gate_until_adjudicated_then_keep_succeeds(self):
        blind, qc = copy.deepcopy(self.blind), copy.deepcopy(self.qc)
        bid = _rid_to_bid(self.key, "RI-DU-003")
        record_blind(blind, self.key, [{"blind_id": bid, "rater": "rater_a",
                                        "valence": "probably_benign",
                                        "confidence": "medium"}], "A-ID", None, TS)
        record_blind(blind, self.key, [{"blind_id": bid, "rater": "rater_b",
                                        "valence": "ambiguous_dual_use",
                                        "confidence": "medium"}], "B-ID", None, TS)
        item = next(i for i in blind["items"] if i["blind_id"] == bid)
        self.assertEqual(item["annotation_status"], "DISAGREEMENT_PENDING_ADJUDICATION")
        self.assertIsNone(item["gate_result"])
        # E2a fail-closed gate: unresolved disagreement opens no context either.
        with self.assertRaises(QCError) as ctx:
            self._context_complete(qc, blind, rid="RI-DU-003")
        self.assertIn("ADJUDICATED", str(ctx.exception))
        with self.assertRaises(QCError):  # disagreement unresolved -> no KEEP
            record_decision(qc, blind, self.key,
                            [{"research_item_id": "RI-DU-003", "decision": "KEEP"}],
                            "D", None, TS)
        with self.assertRaises(QCError):  # fabricated shortcut without both ratings
            record_adjudication(blind, self.key,
                                [{"blind_id": _rid_to_bid(self.key, "RI-DU-004"),
                                  "adjudicated_valence": "ambiguous_dual_use",
                                  "rationale": "x"}], "ADJ", None, TS)
        record_adjudication(blind, self.key,
                            [{"blind_id": bid, "adjudicated_valence": "ambiguous_dual_use",
                              "rationale": "second reading is the designed target"}],
                            "ADJUDICATOR", None, TS)
        item = next(i for i in blind["items"] if i["blind_id"] == bid)
        self.assertEqual(item["annotation_status"], "ADJUDICATED")
        self.assertEqual(item["gate_result"], "PASS")
        # E2a: context opens only after the blind record is ADJUDICATED.
        self._context_complete(qc, blind, rid="RI-DU-003")
        record_decision(qc, blind, self.key,
                        [{"research_item_id": "RI-DU-003", "decision": "KEEP"}],
                        "DECIDER", None, TS)
        self.assertEqual(validate(qc, blind, self.key), [])

    def test_validator_flags_keep_over_partial_state(self):
        qc = copy.deepcopy(self.qc)
        item = qc["items"][0]
        bid = _rid_to_bid(self.key, item["research_item_id"])
        blind = copy.deepcopy(self.blind)
        blind_item = next(i for i in blind["items"] if i["blind_id"] == bid)
        blind_item["annotation_status"] = "PARTIAL_ONE_RATER"
        blind_item["rater_a"]["isolated_prompt_valence_observed"] = "ambiguous_dual_use"
        blind_item["rater_a"]["annotated_at"] = TS
        blind_item["rater_a"]["reviewer_role"] = "solo"
        for section in ("context_review", "safety_review", "naturalness_review"):
            item[section]["status"] = "COMPLETE"
        item["review_decision"] = "KEEP"
        item["stimulus_review_status"] = "KEEP"
        item["researcher_qc"] = True
        item["reviewer_role"] = "r"
        item["review_timestamp"] = TS
        errs = [e for e in validate(qc, blind, self.key) if "ADJUDICATED" in e]
        self.assertTrue(errs)

    def test_phase_completion_requires_all_items_adjudicated(self):
        qc = copy.deepcopy(self.qc)
        qc["counts"]["pending"] = 0
        qc["phase_complete"] = True
        errors = validate(qc, copy.deepcopy(self.blind), self.key)
        self.assertTrue(any("not ADJUDICATED" in e for e in errors))


class RollupDerivationTests(unittest.TestCase):
    """F-03: summary must equal a deterministic derivation from live records."""

    def setUp(self):
        self.blind = load(BLIND)
        self.qc = load(QC)
        self.summary = load(SUMMARY)

    def test_live_rollup_matches_derivation(self):
        self.assertEqual(validate_summary(self.qc, self.blind, self.summary), [])

    def test_stale_summary_is_detected(self):
        stale = copy.deepcopy(self.summary)
        stale["isolated_prompt_review"]["annotations_submitted"] = 0
        errors = validate_summary(self.qc, self.blind, stale)
        self.assertTrue(any("annotations_submitted" in e for e in errors))

    def test_annotation_count_derives_from_history_not_hardcoded(self):
        events = [json.loads(line) for line in HISTORY.read_text().splitlines() if line.strip()]
        expected = len({(e["blind_id"], e.get("raster") or e["rater"])
                        for e in events if e.get("event") == "blind_annotation"})
        actual = sum(1 for i in self.blind["items"]
                     if i["annotation_status"] != "PENDING")
        self.assertEqual(actual, expected)


class MetricsAccountingTests(unittest.TestCase):
    """F-08: errored/excluded rows stay visible; duplicates are reported."""

    @staticmethod
    def _row(eid, *, status="success", error=None, refusal=None, latency=10.0):
        row = {"evaluation_id": eid, "status": status, "error": error,
               "latency_ms": latency, "provider_call_latency_ms": latency,
               "dataset_membership": ["benign"]}
        if refusal is not None:
            row["refusal"] = refusal
        return row

    def test_high_error_run_reports_denominators_honestly(self):
        rows = ([self._row(f"s{i}", refusal={"is_refusal": False}) for i in range(8)]
                + [self._row(f"e{i}", status="error", error="timeout") for i in range(92)])
        m = calculate_metrics(rows)
        acc = m["denominator_accounting"]
        self.assertEqual(acc["n_expected"], 100)
        self.assertEqual(acc["n_observed_success"], 8)
        self.assertEqual(acc["n_error_or_failed"], 92)
        self.assertEqual(m["refusal_rate"], 0.0)
        self.assertEqual(acc["refusal_denominator_rows_with_refusal_object"], 8)
        self.assertLess(m["success_rate"], 0.1)

    def test_duplicate_rows_reported_not_merged(self):
        rows = [self._row("x1"), self._row("x1"), self._row("x2")]
        acc = calculate_metrics(rows)["denominator_accounting"]
        self.assertEqual(acc["duplicate_evaluation_id_rows"], 1)
        self.assertEqual(acc["n_expected"], 3)

    def test_logger_append_guard(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "responses.jsonl"
            JsonlResponseLogger(p).close()  # fresh empty file ok
            p.write_text('{"evaluation_id":"prior-run-1"}\n')  # simulate prior run rows
            with self.assertRaises(LoggingError):
                JsonlResponseLogger(p)  # non-empty -> refuse by default
            JsonlResponseLogger(p, append_ok=True).close()  # explicit opt-in works


def _metadata(**overrides):
    base = dict(
        run_id="run-1", experiment_id="exp-1",
        dataset_id="llm-ctx-pilot-stimuli-en", dataset_version="0.3.0",
        model=ModelSpec(provider="test", name="model-x", version="2026-01-01"),
        configuration="baseline", context_mode="conversation_context",
        created_at="2026-01-01T00:00:00Z",
        generation_parameters={"temperature": 0.0, "top_p": 1.0, "max_output_tokens": 256},
        retry_policy={"max_attempts": 2}, timeout_s=30.0,
    )
    base.update(overrides)
    return ExperimentMetadata(**base)


class PreflightTests(unittest.TestCase):
    """F-10: canonical evaluation cannot start from undocumented defaults."""

    def test_complete_config_passes_and_digest_is_stable(self):
        md = _metadata()
        d1 = assert_run_config_frozen(md)
        d2 = assert_run_config_frozen(_metadata())
        self.assertEqual(d1, d2)
        self.len64 = len(d1) == 64

    def test_missing_generation_parameter_raises(self):
        md = _metadata(generation_parameters={"temperature": 0.0})
        with self.assertRaises(PreflightError) as ctx:
            assert_run_config_frozen(md)
        self.assertIn("max_output_tokens", str(ctx.exception))

    def test_missing_model_version_raises_with_honesty_note(self):
        md = _metadata(model=ModelSpec(provider="p", name="n", version=""))
        with self.assertRaises(PreflightError):
            assert_run_config_frozen(md)

    def test_out_of_range_parameter_raises(self):
        md = _metadata(generation_parameters={"temperature": 5.0, "top_p": 1.0,
                                              "max_output_tokens": 256})
        with self.assertRaises(PreflightError):
            assert_run_config_frozen(md)


class ClarificationInvariantTests(unittest.TestCase):
    """Protected-invariant spot checks for the R1 amendment path."""

    def test_original_preregistration_bytes_unchanged(self):
        want = "7d46e0fba94a88beaa27a4c41efa209e3c89619b3f3dd5e96877997aa99bf87c"
        got = hashlib.sha256((ROOT / "docs/phase7e_preregistration.md").read_bytes()).hexdigest()
        self.assertEqual(got, want)

    def test_stimuli_bytes_unchanged_since_baseline(self):
        baseline = load(ROOT / "remediation/pre_eval/protected_artifacts_baseline.json")
        for rel, want in baseline.items():
            got = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            self.assertEqual(got, want, f"{rel} changed during remediation")

    def test_existing_human_annotation_preserved(self):
        blind = load(BLIND)
        item = next(i for i in blind["items"] if i["blind_id"] == "BLIND-001")
        ra = item["rater_a"]
        self.assertEqual(ra["isolated_prompt_valence_observed"], "probably_benign")
        self.assertEqual(ra["annotated_at"], "2026-08-14T20:15:00Z")
        self.assertEqual(item["accepted_in_session"], 2)
        self.assertIsNone(item["adjudicated_valence"])  # awaiting second rater


if __name__ == "__main__":
    unittest.main()
