#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                            ____                    _   _           _
#?                           |  _ \ _   _  ___  _ __ | |_(_)_ __ ___ (_)_______
#?                           | |_) | | | |/ _ \| '_ \| __| | '_ ` _ \| |_  / _ \
#?                           |  __/| |_| | (_) | |_) | |_| | | | | | | |/ /  __/
#?                           |_|    \__, |\___/| .__/ \__|_|_| |_| |_|_/___\___|
#?                                  |___/      |_|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import numpy as np

from    pymoo.core.problem          import    ElementwiseProblem
from    pymoo.optimize              import    minimize as optmin
from    pymoo.termination           import    get_termination
from    pymoo.algorithms.soo.nonconvex.ga import GA
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

# Settings
POS_FLOOR = 1e-15
EPS_SAFE = 1e-24

# Combined loss weights
W_Z     = 1.0    # complex impedance mismatch
W_Y     = 1.0    # admittance mismatch
W_DB    = 0.3    # dB magnitude mismatch
W_PHASE = 0.01   # phase mismatch
W_REL   = 0.0    # relative magnitude mismatch

def Z_model(params, s):
    """
    This function computes the complex impedance of the parameterized
    circuit topology:

        Z(s) = Rs + s*Ls + ((R1 + s*L1) || (R2 + 1/(s*C)))

    where all parameters are strictly positive. The input frequency
    variable is provided in Laplace-domain form (s = j*2πf).

    Args:
        params (array-like): A length‑6 list or ndarray containing the physical
            circuit parameters in the order:
                [Rs, Ls, R1, L1, R2, C].
        s (ndarray): Complex frequency points at which the impedance is evaluated
            (e.g., s = j*2πf).

    Returns:
        ndarray: Complex impedance Z(s) evaluated at each frequency point.
    """
    Rs, Ls, R1, L1, R2, C = params
    ZA = R1 + s*L1
    ZB = R2 + 1/(s*C)
    Zpar = 1/(1/ZA + 1/ZB)
    return Rs + s*Ls + Zpar

def loss_combined(params, s, Zt, w_Z, w_Y, w_dB, w_phase, w_rel):
    """
    Compute a combined loss for impedance fitting.

    This function evaluates a weighted sum of multiple error components
    between the modeled impedance Z_model(params) and the target measured
    impedance Zt. The components include complex impedance error, admittance
    error, dB magnitude error, unwrapped phase error, and relative magnitude
    error. All components are optional and controlled via weighting factors.

    Args:
        params (array-like): Physical model parameters [Rs, Ls, R1, L1, R2, C].
        s (ndarray): Complex angular frequencies (s = j*2πf).
        Zt (ndarray): Target complex impedance values to fit.
        w_Z (float): Weight for complex impedance mismatch term.
        w_Y (float): Weight for admittance mismatch term (Y = 1/Z).
        w_dB (float): Weight for magnitude mismatch in dB.
        w_phase (float): Weight for unwrapped phase mismatch.
        w_rel (float): Weight for relative magnitude mismatch.

    Returns:
        float: Scalar loss value to be minimized by the optimizer.
    """

    if np.any(params <= 0):
        return 1e300

    Zm = Z_model(params, s)
    loss = 0.0

    # |Z - Zt|^2
    if w_Z > 0:
        loss += w_Z * np.sum(np.abs(Zm - Zt)**2)

    # |Y - Yt|^2
    if w_Y > 0:
        Ym = 1/(Zm + EPS_SAFE)
        Yt = 1/(Zt + EPS_SAFE)
        loss += w_Y * np.sum(np.abs(Ym - Yt)**2)

    # dB error
    if w_dB > 0:
        mag_dB_m = 20*np.log10(np.abs(Zm) + EPS_SAFE)
        mag_dB_t = 20*np.log10(np.abs(Zt) + EPS_SAFE)
        loss += w_dB * np.sum((mag_dB_m - mag_dB_t)**2)

    # phase error (radians)
    if w_phase > 0:
        ph_m = np.unwrap(np.angle(Zm))
        ph_t = np.unwrap(np.angle(Zt))
        loss += w_phase * np.sum((ph_m - ph_t)**2)

    # relative magnitude
    if w_rel > 0:
        mag_rel = (np.abs(Zm) - np.abs(Zt)) / (np.abs(Zt) + EPS_SAFE)
        loss += w_rel * np.sum(mag_rel**2)

    return loss

