"""Four terms x three documents: print every worked-example stage and verify it."""
from fractions import Fraction
import json
import numpy as np
import pandas as pd
from methods import (my_count_matrix, my_tfidf, my_gram, my_svd_power, my_deflate,
                     my_cosine_matrix, my_document_coordinates)
from verification_helpers import (prepare_directories, VerificationLog, RESULTS,
                                  check_svd, save_json)


def main():
    prepare_directories()
    np.set_printoptions(precision=12, suppress=True, linewidth=120)
    tokens = [list('天气'), list('天气足球'), list('足球')]
    c, vocabulary = my_count_matrix(tokens, list('天气足球'))
    a, idf, df = my_tfidf(c)
    exact_c = [[Fraction(int(x)) for x in row] for row in c]
    exact_gram = [[sum(exact_c[t][i]*exact_c[t][j] for t in range(4)) for j in range(3)] for i in range(3)]
    sig, u, v, diagnostics = my_svd_power(a, k=2, trace=True)
    alpha = np.log(1.5)
    true_s = alpha*np.sqrt([6., 2.])
    true_v = np.array([[1/np.sqrt(6), 1/np.sqrt(2)], [2/np.sqrt(6), 0], [1/np.sqrt(6), -1/np.sqrt(2)]])
    true_u = np.array([[1,1], [1,1], [1,-1], [1,-1]], dtype=float)/2
    gram, _ = my_gram(a)
    rank1 = (u[:, :1]*sig[:1])@v[:, :1].T
    stages = {'documents': ['天气', '天气足球', '足球'], 'vocabulary': vocabulary,
              'C': c.tolist(), 'df': df.tolist(), 'idf': idf.tolist(), 'A': a.tolist(),
              'exact_CtC': [[str(x) for x in row] for row in exact_gram],
              'G': gram.tolist(), 'G_deflated_after_first': my_deflate(gram,float(sig[0]**2),v[:,0]).tolist(),
              'characteristic_polynomial_CtC': 'x(x-2)(x-6)',
              'eigenvalues': [float(6*alpha**2), float(2*alpha**2), 0.],
              'null_vector': (np.array([1.,-1.,1.])/np.sqrt(3)).tolist(),
              'sig': sig.tolist(), 'U': u.tolist(), 'Sigma': np.diag(sig).tolist(), 'V': v.tolist(),
              'reconstruction': ((u*sig)@v.T).tolist(), 'rank1_A': rank1.tolist(),
              'rank1_D': my_document_coordinates(v[:, :1],sig[:1]).tolist(),
              'original_cosine': my_cosine_matrix(a.T).tolist(),
              'rank1_cosine': my_cosine_matrix(my_document_coordinates(v[:, :1],sig[:1])).tolist(),
              'rank1_retained_energy': float(sig[0]**2/np.sum(a*a)),
              'rank1_squared_error': float(np.sum((a-rank1)**2)), 'power': diagnostics}
    for name, value in stages.items():
        print('\n'+name+':\n'+(json.dumps(value, ensure_ascii=False, indent=2) if isinstance(value,dict) else str(value)))
    log = VerificationLog()
    log.report('Tiny', 'exact rational Gram', np.array(exact_gram,float), c.T@c, 'Fraction multiplication', atol=0.)
    log.report('Tiny', 'analytic singular values', sig, true_s, 'sqrt(6)*alpha, sqrt(2)*alpha')
    log.report('Tiny', 'analytic reconstruction', (u*sig)@v.T, (true_u*true_s)@true_v.T, 'hand SVD')
    log.report('Tiny', 'eigen-equations', gram@true_v, true_v*(true_s**2), 'Gv=lambda v')
    log.report('Tiny', 'null-space equation', gram@np.array(stages['null_vector']), np.zeros(3), 'Gv0=0')
    log.report('Tiny', 'rank-one cosine', np.array(stages['rank1_cosine']), np.ones((3,3)), 'analytic cosine')
    log.report('Tiny', 'rank-one energy', stages['rank1_retained_energy'], .75, '6/(6+2)')
    log.report('Tiny', 'rank-one squared error', stages['rank1_squared_error'], 2*alpha**2, 'discarded sigma squared')
    check_svd(a,sig,u,v,diagnostics,'Tiny',log)
    log.save('verification_small.csv')
    save_json(RESULTS/'small_example.json',stages)
    pd.DataFrame([{'pair':'1,2','original':stages['original_cosine'][0][1],'rank1':stages['rank1_cosine'][0][1]},
                  {'pair':'1,3','original':stages['original_cosine'][0][2],'rank1':stages['rank1_cosine'][0][2]},
                  {'pair':'2,3','original':stages['original_cosine'][1][2],'rank1':stages['rank1_cosine'][1][2]}]).to_csv(RESULTS/'small_cosines.csv',index=False)


if __name__ == '__main__':
    main()
