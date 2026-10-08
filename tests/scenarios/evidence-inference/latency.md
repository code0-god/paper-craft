# Synthetic manuscript: latency accounting

## Method
Host execution is measured. Accelerator service time is computed from a cycle model at an assumed frequency. DRAM transfer and host-accelerator transfer costs are excluded. No calibration error bound or execution-overlap schedule is supplied.

## Conclusion
We sum measured host time and modeled accelerator service time. Since transfer costs are excluded, this sum is a rigorous lower bound on end-to-end latency, and it constitutes an end-to-end latency measurement.

Only this description is available; no actual timing values, raw data, code or hardware measurements accompany the excerpt.
