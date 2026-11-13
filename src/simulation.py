"""Known-topic simulation and mathematical verification; seed fixed at zero."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from text_vectors import tfidf, cosine_matrix, pair_summary
from svd_method import svd_from_gram, project_query


def main():
    rng = np.random.default_rng(0)
    topic = np.repeat([0, 1], 20)
    theta = np.array([
        rng.dirichlet(np.r_[np.full(25, 2.0), np.full(25, 0.1)]),
        rng.dirichlet(np.r_[np.full(25, 0.1), np.full(25, 2.0)])])
    counts = np.column_stack([rng.multinomial(60, theta[t]) for t in topic]).astype(float)
    a, idf, df = tfidf(counts)
    u, s, vt, diagnostics = svd_from_gram(a)
    k = 2
    d = vt[:k].T * s[:k]
    reduced_cos = cosine_matrix(d)
    original_cos = cosine_matrix(a.T)
    reconstructed = (u[:, :k] * s[:k]) @ vt[:k]
    q = a[:, 0]
    projected = project_query(q, u, s, k)
    folded = project_query(q, u, s, k, folded=True)
    checks = {
        'cosine_min': float(reduced_cos.min()), 'cosine_max': float(reduced_cos.max()),
        'u_orthogonality_max_abs': float(np.max(np.abs(u.T @ u - np.eye(len(s))))),
        'v_orthogonality_max_abs': float(np.max(np.abs(vt @ vt.T - np.eye(len(s))))),
        'full_reconstruction_max_abs': float(np.max(np.abs((u * s) @ vt - a))),
        'projected_coordinates_max_abs': float(np.max(np.abs(u[:, :k].T @ a - s[:k, None] * vt[:k]))),
        'projected_query_max_abs': float(np.max(np.abs(projected - d[0]))),
        'folded_query_max_abs': float(np.max(np.abs(folded - vt[:k, 0]))),
        'reconstructed_cosine_max_abs': float(np.max(np.abs(cosine_matrix(reconstructed.T) - reduced_cos))),
        'frobenius_energy': float(np.sum(a * a)),
        'singular_value_energy': float(np.sum(s * s)),
        **diagnostics}
    # The library routine is used only AFTER our own decomposition, as a check.
    reference_u, reference_s, reference_vt = np.linalg.svd(a, full_matrices=False)
    checks['library_singular_value_max_abs'] = float(np.max(np.abs(s - reference_s[:len(s)])))
    checks['library_rank2_reconstruction_max_abs'] = float(np.max(np.abs(
        reconstructed - (reference_u[:, :k] * reference_s[:k]) @ reference_vt[:k])))
    for key in ['u_orthogonality_max_abs', 'v_orthogonality_max_abs',
                'full_reconstruction_max_abs', 'projected_coordinates_max_abs',
                'projected_query_max_abs', 'folded_query_max_abs',
                'reconstructed_cosine_max_abs', 'library_singular_value_max_abs',
                'library_rank2_reconstruction_max_abs']:
        assert checks[key] < 1e-7, (key, checks[key])
    assert reduced_cos.min() >= -1 - 1e-12 and reduced_cos.max() <= 1 + 1e-12
    errors = []
    for rank in [1, 2, 5, 10, len(s)]:
        approximation = (u[:, :rank] * s[:rank]) @ vt[:rank]
        measured = float(np.sum((a - approximation) ** 2))
        tail = float(np.sum(s[rank:] ** 2))
        errors.append({'k': rank, 'measured_squared_error': measured,
                       'tail_squared_singular_values': tail, 'absolute_difference': abs(measured - tail)})
        assert abs(measured - tail) < 1e-7 * max(1, tail)
    comparisons = []
    for representation, cosines in [('Original TF-IDF', original_cos), ('Rank-2 SVD', reduced_cos)]:
        comparisons.append({'representation': representation, **pair_summary(cosines, topic)})
    probabilities = []
    for t in [0, 1]:
        true_p = float(theta[t, :25].sum())
        successes = int(counts[:25, topic == t].sum())
        total = 20 * 60
        estimate = successes / total
        probabilities.append({'topic': t, 'tokens': total, 'group_A_count': successes,
                              'true_probability': true_p, 'estimated_probability': estimate,
                              'true_standard_error': np.sqrt(true_p * (1 - true_p) / total)})
    prefix = 'docs/iteration2/results/'
    pd.Series(checks, name='value').to_csv(prefix + 'simulation_checks.csv')
    pd.DataFrame(errors).to_csv(prefix + 'reconstruction_errors.csv', index=False)
    pd.DataFrame(comparisons).to_csv(prefix + 'similarity_summary.csv', index=False)
    pd.DataFrame(probabilities).to_csv(prefix + 'topic_probability.csv', index=False)
    pd.DataFrame({'index': np.arange(1, len(s) + 1), 'singular_value': s}).to_csv(
        prefix + 'simulation_singular_values.csv', index=False)
    np.savez('data/processed/simulation.npz', counts=counts, tfidf=a, theta=theta, topic=topic,
             u=u, singular_values=s, vt=vt, idf=idf, document_frequency=df)
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), constrained_layout=True)
    axes[0].plot(np.arange(1, len(s) + 1), s, 'o-', color='#315A82', markersize=3)
    axes[0].axvline(2.5, linestyle='--', color='#A96335', linewidth=1)
    axes[0].set(xlabel='Singular value index', ylabel='Singular value', title='Simulation spectrum')
    for ax, matrix, title in zip(axes[1:], [original_cos, reduced_cos], ['Original TF-IDF', 'Rank-2 SVD']):
        picture = ax.imshow(matrix, vmin=-1, vmax=1, cmap='RdBu_r')
        ax.axhline(19.5, color='black', linewidth=.7)
        ax.axvline(19.5, color='black', linewidth=.7)
        ax.set(xlabel='Document', ylabel='Document', title=title)
    fig.colorbar(picture, ax=list(axes[1:]), shrink=.8, label='Cosine similarity')
    fig.savefig('figures/simulation_overview.png', dpi=180)
    plt.close(fig)
    print(pd.DataFrame(comparisons).to_string(index=False))
    print(pd.Series(checks).to_string())


if __name__ == '__main__':
    main()
