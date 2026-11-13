"""Build tables from measured CSVs, compile LaTeX, and package for Overleaf."""
import csv
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'docs' / 'iteration2'
RESULTS = REPORT / 'results'


def read(name):
    with (RESULTS / name).open(newline='') as handle:
        return list(csv.DictReader(handle))


def number(value):
    value = float(value)
    if value != 0 and (abs(value) < 0.0001 or abs(value) >= 100000):
        coefficient, exponent = f'{value:.2e}'.split('e')
        return '$' + coefficient + r'\times10^{' + str(int(exponent)) + '}$'
    return f'{value:.6f}'


def table(name, caption, headers, rows, columns):
    text = ('\\par\n\\begin{table}[htbp]\\centering\n\\small\n\\caption{' + caption + '}\n'
            '\\begin{tabular}{' + columns + '}\\toprule\n' + ' & '.join(headers)
            + ' \\\\ \\midrule\n')
    text += ''.join(' & '.join(row) + ' \\\\\n' for row in rows)
    text += '\\bottomrule\\end{tabular}\n\\end{table}\n\\par\n'
    (RESULTS / name).write_text(text)


def main():
    hand = {row['']: row['value'] for row in read('hand_example.csv')}
    table('hand_table.tex', 'Independent hand-example checks.',
          ['Quantity', 'Hand value', 'Code value'], [
              ['Original cosine, documents 1 and 2', '$0$', number(hand['original_cos_doc1_doc2'])],
              ['Original cosine, documents 1 and 3', '$1/\\sqrt2$', number(hand['original_cos_doc1_doc3'])],
              ['Folded cosine, documents 1 and 2', '$-1/5$', number(hand['folded_cos_doc1_doc2'])],
              ['Folded cosine, documents 1 and 3', '$\\sqrt{2/5}$', number(hand['folded_cos_doc1_doc3'])],
              ['Squared rank-one error', '$4\\log^2(3/2)$', number(hand['rank1_error_squared'])]], 'lrr')
    table('probability_table.tex', 'Known and estimated first-half token probabilities.',
          ['Topic', 'Tokens', 'Observed count', 'True $p_h$', 'Estimate', 'True SE'],
          [[r['topic'], r['tokens'], r['group_A_count'], number(r['true_probability']),
            number(r['estimated_probability']), number(r['true_standard_error'])]
           for r in read('topic_probability.csv')], 'rrrrrr')
    checks = {r['']: r['value'] for r in read('simulation_checks.csv')}
    labels = [
        ('Projected document identity, max absolute error', 'projected_coordinates_max_abs'),
        ('Projected query versus row of $D$', 'projected_query_max_abs'),
        ('Folded query versus row of $V_k$', 'folded_query_max_abs'),
        ('Reconstructed versus coordinate cosines', 'reconstructed_cosine_max_abs'),
        ('Custom versus library singular values', 'library_singular_value_max_abs'),
        ('Custom versus library rank-two reconstruction', 'library_rank2_reconstruction_max_abs')]
    table('checks_table.tex', 'Measured numerical agreement (seed 0).',
          ['Check', 'Measured error'], [[label, number(checks[key])] for label, key in labels], 'lr')
    table('error_table.tex', 'Squared reconstruction error and discarded singular-value energy.',
          ['$k$', 'Measured error', 'Tail energy', 'Absolute difference'],
          [[r['k'], number(r['measured_squared_error']), number(r['tail_squared_singular_values']),
            number(r['absolute_difference'])] for r in read('reconstruction_errors.csv')], 'rrrr')
    table('similarity_table.tex', 'Synthetic topic similarity, excluding self-pairs.',
          ['Representation', 'Within topic', 'Across topics', 'Same-topic NN rate'],
          [[r['representation'], number(r['within']), number(r['across']), number(r['nearest_same_topic'])]
           for r in read('similarity_summary.csv')], 'lrrr')
    build = ROOT / 'tmp' / 'latex'
    build.mkdir(parents=True, exist_ok=True)
    command = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
               '-output-directory=' + str(build), 'main.tex']
    for _ in range(2):
        result = subprocess.run(command, cwd=REPORT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        (build / 'build-console.txt').write_text(result.stdout)
        if result.returncode:
            print(result.stdout[-5000:])
            raise RuntimeError('LaTeX compilation failed. See tmp/latex/build-console.txt')
    shutil.copy2(build / 'main.pdf', ROOT / 'docs' / 'iteration2_report.pdf')
    archive = ROOT / 'docs' / 'iteration2_overleaf.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        bundle.write(REPORT / 'main.tex', 'main.tex')
        for file in sorted(RESULTS.glob('*.tex')):
            bundle.write(file, 'results/' + file.name)
        for name in ['data_overview.png', 'simulation_overview.png']:
            bundle.write(ROOT / 'figures' / name, 'figures/' + name)
    print('Built docs/iteration2_report.pdf and docs/iteration2_overleaf.zip')


if __name__ == '__main__':
    main()
