# HW/SW co-design review

Use with [architecture.md](architecture.md) and, for service claims, [systems.md](systems.md). Cover compiler–architecture interaction, heterogeneous execution, FPGA/ASIC accelerators, runtime scheduling, and quantized ML deployments.

Use the same claim graph and [contract audit](numerical-contracts.md) across compiler transformations and hardware execution. Check signedness, intermediate precision, saturation stages and reduction order on both sides of the interface. A real-arithmetic proof or source listing alone does not establish actual device behavior. Run the [alternative audit](../core/counterfactual-audit.md) before declaring a cross-layer choice necessary.

Map each proposed change to hardware, compiler, runtime, model/algorithm, and deployment interface. State the contract: supported operations, layouts, precision, scheduling, memory ownership, synchronization, error/fallback behavior, and required software transformations. Separate an implemented joint design from components tested independently.

Ask which mechanism creates the end-to-end benefit. When practical, compare original HW/original SW, changed HW/original SW, original HW/changed SW, and changed HW/changed SW; do not mandate an invalid quadrant when compatibility makes it impossible. Explain such constraints and use a feasible alternative to isolate effects.

Align baseline numerical quality, functionality, resource budgets, compilation/training effort, and runtime conditions. Include layout conversion, transfer, compilation/amortization, calibration, unsupported-operation fallback, buffer growth, and orchestration costs when these affect the claim. Avoid attributing gains to architecture when changed algorithms, data, precision, or batch sizes account for them.

Check joint feasibility: achievable timing and area/power assumptions, compiler mappings, buffer bounds, memory/communication pressure, operator coverage, and real execution constraints. Simulator plus abstract compiler mapping does not establish a completed fabricated accelerator. Validate the boundary where one component relies on another's assumptions.

A contribution can be a new cross-layer principle, integrated capability, practical design trade-off, or measured operational result. Describe the closest integrated alternative, why a simpler composition is insufficient, and the evidence for the resulting system effect. Keep candidate explanations separate from established results.
