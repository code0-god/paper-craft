# Scientific reasoning evaluation protocol

Use `../scientific-cases.json` as the evaluator manifest. All fixtures are controlled synthetic excerpts, including the PoTal-inspired cases. They are not evidence about an actual paper, implementation or hardware.

For each case start a fresh host session with the installed updated skill, provide only that case's inputs and prompt, and save the complete response, host/model/version, date, input SHA-256 hashes, actual invocation, exit code and tool outputs. Do not show expected criteria or other cases to the reviewing model. Use `review_output.py` for a local output destination. Source inputs must remain byte-identical. Different modes may reuse only hash-matching evidence and must reassess conclusions, not assume prior correctness.

An independent evaluator then reads the input, full response and manifest. For every criterion, record PASS/FAIL/UNKNOWN with exact response and source locators and substantive reasoning. Judge correct problem discovery, mathematical/technical validity, evidence restraint, false positives, concrete remedies and consistency. Do not count words or keywords as correctness. Any hard failure fails the case; missing or ambiguous evaluation stays UNKNOWN. A tool/unit-test pass does not pass a semantic case.

Repeat cases in independent sessions when feasible, preserving individual judgments and contradictions instead of reporting only the best run. For contradictory judgments compare assumptions and source locators, explain resolution or mark unresolved. Record unexecuted model cases as NOT_RUN, never as inferred passes. Numerical tool output can establish the synthetic arithmetic result only; scientific interpretation and real implementation claims require separate evaluation.
