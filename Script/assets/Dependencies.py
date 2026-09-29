
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                    ____                            _                 _
#?                                                   |  _ \  ___ _ __   ___ _ __   __| | ___ _ __   ___(_) ___  ___
#?                                                   | | | |/ _ \ '_ \ / _ \ '_ \ / _` |/ _ \ '_ \ / __| |/ _ \/ __|
#?                                                   | |_| |  __/ |_) |  __/ | | | (_| |  __/ | | | (__| |  __/\__ \
#?                                                   |____/ \___| .__/ \___|_| |_|\__,_|\___|_| |_|\___|_|\___||___/
#?                                                              |_|
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import  json
import  time
import  datetime    ,   pathlib
import  random      ,   re
import  importlib
import  numpy                       as        np
import  itertools
import  assets.Mapping.plecs_mapping    as  pmap
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
json_path                               =   pathlib.Path(r"Script\assets\Configuration\Input_vars.json")                                                     #?
JSON                                    =   json.loads(json_path.read_text(encoding="utf-8"))                                                           #?
if (not JSON.get("params"))             :   paramdict_to_use    =   "assets.Parameters.Param_Dicts"                                                     #? Default to "Param_Dicts"
else                                    :   paramdict_to_use    =   "assets.Parameters." + JSON.get("params")                                           #?
try                                     :   Param_Dicts         =   importlib.import_module(paramdict_to_use)                                           #?
except ModuleNotFoundError              :   raise ImportError(f"Module {paramdict_to_use} specified in input_vars.json could not be found.")            #?
globals()["Param_Dicts"]                =   Param_Dicts                                                                                                 #?

url                                     =   "http://127.0.0.1"                                                                                          #? PLECS Host ip address : keep default if used locally.
port                                    =   "1080"                                                                                                      #? Port at which to communicate with PLECS.
METHOD			                        =   "JSON"				                                                                                        #? Options --> "XML", "JSON"


mdlVars                                 =   Param_Dicts.ModelVars                                                                                       #? ModelVars simulation parameters dictionary.
slvOpts                                 =   Param_Dicts.SolverOpts                                                                                      #? SolverOpts simulation parameters dictionary.
anlOpts                                 =   Param_Dicts.AnalysisOpts                                                                                    #? AnalysisOpts simulation parameters dictionary.
scopes                                  =   []                                                                                                          #? Empty global list to hold the model scopes.

Header_File                             =   "Script/assets/Headers/header.json"                                                                         #? Json file path in which we store headers.
html_template_iter                      =   "Script/assets/Templates/HTML_REPORT_TEMPLATE_iter.html"                                                    #? CSS style sheet.
html_template_standalone                =   "Script/assets/Templates/HTML_REPORT_TEMPLATE_std.html"                                                     #? Iteration Html report template file.
html_template                           =   "Script/assets/Templates/HTML_REPORT_TEMPLATE.html"                                                         #? Html standalone template.
stylesheet                              =   "Script/assets/UI/styles.css"                                                                               #? Html report template file.
script_path                             =   ''                                                                                                          #? Path to the current running python script.
headerColor                             =   '#009ADA'                                                                                                 #? Hex color for header
interleaved                             =   lambda l1,l2:list(x for x in itertools.chain.from_iterable(itertools.zip_longest(l1,l2)) if x is not None)  #? Lambda expression for interleaving lists.

cp_mdl                                  =   ''                                                                                                          #? Path to the current running plecs model.
suffix                                  =   ""                                                                                                          #? Suffix used in results folder name.
tinit_sim                               =   time.time()                                                                                                 #? Simulation init Time.

pmapping                                =	[]                                                                                                          #? Plecs mapping list.
pmap_multi	                            =	[]                                                                                                          #? Plecs mapping nested list for multi-plotting purposes.
pmap_plt                                =   {}                                                                                                          #? Plecs mapping dictionary for generating html reports.
constant_dict                           =   {}                                                                                                          #? Plecs mapping dictionary for constants.
pmap_plt_ctrl                           =   {}                                                                                                          #? Plecs mapping dictionary for controls
Y_Length                                =   []                                                                                                          #?
Y_list                                  =   []                                                                                                          #?
Ycumsum                                 =   []                                                                                                          #?
YLcumsum                                =   []                                                                                                          #?
segments                                =   []                                                                                                          #?
pwm_dict                                =   {}                                                                                                          #?
slices                                  =   []                                                                                                          #?

scriptname                              =   JSON['scriptName']                                                                                          #?
Runscript_path                          =   "Lib/RunScripts.py"                                                                                         #?
ScriptBody_path                         =   "assets/Configuration/ScriptBody.py"                                                                                         #?
Resistances                             =   []                                                                                                          #?
Pout_idx                                =   0                                                                                                           #?
Rail_idx                                =   0                                                                                                           #?
Common_idx                              =   0                                                                                                           #?
phase                                   =   0                                                                                                           #?
current_idx                             =   0                                                                                                           #?
com_cols                                =   0                                                                                                           #?


BMW_Base64_Logo                         =   "Script/assets/Templates/BMW_Base64_Logo.txt"                                                               #? Base64 data related to BMW logo used in html reports.
plt_title_list                          =   []                                                                                                          #?
map_index                               =   " "                                                                                                         #?
map_names                               =   " "                                                                                                         #?
pattern                                 =   re.compile(r'\b(power|loss|dissipation|current|voltage|temperature)\b', re.I)                               #?
unit_map                                =   {"current":"[A]", "voltage":"[V]", "temperature":"[C]", "power":"[W]", "loss":"[W]", "dissipation":"[W]"}   #?
iterSplit                               =   True                                                                                                        #?
standalone_exist                        =   False                                                                                                       #? boolean used to decide graphs plotting for standalone
date                                    =   str(datetime.datetime.now().replace(microsecond=0))                                                         #? Date and time variable.
std_headers                             =   []                                                                                                          #?
std_length                              =   0

harmonics                               =   np.arange(0,JSON['hrmcs']+1,1, dtype=int).tolist()                                                          #?
F_Fund                                  =   JSON['FundFreq']                                                                                            #?
updated_params_dict                     =   {}                                                                                                          #?
mode_sim                                =   "Normal"                                                                                                    #?
flag                                    =   False                                                                                                       #?
mode                                    =   " "                                                                                                         #?
mdl_precision                           =   8                                                                                                           #? value precision for init dictionaries.
seed                                    =   random.SystemRandom().randint(0,2**32-1)                                                                    #?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
