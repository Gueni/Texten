
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
    Holds the result dictionary dataclass

    *Attributes:
        data (dict) :   The result dictionary. Defaults to default dict
    """
    data            : dict = field(default_factory=dict)

@dataclass(init=True)
class ProcessContext:
    """
    unified context for each prossess

    *Attributes:
        raw_dat           (dict )  :   Raw time series. Defaults to default list
        thread_index      (int  )  :   Thread index. Defaults to 0
        result_repository (dict )  :   Result dictionary. Defaults to ResultRepository
        res_list          (list )  :   workarround. Defaults to default list
        p_aux             (float)  :   workarround. Defaults to 0
    """
    raw_data            : list              = field(default_factory=list)
    thread_index        : int               = 0
    result_repository   : ResultRepository  = field(default_factory=ResultRepository)
    res_list            : list              = field(default_factory=list) # todo: workarround. Need update of var_update to return full res list at once. Should stay in config instead Context
    p_aux               : float             = 0 # todo: Same workaround

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
