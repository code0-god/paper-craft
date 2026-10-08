# Synthetic manuscript: alignment semantics

## Alignment argument
The design shifts signed INT32 partial sums by delta before adding them. By distributivity, saturation of each shifted fragment followed by addition is exactly equivalent to shifting the sum and applying saturation once. This statement holds for all legal INT32 operands and delta = 1.

## Implementation boundary
Fragment results may be saturated independently. The final accumulator width and final clipping policy are unspecified. Raw traces, RTL and simulator source are unavailable. The manuscript gives no operand-range proof that avoids clipping. No evidence establishes which extreme operands occur in workloads.
