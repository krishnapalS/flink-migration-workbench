# Flink migration workbench

A high-level design for moving legacy and cloud ETL estates to self-managed Apache Flink on AWS, with a small working deterministic compiler to make the core idea concrete.

The design treats migration as a compiler and evidence problem, not a prompt-to-code problem. A conversion is not approved simply because it compiles or a model sounds confident.

**Status:** HLD plus bounded proof of concept. Not an enterprise-ready Informatica converter. All inputs in this repository are synthetic. No customer data, credentials, source email or private correspondence is included.

## Read in this order

1. [High-level design](docs/HLD.md), including architecture and all design decisions.
2. [Architecture sketch](docs/architecture.svg) and [conversion gates](docs/conversion.svg).
3. [Semantic contract](docs/SEMANTICS.md) and [requirements coverage](docs/COVERAGE.md).
4. [Evaluation and cutover plan](docs/EVALUATION.md).
5. [Decisions and tradeoffs](docs/DECISIONS.md) and [sources](docs/SOURCES.md).
6. [Observed test evidence](artifacts/).

## Try it

Python 3.11+:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m migration examples/orders.xml --out build/demo
cat build/demo/mapping.sql
cat build/demo/manifest.json
```

The generated query retains orders whose fixed-decimal amount is at least 100.00. The IR is versioned and the manifest binds hashes to a ruleset. Unknown syntax fails closed, rather than being silently approximated. A successful compiler run returns `compiled_not_approved`, never production approval.

To execute the generated query on real Flink locally, install Java 11 and Maven 3.9+ and run:

```sh
./integration/run.sh
```

The integration harness uses Flink **1.20.5** for this reproducible demo, not as a claim that this is the newest release or a production support recommendation. It creates a bounded table with below-threshold, exact-boundary, duplicate, decimal and null rows, executes the generated SQL, compares its output to an explicit expected bag and proves that changing `>=` to `>` is detected. It uses an embedded local Flink mini-cluster, not AWS. Maven needs internet access to download dependencies. Runtime output is recorded in [artifacts/flink-runtime.txt](artifacts/flink-runtime.txt).

## What is implemented

- A strict, size-limited and entity-safe XML reader for a deliberately narrow PowerCenter-shaped synthetic fixture.
- A versioned relational IR with numeric comparison, direct projection and a small allowlisted `UPPER` expression in the JSON IR.
- Validated SQL emission, decimal precision checks, identifier validation, duplicate detection and fail-closed handling of unsupported inputs.
- Reproducible IR and SQL hashes, review-gate manifests, duplicate-aware typed reconciliation.
- Python unit tests and an actual Flink execution check with a deliberate semantic mutation.
- A CI workflow template for both layers, not activated because current publishing access cannot write workflow files.

## What is designed, not implemented

Real product/version-specific PowerCenter, BDM/DEI and IDMC adapters; inventory scanners; workflow/scheduler conversion; credential handling; model services; retrieval and rule-learning systems; connector provisioning; streaming conversion; AWS deployment; automatic source-versus-target differential validation; approval service and cutover automation.

The XML fixture is **PowerCenter-shaped**, not a vendor-certified export. Real exports have more metadata and may include a DTD. The demo rejects DTD/entity constructs and extra attributes. Production adapters must accept approved vendor structures safely and preserve all relevant metadata rather than stripping unknown fields. See [SEMANTICS.md](docs/SEMANTICS.md).

## Author

Krishna Pal Deora
