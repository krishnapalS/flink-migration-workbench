# Requirements traceability

| Design question | Answer location | Demonstrated or proposed? |
|---|---|---|
| Connect and ingest source systems | HLD §2 | Product adapter design; synthetic XML parser only implemented |
| Landing databases | HLD §3 | Proposed S3 + PostgreSQL; optional vector index |
| Convert imperfect legacy pipelines | HLD §4-5; SEMANTICS | Strict bounded subset implemented; full IR and adapters proposed |
| Learn from each migration | HLD §5 | Proposed outcome ledger and approved regression-rule promotion |
| Validate migrated output | HLD §6; EVALUATION | Actual Flink fixture execution + mutation implemented; legacy differential runs proposed |
| Avoid hallucinations | HLD §5-6; EVALUATION | Allowlisted deterministic compiler implemented; model benchmark/security controls proposed |
| Most performant language | HLD §9; DECISIONS | Qualified Java recommendation; no universal benchmark claim |
| No LLM allowed | HLD §5 | Demo uses no LLM and makes no model calls; production offline lane proposed |
| AI-first versus rigid components | HLD §5 | Explicit boundary design |
| Custom models and orchestration | HLD §5 | Proposed policy router, consented training and versioned evals |
| Human in the loop | HLD §8 | Proposed roles and gates; manifest names remaining gates |
| Other source products | HLD §10 | Adapter contracts and product-specific semantics proposed |
| Other targets and reverse direction | HLD §10 | Conditional bidirectionality with loss reports; not implemented |
| Explain component selections | DECISIONS; private walkthrough | Reasoning and alternatives documented |
