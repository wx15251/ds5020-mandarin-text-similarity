"""Preserved simulation, sample-size truth checks, library checks and stress test."""
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from methods import my_tfidf, my_svd_power, my_cosine_matrix, my_document_coordinates
from simulate import simulate_two_topics
from verification_helpers import (ROOT, RESULTS, FIGURES, PROCESSED, prepare_directories,
                                  VerificationLog, topic_summary, check_svd, save_json,
                                  unsupported_input_checks)


def main():
    prepare_directories()
    old_path = ROOT/'data/processed/simulation.npz'
    counts, labels, theta, _ = simulate_two_topics()
    log = VerificationLog()
    baseline_comparison = 'Original generator reproduced without local NPZ'
    if old_path.exists():
        old = np.load(old_path)
        for key, actual in [('counts',counts),('topic',labels),('theta',theta)]:
            log.report('Baseline', 'unchanged '+key, actual, old[key], 'Iteration 2 NPZ', atol=0.)
        baseline_comparison = hashlib.sha256(old_path.read_bytes()).hexdigest()
    else:
        # Independent literal reproduction of the prior draw sequence, not a new baseline.
        rng = np.random.default_rng(0)
        prior_theta = np.array([rng.dirichlet(np.r_[np.full(25,2.),np.full(25,.1)]),
                                rng.dirichlet(np.r_[np.full(25,.1),np.full(25,2.)])])
        prior_counts = np.column_stack([rng.multinomial(60,prior_theta[t]) for t in np.repeat([0,1],20)]).astype(float)
        log.report('Baseline','unchanged counts',counts,prior_counts,'literal Iteration 2 generator',atol=0.)
        log.report('Baseline','unchanged theta',theta,prior_theta,'literal Iteration 2 generator',atol=0.)
    sizes, probabilities, similarities, diagnostic_rows, assumptions = [40,200,1000], [], [], [], []
    for n in sizes:
        counts, labels, theta, parameters = simulate_two_topics(n_docs=n)
        a, idf, df = my_tfidf(counts)
        sig,u,v,diagnostics = my_svd_power(a,k=2)
        ref_s, details = check_svd(a,sig,u,v,diagnostics,f'Sim n={n}',log)
        diagnostic_rows.append({'n':n,**details, 'retained_energy':diagnostics['retained_energy']})
        for representation, coordinates in [('TF-IDF',a.T),('SVD k=2',my_document_coordinates(v,sig))]:
            statistics = topic_summary(my_cosine_matrix(coordinates),labels)
            similarities.append({'n':n,'representation':representation,**statistics})
            if n==40 and representation=='SVD k=2':
                assert statistics['within_including_self']>.9 and statistics['across']<.2, statistics
        for h in [0,1]:
            p = float(theta[h,:25].sum())
            total = int(counts[:,labels==h].sum())
            observed = int(counts[:25,labels==h].sum())
            estimate = observed/total
            se = float(np.sqrt(p*(1-p)/total))
            error = abs(estimate-p)
            probabilities.append({'n':n,'topic':h,'token_count':total,'observed':observed,
                                  'true_p':p,'estimate':estimate,'absolute_error':error,'se':se,
                                  'within_3se':error<=3*se})
            # Sampling diagnostics are observations, not a deterministic solver guarantee.
        assumptions.append(unsupported_input_checks(a,list(range(50)),idf,
                            list(np.repeat(np.arange(50),counts[:,0].astype(int))),f'Sim n={n}'))
        if n==40:
            np.savez(PROCESSED/'simulation_baseline.npz',counts=counts,topic=labels,theta=theta,tfidf=a)
        save_json(RESULTS/f'simulation_{n}_diagnostics.json',{'parameters':parameters,'method':diagnostics})
    stress = []
    for overlap in [0.,.25,.5,.75,1.]:
        counts,labels,theta,parameters = simulate_two_topics(overlap=overlap)
        a,_,_ = my_tfidf(counts)
        sig,u,v,diagnostics = my_svd_power(a,k=2)
        check_svd(a,sig,u,v,diagnostics,f'Stress rho={overlap}',log)
        for representation, coordinates in [('TF-IDF',a.T),('SVD k=2',my_document_coordinates(v,sig))]:
            stress.append({'overlap':overlap,'representation':representation,
                           **topic_summary(my_cosine_matrix(coordinates),labels)})
    pd.DataFrame(probabilities).to_csv(RESULTS/'simulation_probability.csv',index=False)
    pd.DataFrame(similarities).to_csv(RESULTS/'simulation_similarity.csv',index=False)
    pd.DataFrame(diagnostic_rows).to_csv(RESULTS/'simulation_diagnostics.csv',index=False)
    pd.DataFrame(assumptions).to_csv(RESULTS/'simulation_assumptions.csv',index=False)
    pd.DataFrame(stress).to_csv(RESULTS/'simulation_stress.csv',index=False)
    save_json(RESULTS/'baseline_provenance.json',{'iteration2_npz_sha256':baseline_comparison,
              'same_seed':0,'model':'Dirichlet then 60-token multinomial; grouped topic draw order',
              'sample_sizes':sizes,'larger_samples_nested':False,
              'sampling_curve':'pooled first-25-token probability, conditional on fixed theta'})
    log.save('verification_simulation.csv')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes = plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
    frame = pd.DataFrame(probabilities)
    for h,color in [(0,'#315A82'),(1,'#B56838')]:
        part = frame[frame.topic==h]
        axes[0].loglog(part.n,part.absolute_error,'o-',color=color,label=f'Topic {h}: observed error')
        axes[0].loglog(part.n,part.se,'--',color=color,label=f'Topic {h}: SE')
        axes[0].loglog(part.n,3*part.se,':',color=color,label=f'Topic {h}: 3SE')
    axes[0].set(xlabel='Documents n (60 tokens each)',ylabel='Absolute probability error',title='Known-probability sampling check')
    axes[0].legend(fontsize=7)
    stress_frame = pd.DataFrame(stress)
    for representation,color in [('TF-IDF','#315A82'),('SVD k=2','#B56838')]:
        part = stress_frame[stress_frame.representation==representation]
        axes[1].plot(part.overlap,part.gap,'o-',color=color,label=representation)
    axes[1].axhline(0,color='gray',linewidth=.7)
    axes[1].set(xlabel='Topic-overlap mixing rho',ylabel='Within minus across cosine (no self-pairs)',title='Stress: topics lose separation')
    axes[1].legend()
    fig.savefig(FIGURES/'simulation_checks.png',dpi=190)
    plt.close(fig)
    print(pd.DataFrame(probabilities).to_string(index=False),flush=True)
    print(pd.DataFrame(stress).to_string(index=False),flush=True)


if __name__ == '__main__':
    main()
