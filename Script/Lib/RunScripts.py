
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                           ____              ____            _       _
#?                                          |  _ \ _   _ _ __ / ___|  ___ _ __(_)_ __ | |_ ___
#?                                          | |_) | | | | '_ \\___ \ / __| '__| | '_ \| __/ __|
#?                                          |  _ <| |_| | | | |___) | (__| |  | | |_) | |_\__ \
#?                                          |_| \_\\__,_|_| |_|____/ \___|_|  |_| .__/ \__|___/
#?                                                                              |_|
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import  assets.Dependencies         as      dp
import  Lib.error_handler           as      er
import  Lib.pyplecs_rpc             as      pc
import  Lib.Data_Process            as      PP
import  Lib.Param_Process           as      PM
import  Lib.Pylog                   as      flg
import  Lib.Pyutils                 as      sutl
import  Lib.Pymisc                  as      msc
import  Lib.py_plot                 as      plt
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

@er.safe_class()
class runScripts:
    def __init__(self,jsonInputs):
        """
        This function initializes the runScripts class with the provided JSON inputs.
        It sets up various class attributes and initializes necessary classes for simulation, logging, and post-processing.

        *Args:
            jsonInputs (dict): Dictionary containing JSON inputs for the simulation.
        """

        self.JS                 =   jsonInputs                                                      #  declare json input file
        self.misc               =   msc.Misc()                                                      #  initialize miscellaneous class
        self.fileLog            =   flg.FileAndLogging(json_dir=self.JS['scriptName'])              #  initialize FileAndLogging class
        self.simutil            =   sutl.SimulationUtils()                                          #  initialize SimulationUtils class
        self.plot               =   plt.HTML_REPORT(self.fileLog.resultfolder,self.fileLog.utc)     #  initialize pyplot class
        self.paramProcess       =   PM.ParamProcess()                                               #  initialize ParamProcess class
        self.postProcessing     =   PP.Processing()                                                 #  initialize Processing class

    @er.hint(" hint inside siminit")
    def simInit(self):
        """
        This function initializes the simulation environment
        from PLECS model to parameters to creation of target results folder.
        """

        # Initialize the simulation environment by creating necessary folders.
        # Selecting the mapping for post-processing, initializing simulation variables.
        self.fileLog.createFolders()
        dp.pmap.select_mapping()

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
        self.obj                    =   pc.PlecsRPC(dp.url,dp.port,dp.mdlVars,dp.slvOpts,dp.anlOpts)
        self.obj.PlecsConnect()
        self.obj.Open_Model(self.JS['modelname'])

        # Clear the traces of the desired scopes in the PLECS model.
        self.obj.ClearTrace(self.JS['modelname'],dp.scopes)

    @er.hint(" hint inside simLog")
    def simLog(self,OptStruct):
        """
        This function logs the simulation parameters and updates the iteration number.

        *Args:
            OptStruct (dict): Dictionary containing the simulation parameters.
        """

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
        self.plot.tab_val_list.append(dp.copy.deepcopy(OptStruct['ModelVars']))

        self.plot.iter_param_key.append(self.JS['paramKeys'])
        self.plot.iter_param_val.append(eval(self.JS['paramVals']))
        self.plot.iter_param_unt.append(self.JS['paramUnts'])

    @er.hint(" hint inside simRun")
    def simRun(self,threads=1,parallel=False,callback=""):
        """
        This function runs a simulation or an analysis and records the elapsed time.

        *Args:
            threads   (int, optional) : number of parallel threads to simulate. Defaults to 1.
            parallel  (bool, optional): determine whether a single or parallel simulation. Defaults to False.
            callback  (str, optional) : define a callback fundtion to be executed after simulation is completed. Defaults to "".
        """

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
        """
        This function saves the simulation results to disk and store them in data matrices.
        In addition, it performs post-processing on raw results.

        *Args:
            Simulation  (int, optional)     : simulation package number. Defaults to 0.
            Crash       (bool, optional)    : determine if a crash happened in a previous iteration. Defaults to False.
        """

        # Hold the traces of the desired scopes
        if not dp.scopes == [None] : self.obj.holdTrace(self.JS['modelname'],dp.scopes)

        # Save the simulation results to CSV files and store them in data matrices too then log the time taken for this operation.
        if (self.JS['saveData']):
            self.misc.tic()
            self.simutil.save_data(self.obj.OptStruct,self.simutil,self.fileLog,itr=Simulation,crash=Crash)
            self.fileLog.log('{} = {}'.format("Saving Data".ljust(self.fileLog.PADDING_WIDTH  , ' '),f"{str(self.misc.toc())} seconds.\n"))

    @er.hint(" hint inside Simend")
    def simEnd(self):
        """
        This function plots the processed results graphically in HTML files.
        It also creates copies of simulation files and scripts in the results folder.
        It resets the simulation iteration counter and generates an HTML report from the results and visualizations.
        Finally, it finalizes logging and saves traces of the desired scopes externally.
        """

        # Reset simulation iteration counter
        self.simutil.iterNumber = 0

        # Generate octave-based parameters and script for standalone simulations and write the model variables as initialization commands in PLECS.
        self.fileLog.InitializationCommands(
                                                self.obj.path                                                                                                                       ,
                                                self.fileLog.resultfolder+"/"+"PLECS_MODEL_"+"standalone_"+self.JS['modelname']                                                     ,
                                                self.obj.OptStruct[0]['ModelVars'] if (self.simutil.Threads >= 1 and dp.JSON['parallel']) else self.obj.OptStruct['ModelVars']      ,
                                                (dp.os.getcwd()).replace("\\","/")+"/Script/assets/Configuration/InitializationCommands.m"                                          ,
                                                self.simutil.Map                                                                                                                    ,
                                                self.obj.OptStruct[0]['SolverOpts'] if (self.simutil.Threads >= 1 and dp.JSON['parallel']) else self.obj.OptStruct['SolverOpts']
                                            )

        # Generate HTML report from results and visualizations if data saving is enabled
        if (self.JS['saveData']):
            self.plot.auto_plot(self.simutil,self.fileLog, self.misc,open=self.JS['openHTML'],iterReport=self.JS['iterReport'])

        # Finalize logging and save traces
        self.fileLog.footer(self.simutil)  # Create footer for log file

        # Save the traces of the desired scopes externally
        if not dp.scopes == [None] : self.obj.SaveTraces(self.JS['modelname'],dp.scopes,self.fileLog.resultfolder)

    @er.hint(" hint inside simMissing")
    def simMissing(self, iter, threads_vector, Threads):
        """
        This function determines which simulation thread has crashed during
        parallel runs to repeate it later.

        *Args:
            iter            (int)   : current iteration where a crash occured
            threads_vector  (list)  : the used simulation threads for each simulation package
            Threads         (int)   : number of threads used in parallel simulation

        !Returns:
            MissingIter     (list)  : list of identified simulation iterations that crashed
        """

        # Find missing iteration data file and clean up optstruct
        MissingIter         = self.postProcessing.findMissingResults(self.fileLog.resultfolder+"/CSV_TIME_SERIES",iter,threads_vector,Threads)

        # Reinitialize empty optstruct
        self.obj.OptStruct  = []

        # Convert missing iters array back to list
        MissingIter         = (dp.np.array(MissingIter)-1).tolist()
        return MissingIter

    @er.hint(" hint inside log_header")
    def log_header(self,OptStruct,simulation=0):
        """
        Log the header part of the log file

        *Args:
            OptStruct    (dict)             : the current modelvars dictionary of parameters
            simulation   (int, optional)    : simulation number. Defaults to 0.
        """

        # If simulation number is 0 Log the default parameters and create a header for iterations.
        if not simulation:
            self.fileLog.param_log(OptStruct, self.simutil.Threads,iters=self.simutil.Iterations,sims=self.simutil.Simulations)
            self.fileLog.line_separator()
            self.fileLog.log(dp.pyfiglet.figlet_format("ITERATIONS PARAMETERS", width=200))

        # Log current simulation number.
        self.fileLog.line_separator()
        self.fileLog.log('{} = {}'.format("Simulation Number".ljust(self.fileLog.PADDING_WIDTH  , ' '),f"{simulation+1}/{self.simutil.Simulations}"))

        self.fileLog.line_separator()

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------