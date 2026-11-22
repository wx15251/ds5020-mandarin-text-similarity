# Source code

Run scripts from the repository root using the pinned Python environment.

Iteration 3 entry points and shared modules:

| File | Purpose |
| --- | --- |
| `methods.py` | NumPy-only `my_` functions, equations E1-E14, power iteration and deflation |
| `simulate.py` | Reusable generator preserving the exact original draw order |
| `small_example.py` | Four terms, three documents, every intermediate and an independent check |
| `check_simulation.py` | Truth/library checks, three sizes, sampling-error plot and topic-overlap stress |
| `preprocess_text.py` | Rebuild fixed sample from manifest and save character/jieba tokens |
| `run_real.py` | Both tokenizations, energy-selected rank, top-five query results and audits |
| `verification_helpers.py` | Library checks, common comparison log and evidence paths |
| `verify_iteration3.py` | Tall/wide/rank-deficient/repeated/invalid/nonconvergent cases |
| `build_iteration3_report.py` | Evidence-to-LaTeX tables, XeLaTeX build and Overleaf ZIP |

For reproducibility, run the three required entry points in the order shown in the root README. Library solvers are confined to comparison code. The report builder runs after all result scripts. The code below remains the Iteration 2 implementation and reproduction path.

| File | Purpose |
| --- | --- |
| `download_data.py` | Acquire 1,000 records per category from a pinned mirror revision and record provenance |
| `text_vectors.py` | Character filtering, explicit counts/TF-IDF, query vector, cosine and pair summaries |
| `svd_method.py` | Cyclic Jacobi eigensolver and SVD factors from the smaller Gram matrix |
| `verify.py` | Hand example and independent tall/wide/rank-deficient/repeated/zero/edge-case checks |
| `simulation.py` | Seed-0 known-topic simulation, identities, probability estimates, and figure |
| `load_data.py` | Real-data sample, missingness/type audit, matrix, and exploratory plots |
| `build_report.py` | Measured CSV-to-LaTeX tables, local compilation, and Overleaf ZIP |

The core numerical code uses basic NumPy operations; `numpy.linalg.svd` occurs only in final reference checks. No library routine solves the core decomposition. pandas handles data tables, and Matplotlib produces figures. Standard-library imports are used for file/network/build operations, not as extra numerical/NLP dependencies.

The Gram approach squares the nonzero condition number and discards eigenvalues at or below `1e-12 * lambda_max`. It is intended for the small checked Iteration 2 problems. The real-data script constructs/describes TF-IDF without running the later full retrieval experiment.
