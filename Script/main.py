
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                                           __  __    _    ___ _   _
#?                                                                          |  \/  |  / \  |_ _| \ | |
#?                                                                          | |\/| | / _ \  | ||  \| |
#?                                                                          | |  | |/ ___ \ | || |\  |
#?                                                                          |_|  |_/_/   \_\___|_| \_|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import os
import sys

import  assets.Dependencies     as  dp
import  assets.Configuration.ScriptBody          as  ScriptBody
import  Lib.error_handler       as  er
import  Lib.RunScripts          as  run

from    Lib.RT_Box              import  RT_Box
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def main():
    """
    Main simulation workflow manager that handles parallel &/or serial execution of simulation runs.

    Handles:
            - Initialization of simulation environment and callback setup
            - Parallel execution with thread management (if enabled in config)
            - Error recovery and retry logic for failed simulations
            - Serial execution fallback mode
            - Results logging and final cleanup

    * The execution flow is controlled by JSON configuration which determines:
            *- Parallel/hierarchical mode settings
            *- Number of threads/iterations
            *- Error handling behavior and max retries

    !Dependencies:
            !--> Requires properly configured Dependencies (dp) and ScriptBody modules
            !--> Relies on JSON configuration for runtime parameters
    """

    # RT Box hook: when RT_BOX.RT is true in the config, run the RT Box workflow only 
    # and skip the rest of main() entirely. 
    if (rt_box := RT_Box.from_config(dp.json_path)).enabled : rt_box.run(); return

    dp.script_path  =   os.path.abspath(__file__)

    # Create script runner instance and initialize simulation
    RunScript       = run.runScripts(dp.JSON)

    dp.flag = True
    try :
        RunScript.simInit()
    except:
        RunScript.simEnd()
        sys.exit(-1)
    dp.flag = False

    # Setup callback function for trace holding based on JSON configuration
    Callback        =       RunScript.obj.holdTraceCallback(dp.scopes)

    # Initialize counters for iterations and retries
    i,tries         =       0,0

    #?-------------------------------------------------------
    #? Parallel Execution Section
    #?-------------------------------------------------------
    if dp.JSON['parallel']:

        while i < RunScript.simutil.Simulations:

            # Determine iteration range based on hierarchical or flat parallelization
            if dp.JSON['hierarchical']:
                iteration_range             =   list(range(sum(RunScript.simutil.threads_vector[0:i]),sum(RunScript.simutil.threads_vector[0:i+1])))
                RunScript.simutil.Threads   =   RunScript.simutil.threads_vector[i]
            else:
                iteration_range             =   list(range(i*RunScript.simutil.Threads,RunScript.simutil.Threads*(i+1)))

            # Initialize model options for current parallel batch
            RunScript.obj.modelinit_opts(RunScript.simutil.Threads,iteration_range,RunScript.JS['parallel'])
            j = 0

            # Log default parameters and subheader for iteration parameters
            RunScript.log_header(RunScript.obj.OptStruct[0] , simulation = i)

            while j < RunScript.simutil.Threads:
                # Execute simulation script and log updated values for each thread
                ScriptBody.simScript(RunScript.obj.OptStruct,j,RunScript.simutil.Map,RunScript.simutil.iterNumber,RunScript.fileLog.ResultsPath,RunScript.simutil)
                RunScript.simLog(RunScript.obj.OptStruct[j])
                j+=1

            #?-------------------------------------------------------
            #? Simulation Run and Error Handling Section
            #?-------------------------------------------------------
            with er.allow_exceptions():  # context manager to allow exceptions to propagate
                try:
                    # Normal execution parameter setting
                    crash                           =   False
                    RunScript.simRun(RunScript.simutil.Threads,True,Callback)
                    RunScript.simSave(i,crash)
                    tries                           =   0
                    i+=1

                except:
                    # Error recovery parameter setting
                    crash                           =   True
                    iterNumber                      =   RunScript.simutil.iterNumber

                    # Handle missing iterations after crash
                    MissingIter                     =   RunScript.simMissing(i,RunScript.simutil.threads_vector,RunScript.simutil.Threads)
                    k = 0

                    while k < len(MissingIter):
                        RunScript.simutil.iterNumber   =   MissingIter[k]
                        RunScript.obj.modelinit_opts(1,[RunScript.simutil.iterNumber],True)

                        # Re-run failed simulations
                        ScriptBody.simScript(RunScript.obj.OptStruct,0,RunScript.simutil.Map,RunScript.simutil.iterNumber,RunScript.fileLog.ResultsPath,RunScript.simutil)
                        RunScript.simRun(parallel=True,callback=Callback)
                        k+=1

                    # Save results after recovery
                    RunScript.simSave(i,crash)
                    RunScript.simutil.iterNumber       =   iterNumber

                    # Exit if max retries reached
                    i+=1
                    tries+=1
                    if (tries >= 10):
                        break
                    else:
                        continue

    #?-------------------------------------------------------
    #? Non-parallel execution
    #?-------------------------------------------------------
    else:
        RunScript.obj.modelinit_opts()

        # Log default parameters and subheader for iteration parameters
        RunScript.log_header(RunScript.obj.OptStruct)
        RunScript.simLog(RunScript.obj.OptStruct)

        # Run simulation and save data
        RunScript.simRun(threads=1,parallel=False)
        RunScript.simSave()

    #?-------------------------------------------------------
    #? Cleanup and footer logging Section
    #?-------------------------------------------------------
    RunScript.simEnd()

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__"   :   main()
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------