
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                        ____ ___  _   _ _____ _______  _______
#?                                                       / ___/ _ \| \ | |_   _| ____\ \/ /_   _|
#?                                                      | |  | | | |  \| | | | |  _|  \  /  | |
#?                                                      | |__| |_| | |\  | | | | |___ /  \  | |
#?                                                       \____\___/|_| \_| |_| |_____/_/\_\ |_|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from dataclasses import dataclass, field
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

@dataclass(init=True)
class ResultRepository():
    """
    Wraps the single dict every process reads its inputs from and writes its own result into,
    keyed by process/result name.

    *Args:
        data (dict) :   The result dictionary itself, shared across every process in a run. Defaults to {}.
    """
    data            : dict = field(default_factory=dict)

@dataclass(init=True)
class ProcessContext:
    """
    Unified context passed into every IProcess.execute() call: the raw data to read from, and
    where to write the result.

    *Args:
        raw_data           (list)             :   Raw time series data for this thread/iteration. Defaults to [].
        thread_index       (int)              :   Which thread/iteration this context is for -- processes write their
                                                   result at this index. Defaults to 0.
        result_repository  (ResultRepository) :   Shared result dict every process reads its inputs from and writes into. Defaults to a fresh ResultRepository().
        res_list           (list)             :   Resistance values for ProcessDissipation's resistive-dissipation term.
                                                   Workaround: belongs conceptually in ProcessDissipationsConfig, but lives
                                                   here until var_update() can return the full resistance list at once. Defaults to [].
        p_aux              (float)            :   Auxiliary power draw for ProcessThermalStats. Same kind of workaround as res_list. Defaults to 0.
    """
    raw_data            : list              = field(default_factory=list)
    thread_index        : int               = 0
    result_repository   : ResultRepository  = field(default_factory=ResultRepository)
    res_list            : list              = field(default_factory=list) # todo: workarround. Need update of var_update to return full res list at once. Should stay in config instead Context
    p_aux               : float             = 0 # todo: Same workaround

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
