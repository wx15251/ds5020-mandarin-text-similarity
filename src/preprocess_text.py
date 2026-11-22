"""Rebuild the unchanged real sample; deterministic character/jieba token lists."""
import hashlib
import json
import re
import unicodedata
import jieba
import pandas as pd
from text_vectors import characters
from verification_helpers import ROOT, RESULTS, PROCESSED, save_json


def load_fixed_sample():
    manifest = pd.read_csv(ROOT/'docs/iteration2/results/sample_manifest.csv')
    records, audit = [], []
    for category in ['sports','education','technology']:
        path = ROOT/f'data/raw/{category}.jsonl'
        if not path.exists():
            raise FileNotFoundError('Run python src/download_data.py to acquire the pinned source prefixes.')
        source = [json.loads(line) for line in path.read_text().splitlines()]
        eligible, cleaned_seen = [], set()
        short, duplicates, missing = 0, 0, 0
        for row in source:
            missing += int(not row.get('title') or not row.get('content'))
            cleaned = characters((row.get('title') or '')+'\n'+(row.get('content') or ''))
            if len(cleaned)<30:
                short += 1
            elif cleaned in cleaned_seen:
                duplicates += 1
            else:
                eligible.append(cleaned)
                cleaned_seen.add(cleaned)
        selected = manifest[manifest.category==category]
        for _, item in selected.iterrows():
            raw = source[int(item.source_row)]
            text = (raw.get('title') or '')+'\n'+(raw.get('content') or '')
            assert str(raw['id']) == str(item['id']) and len(characters(text)) == item.character_count
            records.append({'document_id':item.document_id,'category':category,'title':raw['title'],
                            'text':text,'character_count':int(item.character_count)})
        audit.append({'category':category,'source_rows':len(source),'missing_title_or_content':missing,
                      'removed_short':short,'removed_exact_duplicates_after_length_filter':duplicates,
                      'eligible_rows':len(eligible),'selected_rows':len(selected),
                      'eligible_not_selected':len(eligible)-len(selected)})
    frame = pd.DataFrame(records)
    assert frame.document_id.tolist()==manifest.document_id.tolist()
    prior = ROOT/'data/processed/documents.csv'
    if prior.exists():
        old = pd.read_csv(prior)
        assert old.document_id.tolist()==frame.document_id.tolist() and old.text.tolist()==frame.text.tolist()
    pd.DataFrame(audit).to_csv(RESULTS/'real_source_audit.csv',index=False)
    return frame


def tokenize_documents(frame):
    # The default dictionary is packaged with the pinned jieba release.
    tokenizer = jieba.Tokenizer()
    tokenizer.tmp_dir = str(PROCESSED)
    tokenizer.initialize()
    word_tokens, char_tokens, cleaning = [], [], []
    for row in frame.itertuples():
        char_tokens.append(list(characters(row.text)))
        # Replace discarded runs by spaces so unrelated words are not joined across punctuation.
        segmented_input = re.sub(r'[^\u4e00-\u9fff]+',' ',row.text)
        tokens = [t for t in tokenizer.cut(segmented_input,cut_all=False,HMM=True)
                  if t and all('\u4e00'<=ch<='\u9fff' for ch in t)]
        word_tokens.append(tokens)
        cleaning.append({'document_id':row.document_id,'original_characters':len(row.text),
                         'retained_cjk_characters':len(char_tokens[-1]),
                         'discarded_characters':len(row.text)-len(char_tokens[-1]),
                         'punctuation_removed':sum(unicodedata.category(ch).startswith('P') for ch in row.text),
                         'digits_removed':sum(ch.isdigit() for ch in row.text),
                         'word_tokens':len(tokens)})
    hashes = {}
    for name, lists in [('character',char_tokens),('word',word_tokens)]:
        path = PROCESSED/f'{name}_tokens.jsonl'
        with path.open('w') as handle:
            for doc_id, tokens in zip(frame.document_id,lists):
                handle.write(json.dumps({'document_id':doc_id,'tokens':tokens},ensure_ascii=False)+'\n')
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    dictionary = jieba.get_dict_file()
    dictionary_hash = hashlib.sha256(dictionary.read()).hexdigest()
    dictionary.close()
    save_json(RESULTS/'tokenization.json',{'jieba_version':jieba.__version__,'mode':'precise',
              'HMM':True,'dictionary_sha256':dictionary_hash,'stopword_list':None,
              'word_cleaning':'non-U+4E00..U+9FFF runs replaced by spaces; discard space tokens',
              'character_cleaning':'same U+4E00..U+9FFF filter as Iteration 2',
              'token_file_sha256':hashes,'documents_removed_this_iteration':0,'train_test_split':None})
    pd.DataFrame(cleaning).to_csv(RESULTS/'real_cleaning.csv',index=False)
    return {'character':char_tokens,'word':word_tokens}
