# Iteration 3 work plan

Prepared November 21, 2026 for James Cottrell. **Historical plan, followed by user authorization to implement the full iteration. Current progress and measured results are in [working_notes.md](working_notes.md).**

No instructor comments on Iteration 2 were supplied. Iteration 3 is due **tomorrow night, November 22**, and James hoped to start tonight. The exact cutoff time has not been supplied. This plan uses the current workspace and preserves the Iteration 1 proposal and completed Iteration 2 artifacts. Future-tense statements below record the original plan; consult the working notes for completion status.

## Basis and scope

Course requirements come from [iteration3.pdf](../reference/iteration3.pdf), general instructions on pages 1-4 and **Own Topic - Mandarin Text Similarity with the SVD** on pages 16-17. The other project boxes do not apply. The source copy is unchanged, with SHA-256 `24d5cd7e86e1c73ece8cd65cdc5f288639c25aa1c24d04245732ea85bb2bb663`.

The user's current request is to review and plan before beginning implementation. Proposed choices below are our recommendations, not additional instructor requirements or recorded experimental results. The handout's instructions do not independently authorize publication, submission, or contacting anyone. The existing public repository and Overleaf Viewer project are already set up.

## What carries forward and what changes

| Area | Existing work | Iteration 3 work needed |
| --- | --- | --- |
| Mathematics | Definitions, proofs, coordinate conventions and algorithm in Iteration 2 | Connect numbered equations to the new implementation and answer all five new questions |
| Tiny example | Two terms and three documents | New **four-term, three-document** example with every intermediate result and an independent check |
| SVD | From-scratch cyclic Jacobi eigensolver | Implement **power iteration with deflation**, as explicitly required now; retain the previous solver as prior work |
| Core code | Separate TF-IDF, cosine and SVD modules | Required `src/methods.py` with `my_` functions, shared by tiny, simulation and real-data scripts |
| Simulation | Seed 0, 50 terms, 40 documents, two topics, 60 tokens/document | Refactor into a parameterized function, preserve the exact baseline, add at least three sizes and a topic-overlap stress test |
| Real corpus | Local raw files, provenance, fixed 300-document sample, character TF-IDF | Run real retrieval, add jieba word tokens, energy-based rank selection and library verification |
| Reporting | Iteration 2 PDF, LaTeX, Excel tracker, public GitHub and shared Overleaf | Separate Iteration 3 report/results, updated tracker and README commands |

## Requirements mapped to planned evidence

All items in this table are **planned**, not completed results.

| ID | Handout requirement | Planned implementation and report evidence |
| --- | --- | --- |
| G1 | Equations lead the code; core NumPy only (p. 1) | Equation-number comments above each `my_` method; NumPy array operations in the core; library solvers in verification code only |
| G2 | Preserve Iteration 2 data, model, parameters and seed (p. 1) | Same real document IDs and sampling manifest; exact seed-0 simulation reproduction; explain the required new tokenizer, solver and additional simulation sizes |
| G3 | New leader, math/code ownership and second-person checking (p. 1) | James remains the solo owner; record the unresolved solo leader/checker convention honestly; no invented checker or signatures |
| G4 / Q1 | Tiny example with all intermediate results, Fraction where possible, and a second-way check (pp. 1-2, 16) | `small_example.py`: four terms, three documents, counts through SVD and rank-1 cosines; exact integer/rational stages; verify eigen-equations, orthogonality and reconstruction |
| G5 / Q2 | One function per algorithm step in `methods.py`; shared `my_` methods (p. 2, p. 16) | From-scratch counts/TF-IDF, cosine, power iteration, deflation, SVD and projection; same functions used in all three entry points |
| G6 | Parameterized Iteration 2 simulator in `simulate.py` (p. 2) | `simulate_two_topics(n_docs=40, seed=0, ...)` returns counts, labels and true probabilities, including metadata describing the draw order |
| G7 | Compare simulation with truth and library; at least three sizes; log-log error plot (p. 2) | Sizes 40, 200, 1000; label-recovery statistics, known-probability sampling error, SE reference, singular-value and cosine library comparisons |
| G8 | Deliberately break an assumption with a stress test (pp. 2, 17) | Increase overlap of the two topic distributions; measure the within-minus-across cosine gap and label-recovery behavior |
| G9 | Clean real data, record removals/transforms/split, verify numerically (p. 2) | Fixed source/sample audit, saved token sequences, matrix dimensions and zero-vector checks; explicitly describe in-corpus evaluation without a held-out split |
| G10 | One comparison helper and verification table, all numbers from scripts (pp. 2-3) | Shared verification helper writes max absolute and relative errors, tolerance and status to CSV; generate the LaTeX table from those records |
| G11 | Check every Iteration 2 assumption on simulation, then real data (p. 3) | Assumption table described below; distinguish numerical tests, modeling limitations and items that apply only to simulation |
| G12 | All answers under **Iteration 3 - Math Questions** (p. 3) | Explicit Q1-Q5 subsections in the new report |
| G13 | Update Excel, README commands and Overleaf PDF (pp. 3-4) | Use the existing Excel tracker; document the three required entry points; compile/export the new report into `docs/` |
| Q3 | Choose and justify real-data rank using cumulative squared singular-value energy (p. 16) | Energy curve, smallest rank reaching the predeclared 90% target, actual rank and retained energy for each tokenization |
| Q4 | Compare character and word tokens (pp. 16-17) | Same documents and TF-IDF convention; compare vocabulary/matrix size, nonzeros, rank, within/across means and nearest-topic rate |
| Q5 | One query, top five documents before/after SVD, interpreted (p. 16) | Fixed query chosen before viewing rankings; tables of IDs, titles, labels and scores, with self-match excluded |
| P1 | Library agreement to 1e-8 (p. 17) | Singular values versus NumPy; cosine versus scikit-learn; reconstruction/projection and fold-in checks with explicitly reported errors |
| P2 | Simulation within-topic >0.9 and across-topic <0.2 at rank two (p. 17) | Report the baseline results using the starter's self-pair convention, plus a clearly labeled off-diagonal within-topic mean |
| P3 | Existing-document fold-in returns its row of V_k (p. 17) | Compare `Sigma_k^-1 U_k.T @ A[:, j]` with `V_k[j, :]`; keep the retrieval coordinates separate |

