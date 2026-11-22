"""Fixed THUCNews sample: character/word comparison, energy rank and query audit."""
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfTransformer
from methods import (my_count_matrix, my_tfidf, my_svd_power, my_document_coordinates,
                     my_cosine_matrix, my_query_vector, my_project_query,
                     my_query_cosines, my_top_matches, my_energy_rank)
from preprocess_text import load_fixed_sample, tokenize_documents
from verification_helpers import (ROOT, RESULTS, FIGURES, PROCESSED, prepare_directories,
                                  VerificationLog, check_svd, topic_summary,
                                  unsupported_input_checks, save_json)


def main():
    prepare_directories()
    frame = load_fixed_sample()
    tokenizations = tokenize_documents(frame)
    log = VerificationLog()
    summary, similarities, queries, assumptions, spectra, near_duplicates, query_terms = [],[],[],[],[],[],[]
    query_id = frame.document_id.iloc[0]
    save_json(RESULTS/'query_definition.json',{'document_id':query_id,'title':frame.title.iloc[0],
              'selection':'first document of unchanged Iteration 2 sample manifest, before viewing scores',
              'query_text':'full title and body of that document; not included in tracked results',
              'exclude_self':True,'tie_break':'ascending document ID','evaluation':'in-corpus descriptive'})
    for name,tokens in tokenizations.items():
        start = time.perf_counter()
        counts,vocabulary = my_count_matrix(tokens)
        a,idf,df = my_tfidf(counts)
        if name=='character' and (ROOT/'data/processed/tfidf.npy').exists():
            log.report('Character baseline','unchanged TF-IDF',a,np.load(ROOT/'data/processed/tfidf.npy'),
                       'Iteration 2 saved matrix',atol=0.)
        # sklearn uses log(n/df)+1 even when smooth_idf=False; remove its +1 explicitly.
        transformer = TfidfTransformer(norm=None,use_idf=True,smooth_idf=False,sublinear_tf=False)
        transformer.fit(counts.T)
        log.report(name,'IDF convention',idf,transformer.idf_-1,'sklearn IDF minus its additive 1')
        log.report(name,'TF-IDF convention',a,(counts.T*(transformer.idf_-1)).T,'raw TF times adjusted sklearn IDF')
        sig,u,v,diagnostics = my_svd_power(a,k=None,energy=.9)
        k,cumulative = my_energy_rank(sig,float(np.sum(a*a)),.9)
        assert k==len(sig)
        ref_s,details = check_svd(a,sig,u,v,diagnostics,name,log)
        reference_k = int(np.searchsorted(np.cumsum(ref_s**2)/np.sum(ref_s**2),.9)+1)
        log.report(name,'energy-selected rank',k,reference_k,'full NumPy spectrum, 90% target',atol=0.)
        d = my_document_coordinates(v,sig)
        original_cos,reduced_cos = my_cosine_matrix(a.T),my_cosine_matrix(d)
        for representation,cosines in [('TF-IDF',original_cos),('SVD 90%',reduced_cos)]:
            similarities.append({'tokens':name,'representation':representation,
                                 **topic_summary(cosines,frame.category.to_numpy())})
        q = my_query_vector(tokens[0],vocabulary,idf)
        log.report(name,'frozen known query',q,a[:,0],'column of fixed corpus',atol=0.)
        z = my_project_query(q,u,sig)
        for representation,scores in [('TF-IDF',my_query_cosines(q,a.T)),('SVD 90%',my_query_cosines(z,d))]:
            chosen = my_top_matches(scores,frame.document_id,exclude=[query_id])
            for position,j in enumerate(chosen,1):
                row = frame.iloc[j]
                contribution = q * (a[:,j] if representation=='TF-IDF' else u @ d[j])
                term_order = np.argsort(-contribution,kind='stable')
                terms = [int(t) for t in term_order if contribution[t]>0][:5]
                queries.append({'tokens':name,'representation':representation,'position':position,
                                'document_id':row.document_id,'category':row.category,
                                'title':row.title,'cosine':float(scores[j]),
                                'largest_positive_query_terms':' '.join(str(vocabulary[t]) for t in terms)})
                for t in terms:
                    query_terms.append({'tokens':name,'representation':representation,
                                        'document_id':row.document_id,'term':vocabulary[t],
                                        'dot_product_contribution':float(contribution[t])})
        assumption = unsupported_input_checks(a,vocabulary,idf,tokens[0],name)
        assumption.update({'zero_projected_rows':int(np.sum(np.sum(d*d,axis=1)==0)),
                           'exact_duplicate_documents':int(pd.Series([''.join(t) for t in tokens]).duplicated().sum()),
                           'idf_min':float(idf.min()),'idf_max':float(idf.max()),**details})
        # A deliberately looser solver run measures tolerance sensitivity on the same data/rank.
        sensitive_s,sensitive_u,sensitive_v,sensitive_d = my_svd_power(a,k=k,tol=1e-13)
        sensitivity = float(np.max(abs(my_cosine_matrix(sensitive_v*sensitive_s)-reduced_cos)))
        assumption['cosine_change_tolerance_1e_13'] = sensitivity
        log.report(name,'cosine tolerance sensitivity',sensitivity,0.,'tol 1e-13 versus 1e-14',atol=1e-8)
        assumptions.append(assumption)
        upper = np.triu_indices(len(frame),k=1)
        closest = np.argsort(-original_cos[upper],kind='stable')[:10]
        for index in closest:
            i,j = int(upper[0][index]),int(upper[1][index])
            left,right = set(frame.title.iloc[i]),set(frame.title.iloc[j])
            near_duplicates.append({'tokens':name,'left_id':frame.document_id.iloc[i],
                                    'right_id':frame.document_id.iloc[j],
                                    'left_title':frame.title.iloc[i],'right_title':frame.title.iloc[j],
                                    'cosine':float(original_cos[i,j]),
                                    'title_character_jaccard':len(left&right)/len(left|right),
                                    'same_label':bool(frame.category.iloc[i]==frame.category.iloc[j])})
        summary.append({'tokens':name,'documents':a.shape[1],'terms':a.shape[0],
                        'nonzeros':int(np.count_nonzero(a)),'density':float(np.count_nonzero(a)/a.size),
                        'zero_idf_terms':int(np.sum(idf==0)),'k_90':k,
                        'previous_energy':float(np.sum(sig[:-1]**2)/np.sum(a*a)),
                        'retained_energy':diagnostics['retained_energy'],
                        'total_energy':float(np.sum(a*a)),**details,
                        'elapsed_seconds':time.perf_counter()-start})
        for i,s in enumerate(ref_s,1):
            spectra.append({'tokens':name,'index':i,'reference_sigma':float(s),
                            'custom_sigma':float(sig[i-1]) if i<=k else None,
                            'reference_energy':float(np.sum(ref_s[:i]**2)/np.sum(ref_s**2))})
        pd.DataFrame({'term':vocabulary,'df':df,'idf':idf}).to_csv(PROCESSED/f'{name}_vocabulary.csv',index=False)
        np.savez(PROCESSED/f'{name}_model.npz',counts=counts,tfidf=a,idf=idf,sig=sig,u=u,v=v)
        save_json(RESULTS/f'{name}_method_diagnostics.json',diagnostics)
        print(f'{name}: {a.shape}, k={k}, elapsed={time.perf_counter()-start:.2f}s',flush=True)
    pd.DataFrame(summary).to_csv(RESULTS/'real_summary.csv',index=False)
    pd.DataFrame(similarities).to_csv(RESULTS/'real_similarity.csv',index=False)
    pd.DataFrame(queries).to_csv(RESULTS/'query_top5.csv',index=False)
    pd.DataFrame(query_terms).to_csv(RESULTS/'query_term_contributions.csv',index=False)
    pd.DataFrame(assumptions).to_csv(RESULTS/'real_assumptions.csv',index=False)
    pd.DataFrame(spectra).to_csv(RESULTS/'real_spectrum.csv',index=False)
    pd.DataFrame(near_duplicates).to_csv(RESULTS/'near_duplicate_candidates.csv',index=False)
    log.save('verification_real.csv')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes = plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
    for name,color in [('character','#315A82'),('word','#B56838')]:
        part = pd.DataFrame(spectra).query('tokens == @name')
        axes[0].plot(part['index'],part.reference_energy,color=color,label=name)
        match = next(row for row in summary if row['tokens']==name)
        axes[0].scatter([match['k_90']],[match['retained_energy']],color=color,s=25)
    axes[0].axhline(.9,color='gray',linestyle='--',linewidth=.8)
    axes[0].set(xlabel='Retained rank k',ylabel='Cumulative squared-singular-value energy',title='Energy-based rank selection')
    axes[0].legend()
    sim = pd.DataFrame(similarities)
    x = np.arange(len(sim))
    axes[1].bar(x-.16,sim.within,width=.32,label='Within topic',color='#315A82')
    axes[1].bar(x+.16,sim.across,width=.32,label='Across topics',color='#B56838')
    axes[1].set(xticks=x,xticklabels=['Char\nTF-IDF','Char\nSVD','Word\nTF-IDF','Word\nSVD'],
                ylabel='Mean cosine (self-pairs excluded)',title='Real data: topical similarity')
    axes[1].legend()
    fig.savefig(FIGURES/'real_comparison.png',dpi=190)
    plt.close(fig)
    print(pd.DataFrame(summary).to_string(index=False),flush=True)
    print(pd.DataFrame(similarities).to_string(index=False),flush=True)


if __name__ == '__main__':
    main()
