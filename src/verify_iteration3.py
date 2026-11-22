"""Numerical regression cases for the new core, beyond the required worked example."""
import numpy as np
from methods import (my_svd_power, my_cosine_matrix, my_energy_rank,
                     my_count_matrix, my_tfidf, my_query_vector)
from verification_helpers import prepare_directories, VerificationLog


def main():
    prepare_directories()
    log = VerificationLog()
    rng = np.random.default_rng(42)
    tall = rng.normal(size=(7,4))
    for name,a,k in [('tall',tall,4),('wide',tall.T,4),
                     ('rank deficient',np.outer([1.,2.,3.],[2.,-1.]),1),
                     ('repeated values',np.diag([3.,3.,1.]),3)]:
        sig,u,v,diagnostics = my_svd_power(a,k=k)
        log.report(name,'singular values',sig,np.linalg.svd(a,compute_uv=False)[:k],'NumPy SVD')
        log.report(name,'full resolved reconstruction',(u*sig)@v.T,a,'input matrix')
    sig,u,v,diag = my_svd_power(np.diag([4.,2.,1.]),k=None,energy=.9)
    rank,_ = my_energy_rank(sig,21.,.9)
    log.report('energy selection','minimum rank',rank,2.,'16/21<.9, 20/21>=.9',atol=0.)
    c,vocabulary = my_count_matrix([['a','a'],['b'],['a','b']])
    a,idf,_ = my_tfidf(c)
    log.report('frozen query','known column',my_query_vector(['a','a'],vocabulary,idf),a[:,0],'first document',atol=0.)
    rejected = 0
    for operation in [lambda:my_svd_power(np.zeros((2,2)),k=1),
                      lambda:my_cosine_matrix(np.array([[0.,0.]])),
                      lambda:my_tfidf(np.array([[-1.]])),
                      lambda:my_svd_power(np.eye(2),k=3),
                      lambda:my_svd_power(np.diag([2.,1.]),k=1,max_iter=1)]:
        try:
            operation()
        except (ValueError,ArithmeticError):
            rejected += 1
    log.report('invalid inputs','explicit failures',rejected,5.,'five expected failures',atol=0.)
    log.save('verification_edges.csv')


if __name__ == '__main__':
    main()
