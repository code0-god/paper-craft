# Computer Architecture review

Read for processors, parallel architecture, caches/DRAM/NVM, memory hierarchies, accelerators, systolic arrays, DNN/LLM hardware, quantization, FPGA/ASIC, or compiler–architecture research. Select checks from the claims; no paper needs every metric below.

## Establish what was implemented and measured

Tag each result as **physical measurement**, **RTL simulation**, **cycle model**, **analytical model**, or **estimate**. Record platform or model version, calibration evidence, assumptions, workload, configuration, measurement boundaries, and uncertainty. For FPGA or ASIC flows distinguish synthesis estimates, placement/routing results, timing closure, and fabricated measurements. A modeled value is not a verified physical value.

Trace the workload through compute, memory hierarchy, communication, synchronization, and host/runtime overhead. Connect a claimed bottleneck to measurements or a clearly labeled hypothesis. Check whether local kernel gains survive full application execution, pre/post-processing, data transfer, memory capacity limits, and fallback paths.

## Claim-specific checks

- **Performance, latency, throughput:** define the metric and direction, batch size, concurrency, clock/frequency, warm-up, workload inputs, and inclusion of host/device transfer. Explain saturation versus single-request behavior.
- **Area, power, energy:** record process/library, synthesis conditions, voltage/frequency, memory and interconnect inclusion, power measurement or estimation method, and energy accounting interval. Area comparisons across technologies require explicit normalization assumptions; do not invent a scaling rule.
- **Memory traffic, data movement, bandwidth:** identify hierarchy level and transferred bytes, reads/writes, reuse, cache behavior, sparsity/packing overhead, and bandwidth constraints. Fewer operations do not establish fewer bytes or lower energy.
- **Utilization and complexity:** identify occupancy, pipeline stalls, control and buffer overhead, critical path, routing/resource constraints, and achievable timing. Peak operations per second is not sustained utilization.
- **DNN/LLM and quantization:** state model versions, tasks/datasets, numerical precision, calibration/training costs, sparsity assumptions, quality metrics, sequence lengths, prefill/decode distinction when relevant, and unsupported operations. Compare matched quality and workload conditions.
- **Scalability and design space:** test ranges justified by the claim; expose capacity walls, contention, workload regressions, design trade-offs, and sensitivity to uncertain parameters. Avoid arbitrary sweep or benchmark quotas.

## Baseline fairness and design rationale

Compare the closest plausible architecture and a simple design that tests the claimed insight. Align process assumptions, resource budgets, compiler/runtime tuning, memory capacity/bandwidth, precision/quality, and clock treatment where meaningful. Explain mismatches and which conclusions survive them. Novelty may lie in dataflow, scheduling, implementation feasibility, a new measured behavior, or a trade-off, not merely a larger array.

Use targeted ablations or alternate implementations to separate mechanism, scaling, and resource increases. Mark impossible comparisons and missing baselines as open evidence questions. Sensitivity studies can support robustness; they do not replace actual hardware verification for claims about a fabricated device.

Output a technical review, Claim–Evidence Matrix, Baseline Fairness Analysis, Missing Evaluation, and Priority Findings. Proposed tests must remain proposals with no result values.
