# Verified environment

The computations were run on November 13, 2026 in the project-local `.venv`.

| Component | Observed version |
| --- | --- |
| Python | 3.12.14 |
| NumPy | 2.5.4 |
| pandas | 3.1.1 |
| Matplotlib | 3.11.2 |
| SciPy | 1.18.1 |
| LaTeX | Local TeX Live 2026, `pdflatex` |

`requirements.txt` pins the four direct numerical dependencies; `requirements-lock.txt` records the installed Python dependency set. Standard-library modules handle I/O and report building. Artifact-authoring tools used for Excel are separate from the submitted numerical method and its environment.

Core method: no `numpy.linalg` decomposition/solver. Reference comparisons: `numpy.linalg.svd` in `verify.py` and `simulation.py`. No scikit-learn, jieba, or additional numerical/NLP package is used. Matplotlib uses the noninteractive Agg backend for script execution.

All random draws use `np.random.default_rng(0)`. The real-data sampling and simulation each initialize their own generator, so running one does not change the other's random state. CSV outputs preserve the measured numbers. Tiny floating-point differences on another BLAS/platform are possible; numerical checks use explicit tolerances.
