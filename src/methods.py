"""Iteration 3 numerical core. NumPy array operations only; no library solvers.

A is terms x documents; my_svd_power returns sig, U, V (not V.T).
Equation tags refer to docs/iteration3/main.tex.
"""
import numpy as np


# (E1) C[t,j] = sum over tokens x in document j of 1{x = vocabulary[t]}.
def my_count_matrix(token_lists, vocabulary=None):
    token_lists = [list(tokens) for tokens in token_lists]
    if not token_lists:
        raise ValueError('At least one document is required.')
    vocabulary = sorted({t for tokens in token_lists for t in tokens}) if vocabulary is None else list(vocabulary)
    if len(set(vocabulary)) != len(vocabulary):
        raise ValueError('Vocabulary must contain unique terms.')
    index = {term: i for i, term in enumerate(vocabulary)}
    counts = np.zeros((len(vocabulary), len(token_lists)), dtype=float)
    for j, tokens in enumerate(token_lists):
        for term in tokens:
            if term in index:
                counts[index[term], j] += 1
    return counts, vocabulary


# (E2) df_t = sum_j 1{C_tj > 0}, w_t = log(n/df_t), A_tj = C_tj w_t.
def my_tfidf(counts):
    counts = np.asarray(counts, dtype=float)
    if counts.ndim != 2 or counts.shape[1] == 0 or not np.isfinite(counts).all() or (counts < 0).any():
        raise ValueError('Counts must be a finite nonnegative terms-by-documents matrix.')
    df = np.sum(counts > 0, axis=1)
    idf = np.zeros(len(df))
    observed = df > 0
    idf[observed] = np.log(counts.shape[1] / df[observed])
    return counts * idf[:, None], idf, df


# (E3) q_t = query_count_t * fitted_idf_t in the frozen document vocabulary.
def my_query_vector(tokens, vocabulary, idf):
    counts, _ = my_count_matrix([tokens], vocabulary)
    idf = np.asarray(idf, dtype=float)
    if idf.shape != (len(vocabulary),) or not np.isfinite(idf).all():
        raise ValueError('IDF must match the frozen vocabulary.')
    return counts[:, 0] * idf


# (E4) G = A.T A if n <= m, otherwise G = A A.T; p = min(m,n).
def my_gram(a):
    a = np.asarray(a, dtype=float)
    if a.ndim != 2 or min(a.shape) == 0 or not np.isfinite(a).all():
        raise ValueError('A must be a nonempty finite matrix.')
    right = a.shape[1] <= a.shape[0]
    return (a.T @ a if right else a @ a.T), right


# (E5) x <- (I - QQ.T)x, applied twice to reduce floating-point loss of orthogonality.
def my_reorthogonalize(x, basis):
    x = np.asarray(x, dtype=float).copy()
    if basis.shape[1]:
        for _ in range(2):
            x -= basis @ (basis.T @ x)
    return x


# (E6) x_{t+1} = P G x_t / ||P G x_t||, lambda = x.T G x; P = I - QQ.T.
def my_power_iteration(g, basis, rng, scale, tol=1e-14, max_iter=200000, trace=False):
    if not 0 < tol < 1 or max_iter < 1:
        raise ValueError('Positive tolerance and iteration limit required.')
    x = my_reorthogonalize(rng.normal(size=len(g)), basis)
    length = np.sqrt(np.sum(x * x))
    if length < 1e-14:
        raise ArithmeticError('Starting vector has no resolved orthogonal component.')
    x /= length
    history = []
    if trace:
        gx = my_reorthogonalize(g @ x, basis)
        value = float(x @ gx)
        history.append({'iteration':0,'vector':x.tolist(),'eigenvalue':value,
                        'residual':float(np.sqrt(np.sum((gx-value*x)**2)))})
    for iteration in range(1, max_iter + 1):
        y = my_reorthogonalize(g @ x, basis)
        length = np.sqrt(np.sum(y * y))
        if length <= np.finfo(float).eps * scale:
            raise ArithmeticError('No resolved positive direction remains.')
        x = y / length
        gx = my_reorthogonalize(g @ x, basis)
        value = float(x @ gx)
        residual = float(np.sqrt(np.sum((gx - value * x) ** 2)))
        if trace:
            history.append({'iteration': iteration, 'vector': x.tolist(),
                            'eigenvalue': value, 'residual': residual})
        if residual <= tol * scale:
            return x, value, iteration, residual, history
    raise ArithmeticError(f'Power iteration did not converge in {max_iter} steps; residual={residual:.3e}.')


# (E7) G_next = G - lambda v v.T; symmetrize only to remove roundoff asymmetry.
def my_deflate(g, value, vector):
    remaining = g - value * np.outer(vector, vector)
    return (remaining + remaining.T) / 2


