# Synthetic positive control: bounded design choice

## Scope
This design targets a fixed interface with one scale register per stripe and no per-row scale address field. The supplied interface contract is authoritative for this synthetic exercise. Changing the interface is outside the claimed drop-in compatibility scope.

## Comparison
Our stripe design and a simple block-local baseline both satisfy the interface and a maximum 1% error requirement. In the manuscript's paired simulator records at the same clock, workload, memory capacity and precision, stripe cycles are [80, 82, 81] and baseline cycles are [100, 102, 101]. Error is 0.8% and 0.6%, respectively. These are synthetic reported records, not independent hardware results.

## Claim
For these three simulated inputs, stripe sharing satisfies the fixed interface and error requirement and uses fewer modeled cycles than the tested baseline. We do not claim superiority over a redesigned interface or mathematical necessity of stripe sharing. The contribution is integration of established blocks into a compatible execution path; global novelty remains open pending prior-work comparison.
