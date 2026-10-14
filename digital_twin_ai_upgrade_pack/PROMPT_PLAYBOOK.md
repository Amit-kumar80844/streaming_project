# Prompt Playbook — Run the project upgrade end-to-end

Use `MASTER_AI_IMPLEMENTATION_PROMPT.md` for the complete task. The prompts below are focused recovery prompts if your coding agent hits context limits or finishes one workstream without completing the entire job. Run them **in the same repository and same agent session** so it can inspect the current code.

## Prompt 1 — Continue implementation, don't just describe it

> Review `MASTER_AI_IMPLEMENTATION_PROMPT.md` and `docs/IMPLEMENTATION_AUDIT.md`. Inspect the current Git diff and repository files. Continue implementing the remaining requirements directly in source. Do not repeat the plan. Preserve existing changes and user data. At the end, update the validation report with only checks actually run and mark anything unverified as NOT RUN.

## Prompt 2 — Fix Kafka and Spark connectivity

> Audit the actual Kafka producer, consumer, Compose listeners, topic setup, and Spark job. Fix the root causes of `NoBrokersAvailable` and `Failed to find data source: kafka`. Use the Compose DNS name for in-network connections; distinguish host and container listener configuration; add readiness/retry behaviour; resolve the exact Spark/Scala Kafka connector version; and create an integration smoke test that publishes and consumes an event. Do not only change error messages or suppress exceptions. Record effective versions and verification evidence in `docs/TROUBLESHOOTING.md` and `docs/VALIDATION_REPORT.md`.

## Prompt 3 — Fix model and Python dependency compatibility

> Inspect the serialized model artefacts and training code. Resolve the reported scikit-learn 1.5.1 versus 1.9.1 mismatch by pinning a compatible inference runtime or retraining/re-exporting all required artifacts in a consistent environment. Pin a supported Python/pandas/PySpark/Java set, verify feature ordering and scaler dimensions, and add a model-loading + deterministic prediction test. Do not suppress the warning without fixing compatibility. Document which artifacts were regenerated and what metrics were re-evaluated.

## Prompt 4 — Build the control plane and dashboard actions

> Inspect the actual services and APIs, then wire every visible Start/Stop/Restart, fault injection, reset, and log-viewing control to a real backend operation. Use an allowlisted service registry and accurate observed lifecycle states; add idempotency, timeouts, failure reporting, and state reconciliation. Keep the dashboard/controller alive while worker services are stopped. Do not expose Docker Engine to the browser or create an arbitrary shell endpoint. Confirm each button's effect with automated tests or explicitly report what remains unverified.

## Prompt 5 — Upgrade the UI without fake metrics

> Redesign the dashboard into a readable, responsive industrial observability console. Fix hierarchy, unused space, overly small labels, card density, chart axes/units, loading/empty/offline states, fault controls, service health, and audit history. Reuse the existing frontend stack unless there is a concrete reason to migrate. Make every chart and KPI use actual backend payloads. Clearly label simulated values, unavailable measurements, reproduced benchmark metrics, and paper-reported metrics. Remove dead controls and test wide/narrow layouts.

## Prompt 6 — Docker readiness and no-terminal startup

> Finalize the Compose-based build and local run experience. Ensure service DNS, healthy dependencies, Kafka topic readiness, Spark connector resolution, model artefact compatibility, environment variables, persistent data, and graceful shutdown are configured. Create a Windows double-click `start.bat` that checks Docker Desktop/Engine, starts/builds the stack, waits for the app's health check, and opens the UI; create a safe `stop.bat` that doesn't delete volumes. Verify the launcher as far as the environment allows and record any Docker-dependent checks not run.

## Prompt 7 — Produce the deep documentation and validate claims

> Read the actual final source, configuration, test results, and current Git diff. Generate/update every documentation file required in Workstream H of `MASTER_AI_IMPLEMENTATION_PROMPT.md`, including `docs/PROJECT_MASTER_GUIDE.md`. Explain each subsystem, event dataflow, every important file, formulas, class mapping, service lifecycle, Docker operation, UI controls, debugging, version compatibility, metrics provenance, safe extension steps, and roadmap. Do not invent behaviour or mark unrun checks as passed. Distinguish paper-reported figures, existing report claims, newly reproduced benchmark metrics, and live measurements.

## Prompt 8 — Final adversarial review

> Act as a reviewer who assumes the upgrade may still contain hidden failures. Check the Git diff and all requirements in `MASTER_AI_IMPLEMENTATION_PROMPT.md`. Look for fake/hardcoded telemetry, buttons that don't perform actions, duplicated pipeline events, unsafe Docker control, broken Compose networking, incompatible Spark connector coordinates, unresolved sklearn artifact warnings, unhandled task cancellation, broken browser reconnects, data loss on stop, inaccessible UI, inaccurate documentation, and unrun tests presented as passed. Fix issues you can reproduce; otherwise document evidence and the remaining blocker. End with a requirement-by-requirement pass/fail/not-run matrix.
