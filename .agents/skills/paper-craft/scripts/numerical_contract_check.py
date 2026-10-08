#!/usr/bin/env python3
"""Evaluate a bounded synthetic signed-saturation contract; never execute TeX/RTL."""
from __future__ import annotations

import argparse
import json
from typing import TypedDict


class ContractResult(TypedDict):
    width: int
    a: int
    b: int
    shift: int
    fragment_a: int
    fragment_b: int
    fragment_sum: int
    fragment_sum_final_saturation: int
    joint_saturation: int
    equivalent: bool
    equivalent_after_final_saturation: bool
    verification_scope: str
    contract: str
    limitation: str


def saturate(value: int, width: int) -> int:
    return min((1 << (width - 1)) - 1, max(-(1 << (width - 1)), value))


def evaluate(a: int, b: int, shift: int = 1, width: int = 32) -> ContractResult:
    if not 2 <= width <= 64 or not 0 <= shift <= 64:
        raise ValueError("width must be 2..64 and shift must be 0..64")
    lower, upper = -(1 << (width - 1)), (1 << (width - 1)) - 1
    if not lower <= a <= upper or not lower <= b <= upper:
        raise ValueError("a and b must fit the selected signed width")
    left, right = saturate(a * (1 << shift), width), saturate(b * (1 << shift), width)
    total = left + right
    final = saturate(total, width)
    joint = saturate((a + b) * (1 << shift), width)
    return {
        "width": width, "a": a, "b": b, "shift": shift,
        "fragment_a": left, "fragment_b": right, "fragment_sum": total,
        "fragment_sum_final_saturation": final, "joint_saturation": joint,
        "equivalent": total == joint, "equivalent_after_final_saturation": final == joint,
        "verification_scope": "numerical_reproduction",
        "contract": "Signed saturation; scaling and addition use exact Python integers; no wrap or rounding.",
        "limitation": "Synthetic arithmetic only; no workload, source-code, RTL, simulator or hardware execution verified.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=32)
    parser.add_argument("--a", type=int, default=1 << 30)
    parser.add_argument("--b", type=int, default=-(1 << 30))
    parser.add_argument("--shift", type=int, default=1)
    args = parser.parse_args()
    try:
        result = evaluate(args.a, args.b, args.shift, args.width)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
