
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

sim_utc_original = "1784109862131"
sim_utc_test = "1784117541847"

sim_name = "Run_Single_Rail_Sweep_SR_Entry"
path_original = f"C:/Users/QXZ3MAB/GitHub/PyPLECS/Script/Data/Res/{sim_name}_{sim_utc_original}/CSV_MAPS/"
path_test = f"C:/Users/QXZ3MAB/GitHub/PyPLECS/Script/Data/Res/{sim_name}_{sim_utc_test}/CSV_MAPS/"

input_ctx = Reader.InputContext()
output_ctx = Writer.OutputContext()
output_ctx.mode = "a"

reader = Reader.CSVReader()
writer = Writer.CSVWriter()

original = {}
test = {}
res = {}

files = [f for f in listdir(path_original) if isfile(join(path_original, f))]

for file in files:
    input_ctx.rawDataPath = f"{path_original}{file}"
    reader.read(input_ctx)
    originalNP = np.array([np.array(subarr,dtype=np.float64)[~pd.isnull(np.array(subarr))] for subarr in input_ctx.data])
    original[file] = originalNP

files = [f for f in listdir(path_test) if isfile(join(path_test, f))]

for file in files:
    input_ctx.rawDataPath = f"{path_test}{file}"
    reader.read(input_ctx)
    testNP = np.array([np.array(subarr,dtype=np.float64)[~pd.isnull(np.array(subarr))] for subarr in input_ctx.data])
    test[file] = testNP

for map in original:
    with np.errstate(divide="ignore", invalid="ignore"):
        percent_err = np.where(original[map] != 0, np.abs((original[map] - test[map]) / original[map]) * 100, 0)
    max_total_err = np.max(percent_err)
    max_err_index = np.unravel_index(np.argmax(percent_err), percent_err.shape)
    res[map] = [max_err_index, max_total_err]
    print(f"Index: {max_err_index}, total err: {max_total_err} in: {map}")
