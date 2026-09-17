
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                       ____  _                 _       _   _             _   _ _   _ _
#?                                      / ___|(_)_ __ ___  _   _| | __ _| |_(_) ___  _ __ | | | | |_(_) |___
#?                                      \___ \| | '_ ` _ \| | | | |/ _` | __| |/ _ \| '_ \| | | | __| | / __|
#?                                       ___) | | | | | | | |_| | | (_| | |_| | (_) | | | | |_| | |_| | \__ \
#?                                      |____/|_|_| |_| |_|\__,_|_|\__,_|\__|_|\___/|_| |_|\___/ \__|_|_|___/
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import  assets.Dependencies         as        dp
import  Lib.Data_Process            as        PP

import numpy as np
import pandas as pd
import json

from Lib.io import Reader, Writer
from Lib.MapCalculation.MapCalculation import MapContext
from Lib.postprocessor.core.interfaces import IProcessor
from Lib.postprocessor.core.context import ProcessContext
from Lib.postprocessor.engine.processor_builder import ProcessorBuilder

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class SimulationUtils:
    def __init__(self):
        """Initialize the SimulationUtils class with various attributes
        """
        self.sweepMatrix                                                = []                            # Define SweepMatrix
        self.postProcessing                                             = PP.Processing()               # Call the Post-Processing class and point to log data
        self.Map, self.Iterations                                       = '', 1                         # Define mapping parameters Maps and Iterations
        self.iterNumber, self.Threads, self.Simulations                 = 0, 1, 1                       # Define Iteration Number, Threads and Simulations
        self.threads_vector                                             = []                            # Define vector of threads for hierarchical simulations
        self.iter_continuous                                            = 0                             # Define continuous iteration counter
        self.iter_10s                                                   = 0                             # Define 10s iteration counter
        self.MAT_dict                                                   = {}                            # Define list of data matrices
        self.mode                                                       = ""                            # Define simulation mode
        self.inputContext                                               = Reader.InputContext()
        self.reader                                                     = Reader.CSVReader()
        self.readerHeader                                               = Reader.CSVReaderHeader()
        self.output_ctx                                                 = Writer.OutputContext()
        self.output_ctx.mode                                            = "w"
        self.writer                                                     = Writer.CSVWriter()
        self.process_ctx                                                = ProcessContext()
        self.process_ctx.result_repository.data                         = self.MAT_dict
        self.processor                                                  : IProcessor

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? Simulation Maps
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def simThreads(self,desired_threads=1):
        """
        Calculates the number of threads that should be used for a simulation.

        This function determines the optimal number of threads to use for a simulation
        by comparing the desired number of threads with the available CPU cores.
        It ensures efficient resource utilization by preventing overallocation of
        CPU resources while allowing for parallel processing when beneficial.

        *Args:
            desired_threads (int)   : The number of threads requested for the simulation.Defaults to 1.

        !Returns:
                            (int)   : The number of threads that will be used for the simulation.
        """

        # Compare the desired number of threads with the available CPU cores
        return min(dp.multiprocessing.cpu_count(), desired_threads)

    def paralellThreads(self,Threads,Iterations):
        """
        Determines the optimal number of parallel threads for a given number of iterations.

        *Args:
                Threads     (int)   : The maximum number of threads that can be used simultaneously.
                Iterations  (int)   : The total number of iterations that need to be completed.

        !Returns:
                            (int)   : The optimal number of parallel threads to use.

        ?Example:
                If Threads=4 and Iterations=16, the function will return 4 because it is the maximum number
                of threads that can be used to complete all iterations simultaneously.
        """

        # Validate input parameters threads should be positive integers and iterations should be positive integers
        if not isinstance(Threads, int) or not isinstance(Iterations, int) or Threads <= 0 or Iterations <= 0:
            raise ValueError("Threads and Iterations must be positive integers.")

        # Find the largest number of threads that evenly divides the total iterations
        for i in range(Threads, 0, -1):
            remainder = Iterations % i
            if remainder == 0:
                return i

        return 1

    def detect_mode(self, config):
        """
        Detects the mode of operation for the current simulation.

        *Args:
            Xs      (list)      : lists of input variables X1-10

        !Returns:
                    (string)    : the operation mode (Normal or WCA)
        """
        if config["parallel"]       != 1    :   return "SINGLE"
        if config["perturbation"]   != 0    :   return "SENSITIVITY"
        if config["points"]                 :   return "MONTECARLO"

        for var in config["sweepMatrix"]:
            if var == [[0]] or var == [0]: continue #* Ignore not used X lists

            for sub in var:
                if isinstance(sub, list) and len(sub) in (2, 4)         :   return "WCA"        #* WCA if [nom, tol] or [nom, tol, min, max]
                if not isinstance(sub, list) and config["permute"]      :   return "PERMUTE"    #* Normal [[1,2,3,4..],.] no sublists
                if not isinstance(sub, list)                            :   return "NORMAL"     #* Normal [[1,2,3,4..],.] no sublists
                # elif isinstance(sub, list) and len(sub) == 1          :   return "NORMAL"     #* Normal [[1],[2]...] with sublists

        return "NONE"

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? Tolerances & Perturbations
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    @dp.deprecated(reason="Candidate for remove")
    def sweepTolerances(self,misc,Comps,Tols,OptStruct,Thread,Config=0,rand=False):
        """Applies tolerance adjustments to specified components in an optimization structure.

        *Args:
            misc        (object)            : Utility object containing helper methods like `transform_key_paths` and `update_dict_value`.
            Comps       (list)              : List of dot-separated key paths representing components to be adjusted.
            Tols        (list)              : List of tolerance values. If `rand` is True, this should be a list of (min, max) tuples for random sampling.
            OptStruct   (list)              : Optimization structure containing model variables.
            Thread      (int)               : Index of the thread accessing the `OptStruct` element to modify.
            Config      (int, optional)     : If non-zero, tolerances will be applied. Defaults to 0.
            rand        (bool, optional)    : If True, applies random tolerance values from the range specified in `Tols`. Defaults to False.
        """

        #* Transform component key paths to match the structure of `OptStruct`
        #* and apply tolerances if `Config` is set to a non-zero value.
        #* If `rand` is True, random values within specified ranges are applied.
        #* Otherwise, fixed tolerance values are used.

        #* Converts a list of dot-separated key paths into bracketed string key paths.
        Comps = ["['" + "']['".join(k.split('.')) + "']" for k in Comps]
        if (Config):
            for i in range(len(Comps)):
                if (rand):
                    randMin                     =   Tols[i][0]
                    randMax                     =   Tols[i][1]
                    randError	                =	dp.random.SystemRandom().uniform(randMin,randMax)
                    misc.update_dict_value(OptStruct[Thread]['ModelVars'], Comps[i], randError)
                else:
                    misc.update_dict_value(OptStruct[Thread]['ModelVars'], Comps[i], Tols[i])

    def applyTolerances(self,Comps,Tols,mdlVars,Config=0,rand=False):
        """
        This function allows you to apply tolerances to selected components in the model variables.
        The specified components will have their values modified based on the provided tolerances.

        *Args:
            comps       (list)  :   A list of component names to which tolerances will be applied.
            Tols        (list)  :   A list of tolerance values to apply to the corresponding components.
            mdlVars     (dict)  :   A dictionary containing the model variables.
            Config      (int)   :   Integer, Optional A flag indicating whether to apply tolerances (1) or not (0). Defaults to 0.

        !Returns:
                        (dict)  :   A dictionary containing the model variables with applied tolerances, or the original model variables if Config is set to 0.
        """

        #* Apply tolerances to specified components in the model variables if Config is set to a non-zero value.
        #* If rand is True, random tolerance values within specified ranges are applied.
        #* Otherwise, fixed tolerance values are used.
        if (Config):
            ModelVars_Flat      =   dp.flatdict.FlatDict(mdlVars, delimiter='.')

            for i in range(len(Comps)):
                if (rand):
                    randMin                     =  -Tols[i]
                    randMax                     =   Tols[i]
                    randError	                =	dp.random.SystemRandom().uniform(randMin,randMax)
                    ModelVars_Flat[Comps[i]]    =   ModelVars_Flat[Comps[i]] + ModelVars_Flat[Comps[i]]*randError
                else:
                    ModelVars_Flat[Comps[i]]    =   ModelVars_Flat[Comps[i]] + ModelVars_Flat[Comps[i]]*Tols[i]

            ModelVars_Unflat    =   dp.unflatten.unflatten(ModelVars_Flat)
            return ModelVars_Unflat

        else:
            return mdlVars

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? Initialization
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    # todo: remove pattern
    def init_sim(self, maxThreads=1, X1=[[0]], X2=[[0]], X3=[[0]], X4=[[0]], X5=[[0]], X6=[[0]], X7=[[0]], X8=[[0]], X9=[[0]], X10=[[0]],pattern=True):
        """
        Initialize simulation with parameter sweeps.

        *Args:
            maxThreads  (int , optional)    : maximum number of threads. Defaults to 1.

            X1          (list, optional)    : parameters sweep list number 1 . Defaults to [[0]].
            X2          (list, optional)    : parameters sweep list number 2 . Defaults to [[0]].
            X3          (list, optional)    : parameters sweep list number 3 . Defaults to [[0]].
            X4          (list, optional)    : parameters sweep list number 4 . Defaults to [[0]].
            X5          (list, optional)    : parameters sweep list number 5 . Defaults to [[0]].
            X6          (list, optional)    : parameters sweep list number 6 . Defaults to [[0]].
            X7          (list, optional)    : parameters sweep list number 7 . Defaults to [[0]].
            X8          (list, optional)    : parameters sweep list number 8 . Defaults to [[0]].
            X9          (list, optional)    : parameters sweep list number 9 . Defaults to [[0]].
            X10         (list, optional)    : parameters sweep list number 10. Defaults to [[0]].

            pattern     (bool, optional)    : Sweep Map permutation pattern. Defaults to True.
        """

        MapConfig = {
            "permute"           :   dp.JSON['permute']                          ,
            "parallel"          :   dp.JSON['parallel']                         ,
            "perturbation"      :   dp.JSON["perturbation"]                     ,
            "nvars"             :   dp.JSON["nvars"]                            ,
            "points"            :   dp.JSON["points"]                           ,
            "Tols"              :   dp.JSON["Tols"]                             ,
            "seed"              :   dp.seed                                     ,
            "sweepMatrix"       :   [X1, X2, X3, X4, X5, X6, X7, X8, X9, X10]
            }

        self.mode = self.detect_mode(MapConfig)

        if (self.mode == "NONE"):
            print("Mode Error") # Todo: add propper error handling
            return
        elif (self.mode == "SINGLE"):
            return

        map_context = MapContext(self.mode)
        self.sweepMatrix, self.Map, self.Iterations = map_context.generate_map(MapConfig)

        #?--------------------------------------------------------
        #* Initialize iteration counter
        self.iterNumber = 0

        #* If hierarchical simulations are enabled in JSON input file
        if dp.JSON['hierarchical']:
            # use hierarchicalSims function to determine count of paralleled simulations
            self.threads_vector         =   self.postProcessing.hierarchicalSims(self.Map)
            self.Simulations            =   len(self.threads_vector)
        else:
            #* Determine count of paralleled simualtions
            maxThreads               =   self.simThreads(maxThreads)
            self.Threads             =   self.paralellThreads(maxThreads,self.Iterations)
            self.Simulations         =   self.Iterations//self.Threads

        return self  #* Return self for method chaining

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? Saving
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def var_update(self,Threads,crash,optstruct,l):
        """
        Retrieves resistance values and auxiliary power from an optimization structure based on threading and crash conditions.

        *Args:
            Threads     (int)           : Number of threads used for parallel processing.
            crash       (bool)          : Indicator if a crash condition has occurred.
            optstruct   (list or dict)  : The optimization structure containing model variables.
            l           (int)           : Index used to access a specific element in `optstruct` if threading is enabled.

        !Returns:
                        (tuple)         : A tuple containing :
                                                                - res_list  (list)  : List of resistance values.
                                                                - P_aux     (float) : Auxiliary power value from the thermal model variables.
        """

        #* Retrieve resistance values and auxiliary power based on threading and crash conditions.
        #* If multiple threads are used and parallel processing is enabled without a crash,
        #* access the specific element in optstruct using index l.
        if (Threads >= 1 and dp.JSON['parallel'] and not crash):
                res_list                        = dp.pmap.return_resistances(optstruct[l])
                P_aux                           = optstruct[l]['ModelVars']['Common']['Thermal']['Paux']

        #* If a crash has occurred, access the first element of optstruct.
        elif (crash):
                res_list                        = dp.pmap.return_resistances(optstruct[0])
                P_aux                           = optstruct[0]['ModelVars']['Common']['Thermal']['Paux']

        #* If single-threaded or not parallel, access the first element of optstruct.
        else:
                res_list                        = dp.pmap.return_resistances(optstruct)
                P_aux                           = optstruct['ModelVars']['Common']['Thermal']['Paux']

        #* Return the list of resistances and auxiliary power.
        return res_list,P_aux

    # todo: remove saveMode
    def save_data(self,optstruct,simutil,fileLog,itr=0,saveMode='w',crash=False):
        """
        Save the simulation results as csv files and store them in data matrices.

        *Args:
            optstruct   (np.ndarray)        : The simulation results to be saved
            simutil     (obj)               : object instance of pyutils class.
            fileLog     (obj)               : object instance of pylog class.
            itr         (int, optional)     : The iteration index. Default is 0.
            saveMode    (str, optional)     : The mode of saving the data to disk. Can be 'a' for appending or 'w' for overwriting. Defaults to 'w'.
            crash       (bool, optional)    : Sim Crash flag. Defaults to False.
        """
        #* iteration_range is determined based on whether hierarchical parallelization is enabled
        iteration_range     = list(range(sum(self.threads_vector[0:itr]),sum(self.threads_vector[0:itr+1]))) if dp.JSON['hierarchical'] else list(range(itr*simutil.Threads,simutil.Threads*(itr+1)))

        if dp.JSON["model"]:
            pre_fix     = ""
            post_fix    = ""
        else:
            pre_fix     = "Standalone_"
            post_fix    = "_Standalone"

        #* Loop through each thread in the current simulation batch. For each thread, generate the result file and process the CSV data
        #* Normalize the results and convert them to a numpy array
        #* Remove NaN values from each sub-array in the nested results and perform specified operations on the time vector and normalized results
        #* threads_idx is calculated based on whether hierarchical parallelization is enabled
        for l in range(simutil.Threads):

            self.inputContext.rawDataPath = fileLog.resultfolder+f"/CSV_TIME_SERIES/results_{fileLog.utc}_{str(iteration_range[l]+1)}{post_fix}"
            self.reader.read(self.inputContext)

            if iteration_range[l] ==0:
                self.readerHeader.read(self.inputContext)
                dp.std_headers                  = self.inputContext.header
                dp.std_length                   = self.inputContext.headerLen
                processor_builder               = ProcessorBuilder()

                self.processor, self.processes  = processor_builder.build_processor(
                                                                                    MAT_dict    = self.MAT_dict     ,
                                                                                    dp          = dp                ,
                                                                                    iterations  = self.Iterations   ,
                                                                                    mode        = self.mode
                                                                                    )

            if dp.JSON["model"]:
                res_list,   P_aux               = self.var_update(simutil.Threads,crash,optstruct,l)
                self.process_ctx.p_aux          = P_aux
                self.process_ctx.res_list       = res_list
            else:
                dp.standalone_exist             = True
                dp.os.makedirs(fileLog.resultfolder + "/HEADERS", exist_ok = True)
                dp.json.dump(dp.std_headers, open(f"{fileLog.resultfolder}/HEADERS/headers.json","w" ,encoding = "utf-8"))

            nestedresults                       = dp.np.array(self.postProcessing.norm_results_csv(self.inputContext.data))
            self.process_ctx.raw_data           = dp.np.array([dp.np.array(subarr,dtype = dp.np.float64)[~dp.pd.isnull(dp.np.array(subarr))] for subarr in nestedresults])
            self.process_ctx.thread_index       = l+sum(self.threads_vector[0:itr]) if dp.JSON['hierarchical'] else l+itr*simutil.Threads

            self.processor.process(self.process_ctx)

        #?------------------------------------------------------
        #? Save csv Maps
        #?------------------------------------------------------
        #* Save the data matrices to CSV files in the specified results folder
        #* Each matrix is saved with a corresponding name from map_names
        for result_name in self.process_ctx.result_repository.data:
            if not "intermediate" in self.processes[result_name]:

                self.output_ctx.path            = f"{fileLog.resultfolder}/CSV_MAPS/{pre_fix}{result_name}_Map"
                self.output_ctx.data            = self.process_ctx.result_repository.data[result_name].tolist()

                if len(self.output_ctx.data) != 0:
                    self.writer.write(self.output_ctx)  # todo len check to writer with propper error handling
                else:
                    print(f"{result_name} is empty:")
                    print(self.output_ctx.data)

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
