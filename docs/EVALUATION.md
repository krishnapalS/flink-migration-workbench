# Evaluation and release protocol

## Executed evidence

1. `python -m unittest discover -s tests -v`: 24 unit tests passed locally. Evidence in `artifacts/unit-tests.txt`.
2. A Java 11, Flink 1.20.5 mini-cluster executed the generated SELECT on seven synthetic rows. The expected output bag contained four rows: id 2 once, id 3 twice, id 6 once. The null amount and below-threshold amounts were excluded. Exact decimal and duplicate counts matched.
3. Mutating `>=` to `>` lost id 2 and the harness detected the mismatch. Evidence in `artifacts/flink-runtime.txt`.

This is one runtime scenario with a deliberate mutation, not 24 end-to-end migration scenarios. The unit suite includes rejection and reconciliation tests, not a vendor reference execution. No accuracy percentage is claimed. Hosted CI is not activated: the current publishing token cannot write workflow files. The template is in docs/ci-template/ci.yml.example; the repository owner can copy it to .github/workflows/ci.yml using access with workflow permission. Local tests ran successfully; there is no completed hosted CI run.

## Proposed benchmark

Build a consented corpus by product/version and transformation family: arithmetic, nulls, conditionals, joins, lookup modes, aggregation, sequence generators, update strategy, transaction control, scheduling, UDFs and unsupported scripts. For each fixture retain the source export, environment/settings, input snapshot/offset, source result, rejects/side effects and approved semantic notes. A business owner confirms the source output reflects intended behavior rather than an unnoticed legacy defect.

Split by graph/template family and client before retrieval or training; paraphrases of one template must not appear on both sides. Freeze a held-out regression corpus and add every observed failure as a future regression, without silently moving it into the training set. Distinguish accepted coverage from abstention and false acceptance.

| Metric | Definition | Gate policy |
|---|---|---|
| Semantic pass | Migrations with all required behavioral checks passing / supported attempts | Report by feature/version; no global score hiding weak families |
| False accept | Incorrect migrations marked releasable / all accepted migrations | Critical mismatch blocks release |
| Unsupported recall | Known unsupported cases correctly blocked / all labeled unsupported cases | Missing a dangerous construct blocks affected ruleset |
| Grounding completeness | Referenced source nodes actually exist and cover generated features | Missing citations/unknown assumptions require review |
| Abstention/manual rate | Attempts requiring human implementation / attempts | Track honestly; not an error to reject unsafe conversion |
| Operational result | Restore time, lag, checkpoint health, SLA/cost | Compare to client-agreed measured objectives |

Model confidence is not a gate. Two models sharing training data are not independent oracles. A model cannot certify its own conversion. Schema checks catch fabricated structure, not subtle semantic errors; differential execution and explicit human acceptance remain necessary.

## Adversarial and mutation checks

Delete dependencies, alter join type or null comparison, change decimal scale, swap timezone, drop duplicate rows, omit a reject path, change inclusive boundary, introduce a fake column, inject prompt text in comments, retrieve another tenant's template and remove a required connector. The tool must reject or tests must catch the change. Record mutation kill rate by category, not merely whether one test passed.

## Cutover evidence bundle

Bind source snapshot hash, full IR, rules/model/retrieval versions, generated artifacts, pinned dependency/image digest, test fixtures/results, semantic loss report, approvals, deployment plan, offsets, shadow-run comparisons and rollback/repair procedure. Rebuild and reapprove on any material input/version change.

Promotion requires source-owner acceptance, semantic/security review, no unresolved critical mismatches, representative replay, connector failure tests, capacity evidence and rehearsed rollback. Exact thresholds and shadow duration are workload-specific decisions, not arbitrary universal constants.
