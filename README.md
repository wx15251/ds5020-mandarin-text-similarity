# Finding Similar Mandarin Texts Using Linear Algebra

James Cottrell | DS5020 Intro Linear Algebra & Probability | Fall 2026

This is the main workspace for the individual project. Iteration 2's local mathematical and computational deliverables are complete. Overleaf upload/read-only sharing, the instructor's solo-checker convention, and final student review/submission remain open.

## Deliverables

- [Compiled report](docs/iteration2_report.pdf): all five math questions, full proofs, notation, assumptions, a hand example, algorithm/costs, real-data description, and known-truth simulation.
- [Overleaf source ZIP](docs/iteration2_overleaf.zip): upload as a new Overleaf project. The PDF here is compiled locally from the same source; it has not been exported from Overleaf yet.
- [LaTeX source](docs/iteration2/main.tex) and [measured result tables](docs/iteration2/results/).
- [Excel plan](docs/project_plan.xlsx): owners, checker fields, task status, timeline, and contributions.
- [Submission checklist](docs/iteration2/submission_checklist.md): remaining actions and their exact status.
- [Check-in study guide](docs/iteration2/checkin_guide.md): the main ideas to explain in your own words.

GitHub: https://github.com/wx15251/ds5020-mandarin-text-similarity (private; instructor access still needs arranging).

Likely due date: Sunday, November 15, 2026, per the user's November 13 update; not confirmed. The working target was to complete preparation on November 13. No official Overleaf/Excel template has been supplied.

## Reproduce the computation

Use Python 3.12. All commands below run from the repository root.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python src/download_data.py
python src/verify.py
python src/simulation.py
python src/load_data.py
python src/build_report.py
```

`build_report.py` additionally needs a TeX distribution providing `pdflatex` and the packages used in `main.tex`. Overleaf can compile the source ZIP without a local TeX installation. The checked local environment is recorded in [environment.md](docs/iteration2/environment.md).

The input/output folders are committed as placeholders, so the scripts can be run after a normal clone. The downloader reads finite JSONL prefixes and records pinned URLs, revision, and SHA-256 hashes. Raw articles and derived document text/matrices stay out of Git. See [data/README.md](data/README.md) for acquisition and sampling details.

## Method and verification

The mathematical matrix is **terms by documents**. The real sample contains 300 full news documents, 100 each from sports, education, and technology, with 3,123 retained Chinese character terms. TF-IDF uses raw counts and natural-log unsmoothed IDF.

`src/svd_method.py` implements a cyclic Jacobi eigensolver on the smaller Gram matrix and derives the SVD factors from it. It does not call `numpy.linalg` solvers. The numerical cutoff and Gram-conditioning limitation are documented. Library SVD calls appear only in `verify.py` and `simulation.py` as final comparisons.

The seed-0 simulation uses 50 terms, 40 documents, two hidden topics, and 60 tokens per document. Checks include reconstruction, orthogonality, cosine bounds, query folding, and discarded-energy error. The custom singular values agree with NumPy within 2.14e-14 on that simulation. The hand example and tall/wide/rank-deficient/repeated/zero cases pass independent checks.

For retrieval, projected query coordinates `U_k.T @ q` must be compared with rows of `V_k Sigma_k`. The assigned folded query `Sigma_k^-1 U_k.T @ q` instead matches rows of `V_k`. These scalings generally change angles.

## Folder layout

```text
src/                       Acquisition, core numerical code, checks, report build
 data/raw/                 Local pinned source prefixes (ignored by Git)
 data/processed/           Local documents, vocabulary, matrices (ignored)
 data/source_manifest.json Source URLs, revision, byte sizes, hashes
figures/                   Generated data and simulation plots
 docs/reference/           Unchanged instructor PDFs
 docs/iteration1/          Original proposal, preserved verbatim
 docs/iteration2/          Requirements, report source, results, review notes
 docs/iteration2_report.pdf
 docs/iteration2_overleaf.zip
 docs/project_plan.xlsx
```

## Scope and authorship

Iteration 2 describes real data and verifies the mathematics on controlled examples; it does not claim a completed real-data retrieval experiment. The specific Iteration 3/4 handouts are still unavailable. Work was prepared with AI assistance. The Excel plan records preparation honestly and does not invent a second checker, signatures, or student hours. James should review the derivations and code before check-in or submission.
