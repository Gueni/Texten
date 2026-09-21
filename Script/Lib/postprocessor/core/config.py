
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                            ____ ___  _   _ _____ ___ ____
#?                                                           / ___/ _ \| \ | |  ___|_ _/ ___|
#?                                                          | |  | | | |  \| | |_   | | |  _
#?                                                          | |__| |_| | |\  |  _|  | | |_| |
#?                                                           \____\___/|_| \_|_|   |___\____|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from dataclasses import dataclass, field
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

@dataclass(init=True)
class ProcessorConfig:

    """
    Top-level config for one processor run: which processes to build, how to slice the raw
    data for each, and which simulation type this run is for.

    *Args:
        sim_type     (str ) :  Which config this run loaded ("DCDC_S"/"DCDC_D" or "Standalone", from the
                              matching process_config_*.json's "Config_Name"). Defaults to "Standalone".
        slice_map    (dict) :  Named data slices (from the process_config_*.json's "Slicing" section),
                              looked up by each process to know which rows of raw_data are its own. Defaults to {}.
        process_dict (dict) :  Which processes to build, keyed by process name (from process_config_*.json's
                              "Processes" section). Defaults to {}.
        process_cfg  (dict) :  Per-process-type config dataclasses (e.g. ProcessFFTConfig), keyed by
                              processor type name. Defaults to {}.
    """
    sim_type        : str   = "Standalone"
    slice_map       : dict  = field(default_factory=dict)
    process_dict    : dict  = field(default_factory=dict)
    process_cfg     : dict  = field(default_factory=dict)

@dataclass(init=True)
class ProcessBaseConfig:
    """
    Base config shared by every process: which result key to write under, and which rows of the
    raw data it operates on. Concrete process configs (ProcessFFTConfig, etc.) extend this.

    *Args:
        process_name (str)      :   Key this process's result is stored under in the result repository. Defaults to "none".
        data_slice   (slice)    :   Which rows of raw_data this process reads. Defaults to slice(None) (all rows).
    """
    process_name    : str   = "none"
    data_slice      : slice = field(default_factory=lambda: slice(None))

@dataclass(init=True)
class ProcessFFTConfig(ProcessBaseConfig):
    """
    Config for the FFT process.

    *Args:
        fund_freq   (int)   : Fundamental frequency in Hz, used to locate harmonics in the spectrum. Defaults to 0.
        hrmcs       (int)   : Highest harmonic order to keep (0 = DC only). Defaults to 0.
        to_file_ts  (int)   : Sample step the data was saved at; 0 means the data isn't uniformly sampled
                              and must be resampled before FFT. Defaults to 0.
    """
    fund_freq       : int = 0
    hrmcs           : int = 0
    to_file_ts      : int = 0

@dataclass(init=True)
class ProcessDissipationsConfig(ProcessBaseConfig):
    """
    Config for the total-dissipation process.

    *Args:
        res_list    (list)  : Resistance values for computing resistive dissipation. Currently unused by
                              ProcessDissipation.execute() -- it reads context.res_list instead (see the
                              "workarround" note on ProcessContext.res_list). Defaults to [].
        current_idx (int)   : How many of the RMS current results to include in the resistive dissipation. Defaults to 0.
    """
    res_list        : list  = field(default_factory=list)
    current_idx     : int   = 0

@dataclass(init=True)
class ProcessThermalStatsConfig(ProcessBaseConfig):
    """
    Config for the thermal-stats process (efficiency, total dissipation, input power).

    *Args:
        dcdc_d      (bool)  :   Whether this is a dual-rail DCDC_D model (vs. single-rail DCDC_S). Defaults to False.
        rail_idx    (int)   :   Index of the rail being processed. Defaults to 0.
        common_idx  (int)   :   Index into the common (shared) results. Defaults to 0.
        pout_idx    (int)   :   Index of the output power result to use. Defaults to 0.
        p_aux       (float) :   Auxiliary power draw, added to the rail's own dissipation. Defaults to 0.
        phase       (int)   :   Phase index, for multi-phase converters. Defaults to 0.
    """
    dcdc_d          : bool  = False
    rail_idx        : int   = 0
    common_idx      : int   = 0
    pout_idx        : int   = 0
    p_aux           : float = 0
    phase           : int   = 0

@dataclass(init=True)
class ProcessSensitivityConfig(ProcessBaseConfig):
    """
    Config for the sensitivity process (percent change in a parent process's result, relative
    to its baseline, per perturbed parameter).

    *Args:
        perturbation (float)            : Perturbation size applied to each parameter, as a percent. Defaults to 0.
        post_fix     (str  )            : Suffix stripped from this process's own name to find its parent process's result. Defaults to "".
        fft_cfg      (ProcessFFTConfig) : The parent process's own FFT config, if the parent is FFT-shaped
                                          (used to know how many harmonics each thread's slice spans). Defaults to a fresh ProcessFFTConfig().
    """
    perturbation    : float             = 0
    post_fix        : str               = ""
    fft_cfg         : ProcessFFTConfig  = field(default_factory=ProcessFFTConfig)

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------