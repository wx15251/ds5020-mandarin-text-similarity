"""Independent hand-example, edge-case, and solver comparisons."""
import numpy as np
import pandas as pd
from text_vectors import tfidf, cosine_matrix, count_matrix, query_vector
from svd_method import svd_from_gram


def main():
    alpha = np.log(3 / 2)
    counts = np.array([[2, 0, 1], [0, 2, 1]], dtype=float)
    a, idf, _ = tfidf(counts)
    u, s, vt, _ = svd_from_gram(a)
    hand_s = alpha * np.array([np.sqrt(6), 2])
    rank1 = (u[:, :1] * s[:1]) @ vt[:1]
    expected = alpha * np.ones((2, 3))
    hand_results = {
        'alpha': alpha,
        'sigma_1': s[0], 'sigma_2': s[1],
        'rank1_error_squared': np.sum((a - rank1) ** 2),
        'expected_error_squared': 4 * alpha ** 2,
        'original_cos_doc1_doc2': cosine_matrix(a.T)[0, 1],
        'original_cos_doc1_doc3': cosine_matrix(a.T)[0, 2],
        'folded_cos_doc1_doc2': cosine_matrix(vt.T)[0, 1],
        'folded_cos_doc1_doc3': cosine_matrix(vt.T)[0, 2],
        'rank1_cos_doc1_doc2': cosine_matrix(rank1.T)[0, 1]}
    assert np.allclose(s, hand_s, atol=1e-12)
    assert np.allclose(rank1, expected, atol=1e-12)
    assert abs(hand_results['folded_cos_doc1_doc2'] + .2) < 1e-12
    assert abs(hand_results['folded_cos_doc1_doc3'] - np.sqrt(2 / 5)) < 1e-12
    pd.Series(hand_results, name='value').to_csv('docs/iteration2/results/hand_example.csv')
    rng = np.random.default_rng(0)
    cases = {'tall': rng.normal(size=(9, 5)), 'wide': rng.normal(size=(5, 9)),
             'rank_deficient': np.array([[1., 2, 3], [2., 4, 6], [0., 0, 0]]),
             'repeated_singular_values': np.diag([3., 3., 1.]),
             'zero': np.zeros((3, 4))}
    results = []
    for name, matrix in cases.items():
        cu, cs, cvt, diagnostics = svd_from_gram(matrix)
        reference = np.linalg.svd(matrix, compute_uv=False)  # Verification only.
        reconstruction = float(np.max(np.abs((cu * cs) @ cvt - matrix)))
        difference = float(np.max(np.abs(cs - reference[:len(cs)]))) if len(cs) else 0.
        assert reconstruction < 1e-8, (name, reconstruction)
        assert difference < 1e-8, (name, difference)
        results.append({'case': name, 'reconstruction_max_abs': reconstruction,
                        'singular_values_max_abs': difference, **diagnostics})
    # Universal terms receive IDF zero; absent terms never trigger log(0).
    weighted, zero_idf, _ = tfidf(np.array([[1., 1], [0, 0]]))
    assert np.all(weighted == 0) and np.all(zero_idf == 0)
    for invalid in [np.zeros((2, 3)), np.array([[1., np.nan]])]:
        try:
            cosine_matrix(invalid)
            raise AssertionError('Expected undefined/non-finite cosine rejection.')
        except ValueError:
            pass
    count, vocab = count_matrix(['天气天气！', '足球 123'])
    assert count.sum() == 6 and len(vocab) == 4
    assert np.all(query_vector('unknown', vocab, np.ones(len(vocab))) == 0)
    pd.DataFrame(results).to_csv('docs/iteration2/results/verification.csv', index=False)
    print('Passed hand example, tall/wide/deficient/repeated/zero matrices, and text/cosine edge cases.')
    print(pd.DataFrame(results).to_string(index=False))


if __name__ == '__main__':
    main()
