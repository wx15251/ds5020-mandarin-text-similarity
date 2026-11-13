"""Download finite prefixes of pinned THUCNews mirror files; no corpus in Git.

Standard-library imports below handle network/file provenance only. Numerical
method code uses NumPy; no additional numerical/NLP package is required.
"""
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

REVISION = 'ae77e363396e90b54cdaa9eafdbc5e102a3d4019'
CATEGORIES = {'sports': '体育', 'education': '教育', 'technology': '科技'}
ROOT = Path(__file__).resolve().parents[1]


def main():
    raw = ROOT / 'data' / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    records = []
    for label, chinese in CATEGORIES.items():
        url = ('https://huggingface.co/datasets/Tongjilibo/THUCNews/resolve/'
               + REVISION + '/' + quote(chinese + '.jsonl'))
        path = raw / (label + '.jsonl')
        if not path.exists():
            lines = []
            with urlopen(url, timeout=60) as response:
                for _ in range(1000):
                    line = response.readline()
                    if not line:
                        raise ValueError('Source contains fewer than 1000 records: ' + label)
                    json.loads(line)  # Check complete JSON before saving any output.
                    lines.append(line)
            path.write_bytes(b''.join(lines))
        content = path.read_bytes()
        if len(content.splitlines()) != 1000:
            raise ValueError('Expected exactly 1000 source records: ' + str(path))
        records.append({'category': label, 'original_category': chinese,
                        'url': url, 'revision': REVISION, 'prefix_rows': 1000,
                        'sha256': hashlib.sha256(content).hexdigest(),
                        'bytes': len(content)})
        print(label, len(content), 'bytes; 1000 source records')
    (ROOT / 'data' / 'source_manifest.json').write_text(
        json.dumps({'retrieved_on': '2026-11-13', 'sources': records},
                   ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
