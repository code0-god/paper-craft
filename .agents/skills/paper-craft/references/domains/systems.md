# Computer Systems review

Read for operating systems, distributed systems, storage, networking, cloud infrastructure, runtimes, resource management, scheduling, ML systems, or production experience. Respect the exact venue and track: implementation, measurement, and operational insights can be contributions without new algorithms.

Use the [shared scientific review](../core/scientific-review.md) and early [minimal alternative audit](../core/counterfactual-audit.md) for comprehensive reviews. Consider a simpler configuration, scheduling policy or integration under the same guarantees. Accept exclusions demonstrated by real constraints. Evaluate observation, measurement method and inferred cause separately using [evidence.md](../core/evidence.md); successful integration or operational knowledge need not imply algorithmic novelty.

## Problem, mechanism, and implementation

Identify the deployment constraint and whose outcome improves. Separate a trace-observed failure, hypothesized cause, prototype result, controlled deployment result, and production experience. Trace requests through the whole system and define boundaries, dependencies, trust assumptions, and integration cost. Confirm which components are implemented, emulated, mocked, or proposed.

Assess architectural invariants and failure assumptions before efficiency: consistency, persistence, isolation, scheduling fairness, recovery, security boundaries, and correctness under concurrency when claimed. Do not demand every property if the paper deliberately scopes it out; record the consequences of that scope.

## Evaluation aligned with claims

- **End-to-end behavior:** include client, queueing, network, serialization, storage, coordination, recovery, and runtime overhead relevant to the user-visible claim. A microbenchmark supports the measured component, not an unmeasured service.
- **Tail latency and throughput:** define percentiles, workload arrival model, offered versus achieved load, concurrency, sample counts, duration, warm-up, coordinated-omission risk, and saturation behavior. Average latency alone cannot support a p99 claim.
- **Scalability:** vary the dimension the claim names (nodes, requests, objects, tenants, data size); distinguish strong from weak scaling and bottleneck movement. Test imbalance and shared-resource contention when relevant.
- **Fault tolerance:** define the failure model, injection method, time-to-recovery, data loss/corruption checks, degraded behavior, and exclusions. Successful requests in a failure-free run do not establish recovery safety.
- **Overhead and integration:** account for CPU, memory, storage, network, deployment/migration burden, compatibility, maintenance, and system dependencies. Separate one-time costs from steady-state overhead.
- **Workload representativeness:** identify traces, privacy transformations, synthetic generators, skew, burstiness, access patterns, tenant diversity, version drift, and how the workload matches claimed deployment conditions.
- **Reproducibility and experience:** document configurations and data/trace availability, unavailable production resources, measurement instrumentation, failed approaches, anomalies, and operational lessons. An experience claim needs authentic observations and bounded context rather than a novel algorithm.

## Fair comparison and causal interpretation

Check baseline implementation versions, tuning, resource/capacity budgets, consistency or durability settings, cache state, client behavior, and capabilities. Compare designs that could serve the same task under compatible guarantees. Explain differing guarantees instead of treating all performance numbers as comparable.

Use controlled interventions, tracing, targeted ablations, or carefully qualified observational analysis for causal claims. Be explicit when an intervention cannot be performed in production. Do not replace a missing fault test with a hypothetical successful recovery story. Generalization beyond supplied deployments is a hypothesis.

Output findings by significance, soundness, end-to-end evidence, fairness, reproducibility, and limitations, linked to exact artifacts and evidence states.
