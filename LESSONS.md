# Lessons for KOML

Attention sparsity is a property of an edge mask; fewer edges alone do not establish faster kernels or better model quality. Exact match detection and per-edge false positives measure different things and need separate definitions.

Validated by planted ground truth: four deterministic masks can be compared with exact integer arithmetic and fully reconciled counts. Changing supplied references changes the result. The assumption that structural sparsity demonstrates runtime benefit remains untested and is excluded from claims.

Operating rule: specify the unit of measurement and an independent reference before building a report, then corrupt that reference in a test to show the report computes rather than repeats metadata.
