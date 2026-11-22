"""Iteration 2 two-topic model as a reusable, parameterized generator."""
import numpy as np


def simulate_two_topics(n_docs=40, seed=0, n_terms=50, tokens_per_doc=60, overlap=0.0):
    """Return C, topic labels, theta and parameters; exact original draw order at n=40.

    Each call redraws theta first from the same seed; hence fixed seed keeps theta
    identical across sample sizes. Documents are balanced, grouped by topic.
    Larger samples are not nested for topic 1 because the topic-0 draw count changes.
    overlap is an explicitly declared stress-test change only.
    """
    if n_docs < 4 or n_docs % 2 or n_terms != 50 or tokens_per_doc < 1 or not 0 <= overlap <= 1:
        raise ValueError('Use balanced even n>=4, 50 terms, positive length and overlap in [0,1].')
    rng = np.random.default_rng(seed)
    theta = np.array([
        rng.dirichlet(np.r_[np.full(25, 2.0), np.full(25, 0.1)]),
        rng.dirichlet(np.r_[np.full(25, 0.1), np.full(25, 2.0)])])
    if overlap:
        theta = (1 - overlap) * theta + overlap * theta.mean(axis=0)
    topic = np.repeat([0, 1], n_docs // 2)
    counts = np.column_stack([rng.multinomial(tokens_per_doc, theta[t]) for t in topic]).astype(float)
    return counts, topic, theta, {'n_docs': n_docs, 'n_terms': n_terms, 'seed': seed,
                                'tokens_per_doc': tokens_per_doc, 'overlap': overlap}
