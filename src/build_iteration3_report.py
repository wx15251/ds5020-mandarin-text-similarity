"""Generate Iteration 3 tables from evidence, compile XeLaTeX, package Overleaf."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
import numpy as np
import pandas as pd
from verification_helpers import ROOT, RESULTS, FIGURES

REPORT = ROOT/'docs/iteration3/report'


def escape(value):
    replacements = {'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$',
                    '#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(replacements.get(ch,ch) for ch in str(value)).strip()


def number(value, digits=6):
    value = float(value)
    if value and (abs(value)<1e-4 or abs(value)>=1e5):
        coefficient,exponent = f'{value:.2e}'.split('e')
        return '$'+coefficient+r'\times10^{'+str(int(exponent))+'}$'
    return f'{value:.{digits}f}'


def table(filename, caption, headers, rows, columns):
    size = r'\footnotesize\renewcommand{\arraystretch}{1}' if filename=='tiny_trace.tex' else r'\small\renewcommand{\arraystretch}{1.05}'
    text = '{'+size+'\n\\begin{longtable}{'+columns+'}\n'
    text += '\\caption{'+caption+'}\\\\\n\\toprule\n'+' & '.join(headers)+' \\\\ \\midrule\\endfirsthead\n'
    text += '\\toprule\n'+' & '.join(headers)+' \\\\ \\midrule\\endhead\n'
    text += ''.join(' & '.join(row)+' \\\\\n' for row in rows)
    text += '\\bottomrule\n\\end{longtable}\n}\n'
    (RESULTS/filename).write_text(text)


def generate_tables():
    small = json.loads((RESULTS/'small_example.json').read_text())
    real = pd.read_csv(RESULTS/'real_summary.csv')
    similarities = pd.read_csv(RESULTS/'real_similarity.csv')
    probabilities = pd.read_csv(RESULTS/'simulation_probability.csv')
    stress = pd.read_csv(RESULTS/'simulation_stress.csv')
    all_checks = pd.concat([pd.read_csv(path) for path in sorted(RESULTS.glob('verification_*.csv'))
                            if path.name not in ['verification_all.csv']],ignore_index=True)
    assert all_checks['pass'].all()
    all_checks.to_csv(RESULTS/'verification_all.csv',index=False)
    macros = {'VerificationCount':str(len(all_checks)),
              'MaxSigmaError':number(all_checks.loc[all_checks.quantity=='singular values','max_abs_error'].max()),
              'MaxCosineError':number(all_checks.loc[all_checks.quantity=='reduced cosine vs library SVD','max_abs_error'].max())}
    for name,prefix in [('character','Char'),('word','Word')]:
        row = real[real.tokens==name].iloc[0]
        for suffix,col in [('Terms','terms'),('Rank','k_90'),('Iterations','iterations_total')]:
            macros[prefix+suffix] = str(int(row[col]))
        for suffix,col in [('Energy','retained_energy'),('PreviousEnergy','previous_energy'),
                           ('BoundaryRatio','boundary_ratio_next_over_retained'),('Condition','resolved_condition_number')]:
            macros[prefix+suffix] = number(row[col])
    (RESULTS/'macros.tex').write_text('\n'.join('\\newcommand{\\'+key+'}{'+value+'}' for key,value in macros.items())+'\n')
    table('tiny_cosines.tex','Worked-example distinct-document cosines.',
          ['Pair','Original','Rank 1'],[[escape(row.pair),number(row.original),number(row.rank1)]
          for row in pd.read_csv(RESULTS/'small_cosines.csv').itertuples()], 'lrr')
    matrices = []
    for key,label in [('A','A'),('G','G'),('G_deflated_after_first',r'G^{(1)}'),
                      ('U','U'),('Sigma',r'\Sigma'),('V','V'),('reconstruction',r'U\Sigma V^\top'),
                      ('rank1_A','A_1'),('rank1_D','D_1'),('original_cosine','S'),('rank1_cosine','S_1')]:
        matrix = np.asarray(small[key])
        body = r'\\'.join(' & '.join(f'{float(x):.9f}' for x in row) for row in matrix)
        matrices.append('\\[ '+label+'=\\begin{bmatrix}'+body+'\\end{bmatrix}. \\]\n')
    paired = []
    for start in range(0,len(matrices),2):
        pair = matrices[start:start+2]
        paired.append('\\noindent'+r'\hfill'.join(
            r'\begin{minipage}[t]{.48\textwidth}\footnotesize\setlength{\arraycolsep}{3pt}'+item+r'\end{minipage}' for item in pair)+r'\par'+'\n')
    (RESULTS/'tiny_matrices.tex').write_text(''.join(paired))
    trace_rows = []
    for component in small['power']['components']:
        for row in component['history']:
            trace_rows.append([str(component['component']),str(row['iteration'])]+
                              [f'{x:.8f}' for x in row['vector']]+[number(row['eigenvalue']),number(row['residual'])])
    table('tiny_trace.tex','Every power-iteration vector in the tiny example (including each starting vector).',
          ['Direction','Step','$v_1$','$v_2$','$v_3$',r'$\lambda$','Residual'],trace_rows,'rrrrrrr')
    table('simulation_probability.tex','Known-probability sampling checks. SE uses the true fixed probability.',
          ['$n$','Topic','$N_h$','True $p_h$',r'$\widehat p_h$','Absolute error','SE','Within 3SE'],
          [[str(int(r.n)),str(int(r.topic)),str(int(r.token_count)),number(r.true_p),number(r.estimate),
            number(r.absolute_error),number(r.se),'Yes' if r.within_3se else 'No']
           for r in probabilities.itertuples()],'rrrrrrrl')
    sim = pd.read_csv(RESULTS/'simulation_similarity.csv')
    table('simulation_similarity.tex','Simulation topic recovery; within means exclude self-pairs.',
          ['$n$','Representation','Within','Across','Gap','Same-topic NN'],
          [[str(r.n),escape(r.representation),number(r.within),number(r.across),number(r.gap),number(r.nearest_same_topic)]
           for r in sim.itertuples()],'rlrrrr')
    table('stress.tex','Topic-overlap stress test; gap uses off-diagonal within-topic means.',
          ['$\rho$','Representation','Within','Across','Gap','Same-topic NN'],
          [[f'{r.overlap:.2f}',escape(r.representation),number(r.within),number(r.across),number(r.gap),number(r.nearest_same_topic)]
           for r in stress.itertuples()],'rlrrrr')
    table('real_shapes.tex','Same 300 documents under both tokenizations; rank chosen at 90 percent energy.',
          ['Tokens','Terms','Nonzeros','Density','$k$','$E_{k-1}$','$E_k$'],
          [[escape(r.tokens),f'{r.terms:,}',f'{r.nonzeros:,}',number(r.density),str(r.k_90),
            number(r.previous_energy),number(r.retained_energy)] for r in real.itertuples()],'lrrrrrr')
    table('real_similarity.tex','Real-data topic similarity, excluding self-pairs.',
          ['Tokens','Representation','Within','Across','Gap','Same-topic NN'],
          [[escape(r.tokens),escape(r.representation),number(r.within),number(r.across),number(r.gap),number(r.nearest_same_topic)]
           for r in similarities.itertuples()],'llrrrr')
    audit = pd.read_csv(RESULTS/'real_source_audit.csv')
    table('cleaning.tex','Unchanged source-prefix filtering and fixed sample.',
          ['Category','Source rows','Missing','Short','Duplicates','Eligible','Selected'],
          [[escape(r.category),str(r.source_rows),str(r.missing_title_or_content),str(r.removed_short),
            str(r.removed_exact_duplicates_after_length_filter),str(r.eligible_rows),str(r.selected_rows)]
           for r in audit.itertuples()],'lrrrrrr')
    query = pd.read_csv(RESULTS/'query_top5.csv')
    for name in ['character','word']:
        for representation,suffix in [('TF-IDF','original'),('SVD 90%','reduced')]:
            part = query[(query.tokens==name)&(query.representation==representation)]
            table(f'query_{name}_{suffix}.tex',escape(name+' tokens, '+representation+': top five, query itself excluded.'),
                  ['Rank','ID (category prefix)','Title','Cosine'],
                  [[str(r.position),escape(r.document_id),escape(r.title),number(r.cosine)]
                   for r in part.itertuples()],r'rp{.22\textwidth}p{.47\textwidth}r')
    assumption = pd.read_csv(RESULTS/'real_assumptions.csv')
    table('numerical_assumptions.tex','Real-data numerical diagnostics; zeros and duplicates checked before interpreting cosines.',
          ['Quantity','Characters','Words'],
          [[label]+[number(assumption.loc[assumption.data==name,col].iloc[0]) for name in ['character','word']]
           for label,col in [('Zero original vectors','zero_original_columns'),('Zero projected vectors','zero_projected_rows'),
                             ('Exact duplicates','exact_duplicate_documents'),('U orthogonality error','u_orthogonality'),
                             ('V orthogonality error','v_orthogonality'),('Smallest retained singular value','smallest_retained_sigma'),
                             ('Next / last retained singular value','boundary_ratio_next_over_retained'),
                             ('Resolved condition number (library check)','resolved_condition_number'),
                             ('Cosine change at tolerance $10^{-13}$','cosine_change_tolerance_1e_13')]],'lrr')
    selected = []
    for row in all_checks.itertuples():
        keep = ((row.data=='Tiny' and row.quantity in ['exact rational Gram','analytic reconstruction','rank-one squared error'])
                or (row.quantity in ['singular values','reduced cosine vs library SVD','fold-in']
                    and (row.data.startswith('Sim ') or row.data in ['character','word']))
                or (row.data.startswith('Baseline') and row.quantity=='unchanged counts'))
        if keep:
            selected.append([escape(row.data),escape(row.quantity),escape(row.compared_with),number(row.max_abs_error),'Yes'])
    for row in probabilities.itertuples():
        selected.append([f'Sim n={row.n}',f'$p_{{{row.topic}}}$ sampling',f'true $p$; limit $3SE={row.se*3:.6f}$',
                         number(row.absolute_error),'Yes' if row.within_3se else 'No'])
    table('verification.tex',r'Unified verification table. Full absolute/relative errors and limits are in verification\_all.csv.',
          ['Data','Quantity','Compared with','Difference','Pass?'],selected,
          r'p{.14\textwidth}p{.25\textwidth}p{.29\textwidth}rl')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--tables-only',action='store_true')
    args=parser.parse_args()
    generate_tables()
    if args.tables_only:
        return
    build=ROOT/'tmp/latex_iteration3'
    build.mkdir(parents=True,exist_ok=True)
    for _ in range(2):
        result=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',
                               '-output-directory='+str(build),'main.tex'],cwd=REPORT,
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (build/'build-console.txt').write_text(result.stdout)
        if result.returncode:
            print(result.stdout[-6000:])
            raise RuntimeError('XeLaTeX failed; see tmp/latex_iteration3/build-console.txt')
    shutil.copy2(build/'main.pdf',ROOT/'docs/iteration3_report.pdf')
    with zipfile.ZipFile(ROOT/'docs/iteration3_overleaf.zip','w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('main.tex',(REPORT/'main.tex').read_text().replace('{../results}','{results}'))
        for path in sorted(REPORT.glob('*.tex')):
            if path.name != 'main.tex':
                archive.write(path,path.name)
        for path in sorted(RESULTS.glob('*.tex')):
            archive.write(path,'results/'+path.name)
        for path in sorted(FIGURES.glob('*.png')):
            archive.write(path,'figures/'+path.name)
        archive.writestr('README.txt','Compile main.tex with XeLaTeX. Generated from the public project source.\n')
    print('Built docs/iteration3_report.pdf and docs/iteration3_overleaf.zip')


if __name__=='__main__':
    main()
