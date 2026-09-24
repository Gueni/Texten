
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                                   ____   ____ ____  ___ ____ _____ ____   ___  ______   __
#?                                                                  / ___| / ___|  _ \|_ _|  _ \_   _| __ ) / _ \|  _ \ \ / /
#?                                                                  \___ \| |   | |_) || || |_) || | |  _ \| | | | | | \ V /
#?                                                                   ___) | |___|  _ < | ||  __/ | | | |_) | |_| | |_| || |
#?                                                                  |____/ \____|_| \_\___|_|    |_| |____/ \___/|____/ |_|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import  assets.Dependencies         as        dp
import  Lib.Data_Process            as        PP
import  Lib.Param_Process           as        PM
import  Lib.TrackableDict           as        TD
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
paramProcess            =	PM.ParamProcess()
dataProcess             =   PP.Processing()
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def simScript(OptStruct,Thread,Map,iterNumber,ResultsPath,misc,crash=False):
    """
    * This function is used to write scripts for automated simulations.
    * Multiple simulations with parameters or conditions variations can be programmed here.

    !--> Please make a copy of this file and rename it to 'ScriptBody.py' and place it in the same directory as this file.
    !--> Please don't delete or make changes to this file.

    Args:
        OptStruct       (list)      : Nested list that contains simulation parameters.
        Thread          (int)       : Current working thread number.
        Map             (list)      : Nested list containing all simulation sweep parameters.
        iterNumber      (int)       : Current working iteration number.
        ResultsPath     (string)    : Current results folder location.
        misc            (class)     : Miscellaneous class object for simulation data handling.
        crash           (bool)      : Boolean to determine if a simulation crash happened in the previous iteration.
    """

    mdlVars                                            =   OptStruct[Thread]['ModelVars']                               #? PLECS's ModelVars dictionary of model parameters.
    mapVars                                            =   Map[iterNumber]                                              #? Current simulation values matrix.
    X1,X2,X3,X4,X5,X6,X7,X8,X9,X10                     =   range(10)                                                    #? Index range of user parameters lists.
    mdlVars['Common']['ToFile']['FileName']            =   ResultsPath + str(iterNumber+1)                              #? Current simulation results filename.
    mdlVars['Common']['ToFile']['FileNameStandalone']  =   mdlVars['Common']['ToFile']['FileName'] + '_Standalone'      #? Current standalone simulation results filename.
    mdlVars                                            =   TD.TrackableDict(mdlVars)                                    #? Trackable version of PLECS's ModelVars dictionary of model parameters.

    with mdlVars.track_scope():
        pass

    #! -------------------------------------------------------------------------------------Don't change above this line---------------------------------------------------------------------------
        mdlVars['Common']['Control']['Targets']['Vout']           = mapVars[X3]
        mdlVars['Common']['Control']['Targets']['Pout']           = mapVars[X4]
        mdlVars['DCDC_Rail1']['Control']['Inputs']['Vin']         = mapVars[X2]
        mdlVars['Common']['Thermal']['Twater']                    = mapVars[X1]
        mdlVars['Common']['Load']['Front']['R_L']                 = mdlVars['Common']['Control']['Targets']['Vout']**2/mdlVars['Common']['Control']['Targets']['Pout']

    #! -------------------------------------------------------------------------------------Don't change under this line---------------------------------------------------------------------------

    dp.updated_params_dict                                                          =   mdlVars.assignments
    mdlVars                                                                         =   dict(mdlVars)
    OptStruct[Thread]['ModelVars']                                                  =   mdlVars

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------