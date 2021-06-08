import numpy as np


def fit_distributions(X, y, normalize=False):
    """Fit distribution p(x|E), p(x|~E) as a mixture of Gaussian and Uniform, see Fonteijn 
    section `Mixture models for the data likelihood`. 
    - P(x|E) = P(x > X | E)
    - P(x|~E) = P(x < X| ~E)
    """
    # TODO: not sure about how to compute probabilities
    from scipy.stats import norm, uniform
    if normalize:
        X = X / X.max(axis=1)[:, np.newaxis]
    
    avg = X[y==0, ...].mean(axis=0)
    std = X[y==0, ...].std(axis=0)
    p_not_e = [norm(loc, s) for loc, s in zip(avg, std)]

    left_min = X.min(axis=0)
    right_max = avg.copy()
    p_e = [uniform(m1, m2-m1) for m1, m2 in zip(left_min, right_max)]
    return p_e, p_not_e, left_min, right_max


def log_distributions(X, y, *, X_test=None, y_test=None, normalize=False, eps=1e-6):
    """Precomute probabilities for all features."""
    X = np.array(X).astype(np.float64)
    y = np.array(y)
    cdf_p_e, cdf_p_not_e, left_min, right_max = fit_distributions(X, y, normalize=normalize)
    
    if X_test is not None:
        X = np.array(X_test).astype(np.float64)
        y = np.array(y_test)
        
    n, m = X.shape
    log_p_e, log_p_not_e = np.zeros_like(X), np.zeros_like(X)

    for i in range(n):
        for j in range(m):
            log_p_e[i,j] = np.log(1 - cdf_p_e[j].cdf(np.clip(X[i, j], left_min[j]+eps, right_max[j]-eps))+eps)
            log_p_not_e[i,j] = np.log(cdf_p_not_e[j].cdf(X[i, j])+eps)
    return log_p_e, log_p_not_e


def predict_stage(event_order, log_p_e, log_p_not_e):
    likelihood = []
    for k in range(n_stages):
        likelihood.append(log_p_e[:, event_order[k]]- log_p_not_e[:, event_order[k]]) 
    return np.array(likelihood)
