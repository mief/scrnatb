import numpy as np
from scipy import optimize
from GPclust import OMGP
from tqdm import tqdm

def predict_grid(bgplvm, resolution=50, which_indices=(0,1)):
    X = bgplvm.X.mean[:, which_indices]
    xi, yi = np.meshgrid(1.1 * np.linspace(X[:, 0].min(), X[:, 0].max(), resolution),
                         1.1 * np.linspace(X[:, 1].min(), X[:, 1].max(), resolution))

    pred_X = np.zeros((bgplvm.X.shape[1], resolution ** 2))
    pred_X[which_indices[0]] = xi.reshape(resolution ** 2)
    pred_X[which_indices[1]] = yi.reshape(resolution ** 2)

    pred_Y, pred_Y_var = bgplvm.predict(pred_X.T)
    
    extent = [xi.min(), xi.max(), yi.min(), yi.max()]
    
    return pred_Y, pred_Y_var, extent


def breakpoint_linear(x, ts, k1, k2, c1):
    return np.piecewise(x, [x < ts], [lambda x: k1 * x + c1,
                                      lambda x: k2 * x + (k1 - k2) * ts + c1])


def identify_bifurcation_point(omgp, n_splits=30):
    mix_m = OMGP(omgp.X, omgp.Y, K=omgp.K, kernels=omgp.kern)
    mix_m.variance = omgp.variance
    
    phi = omgp.phi

    log_liks = []

    t_splits = np.linspace(mix_m.X.min(), mix_m.X.max(), n_splits)
    for t_s in tqdm(t_splits):
        mask = mix_m.X > t_s
        phi_mix = np.ones_like(phi) * 0.5
        phi_mix[mask[:, 0]] = phi[mask[:, 0]]

        mix_m.phi = phi_mix
        log_liks.append(mix_m.log_likelihood())

    x = t_splits
    y = np.array(log_liks)
    p, e = optimize.curve_fit(breakpoint_linear, x, y)
    
    return p[0]
