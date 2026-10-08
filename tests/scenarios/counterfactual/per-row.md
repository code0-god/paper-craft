# Synthetic manuscript: scale sharing

## Question and design
We target weight-stationary systolic matrix multiplication with activation scales that vary across token rows and blocks. Partial integer dot products are P(i,j,b); weight scales are sW(b,j). The baseline quantizer uses activation scale sX(i,b).

We replace these with one activation scale shared over a stripe of token rows. Because token rows otherwise have different scales, only stripe sharing can move activation scaling after the block reduction. Thus stripe sharing is necessary for efficient output folding.

## Evaluation boundary
We evaluated only stripe sharing against the original block-local quantizer. No alternative activation scale granularity was evaluated. Row metadata lifetime, output scaling bandwidth and residual cost comparisons are not provided. Quality under a different activation quantizer has not been measured. There is no RTL or executable model attached.
