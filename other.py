#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#? ____ ____ _ _
#? | _ \ _ _ _ __ / ___| ___ _ __(_)_ __ | |_ ___
#? | |_) | | | | '_ \\___ \ / __| '__| | '_ \| __/ __|
#? | _ <| |_| | | | |___) | (__| | | | |_) | |_\__ \
#? |_| \_\\__,_|_| |_|____/ \___|_| |_| .__/ \__|___/
#? |_|
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import copy
import numpy as np
import os
import assets.Mapping.plecs_mapping as pmap
import pyfiglet
import  assets.Dependencies         as        dp
import  Lib.error_handler           as      er
import  Lib.pyplecs_rpc             as      pc
import  Lib.Data_Process            as      PP
import  Lib.Param_Process           as      PM
import  Lib.Pylog                   as      flg
import  Lib.Pyutils                 as      sutl
import  Lib.Pymisc                  as      msc
import  Lib.py_plot                 as      plt
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

class _AutoVivDict(dict):
    """ A dict that creates missing keys as another _AutoVivDict on first access, instead of raising KeyError -- so a nested assignment like d['Common']['simParams']['tSim'] = 0.00085 works starting from a completely empty {}, with none of d's parent keys needing to exist first. ?NOTE: Used only to rebuild ModelVars/SolverOpts containing strictly what Input_vars.json's own ModelVars list sets (see runScripts.simInit()) -- dp.mdlVars/dp.slvOpts themselves start from Param_Dicts.ModelVars/SolverOpts, large pre-populated baselines, so the list's entries (written as dp.mdlVars['Common']['simParams']['tSim'] = ...) can't be re-run against an empty plain dict without this. """
    def __missing__(self, key):
        value       = self[key] = _AutoVivDict()
        return value


def build_modelvars_from_list(modelvars_list):
    """ Runs the given list of "dp.mdlVars[...] = ..." / "dp.slvOpts[...] = ..." exec() strings -- exactly the shape of Input_vars.json's own "ModelVars" entries -- against fresh, empty structures, entirely separate from dp.mdlVars/dp.slvOpts's own Param_Dicts.ModelVars/SolverOpts baseline (both of which start as large, pre-populated dicts, not empty). Returns what the list itself sets, as plain nested dicts -- nothing from that baseline. ?NOTE: Uses _AutoVivDict so a nested assignment like dp.mdlVars['Common']['simParams']['tSim'] = ... works starting from {}, then converts the result to plain dicts before returning -- callers get ordinary dicts, not _AutoVivDict instances. If any item in modelvars_list *reads* a nested path that no earlier item in the same list already wrote (relying on it coming from the real baseline instead), that read resolves to an empty {} here rather than the real baseline value, since nothing is pre-populated. modelvars_list needs to be self-sufficient -- every value an item reads should already have been set by an earlier item in the same list -- for this to produce correct results. *Args: modelvars_list (list[str]) : The exec() strings, e.g. Input_vars.json's "ModelVars" entry. !Returns: tuple[dict, dict] : (mdlVars, slvOpts), built strictly from modelvars_list. """
    def _to_plain(d):
        return {k: (_to_plain(v) if isinstance(v, dict) else v) for k, v in d.items()}

    real_mdlVars, real_slvOpts  =   dp.mdlVars, dp.slvOpts
    dp.mdlVars, dp.slvOpts      =   _AutoVivDict(), _AutoVivDict()

    for item in modelvars_list  :   exec(item)

    mdlVars, slvOpts            =   _to_plain(dp.mdlVars), _to_plain(dp.slvOpts)
    dp.mdlVars, dp.slvOpts      =   real_mdlVars, real_slvOpts

    return mdlVars, slvOpts

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