## Proposed defaults

These choices keep the project small enough for the deadline and do not depend on further user input.

- **Real sample:** the same 300 THUCNews documents, 100 per category (sports, education, technology), with the existing pinned source revision and IDs. Reuse rather than resample. The existing character matrix has 3,123 rows; verify reproduction before using it as the baseline.
- **TF-IDF:** retain raw counts times `log(n / df)`, no smoothing or centering. Give unobserved fixed-vocabulary rows weight zero. Keep terms in rows and documents in columns.
- **Word processing:** jieba segmentation with recorded version/settings, punctuation/digits removed, retained Chinese tokens, no new stopword list or frequency cutoff initially. Preserve token boundaries when removing non-Chinese material. Save ordered per-document token lists locally, with hashes/settings and counts in the audit. Character preprocessing must still reproduce Iteration 2 exactly.
- **Real-data rank:** smallest positive rank retaining at least **90%** of squared singular-value energy, separately for characters and words. This is a proposed analysis choice; the Mandarin handout does not specify a percentage. Report the achieved energy and discuss the loss of detail. A 95% or matched-rank sensitivity comparison is optional after required work passes.
- **Query:** use the full title/body of the first document in the existing sample manifest, chosen before inspecting results. This is a transparent in-corpus query. Exclude its own ID from the top five and use deterministic ID ordering for ties. Use the same text for both tokenizations.
- **Evaluation:** descriptive retrieval within the fixed corpus; no held-out generalization claim. Labels are evaluation metadata only. A train/test split is not specified in the Mandarin box. State explicitly that none is used. If a held-out design is later requested, fit vocabulary/IDF only on training documents.
- **Simulation:** keep the seed-0, 40-document baseline intact; extend to balanced sizes **40, 200, 1000**, retaining 50 terms, 60 tokens per document and the same realized topic distributions. Additional sizes are the change needed to satisfy the new scaling experiment.

## Tiny example design (Q1)

Use four character terms `天, 气, 足, 球` in that explicit row order and three toy documents `天气`, `天气足球`, `足球`. These strings are a designed mathematical example, not sampled news. The planned counts and TF-IDF are

```text
C = [[1, 1, 0],       df = [2, 2, 2, 2]
     [1, 1, 0],       alpha = log(3/2)
     [0, 1, 1],       A = alpha C, shape 4 x 3
     [0, 1, 1]]

A.T A = alpha^2 [[2, 2, 0],
                 [2, 4, 2],
                 [0, 2, 2]]
```