def select_and_decimate(freq, Z, fmin, fmax, n_points=2000):
    """
    Select a frequency range and decimate to a log-spaced grid.

    This function extracts the portion of the frequency response between
    fmin and fmax and resamples the impedance to a specified number of
    logarithmically spaced frequency points. The decimation preserves
    the overall shape while reducing data size for optimization.

    Args:
        freq (ndarray): Original frequency vector in Hz.
        Z (ndarray): Complex impedance array corresponding to `freq`.
        fmin (float): Minimum frequency of interest in Hz.
        fmax (float): Maximum frequency of interest in Hz.
        n_points (int, optional): Number of log-spaced output samples.
            Defaults to 2000.

    Returns:
        tuple:
            ndarray: Log-spaced frequency vector.
            ndarray: Complex impedance resampled at the new frequencies.
    """
    mask = (freq >= fmin) & (freq <= fmax)
    f = freq[mask]
    z = Z[mask]
    if len(f) == 0:
        raise ValueError("No points in selected frequency range.")
    if len(f) <= n_points:
        return f, z
    f_new = np.logspace(np.log10(f.min()), np.log10(f.max()), n_points)
    z_new = np.interp(f_new, f, z.real) + 1j*np.interp(f_new, f, z.imag)
    return f_new, z_new

def encode_bounds(space):
    """
    Encode parameter bounds for log-space optimization.

    This converts the physical lower/upper bounds into the search-space
    representation used by the GA. Parameters flagged with log_scale=True
    are encoded using log10, while others remain linear.

    Args:
        space (list of tuples): Each tuple has the form
            (lower_bound, upper_bound, log_scale),
            defining the parameter range and scaling mode.

    Returns:
        tuple:
            ndarray: Lower bounds of encoded parameters.
            ndarray: Upper bounds of encoded parameters.
    """

    xl, xu = [], []
    for lo, hi, log_scale in space:
        if log_scale:
            xl.append(np.log10(lo))
            xu.append(np.log10(hi))
        else:
            xl.append(lo)
            xu.append(hi)
    return np.array(xl), np.array(xu)

def decode_params(x, space):
    """
    Decode optimization parameters from search space to physical values.

    This converts a GA decision vector (possibly in log10-space) into actual
    physical parameter values. Strict positivity is enforced.

    Args:
        x (ndarray): Encoded GA decision vector.
        space (list of tuples): Parameter metadata of the form
            (lower_bound, upper_bound, log_scale).

    Returns:
        ndarray: Decoded physical parameters suitable for the circuit model.
    """

    vals = []
    for xi, (lo, hi, log_scale) in zip(x, space):
        if log_scale:
            vals.append(10**xi)
        else:
            vals.append(xi)
    p = np.array(vals)
    p[p <= 0] = POS_FLOOR
    return p

class ImpedanceProblem(ElementwiseProblem):
    """
    pymoo optimization problem wrapper for impedance model fitting.

    This class defines the optimization space, decodes GA parameters,
    and evaluates the combined loss function for a single candidate
    solution. It provides the interface required by pymoo's GA engine.

    Args:
        s (ndarray): Complex angular frequencies (s = j*2πf) used in evaluation.
        Zt (ndarray): Target impedance values to be matched.
        space (list of tuples): Parameter bounds and log-scaling information
            for each of the 6 physical parameters:
                (lower_bound, upper_bound, log_scale).
    """

    def __init__(self, s, Zt, space):
        xl, xu = encode_bounds(space)
        super().__init__(n_var=6, n_obj=1, xl=xl, xu=xu)
        self.s = s
        self.Zt = Zt
        self.space = space

    def _evaluate(self, x, out):
        params = decode_params(x, self.space)
        out["F"] = loss_combined(params, self.s, self.Zt, W_Z, W_Y, W_DB, W_PHASE, W_REL)