@er.safe_class()
class runScripts:
    def __init__(self,jsonInputs):
        """ This function initializes the runScripts class with the provided JSON inputs. It sets up various class attributes and initializes necessary classes for simulation, logging, and post-processing. *Args: jsonInputs (dict): Dictionary containing JSON inputs for the simulation. """

        self.JS                 =   jsonInputs                                                      # declare json input file
        self.misc               =   msc.Misc()                                                      # initialize miscellaneous class
        self.fileLog            =   flg.FileAndLogging(json_dir=self.JS['scriptName'])              # initialize FileAndLogging class
        self.simutil            =   sutl.SimulationUtils()                                          # initialize SimulationUtils class
        self.plot               =   plt.HTML_REPORT(self.fileLog.resultfolder,self.fileLog.utc)     # initialize pyplot class
        self.paramProcess       =   PM.ParamProcess()                                               # initialize ParamProcess class
        self.postProcessing     =   PP.Processing()                                                 # initialize Processing class

        # RT Box capability now lives directly on self.obj (PlecsRPC), built in simInit() once the
        # PLECS connection exists -- no separate object to construct here. self.rt_enabled_flag is
        # kept as a bare copy, set here (before self.obj exists) rather than only on self.obj, so
        # simEnd() can check it safely even if simInit() fails before self.obj gets created at all.
        self.rt_enabled_flag    =   dp.JSON.get("RT", False)

@er.hint(" hint inside siminit")
    def simInit(self):
        """ This function initializes the simulation environment from PLECS model to parameters to creation of target results folder. """

        # Initialize the simulation environment by creating necessary folders.
        # Selecting the mapping for post-processing, initializing simulation variables.
        self.fileLog.createFolders()
        pmap.select_mapping()

        # ModelVars/SolverOpts containing strictly what Input_vars.json's own ModelVars list sets --
        # nothing from dp.mdlVars/dp.slvOpts's own Param_Dicts.ModelVars/SolverOpts baseline (both
        # start as large pre-populated dicts, not empty). Used by simEnd()'s InitializationCommands()
        # call for the standalone case (model == "").
        self.standalone_mdlVars, self.standalone_slvOpts  =   build_modelvars_from_list(self.JS['ModelVars'])

        # Initialize the PLECS model and set up the model variables, solver options, and analysis options.
        for item in self.JS['ModelVars']    :   exec(item)

        # initialize the simulation variables and class objects
        self.simutil.init_sim(self.JS['maxThreads'],*[eval(self.JS[f"X{i}"]) for i in range(1, 11)],pattern=self.JS['permute'])
        dp.mode_sim = self.simutil.mode

        # Add a Note to the HTML report and define the log file header.
        self.fileLog.header()

        # Initialize Analysis options with the provided JSON input.
        dp.anlOpts                  =   self.JS['AnalysisOpts']
        dp.mdlVars['AnalysisOpts']  =   self.JS['AnalysisOpts']

        # Apply tolerances to the model variables if not running in parallel.
        if not dp.JSON['parallel']:
            dp.mdlVars              =   self.simutil.applyTolerances(self.JS['Comps'],eval(self.JS['Tols']),dp.mdlVars,self.JS['applyTol'],False)

        # DCDC Average Model Calculation
        if dp.JSON['model'] == 'DCDC_S' or 'DCDC_D':
            dp.mdlVars['DCDC_Average']  =   self.paramProcess.dcdcAverageModelCalculate(dp.mdlVars)

        # Connect to the PLECS model through the RPC server.
        # Initialize the PLECS model with the specified model name.
        # RT Box capability rides along on this same connection, reusing dp.url/dp.port/METHOD/
        # self.server directly -- no separate rtbox_url/rtbox_port/rtbox_server, and no
        # rtbox_model_name either (PlecsRPC derives it from dp.cp_mdl once Open_Model() sets that).
        # codegen_only=True builds the .elf but never connects to, uploads to, or starts anything on
        # actual RT Box hardware -- for generating without hardware attached.
        self.obj                    =   pc.PlecsRPC(
                                                        dp.url, dp.port, dp.mdlVars, dp.slvOpts, dp.anlOpts   ,
                                                        rtbox_enabled       =   self.rt_enabled_flag          ,
                                                        rtbox_codegen_only  =   dp.JSON.get("codegen_only", False)  ,
                                                    )
        # PlecsConnect() connects once, to PLECS -- and that same connection is reused directly for
        # RT Box calls too (rtbox.*/plecs.* are just different method-name namespaces on the one
        # endpoint, since PLECS and the RT Box are assumed to share the same address/port). This
        # assumption should be confirmed against real hardware -- see PlecsConnect()'s own docstring.
        self.obj.PlecsConnect()
        self.obj.Open_Model(self.JS['modelname'])

        # Clear the traces of the desired scopes in the PLECS model.
        self.obj.ClearTrace(self.JS['modelname'],dp.scopes)

