# Synthetic operational study

All records below are artificial test inputs, not production facts.

The study uses existing storage and scheduling algorithms; it proposes no new algorithm.
Its candidate contribution is an operational finding: rare metadata lock convoys coincide with backup windows in one deployment configuration.
The supplied trace summary says 8 of 10 observed convoy incidents overlapped backup windows; 2 did not.
A prototype deployment with shifted backup timing recorded fewer incidents, but traffic load also changed.
This is a possible operational or measurement contribution; causal attribution and novelty relative to prior operational reports remain unverified.
The paper claims the mechanism is proved and the remedy will work for every storage deployment.
Raw traces, workload controls, implementation details, and closest prior work were not supplied.