def nelder_mead(func, x0, args=(), max_iter=3000, alpha=1.0, gamma=2.0, rho=0.5, sigma=0.5):
    """
    Perform Nelder Mead simplex optimization.

    This implements a local derivative-free optimization method used to refine
    the solution found by the genetic algorithm. The simplex adapts the search
    region using reflection, expansion, contraction, and shrink operations.

    Args:
        func (callable): Objective function returning a scalar loss.
        x0 (ndarray): Initial parameter vector (positive physical values).
        args (tuple, optional): Extra arguments passed to `func`.
        max_iter (int, optional): Maximum number of iterations. Defaults to 3000.
        alpha (float, optional): Reflection coefficient. Defaults to 1.0.
        gamma (float, optional): Expansion coefficient. Defaults to 2.0.
        rho (float, optional): Contraction coefficient. Defaults to 0.5.
        sigma (float, optional): Shrinkage coefficient. Defaults to 0.5.

    Returns:
        tuple:
            ndarray: Optimized parameter vector.
            float: Final loss value.
    """

    n = len(x0)
    simplex = np.zeros((n+1, n))
    x0 = np.maximum(x0, POS_FLOOR)
    simplex[0] = x0

    for i in range(n):
        y = simplex[0].copy()
        y[i] = max(y[i]*1.2, POS_FLOOR)
        simplex[i+1] = y

    fvals = np.array([func(simplex[i], *args) for i in range(n+1)])

    for _ in range(max_iter):
        idx = np.argsort(fvals)
        simplex = simplex[idx]
        fvals = fvals[idx]

        best = simplex[0]
        worst = simplex[-1]
        centroid = np.mean(simplex[:-1], axis=0)

        xr = np.maximum(centroid + alpha*(centroid - worst), POS_FLOOR)
        fr = func(xr, *args)

        if fvals[0] <= fr < fvals[-2]:
            simplex[-1] = xr; fvals[-1] = fr; continue

        if fr < fvals[0]:
            xe = np.maximum(centroid + gamma*(xr - centroid), POS_FLOOR)
            fe = func(xe, *args)
            if fe < fr:
                simplex[-1] = xe; fvals[-1] = fe
            else:
                simplex[-1] = xr; fvals[-1] = fr
            continue

        xc = np.maximum(centroid + rho*(worst - centroid), POS_FLOOR)
        fc = func(xc, *args)
        if fc < fvals[-1]:
            simplex[-1] = xc; fvals[-1] = fc; continue

        for i in range(1, n+1):
            simplex[i] = np.maximum(best + sigma*(simplex[i] - best), POS_FLOOR)
            fvals[i] = func(simplex[i], *args)

    return simplex[0], fvals[0]

# def plot_impedance(freq, Z_raw, params, title):
#     """
#     Plot magnitude and phase of the fitted impedance against the raw data.

#     This function computes the modeled impedance for the final optimized
#     parameters and overlays it with the measured impedance.

#     Args:
#         freq (ndarray): Frequency vector in Hz.
#         Z_raw (ndarray): Measured complex impedance values.
#         params (array-like): Final optimized circuit parameters.
#         title (str): Label indicating which optimization method produced the fit.

#     Returns:
#         None: Displays two Matplotlib subplots (magnitude and phase).
#     """

#     s = 1j*2*np.pi*freq
#     Z_fit = Z_model(params, s)

#     mag_raw = 20*np.log10(np.abs(Z_raw))
#     mag_fit = 20*np.log10(np.abs(Z_fit))
#     ph_raw  = np.angle(Z_raw, deg=True)
#     ph_fit  = np.angle(Z_fit, deg=True)

#     fig,(ax1,ax2)=plt.subplots(2,1,figsize=(10,8),sharex=True)

#     ax1.plot(freq, mag_raw, lw=2, label="Raw")
#     ax1.plot(freq, mag_fit, '--', lw=2, label=title)
#     ax1.set_xscale("log"); ax1.minorticks_on()
#     ax1.grid(True, which="both", ls=":")
#     ax1.set_ylabel("Magnitude (dB)")
#     ax1.legend()

#     ax2.plot(freq, ph_raw, lw=2)
#     ax2.plot(freq, ph_fit, '--', lw=2)
#     ax2.set_xscale("log"); ax2.minorticks_on()
#     ax2.grid(True, which="both", ls=":")
#     ax2.set_ylabel("Phase (°)")
#     ax2.set_xlabel("Frequency (Hz)")

#     plt.tight_layout(); plt.show()