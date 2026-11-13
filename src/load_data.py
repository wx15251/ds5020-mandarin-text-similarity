"""Describe real documents and build A; run from the repository root."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from text_vectors import characters, count_matrix, tfidf


def main():
    rng = np.random.default_rng(0)
    selected, source_audit = [], []
    for category in ['sports', 'education', 'technology']:
        frame = pd.read_json('data/raw/' + category + '.jsonl', lines=True)
        if not {'id', 'title', 'content'}.issubset(frame.columns):
            raise ValueError('Unexpected mirror schema.')
        frame['source_row'] = np.arange(len(frame))
        for field in ['id', 'title', 'content']:
            source_audit.append({'category': category, 'field': field,
                                 'dtype': str(frame[field].dtype),
                                 'missing': int(frame[field].isna().sum()),
                                 'source_rows': len(frame)})
        frame['text'] = frame['title'].fillna('') + '\n' + frame['content'].fillna('')
        frame['cleaned'] = frame['text'].map(characters)
        eligible = frame[frame['cleaned'].str.len() >= 30].copy()
        eligible = eligible.drop_duplicates(subset='cleaned')
        indices = rng.choice(len(eligible), size=100, replace=False)
        sample = eligible.iloc[np.sort(indices)].copy()
        sample['category'] = category
        selected.append(sample)
    data = pd.concat(selected, ignore_index=True)
    cross_duplicates = int(data.duplicated('cleaned').sum())
    if cross_duplicates:
        raise ValueError('Cross-category duplicate detected; review sample policy.')
    data['document_id'] = [category + ':' + str(row) for category, row in
                           zip(data['category'], data['source_row'])]
    data['character_count'] = data['cleaned'].str.len()
    counts, vocabulary = count_matrix(data['text'])
    a, idf, df = tfidf(counts)
    zero_documents = int(np.sum(np.sum(a * a, axis=0) == 0))
    pd.DataFrame(source_audit).to_csv('docs/iteration2/results/source_audit.csv', index=False)
    data[['document_id', 'category', 'source_row', 'id', 'character_count']].to_csv(
        'docs/iteration2/results/sample_manifest.csv', index=False)
    data[['document_id', 'category', 'text', 'character_count']].to_csv(
        'data/processed/documents.csv', index=False)
    pd.DataFrame({'term': vocabulary, 'document_frequency': df, 'idf': idf}).to_csv(
        'data/processed/vocabulary.csv', index=False)
    np.save('data/processed/tfidf.npy', a)
    summary = {'documents': len(data), 'categories': 3, 'per_category': 100,
               'source_rows_examined': 3000, 'metadata_columns': 4,
               'terms': len(vocabulary), 'zero_idf_terms': int(np.sum(idf == 0)),
               'zero_tfidf_documents': zero_documents,
               'duplicate_cleaned_documents': cross_duplicates,
               'nonzero_entries': int(np.count_nonzero(a)),
               'density': float(np.count_nonzero(a) / a.size),
               'min_characters': int(data['character_count'].min()),
               'median_characters': float(data['character_count'].median()),
               'max_characters': int(data['character_count'].max()),
               'mean_characters': float(data['character_count'].mean())}
    pd.Series(summary, name='value').to_csv('docs/iteration2/results/data_summary.csv')
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), constrained_layout=True)
    colors = ['#315A82', '#B36A3C', '#47806B']
    groups = ['sports', 'education', 'technology']
    axes[0].bar(groups, [100, 100, 100], color=colors)
    axes[0].set(ylabel='Documents', title='Selected topic counts', ylim=(0, 120))
    for group, color in zip(groups, colors):
        axes[1].hist(data.loc[data.category == group, 'character_count'], bins=20,
                     histtype='step', linewidth=1.8, label=group, color=color)
    axes[1].set(xlabel='Retained Chinese characters', ylabel='Documents',
                title='Document length by topic')
    axes[1].legend(frameon=False)
    fig.savefig('figures/data_overview.png', dpi=180)
    plt.close(fig)
    print(pd.Series(summary).to_string())


if __name__ == '__main__':
    main()
