# Dataset acquisition and provenance

The instructor suggests THUCNews. We use full title-plus-body news from the [Tongjilibo THUCNews mirror](https://huggingface.co/datasets/Tongjilibo/THUCNews), with the [original THUNLP description](https://github.com/thunlp/THUCTC) as the corpus reference.

- Pinned mirror revision: `ae77e363396e90b54cdaa9eafdbc5e102a3d4019`.
- Accessed: November 13, 2026.
- Source files: `体育.jsonl` (sports), `教育.jsonl` (education), `科技.jsonl` (technology).
- Mirror metadata labels the dataset Apache-2.0. Raw article text is kept local; no blanket claim is made about rights to republish the original news.

Run `python src/download_data.py` from the repository root. It reads exactly the first 1,000 complete JSONL records per file and closes the remote response. It saves local prefixes under `data/raw/` and records URLs, SHA-256 hashes, byte sizes, and revision in `source_manifest.json`. No Hugging Face account or dataset package is needed.

Run `python src/load_data.py` to concatenate title/body, keep U+4E00..U+9FFF characters, require at least 30 retained characters, and remove exact within-category duplicates. In fixed order sports, education, technology, seed 0 selects 100 eligible rows without replacement per category. The chosen rows are sorted by source index. Cross-category exact duplicates are checked and cause an error if found.

This is a sample of a **finite source prefix**, not a random sample of the complete corpus. Source ordering may bias subtopics and dates. Selected original row IDs and file IDs are recorded in `docs/iteration2/results/sample_manifest.csv` without reproducing article text.

The processed document table has `document_id` (string), `category` (string), `text` (string), and `character_count` (integer). The sample has 300 documents, 3,123 terms, and no missing processed fields or zero TF-IDF documents. Raw source fields `id`, `title`, `content` have zero missing entries in the 3,000 examined records. The source audit and data summary are saved with the results.

`raw/` contains unchanged local prefixes. `processed/` contains document text, vocabulary/IDF, the terms-by-documents TF-IDF matrix, and the simulation arrays. Both folders are excluded from Git. The downloader can reacquire the inputs after cloning; compare hashes against the committed manifest. Delete only local source-prefix files if you intentionally want to redownload them.

Iteration 3 uses `python src/run_real.py` after acquisition. It reads the exact recorded sample IDs rather than resampling and can rebuild without the old processed files. It checks an existing Iteration 2 document table/matrix when those are available. Character filtering is unchanged; word preprocessing uses pinned jieba precise mode with HMM enabled and no stopword list. Punctuation, digits and other non-Chinese runs are replaced by spaces before word segmentation to preserve boundaries.

Ordered token lists, vocabulary/IDF and model arrays are stored locally under `data/processed/iteration3/`, also ignored by Git. Settings, dictionary and token-file hashes, cleaning counts and numerical summaries are tracked under `docs/iteration3/results/`. No selected document is dropped. Evaluation is descriptive within the fixed collection, with the query self-match excluded; no train/test split is used.