@er.hint(" hint inside simLog")
    def simLog(self,OptStruct):
        """ This function logs the simulation parameters and updates the iteration number. *Args: OptStruct (dict): Dictionary containing the simulation parameters. """

        # Increment the iteration number and log the current iteration number.
        # It also logs the updated parameters and the name of the simulation.
        self.simutil.iterNumber    +=  1
        itr                         =   self.simutil.iterNumber
        self.fileLog.log('{} = {}'.format("Iteration Number".ljust(self.fileLog.PADDING_WIDTH  , ' '),f"{str(itr)}/{str(self.simutil.Iterations)}"))

        # Log the changes made to the model parameters.
        # It iterates through the dictionary and logs the key and new value of each updated parameter.
        dp.updated_params_dict = {key[2:-2]: value for key, value in dp.updated_params_dict.items()}
        self.fileLog.param_log(dp.updated_params_dict,isFirst=False)

        # Log the current iteration name
        self.fileLog.log('{} = {}'.format("['Name']".ljust(self.fileLog.PADDING_WIDTH  , ' '),str(OptStruct['Name']) +'\n'))

        # Log the parameters of the current simulation iteration for HTML tables.
        self.plot.tab_val_list.append(copy.deepcopy(OptStruct['ModelVars']))

        self.plot.iter_param_key.append(self.JS['paramKeys'])
        self.plot.iter_param_val.append(eval(self.JS['paramVals']))
        self.plot.iter_param_unt.append(self.JS['paramUnts'])

@er.hint(" hint inside simRun")
    def simRun(self,threads=1,parallel=False,callback=""):
        """ This function runs a simulation or an analysis and records the elapsed time. When RT Box is enabled (Input_vars.json's "RT"), self.obj.LaunchSim() itself runs the RT Box workflow on the real hardware instead of an offline PLECS simulation -- decided entirely inside PlecsRPC, so there's no RT-Box-specific branch to make here; this calls LaunchSim()/LaunchAnalysis() exactly as it always did. *Args: threads (int, optional) : number of parallel threads to simulate. Defaults to 1. parallel (bool, optional): determine whether a single or parallel simulation. Defaults to False. callback (str, optional) : define a callback fundtion to be executed after simulation is completed. Defaults to "". """

        # Selects between simulation and analysis based on the JSON input.
        self.misc.tic()

        if (not self.JS['analysis']):
            self.obj.LaunchSim(threads,self.obj.path,parallel,callback)
        else:
            self.obj.LaunchAnalysis(threads,self.obj.path,self.JS['analysisName'],parallel,callback)

        # Logs the time taken for the simulation or analysis to complete.
        self.fileLog.log('{} = {}'.format("Simulation Time".ljust(self.fileLog.PADDING_WIDTH  , ' '),f"{str(self.misc.toc())} seconds.\n"))

        self.misc.tic()

@er.hint(" hint inside simSave")
    def simSave(self,Simulation=0,Crash=False):
        """ This function saves the simulation results to disk and store them in data matrices. In addition, it performs post-processing on raw results. Skipped entirely when RT Box is enabled: there's no PLECS simulation output to hold traces of or save (the run went to real-time hardware instead) -- only the log file still gets written. *Args: Simulation (int, optional) : simulation package number. Defaults to 0. Crash (bool, optional) : determine if a crash happened in a previous iteration. Defaults to False. """

        if self.obj.rtbox_enabled : return

        # Hold the traces of the desired scopes
        if not dp.scopes == [None] : self.obj.holdTrace(self.JS['modelname'],dp.scopes)

        # Save the simulation results to CSV files and store them in data matrices too then log the time taken for this operation.
        if (self.JS['saveData']):
            self.misc.tic()
            self.simutil.save_data(self.obj.OptStruct,self.simutil,self.fileLog,itr=Simulation,crash=Crash)
            self.fileLog.log('{} = {}'.format("Saving Data".ljust(self.fileLog.PADDING_WIDTH  , ' '),f"{str(self.misc.toc())} seconds.\n"))