The analytic target has Gram eigenvalues `6 alpha^2, 2 alpha^2, 0`, positive singular values `sqrt(6) alpha, sqrt(2) alpha`, and right directions `(1,2,1)/sqrt(6)`, `(1,0,-1)/sqrt(2)`. The left directions are `(1,1,1,1)/2` and `(1,1,-1,-1)/2`. Original cosines between distinct documents are `1/sqrt(2), 0, 1/sqrt(2)` for pairs (1,2), (1,3), (2,3); rank one makes all three equal to one.

These are analytic design targets, not results from an implemented Iteration 3 script. During implementation, print the vocabulary, C, df, IDF, A, Gram matrix, characteristic polynomial/eigenpairs, power-iteration diagnostics, U/Sigma/V, rank-1 approximation, document coordinates and both cosine matrices. Use `Fraction` for exact rational stages; retain logarithms and square roots symbolically in the report and compare their floating-point evaluations. Confirm eigen-equations and full reconstruction as a second check, and show that rank one retains 75% of the squared energy while merging distinct directions.

## Core method and numerical checks (Q2)

For `A` of shape `m x n`, use a small collection of explainable functions. Equation labels will be fixed in the report before linking comments to code.

| Step | Planned function(s) | Equation / dimensions |
| --- | --- | --- |
| 1 | `my_count_matrix` | Count the supplied token lists in one fixed vocabulary, C: m x n |
| 2 | `my_tfidf` | df_t = sum_j 1(C_tj > 0); w_t = log(n/df_t); A = diag(w) C |
| 3 | `my_gram` | G = A.T A: n x n; use A A.T: m x m when m < n, explaining the equivalent smaller-Gram construction |
| 4 | `my_power_iteration`, `my_deflate` | Normalize Gv, test an eigen-residual, lambda = v.T Gv, deflate G - lambda vv.T; reorthogonalize against retained directions |
| 5 | `my_svd_power` | sigma = sqrt(lambda); u = Av/sigma for the right-Gram route, with the corresponding left-Gram formula; return sig, U_k, V_k and convergence diagnostics |
| 6 | `my_document_coordinates`, `my_project_query` | D = V_k Sigma_k: n x k; z = U_k.T q: k; optional folded q_hat = z/sig |
| 7 | `my_cosine_matrix`, `my_query_cosines` | Normalize nonzero rows and multiply; reject non-finite/zero vectors explicitly |
| 8 | `my_energy_rank`, `my_top_matches` | Smallest k meeting cumulative energy; deterministic top-five ordering with exclusions |

Keep norm calculations in the core as square roots of sums of squares. No `numpy.linalg`, SciPy or scikit-learn solvers in `methods.py`. jieba belongs to preprocessing, not the linear algebra solver. Verification helpers and plotting/report generation remain outside the core.

Power iteration needs a fixed starting RNG, two-pass reorthogonalization, residual-based stopping and a finite iteration limit with an explicit failure. Check descending positive singular values, Gram residuals, U/V orthogonality and projection identities. Gram matrices square the condition number; report cutoff behavior rather than dividing by tiny singular values.

**First implementation gate:** demonstrate 1e-8 library agreement on the tiny example and the unchanged rank-2 simulation, then profile the real-data energy calculation. Closely spaced eigenvalues can slow power iteration. Do not silently relax the handout's accuracy target or substitute the old Jacobi solver as the required new method. If the gate fails, resolve or report the numerical issue before writing conclusions.

For real-data energy, the denominator can be computed directly as `sum(A*A) = sum_i sigma_i^2` by the Iteration 2 Frobenius identity. Extract successive components until the target is reached instead of requiring a full spectrum just to determine the denominator. Verify the selected rank and energy against a full library SVD afterward. If a near tie crosses the cutoff, explain the rank/subspace sensitivity. Compare sign-aligned vectors only for isolated directions; compare projectors/reconstructions for repeated singular-value groups.

**Coordinate rule:** query `z = U_k.T @ q` is compared with rows of `D = V_k Sigma_k`. The handout's folded query `q_hat = z / sig` is checked against a row of `V_k`. Axis rescaling changes cosines, so those two geometries must not be mixed.

## Simulation design and interpretation

Refactor the existing generator without changing its baseline draw order: draw the two Dirichlet topic distributions, then generate all topic-0 documents followed by topic-1 documents, with `default_rng(0)`. Confirm that the 40-document output exactly matches the existing `data/processed/simulation.npz` counts, labels and true probabilities before running new sizes. Keep the baseline artifact untouched. The model has noisy multinomial counts; the observed TF-IDF matrix need not have rank two.

