# Mathematical, numerical, hardware and evaluation contracts

Read alongside the domain guide when a core claim depends on arithmetic, implementation semantics or a model. Select relevant checks, state unperformed ones, and link each to the common argument graph.

| Contract | Record and challenge |
| --- | --- |
| Mathematical | Symbol definitions, variable domains, premises, approximation error, claimed equivalence, computation/reduction order and conditions for rearrangement. |
| Numerical | Integer widths, signedness, rounding and tie handling, overflow/underflow, saturation or wrap, shift semantics, accumulator/intermediate precision, fragment boundaries and reduction order. |
| Hardware | Dataflow, pipeline and fragment stages, buffer/accumulator bounds, metadata handling, memory traffic, utilization, area/timing/energy assumptions, host interface and schedule. |
| Evaluation | Measurement versus RTL/cycle/analytical model/estimate, model validation and uncertainty, baseline configuration, matched workload/quality, kernel versus end-to-end boundaries and excluded costs. |

An algebraic rearrangement over real or unbounded integer arithmetic does not prove equivalence after intermediate clipping or rounding. Map every arithmetic step to the stage that implements it. If the actual schedule, RTL or raw data are absent, leave implementation correctness unresolved; do not silently choose a convenient contract.

## Signed INT32 saturation counterexample

Define `sat32(x) = min(2147483647, max(-2147483648, x))`. Evaluate shifts as exact integer multiplication by `2**delta`, then saturate; the addition outside `sat32` below is exact, not an implicit wrapping INT32 add.

For `a = 1073741824`, `b = -1073741824`, `delta = 1`:

```
sat32(a * 2) + sat32(b * 2) = 2147483647 - 2147483648 = -1
sat32((a + b) * 2) = sat32(0) = 0
```

An additional final saturation on the first sum leaves `-1`, so the mismatch persists. Without clipping of the scaled intermediates, distributivity gives equality under this exact arithmetic contract; actual signed shifts, wrapping additions or rounding need their own semantics. The example disproves unrestricted equivalence, not a particular accelerator's correctness or the frequency of clipping in real workloads.

Run `python3 "$PAPER_CRAFT/scripts/numerical_contract_check.py"` for a reproducible JSON calculation. Record the invocation/output and classify it as numerical reproduction of this synthetic contract. To assess the real design, obtain fragment/block/final saturation order, widths, signs, legal operand ranges and traces; test whether reachable values include a counterexample. No RTL, simulation or hardware measurement is performed by this tool.

## Mixed modeled and measured latency

For a reported `host measured time + modeled accelerator cycles / assumed frequency`, inspect the schedule, units, frequency assumptions and model uncertainty. Excluded DRAM and host-device transfer means incomplete cost coverage; it does not by itself establish a mathematically strict end-to-end lower bound.

A lower-bound proof needs each retained term to bound its corresponding real cost and a valid composition under the actual dependency schedule. Nonnegative omitted costs can justify omission only within that composition. Adding host and device terms may overestimate elapsed time when execution overlaps; an optimistic or pessimistic cycle model has no guaranteed bound without evidence. Ask which costs are serialized, which overlap, whether costs are double counted, and whether measurements refer to matched workloads. Until justified, describe a mixed measured/modeled partial latency estimate, with exclusions and uncertainty, rather than a measured end-to-end latency or certified lower bound.