@er.hint(" hint inside Simend")
    def simEnd(self):
        """ This function plots the processed results graphically in HTML files. It also creates copies of simulation files and scripts in the results folder. It resets the simulation iteration counter and generates an HTML report from the results and visualizations. Finally, it finalizes logging and saves traces of the desired scopes externally. If RT Box was enabled for this run, every file in the model's own folder (the .elf, and whatever else PLECS Coder / the A2L-INCA merge produced alongside it -- .c/.h if codegen_only, .a2l files, etc.) is copied into the results folder too, as a whole "RT_BOX_CODEGEN" subfolder -- handled by copyfiles() (called via footer() below), the same shutil.copytree() mechanism already used for the other directories it copies. """

        # Reset simulation iteration counter
        self.simutil.iterNumber = 0

        if not self.rt_enabled_flag and hasattr(self, 'obj'):
            # Generate octave-based parameters and script for standalone simulations and write the model variables as initialization commands in PLECS.
            # Standalone (model == ""): use the snapshot taken right after Input_vars.json's own
            # ModelVars list ran, so the generated file reflects only what was explicitly put
            # there -- not AnalysisOpts injection, applyTolerances(), or dcdcAverageModelCalculate().
            # Any other model (DCDC_S/DCDC_D, ...): keep using OptStruct as before, since those
            # additions are legitimately part of that model's parameters.
            if dp.JSON.get("model", "") == "":
                init_mdlVars = self.standalone_mdlVars
                init_slvOpts = self.standalone_slvOpts
            else:
                init_mdlVars = self.obj.OptStruct[0]['ModelVars'] if (self.simutil.Threads >= 1 and dp.JSON['parallel']) else self.obj.OptStruct['ModelVars']
                init_slvOpts = self.obj.OptStruct[0]['SolverOpts'] if (self.simutil.Threads >= 1 and dp.JSON['parallel']) else self.obj.OptStruct['SolverOpts']

            self.fileLog.InitializationCommands(
                                                    self.obj.path                                                                                                                       ,
                                                    self.fileLog.resultfolder+"/"+"PLECS_MODEL_"+"standalone_"+self.JS['modelname']                                                     ,
                                                    init_mdlVars                                                                                                                         ,
                                                    (os.getcwd()).replace("\\","/")+"/Script/assets/Configuration/InitializationCommands.m"                                          ,
                                                    self.simutil.Map                                                                                                                    ,
                                                    init_slvOpts
                                                )

        # Generate HTML report from results and visualizations if data saving is enabled
        # (skipped for RT Box runs -- nothing was saved above for it to plot)
        if (self.JS['saveData']) and not self.rt_enabled_flag and hasattr(self, 'obj'):
            self.plot.auto_plot(self.simutil,self.fileLog, self.misc,open=self.JS['openHTML'],iterReport=self.JS['iterReport'])

        # Finalize logging and save traces
        self.fileLog.footer(self.simutil)  # Create footer for log file

        # Save the traces of the desired scopes externally
        if not dp.scopes == [None] and not self.rt_enabled_flag and hasattr(self, 'obj') : self.obj.SaveTraces(self.JS['modelname'],dp.scopes,self.fileLog.resultfolder)

@er.hint(" hint inside simMissing")
    def simMissing(self, iter, threads_vector, Threads):
        """ This function determines which simulation thread has crashed during parallel runs to repeate it later. *Args: iter (int) : current iteration where a crash occured threads_vector (list) : the used simulation threads for each simulation package Threads (int) : number of threads used in parallel simulation !Returns: MissingIter (list) : list of identified simulation iterations that crashed """

        # Find missing iteration data file and clean up optstruct
        MissingIter         = self.postProcessing.findMissingResults(self.fileLog.resultfolder+"/CSV_TIME_SERIES",iter,threads_vector,Threads)

        # Reinitialize empty optstruct
        self.obj.OptStruct  = []

        # Convert missing iters array back to list
        MissingIter         = (np.array(MissingIter)-1).tolist()
        return MissingIter

@er.hint(" hint inside log_header")
    def log_header(self,OptStruct,simulation=0):
        """ Log the header part of the log file *Args: OptStruct (dict) : the current modelvars dictionary of parameters simulation (int, optional) : simulation number. Defaults to 0. """

        # If simulation number is 0 Log the default parameters and create a header for iterations.
        if not simulation:
            self.fileLog.param_log(OptStruct, self.simutil.Threads,iters=self.simutil.Iterations,sims=self.simutil.Simulations)
            self.fileLog.line_separator()
            self.fileLog.log(pyfiglet.figlet_format("ITERATIONS PARAMETERS", width=200))

        # Log current simulation number.
        self.fileLog.line_separator()
        self.fileLog.log('{} = {}'.format("Simulation Number".ljust(self.fileLog.PADDING_WIDTH  , ' '),f"{simulation+1}/{self.simutil.Simulations}"))

        self.fileLog.line_separator()

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------