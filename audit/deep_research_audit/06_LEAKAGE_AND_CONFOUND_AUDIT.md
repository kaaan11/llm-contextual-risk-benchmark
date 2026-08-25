# 06 — Leakage and Confound Audit (Audit E)

Adversarial question: can conditions/categories be inferred from superficial features instead of
the intended contextual meaning? Design-level and realized-stimulus level both assessed; all
quantities measured on the actual 171 condition instances.

## 1. Category leakage into Condition A (the failure mode that killed Phase 7C)

- Banned-token scan (protocol §2.5 concepts, extended lexicon incl. authorization claims,
  disclaimers, concealment verbs, hedges): **0 hits** in all 37 non-null canonical prompts.
- Builder enforces the same list (`VALENCE_LEAK_TERMS`) as a generation gate; tests re-check.
- Residual risk is paraphrase-level, which is precisely what the pending blind gate measures →
  recorded as HYP-01 with item-level candidates (04 §"gate-risk"), not as demonstrated leakage.

## 2. Trivial-classifier separability of B vs C (context conditions)

Measured feature separability (user-turn context text, final prompt excluded):

| Feature | B | C | Separability |
|---|---|---|---|
| RISK-lexicon density (DU) | 0.15% | 1.31% | ~9× — near-perfect keyword separation |
| LEGITIMACY-lexicon density (DU) | 1.95% | 0.00% | perfect separation |
| First-person assistant stance markers | 0/30 turns | 6/30 (+3/6 NH) | one-directional channel |
| Refusal-preview phrasing in assistant turn | 0 items | 11 items | one-directional |
| Word-count |mean abs diff| | — | 5.0 words (max 25) | weak signal only |

Interpretation, honestly stated: semantic separation between B and C is the *treatment*, so
lexical separability per se is not leakage — a model that cannot distinguish "owned environment"
talk from "unauthorized target" talk has not understood the stimulus. Two components ARE
confound-grade:

1. The **assistant-turn stance channel** (F-01): distinguishable without reading user-turn
   situation at all, and not controlled by D. This is the material finding; see 04.
2. Genre-level risk vocabulary in *user* turns is an unavoidable component of the construct
   (design self-critique §30.1 concedes this); its severity is bounded by: D-arm falsifier for
   generic priming, human gates on realism/materiality (`context_is_material`,
   `context_contains_unnecessary_risk_language` fields exist for exactly this), and the
   null_benign floor whose C arms use concerning-flavored frames over routine tasks.

## 3. Structural/format leakage

- Turn counts identical across B/C(/D) within every item; role patterns uniform (u-a-u or
  u-a-u-u); no formatting markers (code blocks, URLs, IPs, emails — safety scan patterns also
  double as format fingerprints: 0 findings).
- `condition_availability` differs across items but is metadata, not model-visible text.

## 4. Design-term leakage into stimuli

Builder `LEAKAGE_TERMS` scan over every turn of every condition: 0 findings; auditor's
independent grep over the dataset blob for category names/design vocabulary: no hits outside
metadata fields.

## 5. Blind-packet leakage (Phase 7G instrument)

- Packet items contain only `blind_id`, `batch`, prompt, rater containers (validator-enforced).
- Independent scrub: no category prefixes or design terms anywhere in packet text.
- BUT batch composition leaks distributional information: batch 4 contains 6 of the 7
  persistent-ambiguity items; shuffle produces runs of 3–6 same-category items elsewhere →
  F-07 (LOW): a rater doing batches sequentially receives strong base-rate hints for batch 4;
  does not identify any specific item's expected label beyond what the prompt itself shows.

## 6. What could NOT be assessed

Model-side distinguishability (would require running models — out of scope). Everything above is
text-level and therefore prospective for model behavior.
