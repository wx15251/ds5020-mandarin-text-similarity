# Project context

Updated November 14, 2026. Student: **James Cottrell**. Solo DS5020 project: **Finding Similar Mandarin Texts Using Linear Algebra**.

## User decisions and current authorization

The user chose individual work and this folder as the main workspace. Their undergraduate background is Computer Science and Linguistics, and their goal is to apply vector representations and SVD to Mandarin topical similarity. The original Iteration 1 proposal remains unchanged in `iteration1/proposal.md`.

On November 13, the user authorized completion of the full Iteration 2, supplied their report name, and said the likely due date is Sunday, November 15 while aiming to complete today. This replaces the earlier setup-only scope. They have no existing GitHub or Overleaf projects. No exact deadline, official template, or solo checker clarification has been supplied.

The new `/Users/jc/Downloads/iteration2-1.pdf` is byte-identical to `reference/iteration2.pdf` (17 pages). It adds no requirements or date. Keep instructor documents separate from user authorization. No Canvas submission has occurred.

## Completed local work

- Full LaTeX report and compiled PDF with Q1-Q5, full proofs, notation/assumptions, hand example, mathematical algorithm and operation counts.
- From-scratch cyclic Jacobi SVD, with library decomposition used only for final checks.
- Independent hand-example and numerical edge-case verification.
- Seed-0 50-term, 40-document, two-topic simulation with measured tables and probability/variance calculation.
- Downloaded and described 300 full THUCNews title/body documents (100 each sports, education, technology), 3,123 Chinese character terms.
- Source revision/hashes, finite-prefix sampling procedure, sample IDs, data audit, and figures documented.
- Overleaf upload ZIP and editable Excel plan.

GitHub repository: https://github.com/wx15251/ds5020-mandarin-text-similarity (private). Final push/verification is recorded in the submission checklist. On November 14 the user signed into Overleaf and supplied the copied share link after authorizing ZIP upload. The new project, DS5020 Iteration 2 - Mandarin Text Similarity, compiled all 14 pages. Anyone with the share link has Viewer access. The actual Overleaf PDF export replaced the local PDF; all 14 rendered pages are pixel-identical at 100 DPI to the reviewed local build.

Overleaf project: https://www.overleaf.com/project/6af8a768417dd66bd7ceb644

Overleaf read-only link: https://www.overleaf.com/project/6af8a768417dd66bd7ceb644/share#5cf09d52a11ce3ef3245edb03868e4e76090c54ca34d8b25

## Method choices now in use

Characters U+4E00..U+9FFF; raw-count TF times natural-log unsmoothed IDF; no centering; terms-by-documents orientation. A retained positive singular-value cutoff comes from eigenvalues above `1e-12 * lambda_max`. Projected query coordinates match rows of V_k Sigma_k; folded query coordinates match rows of V_k. Do not mix these geometries.

The real dataset uses a pinned Tongjilibo mirror revision and a random sample from the eligible first 1,000 records per category. This limits representativeness. Topic labels are evaluation metadata, not representation inputs. The full real-data retrieval experiment remains for Iteration 3.

## Remaining human/external steps

On November 14 the user asked for link-based GitHub access but does not have the instructor username. GitHub has no unlisted link-only repository visibility. Public visibility was explained and offered; the user's public/private choice is still pending. No repository visibility change or collaborator invitation has been made. The consolidated deliverables list is `iteration2/submission_links.md`.

Author review and ability to explain the work; instructor's solo-checker/signature convention; any official template if later supplied; instructor access to the private GitHub repository; final Canvas link submission. Overleaf setup, compilation, Viewer sharing, and actual PDF export are complete.

AI preparation is documented separately from student contributions. No invented signatures, independent checkers, student hours, approvals, or submission records. See `iteration2/submission_checklist.md` and `project_plan.xlsx`.
