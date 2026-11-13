"""Educational SVD via a hand-implemented cyclic Jacobi eigensolver.

No numpy.linalg method solver is used here. Gram matrices square the condition
number, so this is suitable for the small verification problems in Iteration 2,
not a claim of production-scale or high-relative-accuracy SVD performance.
"""
import numpy as np


def jacobi_eigh(matrix, tolerance=1e-12, max_sweeps=100):
    original = np.asarray(matrix, dtype=float)
    if original.ndim != 2 or original.shape[0] != original.shape[1]:
        raise ValueError('Jacobi requires a square matrix.')
    if not np.isfinite(original).all():
        raise ValueError('Non-finite matrix.')
    if not np.allclose(original, original.T, rtol=1e-12, atol=1e-14):
        raise ValueError('Jacobi requires a symmetric matrix.')
    g = original.copy()
    size = len(g)
    vectors = np.eye(size)
    scale = float(np.sqrt(np.sum(g * g)))
    if scale == 0:
        return np.zeros(size), vectors, {'sweeps': 0, 'relative_off_diagonal': 0.0}
    for sweep in range(max_sweeps + 1):
        off = g - np.diag(np.diag(g))
        off_norm = float(np.sqrt(np.sum(off * off)))
        if off_norm <= tolerance * scale:
            order = np.argsort(np.diag(g))[::-1]
            return np.diag(g)[order], vectors[:, order], {
                'sweeps': sweep, 'relative_off_diagonal': off_norm / scale}
        if sweep == max_sweeps:
            break
        for p in range(size - 1):
            for q in range(p + 1, size):
                apq = g[p, q]
                if abs(apq) <= tolerance * scale / max(size, 1):
                    continue
                app, aqq = g[p, p], g[q, q]
                tau = (aqq - app) / (2 * apq)
                sign = 1.0 if tau >= 0 else -1.0
                t = sign / (abs(tau) + np.sqrt(1 + tau * tau))
                c = 1 / np.sqrt(1 + t * t)
                s = t * c
                gp, gq = g[:, p].copy(), g[:, q].copy()
                g[:, p], g[:, q] = c * gp - s * gq, s * gp + c * gq
                g[p, :], g[q, :] = g[:, p], g[:, q]
                g[p, p], g[q, q] = app - t * apq, aqq + t * apq
                g[p, q] = g[q, p] = 0.0
                vp, vq = vectors[:, p].copy(), vectors[:, q].copy()
                vectors[:, p], vectors[:, q] = c * vp - s * vq, s * vp + c * vq
    raise ArithmeticError('Jacobi did not meet the off-diagonal tolerance.')


def svd_from_gram(matrix, eigenvalue_cutoff=1e-12):
    a = np.asarray(matrix, dtype=float)
    if a.ndim != 2 or min(a.shape) == 0 or not np.isfinite(a).all():
        raise ValueError('SVD requires a nonempty finite matrix.')
    m, n = a.shape
    gram = a.T @ a if m >= n else a @ a.T
    eigenvalues, basis, diagnostics = jacobi_eigh(gram)
    scale = max(float(eigenvalues[0]), 0.0)
    if np.min(eigenvalues) < -1e-10 * max(scale, 1):
        raise ArithmeticError('Gram matrix has a materially negative eigenvalue.')
    keep = eigenvalues > eigenvalue_cutoff * scale if scale > 0 else np.zeros(len(eigenvalues), bool)
    singular_values = np.sqrt(np.maximum(eigenvalues[keep], 0))
    if m >= n:
        v = basis[:, keep]
        u = (a @ v) / singular_values[None, :]
    else:
        u = basis[:, keep]
        v = (a.T @ u) / singular_values[None, :]
    diagnostics.update({'numerical_rank': len(singular_values),
                        'eigenvalue_cutoff': eigenvalue_cutoff})
    return u, singular_values, v.T, diagnostics


def project_query(query, u, singular_values, k, folded=False):
    if not 1 <= k <= len(singular_values):
        raise ValueError('k must retain positive singular values.')
    projected = u[:, :k].T @ np.asarray(query)
    return projected / singular_values[:k] if folded else projected
