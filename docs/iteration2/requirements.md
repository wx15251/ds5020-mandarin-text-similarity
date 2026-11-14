# Iteration 2 requirements

This checklist paraphrases the supplied course documents. Updated November 14, 2026: report/computation, GitHub, and Overleaf setup/export are complete; remaining student/access steps are tracked in `submission_checklist.md`. This is a project requirements map. Page numbers refer to the unchanged PDFs under `../reference/`. The November 13 attachment is byte-identical to the original.

## General requirements from iteration2.pdf, pages 1-3

| ID | Requirement | Evidence / remaining action |
| --- | --- | --- |
| R01 | Assign a project leader and record an owner and checker for every derivation/question. | Excel plan; student is the solo lead/owner, checker convention pending |
| R02 | Give a notation table with every symbol, meaning, and dimensions. | Report: Notation and Definitions |
| R03 | Formally define every mathematical object used; specify what rows, columns, and entries represent. | Definitions and Q1 |
| R04 | List needed assumptions; explain consequences of failure and checks planned for Iteration 3. | Report: Assumptions |
| R05 | Prove at least three key results as theorems/propositions, showing steps and naming rules. | Q2-Q5 and supporting propositions |
| R06 | Answer every project-specific question under the required Math Questions heading. | All five Mandarin questions |
| R07 | Give numbered mathematical algorithm steps, matrix sizes, and operation counts per step. | Report: Algorithm |
| R08 | Load real data; describe rows, columns, variables/types, missing values, and one or two plots. | Data-loading script, figures, report |
| R09 | Simulate a small dataset with known truth, using `np.random.default_rng(0)`. | Simulation script and recorded outputs |
| R10 | Include Simulation Check: model, parameters, sample size, truth/estimate table, and a sentence connecting each derivation to a numerical check. | Report: Simulation Check |
| R11 | Keep all code in `src/`; use only NumPy, pandas, Matplotlib, and scipy.stats unless permitted otherwise; whole-method library routines only for final comparison. | Source code and method/comparison separation |
| R12 | Set up GitHub with `src/`, `data/`, `figures/`, `docs/`; keep large raw files out of Git; document downloads. | Public GitHub repository and README; anonymous read access verified November 14 |
| R13 | Set up Overleaf using the Iteration 2 template. | Overleaf project created and compiled; Viewer link saved; no official template supplied |
| R14 | Update an Excel plan with task ID, task, owner, checker, status, timeline, and contributions. | `../project_plan.xlsx` |
| R15 | Place the exported Overleaf report PDF in `docs/`. | Actual Overleaf export in `../iteration2_report.pdf`, November 14 |
| R16 | Provide the GitHub repository and Overleaf read-only links. | Public repository and Viewer link available in README |

Each derivation owner signs their work and the checker signs "checked by." The assignment uses team language without explaining how an individual student should satisfy the second-person check. Record the instructor's clarification before filling signatures; do not invent a second member.

## Mandarin-specific questions from iteration2.pdf, page 15

All five are required. The minimum of three derivations does not replace the requirement to answer all five questions.

| Question | Assigned content, paraphrased | Working plan |
| --- | --- | --- |
| Q1 | Define the term-document matrix and TF-IDF, including one entry's meaning. | Terms in rows, documents in columns; explicitly state TF/IDF convention |
| Q2 | Define cosine similarity and prove its range is [-1,1] using Cauchy-Schwarz. | Full proposition and proof for nonzero vectors |
| Q3 | State Eckart-Young and explain why the truncated SVD is the best rank-k approximation. | State norm and rank constraint; derive Frobenius tail-error identity |
| Q4 | Show that reduced document similarities are cosines of rows of V_k Sigma_k. | Derive reduced coordinates using orthonormality |
| Q5 | Derive the query map q-hat = Sigma_k^(-1) U_k^T q. | Derive folded coordinates and relate them to Q4's scaled coordinates |

See `working_notes.md` for the distinction between the Q4 and Q5 coordinate conventions. The report must retain both assigned formulas and explain their relationship.

## Data and simulation from iteration2.pdf, page 16

The handout suggests topic-labeled Chinese news (for example a few hundred THUCNews articles in 3-5 categories), or LCQMC labeled question pairs. Terms may be single characters or segmented words. It mentions jieba, although jieba is outside the general allowed-import list; character terms avoid needing that clarification initially.

The sample simulation uses:

- 50 terms, 40 documents, two hidden topics with 20 documents per topic.
- Two chosen topic term distributions sampled from Dirichlet distributions, followed by 60-token multinomial documents.
- Count TF times `log(n_docs / max(df, 1))` IDF.
- A rank-2 SVD representation and cosine comparison within/across topics.
- An existing document used as a query to check the folded-coordinate formula.
- The Frobenius reconstruction error compared with the sum of discarded singular values squared.

These are the instructor's starter settings. Our completed simulation implements them with the custom SVD, omits self-pairs from within-topic statistics, handles zero vectors, and records actual measurements in `results/`.

## Additional final-project requirements from DS5020_Final_Project_Ideas.pdf

Pages 1-2 also require:

- A tiny hand-worked example before real-data application, checked against code.
- A core implementation built from basic numerical operations, plus a library comparison and a reported numerical difference.
- At least one interpreted probability, expected value, variance, or interval.
- A final LaTeX math appendix containing definitions, derivations, and the hand-worked example.

M2 specifically includes derivations and the small example, so the small example belongs in our Iteration 2 plan. We will plan an uncertainty/probability component now and confirm its final form before the main analysis.

The general document restricts `numpy.linalg` routines to checking results, while the Mandarin starter directly uses `np.linalg.svd`. We resolved this conservatively with a from-scratch cyclic Jacobi core and library decomposition only as a final comparison. No exemption is assumed.

## Completion checks

- [x] All Q1-Q5 answers and more than three complete derivations prepared.
- [x] Notation, definitions, assumptions, tiny example, and algorithm included.
- [x] Real dataset described with two exploratory plots and acquisition instructions.
- [x] Known-truth simulation run; measured results and checks included.
- [x] Strict from-scratch core and pinned numerical environment implemented.
- [x] Local report PDF compiled and visually checked; source ZIP prepared.
- [x] Excel plan updated with actual progress and honest contributions.
- [ ] Author review and signatures/checker treatment under clarified solo convention.
- [ ] Official template incorporated if one is supplied.
- [x] Overleaf project, actual PDF export, and Viewer share link created after user sign-in.
- [x] GitHub public read access enabled with user approval; anonymous access verified.
- [ ] Final author review of report, code, and project links.
