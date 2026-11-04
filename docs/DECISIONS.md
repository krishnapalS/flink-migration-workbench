# Decision record

| Decision | Reason | Alternative and when to change |
|---|---|---|
| Compiler + typed IR | Explicit semantics, repeatable rules, common validation | Direct code translation is simpler initially but makes safety and multiple backends harder |
| S3 artifacts + PostgreSQL metadata | Large immutable bundles plus transactional job/approval state | Graph DB only if measured traversal demand justifies it |
| Java production core and custom Flink operators | JVM ecosystem and type/tool integration | Rust for measured parse bottleneck; Python for readable prototype/evaluation |
| Flink SQL first where semantics fit | Relational plans are inspectable and target-validated | DataStream for state/time/custom logic; no forced SQL approximation |
| AI-assisted proposals, deterministic promotion gates | Helpful with undocumented patterns without surrendering release control | Deterministic-only mode where policy forbids all models |
| Retrieval before custom training | Lower setup cost and easier provenance for early learning | Fine-tune after consented data and benchmark show a real gap |
| EKS application clusters | Isolation and operator lifecycle fit a self-managed AWS target | EC2 if Kubernetes expertise/overhead makes it unsuitable |
| Explicit manual queue | Safe coverage beats silent semantic loss | Expand capability only with a tested rule/adapter |
| Conditional round-trip support | Target-specific features can be lossy | Preserve source/extension nodes and issue a loss report |
| Bounded prototype | Demonstrates the core gate clearly without claiming unknown vendor semantics | Add stateful support only with source oracle, connector and recovery tests |

No language, database or model is universally best. Production choices depend on observed estate complexity, team skills, compliance, volume and operating budget. These are design recommendations, not measured performance comparisons.