# (E8) sigma_i = sqrt(lambda_i), u_i = A v_i/sigma_i (or v_i = A.T u_i/sigma_i).
def my_svd_power(a, k=2, *, energy=None, tol=1e-14, max_iter=200000,
                 seed=0, rank_rtol=1e-12, trace=False):
    a = np.asarray(a, dtype=float)
    gram, right = my_gram(a)
    if energy is not None:
        if k is not None or not 0 < energy <= 1:
            raise ValueError('Use k=None with an energy target in (0,1].')
    elif not isinstance(k, (int, np.integer)) or not 1 <= k <= min(a.shape):
        raise ValueError('k must be a positive integer no larger than min(A.shape).')
    if not 0 < rank_rtol < 1:
        raise ValueError('rank_rtol must lie in (0,1).')
    total = float(np.sum(a * a))
    if total <= 0:
        raise ValueError('Zero matrix has no positive singular directions.')
    # The Frobenius norm of G is an upper bound on its spectral norm.
    scale = float(np.sqrt(np.sum(gram * gram)))
    residual_gram = gram.copy()
    basis = np.empty((len(gram), 0))
    values, records = [], []
    rng = np.random.default_rng(seed)
    limit = min(a.shape) if energy is not None else k
    for component in range(limit):
        vector, _, iterations, projected_residual, history = my_power_iteration(
            residual_gram, basis, rng, scale, tol, max_iter, trace)
        value = float(vector @ gram @ vector)
        if value <= rank_rtol * (values[0] if values else scale):
            raise ArithmeticError('Requested rank/energy reaches numerically unresolved singular values.')
        basis = np.column_stack((basis, vector))
        values.append(value)
        records.append({'component': component + 1, 'iterations': iterations,
                        'eigenvalue': value, 'projected_residual': projected_residual,
                        'original_residual': float(np.sqrt(np.sum((gram @ vector - value * vector) ** 2))),
                        'history': history})
        residual_gram = my_deflate(residual_gram, value, vector)
        if energy is not None and sum(values) / total >= energy:
            break
    order = np.argsort(-np.asarray(values), kind='stable')
    sig = np.sqrt(np.asarray(values)[order])
    basis = basis[:, order]
    if right:
        v, u = basis, (a @ basis) / sig
    else:
        u, v = basis, (a.T @ basis) / sig
    # Canonical signs aid readable output; verification still accounts for sign ambiguity.
    signs = np.where(v[np.argmax(np.abs(v), axis=0), np.arange(len(sig))] < 0, -1.0, 1.0)
    u, v = u * signs, v * signs
    diagnostics = {'gram_side': 'right' if right else 'left', 'tolerance': tol,
                   'rank_rtol': rank_rtol, 'total_energy': total,
                   'retained_energy': float(np.sum(sig * sig) / total), 'components': records,
                   'iterations_total': int(sum(r['iterations'] for r in records))}
    return sig, u, v, diagnostics


# (E9) D = V_k Sigma_k: document coordinates have shape n x k.
def my_document_coordinates(v, sig):
    return np.asarray(v) * np.asarray(sig)


# (E10) z = U_k.T q; folded coordinates h = Sigma_k^-1 z belong with V_k.
def my_project_query(q, u, sig, folded=False):
    q, u, sig = np.asarray(q), np.asarray(u), np.asarray(sig)
    if q.shape != (u.shape[0],) or u.shape[1] != len(sig) or (sig <= 0).any():
        raise ValueError('Query and positive singular factors must have matching dimensions.')
    z = u.T @ q
    return z / sig if folded else z


# (E11) N_i = X_i/||X_i||_2; cosine matrix S = N N.T.
def my_normalize_rows(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or not np.isfinite(values).all():
        raise ValueError('Finite row coordinates required.')
    lengths = np.sqrt(np.sum(values * values, axis=1))
    if (lengths <= 0).any():
        raise ValueError('Cosine is undefined for a zero vector.')
    return values / lengths[:, None]


# (E11) S_ij = dot(X_i,X_j)/(||X_i|| ||X_j||).
def my_cosine_matrix(document_rows):
    normalized = my_normalize_rows(document_rows)
    return normalized @ normalized.T


# (E12) query similarities s_i = dot(D_i,z)/(||D_i|| ||z||).
def my_query_cosines(query, document_rows):
    query = np.asarray(query, dtype=float)
    return (my_normalize_rows(document_rows) @ my_normalize_rows(query[None, :]).T)[:, 0]


# (E13) E_k = sum_{i<=k} sigma_i^2 / ||A||_F^2; select min{k:E_k >= target}.
def my_energy_rank(sig, total_energy, target=0.9):
    sig = np.asarray(sig, dtype=float)
    if not 0 < target <= 1 or total_energy <= 0 or (sig < 0).any():
        raise ValueError('Positive total energy and a target in (0,1] required.')
    cumulative = np.cumsum(sig * sig) / total_energy
    hits = np.flatnonzero(cumulative >= target - 1e-14)
    if not len(hits):
        raise ValueError('Computed spectrum does not reach the requested energy.')
    return int(hits[0] + 1), cumulative


# (E14) arg top-5 s_j, excluding requested IDs, with ascending ID as a tie-breaker.
def my_top_matches(scores, document_ids, number=5, exclude=()):
    scores = np.asarray(scores, dtype=float)
    if scores.shape != (len(document_ids),) or not np.isfinite(scores).all() or number < 1:
        raise ValueError('Finite scores and matching document IDs required.')
    excluded = set(exclude)
    order = sorted((j for j, doc_id in enumerate(document_ids) if doc_id not in excluded),
                   key=lambda j: (-scores[j], str(document_ids[j])))
    return order[:number]
