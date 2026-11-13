# Check-in study guide

Use this to review the completed report, then explain the arguments in your own words.

1. **What does A_td mean?** It is the number of occurrences of a retained Chinese character in one title-plus-body document, multiplied by log(number of documents / documents containing the character). A has term rows and document columns.
2. **Why cosine?** It compares direction. Cauchy-Schwarz bounds the absolute dot product by the product of lengths; dividing by the positive lengths gives [-1,1]. Zero vectors have no cosine.
3. **Where does SVD come from?** The Gram matrix is symmetric positive semidefinite, so it has an orthonormal eigenbasis with nonnegative eigenvalues. Positive eigenvalues give singular values by square roots and the other vectors by multiplying by A and dividing by the singular value.
4. **Why is truncation best?** Projecting onto any k-dimensional column space can capture at most the energy of the top k singular directions. The truncated SVD attains that bound. Orthogonality makes squared residual error the sum of discarded singular values squared.
5. **Why V_k Sigma_k for documents?** Multiplying A on the left by U_k^T selects the retained coordinates: U_k^T A = Sigma_k V_k^T. Transpose to get one row per document.
6. **Why Sigma_k^-1 U_k^T q for a query?** It solves the coefficient least-squares problem in the basis U_k Sigma_k. It matches V_k rows. For the geometry in question 4, use U_k^T q instead and compare against V_k Sigma_k rows. Scaling each axis by a different singular value changes angles.
7. **Can SVD make similarity worse?** Yes. The hand example has originally orthogonal documents whose rank-one reconstructions are identical. The best reconstruction theorem is not a best semantic-retrieval theorem.
8. **What is known in the simulation?** Labels and topic term probabilities. The sampled matrix is noisy and rank 40. There is no claim that its true rank is two.
9. **What improved numerically?** Same-topic mean cosine rose from 0.729660 to 0.999877. Across-topic mean also rose slightly. Nearest-neighbor topic accuracy was already 100% in both representations, so no accuracy improvement was observed.
10. **What are the main limitations?** Bag-of-characters loses order/word meaning, finite-prefix sampling can be biased, topic labels are coarse, and forming a Gram matrix loses accuracy for tiny singular values. Real-data retrieval remains for Iteration 3.

Before submitting, be able to reproduce the two-term/three-document hand example without reading the report. Review `results/` and the numerical code so each reported quantity has a clear origin.