At each proposed size, run the shared core at `k=2`, record the singular-value and cosine checks, within/across topic means, nearest-topic rate, fold-in error, orthogonality and reconstruction/tail-energy checks. The baseline's existing perfect nearest-topic rate does not justify a claim of improved classification accuracy.

The Mandarin box identifies **topic labels** as truth, while the general instructions also require an error-versus-n plot with a sampling-error interpretation. Labels do not supply a uniquely identifiable true SVD vector. Use two explicitly distinguished checks:

1. **Topic recovery:** within/across cosines and nearest-topic agreement with known labels, before/after SVD. Use actual baseline pass criteria. These descriptive metrics need not improve monotonically with sample size.
2. **Sampling error:** extend the already-derived Iteration 2 probability calculation. Conditional on the fixed realized topic probabilities, let p_h be the probability of a token falling in terms 1-25 for topic h. Estimate p_h from the pooled counts of that topic. With N_h = 60 n_h tokens, SE = sqrt(p_h(1-p_h)/N_h). Plot absolute estimation error versus document count on log-log axes, with the theoretical SE (and 3SE reference) and both topics labeled. This validates the known-probability sampling model; it is not an error curve for SVD components.

Keep the same realized topic distributions across sizes and document any different random-stream allocation for larger samples. A single seeded error curve can fluctuate. Show actual observations even if non-monotonic or outside 3SE; do not change seeds to manufacture a trend. If an error is exactly zero, label it explicitly rather than silently taking log(0). Repeated independent count draws for an RMSE curve are an optional extension, with their additional seeds declared.

For the required stress test, interpolate each topic distribution toward their shared average:

```text
theta_h(rho) = (1 - rho) theta_h + rho (theta_0 + theta_1)/2
rho = 0, 0.25, 0.5, 0.75, 1
```

Retain 40 documents, 60 tokens/document and seed 0. This intentionally weakens topic separation. At rho=1 the distributions coincide, so the labels carry no distributional separation. Plot the measured within-minus-across cosine gap and report label-recovery behavior. The exact finite-sample path is not guaranteed to be monotone. Disclose this intentional model change separately from the unchanged baseline.

## Real-data comparison, rank and retrieval (Q3-Q5)

Run the original character pipeline first and verify document IDs, count/TF-IDF dimensions and values against Iteration 2. Add the word pipeline on those same documents. Save processed token lists locally under a versioned `data/processed/iteration3/` path; keep full corpus text and matrices out of Git, as before. Record package versions, tokenizer settings and token-file hashes so the processed inputs can be reproduced. Do not add a new stopword list or sample filtering just to improve results.

For each tokenization, report document/vocabulary counts, matrix shape, nonzero count/density, removed/transformed text counts, zero-column count, energy-selected k, retained energy, and before/after within/across cosines. Keep the starter's diagonal-including simulation pass statistic separate from the more informative off-diagonal means used for interpretation. Include nearest-topic rate as a secondary diagnostic, not semantic ground truth.

Use NumPy SVD and scikit-learn cosine only as checks. Match the project's raw-TF/unsmoothed-IDF convention when validating TF-IDF; a library's default settings may use a different formula. The common comparison helper must report max absolute and relative differences, shapes, tolerances, and a clear status. Handle zero reference norms explicitly. Compare the **same matrix and rank** for all library checks.

Generate the query's original/reduced top-five lists with IDs, titles, category and cosine score. Use character results as the main Q5 table; word results can be a compact companion table for Q4. Explain changes using the actual terms/topics and scores. Do not infer general semantic quality from a single query. Different energy-selected ranks are part of the comparison and must be disclosed.

## Assumption audit carried forward from Iteration 2

Run numerical checks on the simulation first, then the real data. Not every modeling caveat is a binary test, and synthetic tokens cannot establish a real-language assumption.

| Iteration 2 assumption / choice | Planned evidence and limits |
| --- | --- |
| One vocabulary, preprocessing rule and corpus IDF | Freeze each representation; check a known query, partly OOV input and fully unsupported input; report OOV support and deterministic rejection |
| Nonzero original/projected cosine inputs | Count zero vectors before/after projection and verify failure behavior; never silently assign zero-vector cosine zero |
| Positive, resolved retained singular values | Report the cutoff, smallest retained value, spectral gap at the selected rank, and tolerance sensitivity at the important boundary; library condition/rank diagnostics are checks only |
| Approximately orthonormal U/V | Max errors in U.T U - I and V.T V - I, eigen-residuals, coordinate/reconstructed cosine agreement and Frobenius tail identity |
| Topic labels are an imperfect similarity proxy | Use known simulation topics as the reference; inspect the real query examples and explain topical versus semantic relevance |
| No selected exact duplicates; investigate near duplicates | Recheck selected IDs/cleaned text; inspect the highest lexical-similarity/title-overlap pairs and disclose any near duplicates; do not silently drop documents from the fixed sample |
| Finite-prefix sampling limits representativeness | Retain provenance and source-order limitation; do not make whole-corpus claims. Broadening the pool would change the fixed Iteration 2 data and is outside the deadline plan |
| Conditional token independence in the simulation | Check frequencies against known probabilities and SEs; explain that independence is a model construction, not something proved by a finite frequency check. Do not transfer this assumption to real language |

