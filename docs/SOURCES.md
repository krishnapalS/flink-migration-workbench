# Technical sources

Consulted 5 November 2026. Primary documentation is preferred for capability claims. Architecture choices are proposals, not vendor guarantees. URLs using `stable`, `main` or `current-version` can change; production work must pin compatible release documentation. The runnable demo pins Flink 1.20.5 separately.

1. **Informatica, ObjectExport, 10.5.10 command reference.** Supports the PowerCenter XML export and dependency-flag discussion. Does not certify this demo's synthetic parser.
   https://docs.informatica.com/data-integration/common-content-for-data-integration/10-5-10/command-reference/pmrep-command-reference/objectexport.html
2. **Informatica, Exporting objects, platform REST API v3.** Supports the object-ID/export-job/status/ZIP flow and dynamic rate-limit caveat. Service/tenant applicability still needs checking.
   https://docs.informatica.com/integration-cloud/cloud-data-integration-for-powercenter/current-version/rest-api-reference/platform-rest-api-version-3-resources/exporting-objects.html
3. **Apache Flink, Checkpointing.** Supports the recovery/checkpoint and external-sink caveats; defaults do not prove end-to-end guarantees.
   https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/fault-tolerance/checkpointing/
4. **Apache Flink, Savepoints.** Supports savepoint restoration and operator-ID/state compatibility discussion. Not a cross-product rollback mechanism.
   https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/savepoints/
5. **Apache Flink Kubernetes Operator, Lifecycle Management.** Supports reconciliation, snapshot ownership, upgrades and recovery concepts. Main-branch documentation is not a release compatibility guarantee.
   https://nightlies.apache.org/flink/flink-kubernetes-operator-docs-main/docs/concepts/lifecycle-management/
6. **AWS, High availability for Flink Operators and Applications.** An EMR-on-EKS example of S3 HA metadata and JobManager configuration. It informs AWS operational design but is not an upstream-Flink deployment recipe or proof that this project deployed AWS.
   https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/jobruns-flink-using-ha.html
7. **OpenLineage, Facets & Extensibility.** Supports the job/run/dataset lineage exchange model and versioned custom facet concept.
   https://openlineage.io/docs/spec/facets/
8. **Maven Central, Flink Java Table API bridge metadata.** The 1.20.5 version was available at verification time; runtime dependencies were resolved and executed locally. This does not imply newest release or a support policy.
   https://repo.maven.apache.org/maven2/org/apache/flink/flink-table-api-java-bridge/maven-metadata.xml

## Remaining source checks for production

BDM/DEI version-specific exports and privileges; actual IDMC service entitlement/asset coverage; deployed Flink/operator/Java/connector compatibility; source CDC retention; sink transaction guarantees; client AWS security and operating standards. These are discovery tasks, not assertions of completed support.
