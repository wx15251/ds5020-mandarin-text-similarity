# Project context

Updated November 22, 2026. Student: **James Cottrell**. Solo DS5020 project: **Finding Similar Mandarin Texts Using Linear Algebra**.

## Current phase: Iteration 3 prepared for student review

On November 21, James supplied `reference/iteration3.pdf` and asked for a complete plan before beginning implementation. No instructor comments were supplied. Iteration 3 is due tomorrow night, November 22; the exact cutoff time was not supplied. Personal grading details remain in ignored `local/session_notes.md`.

The reviewed plan is in `iteration3/plan.md`. General requirements are on handout pages 1-4 and the Mandarin project on pages 16-17. Important additions are power iteration with deflation, a four-term/three-document worked example, at least three simulation sizes with an error-versus-n plot, a topic-overlap stress test, jieba word tokens compared with characters, energy-based real-data rank selection and top-five query results. Preserve the exact Iteration 2 data/model/seed baseline and explain required changes. Core methods must be NumPy-only in `src/methods.py`, with library solvers used for checks.

After reviewing the plan, James explicitly authorized completing the entire Iteration 3 continuously, including work initially scheduled for tomorrow. The core code, all experiments, 154 passing numerical comparison records, 18-page report/PDF/source ZIP and Excel update are prepared. The work is published to the existing public GitHub repository. After James signed into Overleaf, the new Iteration 3 project compiled using XeLaTeX, Viewer sharing was enabled, and the actual PDF export replaced `iteration3_report.pdf` on November 22. All 18 pages are pixel-identical at 72 DPI to the reviewed local build, and normalized extracted text matches on every page. The source was imported from pinned public GitHub URLs using an equivalent flattened LaTeX file and two figures; the ZIP was not uploaded. The existing Iteration 2 Overleaf deliverable remains complete. See `iteration3/working_notes.md` and `iteration3/overleaf_status.json` for evidence. The handout remains unchanged in `reference/`. Student review and solo checker/new-leader treatment remain open. The Iteration 4 handout is still unavailable.

Iteration 3 Overleaf Viewer: https://www.overleaf.com/project/6b0281bab7fa0104c2372496/share#27de20eef2575feba7a2a772b5d7b4ce9d2296e8fc7c43fd

## Earlier user decisions and Iteration 2 authorization

The user chose individual work and this folder as the main workspace. Their undergraduate background is Computer Science and Linguistics, and their goal is to apply vector representations and SVD to Mandarin topical similarity. The original Iteration 1 proposal remains unchanged in `iteration1/proposal.md`.

On November 13, the user authorized completion of the full Iteration 2, supplied their report name, and said the likely due date was Sunday, November 15 while aiming to complete that day. This replaced the earlier setup-only scope. At that time, there were no existing GitHub or Overleaf projects. No official template or solo checker clarification has since been supplied.

The new `/Users/jc/Downloads/iteration2-1.pdf` is byte-identical to `reference/iteration2.pdf` (17 pages). It adds no requirements or date. Keep instructor documents separate from user authorization.

## Completed local work

- Full LaTeX report and compiled PDF with Q1-Q5, full proofs, notation/assumptions, hand example, mathematical algorithm and operation counts.
- From-scratch cyclic Jacobi SVD, with library decomposition used only for final checks.
- Independent hand-example and numerical edge-case verification.
- Seed-0 50-term, 40-document, two-topic simulation with measured tables and probability/variance calculation.
- Downloaded and described 300 full THUCNews title/body documents (100 each sports, education, technology), 3,123 Chinese character terms.
- Source revision/hashes, finite-prefix sampling procedure, sample IDs, data audit, and figures documented.
- Overleaf upload ZIP and editable Excel plan.

GitHub repository: https://github.com/wx15251/ds5020-mandarin-text-similarity (public; anonymous read access verified November 14). Final push/verification is recorded in the project checklist. On November 14 the user signed into Overleaf and supplied the copied share link after authorizing ZIP upload. The new project, DS5020 Iteration 2 - Mandarin Text Similarity, compiled all 14 pages. Anyone with the share link has Viewer access. The actual Overleaf PDF export replaced the local PDF; all 14 rendered pages are pixel-identical at 100 DPI to the reviewed local build.

Overleaf project: https://www.overleaf.com/project/6af8a768417dd66bd7ceb644

Overleaf read-only link: https://www.overleaf.com/project/6af8a768417dd66bd7ceb644/share#5cf09d52a11ce3ef3245edb03868e4e76090c54ca34d8b25

## Method choices now in use

Characters U+4E00..U+9FFF; raw-count TF times natural-log unsmoothed IDF; no centering; terms-by-documents orientation. A retained positive singular-value cutoff comes from eigenvalues above `1e-12 * lambda_max`. Projected query coordinates match rows of V_k Sigma_k; folded query coordinates match rows of V_k. Do not mix these geometries.

The real dataset uses a pinned Tongjilibo mirror revision and a random sample from the eligible first 1,000 records per category. This limits representativeness. Topic labels are evaluation metadata, not representation inputs. The full real-data retrieval experiment is documented in Iteration 3.

## Remaining human/external steps

On November 14 the user explicitly approved making the existing GitHub repository public after being told that all current contents would be visible to everyone. The visibility change is complete. Anonymous API and README requests returned HTTP 200, and the repository API reports private=false. No instructor account or invitation is needed for reading. The standalone deliverables page was subsequently removed at the user's request; basic artifact links remain in README.

Author review and ability to explain the work; instructor's solo-checker/signature convention; any official template if later supplied. Overleaf setup, compilation, Viewer sharing, and actual PDF export are complete.

AI preparation is documented separately from student contributions. No invented signatures, independent checkers, student hours, approvals, or submission records. See `iteration2/submission_checklist.md` and `project_plan.xlsx`.
