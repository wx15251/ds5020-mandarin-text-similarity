"""Reference checks and generated evidence; library solvers are allowed HERE only."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from methods import (my_cosine_matrix, my_document_coordinates, my_project_query,
                     my_query_vector)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'docs/iteration3/results'
FIGURES = ROOT / 'figures/iteration3'
PROCESSED = ROOT / 'data/processed/iteration3'


def prepare_directories():
    for folder in (RESULTS, FIGURES, PROCESSED):
        folder.mkdir(parents=True, exist_ok=True)


class VerificationLog:
    def __init__(self):
        self.rows = []

    def report(self, data, quantity, mine, ref, compared_with, atol=1e-8, rtol=0.0):
        mine, ref = np.asarray(mine, float), np.asarray(ref, float)
        if mine.shape != ref.shape or not mine.size or not np.isfinite(mine).all() or not np.isfinite(ref).all():
            raise ValueError('Verification needs matching, finite, nonempty quantities.')
        diff = mine - ref
        absolute = float(np.max(np.abs(diff)))
        reference_norm = float(np.sqrt(np.sum(ref * ref)))
        difference_norm = float(np.sqrt(np.sum(diff * diff)))
        relative = difference_norm / reference_norm if reference_norm else (0.0 if difference_norm == 0 else None)
        limit = float(atol + rtol * np.max(np.abs(ref)))
        passed = absolute <= limit
        self.rows.append({'data': data, 'quantity': quantity, 'compared_with': compared_with,
                          'max_abs_error': absolute, 'relative_error': relative,
                          'absolute_limit': limit, 'pass': passed})
        print(f'{data}: {quantity}: max|diff|={absolute:.3e}, relative={relative}, pass={passed}', flush=True)
        if not passed:
            raise AssertionError(self.rows[-1])
        return absolute

    def save(self, name):
        pd.DataFrame(self.rows).to_csv(RESULTS / name, index=False)


def topic_summary(cosines, labels):
    labels = np.asarray(labels)
    same = labels[:, None] == labels[None, :]
    off_diagonal = ~np.eye(len(labels), dtype=bool)
    scores = cosines.copy()
    np.fill_diagonal(scores, -np.inf)
    return {'within_including_self': float(cosines[same].mean()),
            'within': float(cosines[same & off_diagonal].mean()),
            'across': float(cosines[~same].mean()),
            'gap': float(cosines[same & off_diagonal].mean() - cosines[~same].mean()),
            'nearest_same_topic': float(np.mean(labels[np.argmax(scores, axis=1)] == labels))}


def check_svd(a, sig, u, v, diagnostics, data, log):
    """Run comparisons after the custom method; return references only for auditing."""
    k = len(sig)
    ref_u, ref_s, ref_vt = np.linalg.svd(a, full_matrices=False)
    d = my_document_coordinates(v, sig)
    reconstructed = (u * sig) @ v.T
    reference = (ref_u[:, :k] * ref_s[:k]) @ ref_vt[:k]
    log.report(data, 'singular values', sig, ref_s[:k], 'NumPy SVD')
    log.report(data, 'original cosine', my_cosine_matrix(a.T), cosine_similarity(a.T), 'sklearn cosine')
    log.report(data, 'reduced cosine formula', my_cosine_matrix(d), cosine_similarity(d), 'sklearn cosine')
    log.report(data, 'reduced cosine vs library SVD', my_cosine_matrix(d),
               cosine_similarity((ref_s[:k, None] * ref_vt[:k]).T), 'NumPy SVD + sklearn cosine')
    log.report(data, 'U orthogonality', u.T @ u, np.eye(k), 'identity')
    log.report(data, 'V orthogonality', v.T @ v, np.eye(k), 'identity')
    log.report(data, 'fold-in', my_project_query(a[:, 0], u, sig, folded=True), v[0], 'row 0 of V')
    log.report(data, 'projected query', my_project_query(a[:, 0], u, sig), d[0], 'row 0 of D')
    log.report(data, 'reconstructed cosine', my_cosine_matrix(reconstructed.T),
               my_cosine_matrix(d), 'coordinate cosine')
    relative_reconstruction = float(np.sqrt(np.sum((reconstructed-reference)**2) / np.sum(reference**2)))
    log.report(data, 'rank-k reconstruction relative difference', relative_reconstruction, 0.,
               'NumPy rank-k, relative to its Frobenius norm', atol=1e-10)
    measured = float(np.sum((a-reconstructed)**2))
    tail = float(np.sum(ref_s[k:]**2))
    # Divide by total energy to avoid a scale-dependent absolute test on squared errors.
    normalized_tail_difference = abs(measured-tail) / float(np.sum(a*a))
    log.report(data, 'tail identity difference / total energy', normalized_tail_difference, 0.,
               'discarded library singular-value energy', atol=1e-10)
    details = {'k': k, 'u_orthogonality': float(np.max(abs(u.T@u-np.eye(k)))),
               'v_orthogonality': float(np.max(abs(v.T@v-np.eye(k)))),
               'squared_reconstruction_error': measured, 'tail_energy': tail,
               'normalized_tail_difference': normalized_tail_difference,
               'smallest_retained_sigma': float(sig[-1]),
               'boundary_ratio_next_over_retained': float(ref_s[k]/sig[-1]) if k<len(ref_s) else 0.,
               'library_rank': int(np.sum(ref_s > ref_s[0]*1e-6)),
               'resolved_condition_number': float(ref_s[0]/ref_s[ref_s>ref_s[0]*1e-6][-1]),
               'max_original_gram_residual': max(r['original_residual'] for r in diagnostics['components']),
               'iterations_total': diagnostics['iterations_total']}
    return ref_s, details


def unsupported_input_checks(a, vocabulary, idf, tokens, data):
    """One frozen-vocabulary test and explicit unsupported/zero-vector failure checks."""
    known = my_query_vector(tokens, vocabulary, idf)
    mixed = my_query_vector(list(tokens) + ['OUTSIDE_VOCABULARY_000'], vocabulary, idf)
    if not np.array_equal(known, mixed):
        raise AssertionError('OOV terms changed known coordinates.')
    rejected = False
    try:
        my_cosine_matrix(my_query_vector(['OUTSIDE_VOCABULARY_000'], vocabulary, idf)[None, :])
    except ValueError:
        rejected = True
    if not rejected:
        raise AssertionError('Unsupported query was not rejected.')
    return {'data': data, 'known_query_matches_document': bool(np.array_equal(known, a[:, 0])),
            'mixed_oov_unchanged': bool(np.array_equal(known, mixed)),
            'unsupported_query_rejected': rejected,
            'zero_original_columns': int(np.sum(np.sum(a*a, axis=0)==0))}


def save_json(path, values):
    Path(path).write_text(json.dumps(values, ensure_ascii=False, indent=2) + '\n')
