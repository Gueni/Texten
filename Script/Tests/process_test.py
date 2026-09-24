
from  Lib.postprocessing import processor as pr

import pickle
import Lib.io.Reader as Reader
import Lib.io.Writer as Writer
import numpy as np
import pandas as pd
import time
import json

from os import listdir
from os.path import isfile, join

#FROM DATAPROCESS
def norm_results_csv(results):
    """
    Normalize a list of lists by padding shorter sublists with NaN values to match the longest sublist.

    Parameters:
    results (list of lists): A list containing multiple lists of varying lengths.

    Returns:
    list: A list of lists where each sublist has been padded with NaN values to match the longest sublist length.

    Raises:
    ValueError: If the input is not a list of lists.
    """

    # Initialize a list to store the normalized results vectors.
    # Determine the length of the longest sublist in results.
    resultsvect             = []
    longest_length          = max(map(len, results))

    # Loop through each sublist in results to pad shorter items with NaNs.
    # Return the list of normalized results vectors with equal lengths.
    # Create an array of NaNs
    # Prepend NaNs to each item in the sublist so all items have the same length.
    for sublist in results:
        difference_lengths  = longest_length - len(sublist)
        NaNarray            = np.full(difference_lengths, np.nan)
        outputresults       = [np.append(NaNarray, np.array(item)).tolist() for item in sublist]
        resultsvect.append(outputresults)

    return resultsvect

def init_mat_dict(res_dict: dict, processor_cfg: pr.ProcessorConfig, iterations: int):
    sensitivity_len = iterations - 1
    for current_process_name, info in processor_cfg.process_dict.items():
        processor_type = info["processor"]
        slice_string = info["slice"]

        if processor_type == "SENSITIVITY": len = sensitivity_len
        else: len = iterations

        if slice_string != "NONE":
            data_slice = processor_cfg.slice_map.get(slice_string)
            data_slice_length = data_slice.get("length")
            if data_slice_length != 0:
                if "FFT" not in current_process_name:
                    res_dict[current_process_name] = np.zeros((len, data_slice_length))
                else:
                    res_dict[current_process_name] = np.zeros((len * (processor_cfg.process_cfg["FFT"].hrmcs+1), data_slice_length))
            else:
                print(f"Slice length not initialized in; {current_process_name}")
                return ValueError

def add_sensitivity_processes(processor_cfg: pr.ProcessorConfig, post_fix: str):
    additional_process_dict = {}
    for current_process_name, info in processor_cfg.process_dict.items():
        additional_process_dict[current_process_name+post_fix] = dict(slice=info["slice"], processor="SENSITIVITY")
    processor_cfg.process_dict.update(additional_process_dict)

sim_utc = "1776320902058"
sim_name = "DCDC_Standalone_Snubbers_Sensitivity"
path = f"C:/Users/QXZ3MAB/GitHub/PyPLECS/Script/Data/Res/{sim_name}_{sim_utc}/CSV_TIME_SERIES/"
name = f"results_{sim_utc}"

with open("Script\Tests\input\json\process_config_standalone.json", "r") as f:
    content = f.read()

json_config = json.loads(content)
cfg_name = json_config["Config_Name"]
print(f"Config Name: {cfg_name}")
slicing = json_config["Slicing"]
processes = json_config["Processes"]

files = [f for f in listdir(path) if isfile(join(path, f))]

with open(f"Script/Tests/dump/res_list_0.pkl", "rb") as data:
    res_list_dump = pickle.load(data)

with open(f"Script/Tests/dump/P_aux_0.pkl", "rb") as data:
    P_aux_dump = pickle.load(data)

input_ctx = Reader.InputContext()
output_ctx = Writer.OutputContext()
output_ctx.mode = "a"

reader = Reader.CSVReaderNP()
writer = Writer.CSVWriter()

sensitivity_post_fix = "_Sensitivity"
fft_cfg = pr.pp.ProcessFFTConfig(fund_freq = 100e3, hrmcs = 1,to_file_ts = 0)
dissipations_cfg = pr.pp.ProcessDissipationsConfig(res_list=res_list_dump, current_idx=37)
thermal_stats_cfg = pr.pp.ProcessThermalStatsConfig(dcdc_d=False, rail_idx=15, common_idx=53, pout_idx=13, p_aux=30,phase=2)
sensitivity_cfg = pr.pp.ProcessSensitivityConfig(perturbation=0.1, post_fix= sensitivity_post_fix, fft_cfg=fft_cfg)

process_config = {
    "FFT"           : fft_cfg,
    "DISSIPATIONS"  : dissipations_cfg,
    "THERMALSTATS"  : thermal_stats_cfg,
    "SENSITIVITY"   : sensitivity_cfg
}

slicing["all"]["length"] = 2

processor_cfg = pr.ProcessorConfig(sim_type     = cfg_name,
                                   slice_map    = slicing,
                                   process_dict = processes,
                                   process_cfg  = process_config)

add_sensitivity_processes(processor_cfg= processor_cfg, post_fix=sensitivity_post_fix)

MAT_dict = {}
err = init_mat_dict(res_dict= MAT_dict, processor_cfg= processor_cfg, iterations= len(files))
if err: exit(err)

processor = pr.ProcessorFactory().get_processor(processor_cfg)

mat_ctx = pr.pp.ProcessContext()
mat_ctx.result_repository.data = MAT_dict

#dummy sim loop
for i, file in enumerate(files):
    start = time.time()
    input_ctx.rawDataPath = f"{path}{file}"
    reader.read(input_ctx)

    #FROM PYUTILS
    #nestedresults = np.array(norm_results_csv(input_ctx.data))
    #input_ctx.data = np.array([np.array(subarr,dtype=np.float64)[~pd.isnull(np.array(subarr))] for subarr in nestedresults])
    end = time.time()
    print(f"Read Input {input_ctx.rawDataPath}: {end-start}s")

    mat_ctx.raw_data = input_ctx.data
    mat_ctx.thread_index = i

    start = time.time()
    processor.execute(mat_ctx)
    end = time.time()

    print(f"Process Input: {end-start}s")

for result_name in mat_ctx.result_repository.data:
    if not "intermediate" in processes[result_name]:
        output_ctx.path = f"Script/Tests/test_data_{result_name}"
        output_ctx.data = mat_ctx.result_repository.data[result_name].tolist()
        if len(output_ctx.data) != 0: writer.write(output_ctx)
        else:
            print(f"{result_name} is empty:")
            print(output_ctx.data)

#Delete intermediate
# for result_name in processes:
#     if "intermediate" in processes[result_name]:
#         del mat_ctx.result_repository.data[result_name]
#print(mat_ctx.result_repository.data)

# dump data from pyutils
                # with open(f"Script/Tests/dump/res_list_{l}.pkl", "wb") as data: # dump dta for testing
                #     pickle.dump(res_list, data)
                # with open(f"Script/Tests/dump/P_aux_{l}.pkl", "wb") as data:
                #     pickle.dump(P_aux, data)