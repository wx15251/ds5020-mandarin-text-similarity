# Iteration 2 working notes

Updated November 14, 2026. The initial proposals have now been implemented in the local Iteration 2 deliverables. See `main.tex`, the compiled report in `../iteration2_report.pdf`, and `results/` for full arguments and actual measurements.

## Decisions implemented

- Student/sole owner: James Cottrell. User authorized full completion on November 13.
- Likely deadline: Sunday, November 15; working completion target November 13. Exact date remains unconfirmed.
- No official report/Excel template was provided; the local report and plan are working formats.
- Three THUCNews categories, 100 articles each, sampled reproducibly from a documented finite prefix.
- Character terms U+4E00..U+9FFF. Terms-by-documents TF-IDF, raw TF, unsmoothed natural-log IDF, no centering.
- Core SVD implemented from basic NumPy operations with a cyclic Jacobi eigensolver. This satisfies the stricter library policy; decomposition calls are confined to verification.
- Zero vectors are rejected for cosine. Small Gram eigenvalues are excluded explicitly. No word-segmentation package is used.

## Coordinate convention

Projected documents are rows of D = V_k Sigma_k; compare them with z = U_k^T q. The assigned folded map q-hat = Sigma_k^-1 U_k^T q returns the corresponding row of V_k for an existing document. Compare folded queries with V_k rows if deliberately using that geometry. Since z = Sigma_k q-hat, unequal singular values generally change angles between the two systems.

The hand example uses C = [[2,0,1],[0,2,1]], with common IDF log(3/2). It fully derives both singular directions and shows that rank one makes originally orthogonal documents have cosine one. The report includes a projector-based proof of Frobenius optimality as well as cosine, SVD-construction, projection, and folding proofs.

## Measured results

The real sample has 300 documents, 3,123 terms, 94,011 nonzero TF-IDF entries, no zero columns, and no exact duplicates after filtering. The simulated matrix has 50 terms and 40 documents with known topic labels and probabilities; it has numerical rank 40, not two. Rank-two within-topic cosine is 0.999877 versus original 0.729660, excluding self-pairs. Both representations already have same-topic nearest-neighbor rate one. Custom/library singular-value maximum error is 2.13e-14. These are controlled simulation results, not real-data retrieval claims.

## Still unresolved

Overleaf upload, 14-page compilation, Viewer sharing, and actual PDF export were completed on November 14 after the user signed in. Artifact links are in README and export provenance is in `overleaf_export.json`. Independent checker/signature treatment for solo work requires instructor guidance. The user approved public GitHub visibility on November 14; anonymous read access is verified, so no instructor invitation is required. Final author review remains open. No permission question is needed for continued local verification and documentation.

For the next working session, review the finished report with the student, especially the proof of optimality, the coordinate scaling distinction, and the finite-prefix sampling limitation. Do not restart the initial setup or rerun unrelated checks without a reason.
