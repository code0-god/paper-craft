# Counterfactual and minimal alternative audit

Run early for consequential design choices in comprehensive technical reviews. Link the audit to claim IDs in the shared graph; it is not an optional novelty-only checklist.

For each consequential choice, record: claimed problem and observed mechanism; assumptions and constraints; closest realistic simple alternative; mathematical feasibility; implementation feasibility; predicted trade-offs; actual comparison evidence; justified claim and unresolved work. Ask what would happen without the component, with a simpler granularity or mapping, or under a competing explanation. Select alternatives that could test this claim; no fixed count or ablation quota.

Check constraints before calling an omitted baseline a flaw. If an alternative demonstrably violates capacity, interface, correctness or workload requirements, accept that exclusion and identify the evidence. A feasible alternative need not be faster. Adequate proof or a fair measured comparison can already justify a design; do not request redundant experiments. A missing comparison narrows necessity/superiority claims without erasing demonstrated utility or non-algorithmic systems contributions.

## Worked synthetic regression: per-row folding

Suppose a WS systolic-array draft argues that token-dependent activation block scales make stripe-shared scale necessary. Under the **changed quantization assumption of one common activation scale per row**, consider

\[
Y_{i,j}\simeq s_i^X\sum_b s^W_{b,j}P_{i,j}^{(b)}.
\]

This factors the common row scale out of the reduction over blocks in real arithmetic. It does not preserve arbitrary original block-local activation scales for free, remove block-dependent weight scales, or prove identical quantization error. Require the definitions of partial products and scales before claiming equivalence. Finite-precision transformations need a separate contract check.

Compare row and stripe choices on row metadata access/lifetime, output scaling units, interface bandwidth, execution order, array dataflow and accumulator capacity. Also compare quantization accuracy, residual work, data movement and hardware complexity at matched workload/quality. A mathematically possible row alternative may be impractical under the actual interface, or a useful baseline; available evidence decides.

Report a **Design Rationale / Argumentation** gap if the current premises establish a scale-management problem but do not establish stripe-sharing necessity. Suggest the bounded claim that stripe sharing is the evaluated solution under stated conditions; propose the missing feasibility or controlled comparison. Do not conclude per-row is superior, stripe sharing is universally unnecessary, or the actual paper/hardware has been read from this synthetic example.
