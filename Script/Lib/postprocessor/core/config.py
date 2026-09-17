
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
    Processor config dataclass

    *Attributes:
        sim_type     (str ) :  Defaults to "Standalone"
        slice_map    (dict) :  Slice map used to get map slices to signals. Defaults to default dict
        process_dict (dict) :  Dictionary of processes to be created. Defaults to default dict
        process_cfg  (dict) :  Process config dictionary. Defaults to default dict
    """
    sim_type        : str   = "Standalone"
    slice_map       : dict  = field(default_factory=dict)
    process_dict    : dict  = field(default_factory=dict)
    process_cfg     : dict  = field(default_factory=dict)

@dataclass(init=True)
class ProcessBaseConfig:
    """
    Basis config for each prossess

    *Attributes:
        process_name (str)      :   Defaults to none
        data_slice   (slice)    :   Slice to mask data field in raw data. Defaults to slice(None)
    """
    process_name    : str   = "none"
    data_slice      : slice = field(default_factory=lambda: slice(None))

@dataclass(init=True)
class ProcessFFTConfig(ProcessBaseConfig):
    """
    FFT process config dataclass

    *Attributes:
        fund_freq   (int)   : Fundamental frequency. Defaults to 0
        hrmcs       (int)   : Desired number of harmonics. Defaults to 0
        to_file_ts  (int)   : Saving time from input vars. resample if != 0. Defaults to 0
    """
    fund_freq       : int = 0
    hrmcs           : int = 0
    to_file_ts      : int = 0

@dataclass(init=True)
class ProcessDissipationsConfig(ProcessBaseConfig):
    """
    Dissipation process config dataclass

    *Attributes:
        res_list    (list)  : Fundamental frequency. Defaults to default list
        current_idx (int)   : Index to slice current result map till index. Defaults to 0
    """
    res_list        : list  = field(default_factory=list)
    current_idx     : int   = 0

@dataclass(init=True)
class ProcessThermalStatsConfig(ProcessBaseConfig):
    """
    Dissipation process config dataclass

    *Attributes:
        dcdc_d      (bool)      Defaults to False   # todo: add description
        rail_idx    (int)       Defaults to 0       # todo: add description
        common_idx  (int)       Defaults to 0       # todo: add description
        pout_idx    (int)       Defaults to 0       # todo: add description
        p_aux       (float)     Defaults to 0       # todo: add description
        phase       (int)       Defaults to 0       # todo: add description
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
    Sensitivty process config dataclass

    *Attributes:
        perturbation (float) : Perturbation value: Defaults to 0
        post_fix     (str  ) : Perturbation value. Defaults to ""
        fft_cfg      (Obj  ) : ProcessFFTConfig  FFT config. Defaults to default ProcessFFTConfig
    """
    perturbation    : float             = 0
    post_fix        : str               = ""
    fft_cfg         : ProcessFFTConfig  = field(default_factory=ProcessFFTConfig)

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------