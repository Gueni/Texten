import  assets.Dependencies     as  dp
import  Lib.RunScripts          as  run

from Lib.MapCalculation.MapCalculation import MapContext

RunScript       = run.runScripts(dp.JSON)
RunScript.simutil.init_sim(dp.JSON['maxThreads'],*[eval(dp.JSON[f"X{i}"]) for i in range(1, 11)],pattern=dp.JSON['permute'])

print("Sweepmatrix")
print(RunScript.simutil.sweepMatrix)

print("Map")
print(RunScript.simutil.Map)

print("Iterations")
print(RunScript.simutil.Iterations)

# def getMatrix(X1=[[0]], X2=[[0]], X3=[[0]], X4=[[0]], X5=[[0]], X6=[[0]], X7=[[0]], X8=[[0]], X9=[[0]], X10=[[0]]):
#     sweepMatrix = [X1, X2, X3, X4, X5, X6, X7, X8, X9, X10]
#     return sweepMatrix

# def detect_mode(config):
#     """
#     Detects the mode of operation for the current simulation.

#     Args:
#         Xs (list): lists of input variables X1-10

#     Returns: (string) : the operation mode (Normal or WCA)
#     """
#     if config["perturbation"] != 0 :
#         return "SENSITIVITY"

#     for var in config["sweepMatrix"]:
#         if var == [[0]] or var == [0]       :    continue       # Ignore not used X lists

#         for sub in var:
#             if isinstance(sub, list) and len(sub) in (2, 4)         :   return "WCA"    # WCA if [nom, tol] or [nom, tol, min, max]
#             if not isinstance(sub, list) and config["permute"]      :   return "PERMUTE" # Normal [[1,2,3,4..],.] no sublists
#             if not isinstance(sub, list)                            :   return "NORMAL" # Normal [[1,2,3,4..],.] no sublists
#             elif isinstance(sub, list) and len(sub) == 1          :   return "NORMAL" # Normal [[1],[2]...] with sublists

#     return "NORMAL"

# matrix = getMatrix(*[eval(dp.JSON[f"X{i}"]) for i in range(1, 11)])

# config = {
#     "permute"           :   dp.JSON['permute'],
#     "perturbation"      :   dp.JSON["perturbation"],
#     "nvars"             :   dp.JSON["nvars"],
#     "sweepMatrix"       :   getMatrix(*[eval(dp.JSON[f"X{i}"]) for i in range(1, 11)])
# }

# mode = detect_mode(config)
# map_context = MapContext(mode)
# sweepMatrix, Map, Iterations = map_context.generate_map(config)

# print("Sweepmatrix")
# print(sweepMatrix)

# print("Map")
# print(Map)

# print("Iterations")
# print(Iterations)