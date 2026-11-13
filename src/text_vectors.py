"""Explicit character counts, unsmoothed TF-IDF, and cosine similarity."""
import numpy as np


def characters(text):
    """Keep CJK Unified Ideographs U+4E00..U+9FFF, preserving multiplicity."""
    return ''.join(ch for ch in text if '\u4e00' <= ch <= '\u9fff')


def count_matrix(texts, vocabulary=None):
    cleaned = [characters(text) for text in texts]
    if vocabulary is None:
        vocabulary = sorted(set(''.join(cleaned)))
    index = {term: i for i, term in enumerate(vocabulary)}
    counts = np.zeros((len(vocabulary), len(cleaned)), dtype=float)
    for j, text in enumerate(cleaned):
        for term in text:
            if term in index:
                counts[index[term], j] += 1
    return counts, vocabulary


def tfidf(counts):
    counts = np.asarray(counts, dtype=float)
    if counts.ndim != 2 or counts.shape[1] == 0:
        raise ValueError('Counts must be a terms-by-documents matrix with documents.')
    if not np.isfinite(counts).all() or (counts < 0).any():
        raise ValueError('Counts must be finite and nonnegative.')
    df = np.sum(counts > 0, axis=1)
    idf = np.zeros(len(df))
    observed = df > 0
    idf[observed] = np.log(counts.shape[1] / df[observed])
    return counts * idf[:, None], idf, df


def query_vector(text, vocabulary, idf):
    counts, _ = count_matrix([text], vocabulary)
    return counts[:, 0] * idf


def normalize_rows(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or not np.isfinite(values).all():
        raise ValueError('Coordinates must be a finite matrix.')
    lengths = np.sqrt(np.sum(values * values, axis=1))
    if (lengths <= 0).any():
        raise ValueError('Cosine is undefined for a zero vector.')
    return values / lengths[:, None]


def cosine_matrix(document_rows):
    normalized = normalize_rows(document_rows)
    return normalized @ normalized.T


def pair_summary(cosines, labels):
    labels = np.asarray(labels)
    distinct = ~np.eye(len(labels), dtype=bool)
    same = (labels[:, None] == labels[None, :]) & distinct
    different = labels[:, None] != labels[None, :]
    if not same.any() or not different.any():
        raise ValueError('Need within-topic and across-topic pairs.')
    scores = cosines.copy()
    np.fill_diagonal(scores, -np.inf)
    nearest = np.argmax(scores, axis=1)
    return {'within': float(cosines[same].mean()),
            'across': float(cosines[different].mean()),
            'nearest_same_topic': float(np.mean(labels[nearest] == labels))}