## Work sequence for tonight and tomorrow

These are proposed work blocks, not recorded student hours or promises of a completion time. Required work takes priority over optional analyses.

| Block | Target | Work and dependency | Exit condition |
| --- | --- | --- | --- |
| 0 | Completed planning session | Read handout and current work; save this plan and unchanged source; record deadline/feedback | Scope and requirements mapped; no new experiment results claimed |
| 1 | Tonight, first | Freeze baseline comparisons; build the four-term example and `methods.py` power/deflation pipeline | Tiny analytic checks and unchanged simulation satisfy the numerical accuracy gate |
| 2 | Tonight, next | Refactor `simulate.py`; implement `check_simulation.py`; sizes, sampling-error plot and topic-overlap stress test | Script-generated simulation tables/plots; failures visible and interpreted |
| 3 | Tomorrow, first | Reproduce real character baseline; add jieba and saved word tokens; implement `run_real.py` | Both tokenizations run; rank/energy and library checks complete |
| 4 | Tomorrow, next | Fix query, export top-five results; finish all assumption checks | Q3-Q5 tables and evidence-based interpretations ready |
| 5 | Tomorrow, before final review | Write Iteration 3 report using generated tables/figures; update the existing Excel tracker and README commands | Every Q1-Q5 and general requirement covered; no placeholders presented as results |
| 6 | Tomorrow, with time reserved | Reproduce entry points; compile and visually review the report; update/export the existing Overleaf project in the implementation phase | Current PDF/source package and links verified; James reviews the key explanations |

Blocks 1-4 form the numerical dependency path. Build the report outline while results are being produced, but fill numerical claims only from verified outputs. If time becomes tight, omit optional 95%-energy, matched-rank and repeated-seed extensions; retain every required question and experiment. Avoid additional datasets, neural embeddings, web apps or new infrastructure.

## Planned file organization and report

Required new entry points are `src/small_example.py`, `src/check_simulation.py` and `src/run_real.py`, backed by `src/methods.py` and `src/simulate.py`. A shared verification/reporting helper and tokenizer helper can remain small separate modules. Pin required new preprocessing/check packages when implementation begins; no new packages have been installed for planning.

Place the new LaTeX source and script-generated CSV/LaTeX tables under `docs/iteration3/`, figures under `figures/iteration3/`, and local processed inputs under `data/processed/iteration3/`. Plan final report paths `docs/iteration3_report.pdf` and `docs/iteration3_overleaf.zip`. Preserve the old report, ZIP and results. Use `docs/project_plan.xlsx` for actual task status, timeline and contributions during implementation; it has not been edited in this planning-only session. Keep basic artifact links in README rather than creating a standalone deliverables page.

Suggested report order: scope/notation; **Iteration 3 - Math Questions** with Q1 tiny example, Q2 algorithm, Q3 energy, Q4 tokenization and Q5 query; simulation truth/library/scaling/stress results; assumption checks; one unified verification table; limitations and contribution/status notes. Connect equations to the code and show dimensions and the mathematical rule used at each derivation step. All table values and plotted numbers must come from scripts. The final report should stand on its own without requiring the Iteration 2 PDF to interpret new results.

James should be ready to explain why singular-vector signs can differ, why energy selection does not guarantee semantic quality, why rank one merges directions in the toy example, how deflation finds the next direction, and why the two query coordinate conventions must not be mixed.

## Remaining uncertainty and readiness

At planning time, there was **no known access or data blocker to beginning the technical work**. The highest technical risk was power-iteration convergence/accuracy at the real-data rank, which was checked early. The deadline is tomorrow night; the exact cutoff remains unspecified. No instructor comments resolve the solo-checker/new-leader wording. Record that convention as pending and do not invent a second person, approval or signature. No new official template has been supplied.

The plan is ready for implementation when the user starts that phase. No Iteration 3 code, experimental results, report PDF or external project updates are claimed complete here.
