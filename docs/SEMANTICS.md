# Semantic contract and honest limits

## Demo contract

- Bounded inputs only; no event time, watermarks, updates, deletes or state.
- SQL three-valued null filtering: a null comparison does not pass `WHERE`.
- Unordered row bags; duplicates are preserved, not deduplicated.
- BIGINT, STRING and DECIMAL(18,2). Decimal literals arrive as strings, never binary floats. Excess precision/scale and BIGINT overflow are rejected.
- One numeric comparison (`ge`, `gt`, `le`, `lt`, `eq`) with matching operand types.
- Direct field projection and typed literals; `UPPER` is available only through the JSON IR. Its locale/Unicode behavior still requires source-specific comparison before production use.
- One synthetic XML source/filter/target chain with exactly two pass-through edges per field. Real PowerCenter instances, mapplets, sessions, SQL overrides, parameters and workflow metadata are not supported.
- Output is a SELECT, not connector DDL, job submission or an operational deployment.

## Fail-closed behavior

Unknown node/attribute, unsupported type, unsafe identifier, bad connector, invalid numeric literal, mismatched schema or unsupported mode results in `REJECTED` and exit code 2. No artifacts are written before validation succeeds. Existing artifacts in a reused output directory are not deleted by a rejected run; callers must use a fresh directory per immutable attempt and check exit status. Production orchestration must never reuse a stale artifact after failure.

The parser uses defusedxml to reject entity expansion and unsafe XML. Size is capped at 1 MiB for the demo. Production intake also needs stream-level size limits, archive extraction quotas, CPU/memory timeouts, schema-controlled DTD handling and sanitized logs. The demo is not a hardened multi-tenant service.

## Source compatibility is not proven

The example is a minimal PowerCenter-shaped XML document constructed for this proof of concept. It is not an export from a licensed Informatica runtime, does not validate against the vendor DTD and is not evidence of support for a production PowerCenter version. A real export may be rejected for extra metadata. Never remove unknown metadata merely to make it pass.

Flink execution validates the generated query on a small typed fixture. It does not validate Informatica behavior, JDBC/CDC connectors, external transaction semantics, distributed failure behavior or representative performance.

## Production IR additions

A real IR must carry provenance per node, graph ports, reference resolution, parameters, full type metadata, source null/collation/timezone rules, reject paths, state/time/transaction semantics and unknown features. A capability matrix must prevent code generation when those semantics cannot be represented. A source change, ruleset change or target-version change must invalidate prior evidence and approval.
