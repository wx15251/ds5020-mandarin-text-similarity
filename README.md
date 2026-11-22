# Finding Similar Mandarin Texts Using Linear Algebra

James Cottrell | DS5020 Intro Linear Algebra & Probability | Fall 2026

This is the main workspace for the individual project. Iteration 3 implements SVD by power iteration with deflation, verifies a four-term worked example and controlled simulations, and compares character and jieba word representations of the same 300 Mandarin news documents. The code, measured results and local report are prepared. The existing GitHub repository is public.

## Project files

[Iteration 3 report PDF](docs/iteration3_report.pdf), [Excel project plan](docs/project_plan.xlsx), [Overleaf source ZIP](docs/iteration3_overleaf.zip), and [explanation guide](docs/iteration3/checkin_guide.md).

[GitHub repository](https://github.com/wx15251/ds5020-mandarin-text-similarity). The Iteration 3 Overleaf upload/export is pending an authenticated owner session; the PDF above is the verified local XeLaTeX build.

Iteration 2 remains archived: [PDF](docs/iteration2_report.pdf), [source ZIP](docs/iteration2_overleaf.zip), and [Overleaf Viewer project](https://www.overleaf.com/project/6af8a768417dd66bd7ceb644/share#5cf09d52a11ce3ef3245edb03868e4e76090c54ca34d8b25).

## Reproduce the computation

Use Python 3.12. All commands below run from the repository root.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python src/download_data.py
python src/small_example.py
python src/verify_iteration3.py
python src/check_simulation.py
python src/run_real.py
python src/build_iteration3_report.py
```

`small_example.py` prints every tiny-example stage. `check_simulation.py` runs the unchanged baseline, three sample sizes and the overlap stress test. `run_real.py` reconstructs the fixed sample from the original manifest, saves both tokenizations, selects rank, produces query results and checks against libraries. The extra `verify_iteration3.py` tests numerical edge cases.

The report builder needs XeLaTeX with `ctex` and Fandol fonts. On Overleaf, upload the source ZIP and select **XeLaTeX**. The [environment record](docs/iteration3/environment.json) and lock file document tested versions. Commands run on a normal clone after downloading the pinned raw prefixes; no previously processed data are required.

The input/output folders are committed as placeholders, so the scripts can be run after a normal clone. The downloader reads finite JSONL prefixes and records pinned URLs, revision, and SHA-256 hashes. Raw articles and derived document text/matrices stay out of Git. See [data/README.md](data/README.md) for acquisition and sampling details.

## Method and verification

The mathematical matrix is **terms by documents**. The sample contains 100 documents each from sports, education and technology. Character TF-IDF is 3,123 x 300; word TF-IDF is 19,800 x 300. Both use raw counts and natural-log unsmoothed IDF.

`src/methods.py` implements the new core using basic NumPy operations, with equation comments E1-E14. It uses power iteration, two-pass reorthogonalization and deflation on the smaller Gram matrix, with explicit convergence and positivity checks. Library SVD/cosine/TF-IDF routines are used only for verification. jieba is used only for preprocessing. The prior Jacobi solver in `svd_method.py` remains preserved for Iteration 2.

The 50-term, 40-document, seed-0 simulation exactly reproduces Iteration 2, with extensions to 200 and 1000 documents. The stress test merges topic distributions. All 154 deterministic comparison records pass; maximum singular-value disagreement is 9.09e-13 and maximum reduced-cosine disagreement against a reference SVD is 1.62e-10. See [measured evidence](docs/iteration3/results/verification_all.csv).

At 90% energy, the selected ranks are 137 for characters and 176 for words. Both topic-cosine gaps increase, but word nearest-topic agreement falls from 0.943333 to 0.896667 after reduction. The fixed query also reveals weak matches. Energy preservation and numerical agreement do not establish improved semantic retrieval. [Working notes](docs/iteration3/working_notes.md) describe the interpretation and limits.

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
 docs/iteration3/          Plan, report source, measured results and review guide
 docs/iteration2_report.pdf
 docs/iteration2_overleaf.zip
 docs/iteration3_report.pdf
 docs/iteration3_overleaf.zip
 docs/project_plan.xlsx
```

## Scope and authorship

This is an in-corpus descriptive study with no held-out generalization claim. Source-prefix sampling, imperfect topic labels, bag representations and related articles limit interpretation. The Iteration 4 handout remains unavailable. Work was prepared with AI assistance. The Excel plan records assistance separately from supplied student contributions and does not invent a second checker, signatures or student hours. James's review and the instructor's solo-checker convention remain open. No official report/Excel template has been supplied.
