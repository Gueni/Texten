
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                       _____ _ _         _              _ _                      _
#?                                      |  ___(_) | ___   / \   _ __   __| | |    ___   __ _  __ _(_)_ __   __ _
#?                                      | |_  | | |/ _ \ / _ \ | '_ \ / _` | |   / _ \ / _` |/ _` | | '_ \ / _` |
#?                                      |  _| | | |  __// ___ \| | | | (_| | |__| (_) | (_| | (_| | | | | | (_| |
#?                                      |_|   |_|_|\___/_/   \_\_| |_|\__,_|_____\___/ \__, |\__, |_|_| |_|\__, |
#?                                                                                     |___/ |___/         |___/
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import datetime
import flatdict
import jinja2
import json
import natsort
import os
import pathlib
import pyfiglet
import re
import shutil
import subprocess
import sys
import time
import win32con
import win32gui
import  assets.Dependencies         as        dp
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class FileAndLogging:
    def __init__(self, suffix="", json_dir=""):
        """
        Initialize the FileAndLogging class with various attributes
        """

        self.line_length            =   180                                                                                                                     # line separator length
        self.log_offset             =    5                                                                                                                      # paddign offset for log
        self.utc                    =   str(int(time.time()*1000))                                                                                           # current time in milliseconds
        dp.suffix                   =   suffix                                                                                                                  # suffix for result folder
        self.ResultsPath            =   ""                                                                                                                      # path to results folder
        self.basename               =   os.path.basename(sys.argv[0])[:-3]                                                                                # base name of the script without .py
        self.resultfolder           =   (os.getcwd()).replace("\\","/") + "/Script/" + "D".upper() + "ata/Res/"      + json_dir + "_" + self.utc + suffix    # result folder path
        self.logfolder              =   (os.getcwd()).replace("\\","/") + "/Script/" + "D".upper() + "ata/Log/"      + json_dir                              # log folder path
        self.scriptbody_folder      =   (os.getcwd()).replace("\\","/") + "/Script/" + "D".upper() + "ata/Scripts/"  + json_dir                              # scriptbody scripts folder path
        self.jsonfolder             =   (os.getcwd()).replace("\\","/") + "/Script/" + "D".upper() + "ata/Json/"     + json_dir                              # json input folder path
        self.initfolder             =   (os.getcwd()).replace("\\","/") + "/Script/" + "D".upper() + "ata/cmd/"      + json_dir                              # initialization commands folder path
        self.nested_res_hier        =   ''                                                                                                                      # nested results hierarchy
        self.model_vars_names       =   []                                                                                                                      # list of first order dict names

        self.fix_json_strings       =   lambda folder: [f.write_text(json.dumps([s.replace(" ", "_").replace("-", "_") for s in json.loads(f.read_text())], indent=2)) for f in pathlib.Path(folder).glob("*.json")]
        self.filter_non_xi          =   lambda lst: [s for s in lst if not (s.startswith('X') and s[1:].isdigit())]

    def line_separator(self):
        """
        Generate a horizontal line composed of dash characters to visually separate sections in log output.

        """
        # Log the separator line using the log method
        self.log("-" * self.line_length)

    def natsort_files(self,ResDir,standalone=False):
        """
        Sorts out a list of files in a given directory in an alphanumeric way.

        *Args:
            ResDir (string) : dircetory of files.

        !Returns:
            list            : sorted list of files.
        """

        # Initialize an empty list to hold file paths and sort them alphanumerically
        # then return the sorted list of file paths then return it
        file_list   =   []
        if standalone:
            for filename in os.scandir(ResDir):
                if filename.is_file() and filename.path.endswith('_Standalone.csv'):
                    file_list.append(str(filename.path.replace("\\","/")))
        else :
            for filename in os.scandir(ResDir):
                if filename.is_file() and filename.path.endswith('.csv') and not filename.path.endswith('_Map.csv') and not filename.path.endswith('_Standalone.csv'):
                    file_list.append(str(filename.path.replace("\\","/")))
        file_list = natsort.natsorted(file_list)
        return  file_list

    def log(self,msg):
        """
        Redirects all printed statements from consol to a specified file.

        *Args:
            pathf (string)    : path of the file to save to.
            msg   (string)    : message to be logged to file.
        """
        # if the file exists, open it in append mode, otherwise create a new file
        if os.path.exists(self.LogFile):
            sys.stdout  =   open(self.LogFile,'a')
        else :
            sys.stdout  =   open(self.LogFile,'w+')

        # log the message
        print(msg)

        # close the file and restore stdout
        sys.stdout.close()
        sys.stdout = sys.__stdout__

    def createFolders(self):
        """
        Create all necessary folders and return paths.
        """

        try:
            # Create results folder structure
            os.makedirs(self.resultfolder, exist_ok=False)

            [os.makedirs(self.resultfolder + subf, exist_ok=False) for subf in ["/HTML_REPORTS", "/HTML_GRAPHS", "/CSV_MAPS", "/CSV_TIME_SERIES", "/Scopes_Traces"]]

            # Create other folders
            [os.makedirs(f, exist_ok=True) for f in [self.logfolder, self.jsonfolder, self.initfolder, self.scriptbody_folder]]

        except OSError: pass

        # Set paths
        self.ResultsPath    = f"{self.resultfolder}/CSV_TIME_SERIES/results_{self.utc}_"

        # Create a unique log file name based on the current UTC time.
        self.LogF_name      = "log" + "_" + self.utc + ".log"

        # Build the full path to the log file using the specified log folder and file name.
        self.LogFile        = self.logfolder +"/" + self.LogF_name

        return self.ResultsPath, self.LogFile

    def header(self):
        """
        Generates a header for the log file, consisting of a horizontal line,
        a stylized "SIMULATION STARTED" message, and another horizontal line.

        """

        # Generate a header for the log file
        # The header includes a horizontal line, a stylized "SIMULATION STARTED" message
        # and another horizontal line to visually separate the header from the rest of the log content
        self.line_separator()
        self.log(pyfiglet.figlet_format("SIMULATION  STARTED",width=100))
        self.line_separator()

    def footer(self,simutil):
        """
        Generates the footer for the log file, including the total simulation time,
        a message indicating that the simulation has ended, and a copy of all output files.

        *Args:
            simutil (obj)   :   object instance of class pyutils.
        """

        # Generate the footer for the log file
        # The footer includes the total simulation time, a message indicating that the simulation has ended,
        # and a copy of all output files to the result folder
        self.line_separator()
        tf_sim  =   time.time()
        self.log('{} = {}'.format("Total Simulation Time".ljust(self.PADDING_WIDTH  , ' '),f"{str((tf_sim-dp.tinit_sim).__round__(3)/60)} minutes."))

        self.line_separator()
        self.log(pyfiglet.figlet_format("SIMULATION  ENDED",width=100))
        self.line_separator()

        if (dp.JSON['parallel']):
            self.log(pyfiglet.figlet_format("SIMULATION  ITERATIONS",width=150))
            self.line_separator()
            self.log('{} = {}'.format(f"Iterations".ljust(self.PADDING_WIDTH  , ' '),f"{self.filter_non_xi(dp.JSON['sweepNames'])}"))

            if isinstance(simutil.Map, list):
                for i in range(len(simutil.Map)):
                    self.log('{} = {}'.format(f"Iter{' '+str(i+1)}".ljust(self.PADDING_WIDTH  , ' '),f"{simutil.Map[i][:len(self.filter_non_xi(dp.JSON['sweepNames']))]}"))
            else:
                for i in range(len(simutil.Map)):
                    self.log('{} = {}'.format(f"Iter{' '+str(i+1)}".ljust(self.PADDING_WIDTH  , ' '),f"{(simutil.Map[i][:len(self.filter_non_xi(dp.JSON['sweepNames']))]).tolist()}"))

        self.copyfiles()

    def copyfiles(self):
        """
        Copy all required files to the result folder.
        """

        cwd             = os.getcwd().replace("\\", "/")

        # Base files to copy: (source, destination , condition)
        files_to_copy   = [

            (dp.cp_mdl                                                                      ,os.path.join(self.resultfolder  , "PLECS_MODEL_" + dp.cp_mdl.split('\\')[-1])   ,True                   ),    # Plecs model path
            (dp.script_path                                                                 ,os.path.join(self.resultfolder  , f"{self.basename}.py"                     )   ,True                   ),    # Script path
            (f"{cwd}/Script/{dp.Runscript_path}"                                            ,os.path.join(self.resultfolder  , "Runscript.py"                            )   ,True                   ),    # Runscript path
            (self.LogFile                                                                   ,os.path.join(self.resultfolder  , self.LogF_name                            )   ,True                   ),    # Log file path

            (f"{cwd}/Script/assets/UI/scripts.js"                                           ,os.path.join(self.resultfolder  , "HTML_REPORTS/scripts.js"                 )   ,True                   ),    # java script file path
            (f"{cwd}/Script/assets/Configuration/Input_vars.json"                           ,os.path.join(self.resultfolder  , f"Input_vars_{self.utc}.json"             )   ,True                   ),    # Input_vars to results folder
            (f"{cwd}/Script/assets/Parameters/Param_Dicts.py"                               ,os.path.join(self.resultfolder  , "Param_Dicts.py"                          )   ,True                   ),    # Parameters dictionaries file path
            (f"{cwd}/Script/assets/Mapping/plecs_mapping.py"                                ,os.path.join(self.resultfolder  , "plecs_mapping.py"                        )   ,True                   ),    # Plecs signals mapping file path
            (f"{cwd}/Script/assets/Configuration/InitializationCommands.m"                  ,os.path.join(self.resultfolder  , f"InitializationCommands_{self.utc}.m"    )   ,True                   ),    # Plecs Initilization commands file path
            (f"{cwd}/Script/assets/Configuration/Input_vars.json"                           ,os.path.join(self.jsonfolder    , f"Input_vars_{self.utc}.json"             )   ,True                   ),    # Input_vars to json folder
            (f"{cwd}/Script/assets/Configuration/InitializationCommands.m"                  ,os.path.join(self.initfolder    , f"InitializationCommands_{self.utc}.m"    )   ,True                   ),    # InitializationCommands

            (f"{cwd}/Script/{dp.ScriptBody_path}"                                           ,os.path.join(self.resultfolder +"/","ScriptBody_" + self.utc + ".py"        )   ,dp.JSON['parallel']    ),    # ScriptBody
            (f"{cwd}/Script/{dp.ScriptBody_path}"                                           ,os.path.join(self.scriptbody_folder +"/","ScriptBody_" + self.utc + ".py"   )   ,dp.JSON['parallel']    ),    # ScriptBody
            (os.path.join(self.scriptbody_folder +"/","ScriptBody_" + self.utc + ".m")   ,os.path.join(self.resultfolder +"/","ScriptBody_" + self.utc + ".m"         )   ,dp.JSON['parallel']    )     # ScriptBody

                        ]

        # Directories to copy: (source, destination)
        dirs_to_copy = [
                            (f"{cwd}/MyLibraries"                                           , os.path.join(self.resultfolder , "PLECS_Lib")                                 , True                   ),     # Plecs libraries directory
                            (f"{cwd}/Script/assets/Headers"                                 , os.path.join(self.resultfolder , "HEADER_FILES")                              , dp.JSON["model"]       ),     # Headers json files directory
                            (f"{cwd}/Script/assets/Mapping/{dp.JSON.get('model')}"          , os.path.join(self.resultfolder , f"SIGNAL_MAPPING/{dp.JSON.get('model')}")    , dp.JSON["model"]       )      # Model specific signal mapping json directory
                        ]

        # Copy all files
        for src, dst ,cond  in files_to_copy   :
            if cond :   shutil.copy(src, dst)

        # Copy all directories
        for src, dst ,cond  in dirs_to_copy    :
            if cond :   shutil.copytree(src, dst)

        # Fix headers : replace spaces with _ ...
        self.fix_json_strings(os.path.join(self.resultfolder, "Headers"))

    def get_last_commit(self):
        """
        Get the last commit hash and comment.

        !Returns:
            str : Commit hash , commit comment
        """

        # Retrieve the last commit hash and comment from the git repository
        # by running the git log command with specific formatting options.
        # capture the output and splits it into the hash and comment parts.
        # If an error occurs during the command execution, it prints the error message
        # and returns None for both the hash and comment.
        try:
            result = subprocess.run(
                                        ['git', 'log', '-1', '--pretty=format:%H%n%s']  ,
                                        capture_output  = True                          ,
                                        text            = True                          ,
                                        check           = True
                                    )
            commit_hash, commit_comment = result.stdout.split('\n', 1)
            return commit_hash, commit_comment
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
            return None, None

    def param_log(self,dictt,Threads=1,prefix='',isFirst=True,iters=1,sims=1):
        """
        Takes a dictionry then crawls all over its parameters in a recursive way
        and logs everything in a file.

        *Args:
            dictt           (dict)              : input dictionary.
            Threads         (int)               : Number of Threads.
            threads_vector  (list, optional)    : Vector of threads. Defaults to empty.
            hierarchical    (bool, optional)    : Whether the logging is hierarchical. Defaults to False.
            prefix          (str, optional)     : prefix for data tree in dict. Defaults to ''.
            isFirst         (Bool)              : helps make the recursive function run an expression only once. Defaults to True.
        """

        # If this is the first call, log the last commit hash and comment
        # and the current date and time, along with the number of threads.
        if isFirst:
            # Reset max prefix length for this log session
            self.max_prefix_length = 0

            # find the maximum prefix length
            self.find_max_prefix(dictt, '')

            # Add offset to the max prefix length for padding
            self.PADDING_WIDTH = self.max_prefix_length + self.log_offset

            commit_hash, commit_comment = self.get_last_commit()

            if commit_hash and commit_comment:
                self.line_separator()

                self.log('{} = {}'.format("Last Full Commit Hash".ljust(self.PADDING_WIDTH  , ' '),str(commit_hash)))
                self.log('{} = {}'.format("Last Commit Hash".ljust(self.PADDING_WIDTH       , ' '),str(commit_hash[:11])))
                self.log('{} = {}'.format("Last Commit Comment".ljust(self.PADDING_WIDTH    , ' '),str(commit_comment)))

            self.log('{} = {}'.format("Date & Time".ljust(self.PADDING_WIDTH        , ' '),str(datetime.datetime.now())))
            # if hierarchical:
            #     self.log('{} = {}'.format("Threads Vector".ljust(self.PADDING_WIDTH       , ' '),str(threads_vector)))
            # else:
            self.log('{} = {}'.format("Iterations Count".ljust(self.PADDING_WIDTH       , ' '),str(iters)))
            self.log('{} = {}'.format("Threads Count".ljust(self.PADDING_WIDTH       , ' '),str(Threads)))
            self.log('{} = {}'.format("Simulations Count".ljust(self.PADDING_WIDTH       , ' '),str(sims)))

            self.log('{} = {}'.format("Seed ".ljust(self.PADDING_WIDTH  , ' '),f'{dp.seed}'))

            self.line_separator()
            self.log(pyfiglet.figlet_format("DEFAULT PARAMETERS", width=200))
            self.line_separator()

        # If the input is a dictionary, iterate through its items
        # and log each key-value pair with the specified prefix.
        # If the value is another dictionary, recursively call param_log on it
        # with an updated prefix.
        if isinstance(dictt, dict):
            for k, v2 in dictt.items():
                p2 = "{}['{}']".format(prefix, k)
                self.param_log(v2,Threads,p2,isFirst=False)
        else:
            if os.path.exists(self.LogFile):
                sys.stdout = open(self.LogFile, 'a')
            else:
                sys.stdout = open(self.LogFile, 'w+')

            print('{} = {}'.format(prefix.ljust(self.PADDING_WIDTH, ' '), repr(dictt)))

            sys.stdout.close()
            sys.stdout = sys.__stdout__

    def InitializationCommands(self, input_file, output_file, modelvars, m_file, mapvars,solveropts):
        """
        Replaces lines containing searched expression in the input file with content from modelvars.
        The modified content is written to output_file. Specifically, if InitializationCommands ""
        is found, it inserts the modelvars content inside the quotes.

        *Args:
            input_file  (str)       : Path to the input file.
            output_file (str)       : Path to the output file.
            modelvars   (dict)      : ModelVars dictionary.
            solveropts  (dict)      : SolverOpts dictionary.
        """
        # Open the input file for reading and the output file for writing
        # Read each line from the input file, check for the specific line
        # If the line contains 'InitializationCommands ""', replace it with the flattened dictionary string
        # Write the modified line to the output file, otherwise write the line as is
        # Flatten the dictionary to a string using the specified separator

        # Generate Octave code
        if dp.JSON['parallel'] :

            octave_code = self.octave_sweep_script(
                                                    mapvars                                                                                                     ,
                                                    dp.JSON['sweepNames']                                                                                       ,
                                                    self.octave_sweep_mapping(os.path.join(os.getcwd(), "Script", dp.ScriptBody_path).replace("\\", "/")) ,
                                                    modelvars                                                                                                   ,
                                                    dp.scopes                                                                                                   ,
                                                    solveropts
                                                    )

            # write generated octave script code to file.
            with open(f'{self.scriptbody_folder}/ScriptBody_{self.utc}.m', 'w') as f: f.write(octave_code)

        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:

            # First flatten the dictionary using the specified separator
            # Then convert the flattened dictionary to a string
            # where each key-value pair is formatted as `key=value;`
            # and each pair is on a new line
            # e.g., {'a': {'b': 1}} -> "a.b=1;"
            flattened_dict      = flatdict.FlatDict(modelvars,delimiter='.')
            flattened_str_dot   = '\n'.join(f"{key}={value};" if (not isinstance(value,str)) else f"{key}='{value}';" for key, value in flattened_dict.items()  )

            # replace the content of InitializationCommands in case it is empty or not.
            for line in infile:
                    match   = re.search(r'InitializationCommands "(.*?)"', line)
                    if match:
                        existing_content    = match.group(1)

                        if existing_content.strip():
                            combined = existing_content + "\n" + flattened_str_dot
                        else:
                            combined = flattened_str_dot

                        prefix              = line[: match.start(1)]
                        updated_line        = prefix + combined + '"'
                        outfile.write(updated_line)

                    else:
                        outfile.write(line)

        # Create the directory for the .m file if it does not exist
        # and write the flattened dictionary string to the .m file
        # Ensure the directory exists before writing the file
        os.makedirs(os.path.dirname(m_file), exist_ok=True)
        with open(m_file, 'w', encoding='utf-8') as m_out:
            # Write struct definitions at the beginning of the .m file as well
            if self.model_vars_names:
                for name in self.model_vars_names:
                    m_out.write(f"{name} = struct();\n")
                m_out.write("\n")
            m_out.write(flattened_str_dot)
        m_out.close()

        # Break all lib links in standalone model
        # self.break_links(output_file)
        if dp.JSON['parallel'] :
            # Inject the generated Octave script into the standalone PLECS model file
            self.inject_octave(
                                plecs_file_path     =   output_file                                         ,
                                output_file_path    =   output_file                                         ,
                                m_file_path         =   f'{self.scriptbody_folder}/ScriptBody_{self.utc}.m' ,
                                solveropts          =   solveropts
                            )

    def break_links(self,model_path,timeout=120):
        """
        Open standalone model file and break all external library links.

        *Args:
            model_path (string)         : path to the plecs standalone model.
            timeout    (int, optional)  : Timeout to break infinit loop. Defaults to 120.
        """
        model_name  = os.path.basename(model_path).replace('.plecs','')
        os.startfile(model_path)
        start       = time.time()
        Passed      = False

        while True:
            windows = dp.gw.getWindowsWithTitle(model_name)
            if windows and model_name in windows[0].title:
                target_window = windows[0]
                print(f"Model '{model_name}' confirmed open")
                Passed = True
                break  # continue main code

            if time.time() - start > timeout:
                Passed = False
                print(f"TimeoutError( Model '{model_name}' didn't open in {timeout}s --> external lib links where not broken in standalone model file.")
                break

        time.sleep(2)

        if Passed :
            handle = win32gui.FindWindow(None,target_window.title)
            win32gui.ShowWindow(handle,win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(handle)
            target_window.maximize()
            time.sleep(0.5)

            # click on edit
            dp.pyautogui.hotkey('alt','e')
            time.sleep(0.5)
            # go to the end
            dp.pyautogui.press('end')
            time.sleep(0.5)
            # go up once
            dp.pyautogui.press('up')
            time.sleep(0.5)
            # click on Break all external links...
            dp.pyautogui.press('enter')
            time.sleep(0.5)
            # switch from cancel to okay in the warning menu
            dp.pyautogui.press('tab')
            # click okay
            dp.pyautogui.press('enter')
            time.sleep(0.5)
            # click okay in the message menu
            dp.pyautogui.press('enter')
            # click save model
            dp.pyautogui.hotkey('ctrl','s')
            time.sleep(5)
            target_window.restore()
            # click close model
            dp.pyautogui.hotkey('ctrl','F4')

        else : pass

    def find_max_prefix(self, dictt, prefix=''):
        """
        find the maximum prefix length without logging

        *Args:
            dictt  (dict)           : python model vars dictionary.
            prefix (str, optional)  : prefix fetched from dictionary tree. Defaults to ''.
        """
        if isinstance(dictt, dict):
            for k, v in dictt.items():
                new_prefix      = "{}['{}']".format(prefix, k)
                current_length  = len(new_prefix)

                if current_length > self.max_prefix_length:
                    self.max_prefix_length = current_length

                self.find_max_prefix(v, new_prefix)
        else:
            current_length = len(prefix)

            if current_length > self.max_prefix_length:

                self.max_prefix_length = current_length

    def octave_sweep_script(self,mapvars, sweepnames, mappings, model_vars_dict ,scopes_list,solveropts):
        """
        Generate Octave script for parameter sweep simulation.

        *Args:
            mapvars         (list)  : Nested list of parameter values for sweep
            sweepnames      (list)  : List of names for the swept parameters
            mappings        (dict)  : Dictionary of variable mappings for the simulation
            model_vars_dict (dict)  : Dictionary of model variables
            scopes_list     (list)  : List of scope names to capture simulation results

        !Returns:
            (str)                   : Containing the complete Octave script
        """
        # Define the template file name
        template_file       = '/Script/assets/Templates/octave_sweep_template.j2'

        # Create Jinja2 environment with current directory as template loader
        env                 = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()), trim_blocks=True, lstrip_blocks=True)

        # Load the specific template file
        template            = env.get_template(template_file)

        # Filter out sweep names that start with "X" followed by digits (internal indices)
        filtered            = [x for x in sweepnames if not (x.startswith("X") and x[1:].isdigit())]

        # Detect whether mapvars is 2D or 3D structure
        if dp.mode_sim.lower() == "NORMAL".lower() or dp.mode_sim.lower() == "PERMUTE".lower()  : mapvars_dim   =   2
        else                                        : mapvars_dim   =   3

        # Generate the simStruct line from mappings
        # simstruct_line      = self.format_octave_struct(model_vars_dict,mappings, self.dict_to_struct(solveropts))
        simstruct_line      =  f"simStruct = struct('ModelVars', {self.dict_to_struct(model_vars_dict)}, 'SolverOpts', {self.dict_to_struct(solveropts)});"

        # Create the results folder path in the current working directory
        scopes_folder       = os.path.join(self.resultfolder, 'Scopes_Traces')
        csv_folder          = os.path.join(self.resultfolder, 'CSV_TIME_SERIES')

        # Render the template with all the parameters and return the result
        return template.render(
            mapvars                 =   mapvars         ,   # Pass the parameter values
            sweepnames              =   filtered        ,   # Pass filtered sweep names
            mappings                =   mappings        ,   # Pass variable mappings
            num_params              =   len(filtered)   ,   # Pass number of parameters
            simstruct_line          =   simstruct_line  ,   # Pass simStruct initialization line
            mapvars_dim             =   mapvars_dim     ,   # Pass dimension information
            scopes                  =   scopes_list     ,   # Pass list of scopes
            scopes_folder           =   scopes_folder   ,   # Pass the scopes folder path
            csv_folder              =   csv_folder      ,   # Pass the csv time series folder path
            FileNameStandalonePath  =   self.ResultsPath    # Pass the Filename for the standalone
        )

    def octave_sweep_mapping(self,file_path):
        """
        Extract mappings from ScriptBody.py with support for both 2D and 3D mapvars.

        *Args:
            file_path (str)   : Path to the Python script file containing mappings
            mapvars   (list)  : The mapvars structure to determine dimensions

        !Returns:
                      (dict)  : Dictionary of mappings with sequential keys preserving original order
        """

        # Detect the dimensions of mapvars (2D or 3D)
        if dp.mode_sim.lower() == "Normal".lower()  : mapvars_dim   =   2
        else                                        : mapvars_dim   =   3

        # Initialize empty dictionary to store mapping results
        mappings            = {}

        # Open the scriptbody file
        # Read the entire file content as a single string
        with open(file_path, 'r') as f: content = f.read()

        # Define the section markers that delimit the area with user-editable code
        start_marker = "#! -------------------------------------------------------------------------------------Don't change above this line---------------------------------------------------------------------------"
        end_marker   = "#! -------------------------------------------------------------------------------------Don't change under this line---------------------------------------------------------------------------"

        # Create a regex pattern to extract the content between the start and end markers
        section_pattern = start_marker + r"\s*(.*?)\s*" + end_marker

        # DOTALL allows '.' to match newlines
        section_match   = re.search(section_pattern, content, re.DOTALL)

        # Warn and return empty dictionary if the section was not found
        if not section_match:
            print("Warning: No assignements were made in scriptbody !")
            return {}

        # Extract the content of the section
        section_content     = section_match.group(1)

        # Split the section content into individual lines
        lines               = section_content.split('\n')

        # Counter to create sequential dictionary keys
        mapping_counter     = 1

        # Process each line in the extracted section
        for line in lines:

            # Remove leading/trailing whitespace
            line = line.strip()

            # Skip empty lines, comments, or lines without assignment
            if not line or line.startswith('#') or '=' not in line: continue

            # Split the line into left-hand side (variable) and right-hand side (value/expression)
            left, right = line.split('=', 1)
            left        = left.strip()          # Trim whitespace from LHS
            right       = right.strip()         # Trim whitespace from RHS

            # Match the left-hand side variable path starting with 'mdlVars'
            path_match  = re.search(r"mdlVars(.*?)$", left)

            # Skip if LHS does not contain mdlVars
            if not path_match:continue

            # Extract the variable path after 'mdlVars'
            path        = path_match.group(1)

            # Initialize full path starting with 'mdlVars'
            full_path   = 'mdlVars'

            # Convert indexing like ['Common']['Thermal'] to dot notation
            for part in re.findall(r"\[['\"](.*?)['\"]\]", path):    full_path += f'.{part}'

            # Convert Python-style 'mdlVars' path to Octave simStruct.ModelVars path
            if full_path.startswith('mdlVars.'):
                octave_path = 'simStruct.ModelVars.' + full_path[8:]  # Remove 'mdlVars.' prefix
            else:
                octave_path = 'simStruct.ModelVars.' + full_path      # Otherwise, pre append full prefix

            # ---------- Handle derived parameters containing other mdlVars references ----------
            if re.search(r"mdlVars(\[['\"].*?['\"]\])+", right):

                expr = right                        # Store the right-hand side expression
                expr = expr.replace('**', '^')      # Convert Python exponent '**' to Octave '^'

                # ---------- Handle dp.mdlVars (external module reference) ----------
                if 'dp.mdlVars' in expr:

                    def replace_dp(match):

                        # Extract the keys inside brackets, like  ['Common']['Thermal']
                        parts   = re.findall(r"\[['\"](.*?)['\"]\]", match.group(0))

                        # Start from the dp.mdlVars module
                        val     = dp.mdlVars

                        for p in parts:
                            val = val[p]    # Traverse nested dictionaries
                        return str(val)     # Return the actual value as string

                    # Replace all dp.mdlVars[...] occurrences in the expression with actual values
                    expr = re.sub(r"dp\.mdlVars(\[['\"].*?['\"]\])+", replace_dp, expr)

                # ---------- Handle mapVars references inside derived expression ----------

                mapvar_pattern  = r"mapVars\[X(\d+)\](?:\[(\d+)\])?"
                all_matches     = list(re.finditer(mapvar_pattern, expr))

                for match in all_matches:
                    x_num   = match.group(1)    # Which X variable
                    idx1    = match.group(2)    # Optional index inside X (for wca)

                    # Replace with appropriate Octave data reference depending on mapvars dimension
                    if mapvars_dim == 3:
                        replacement = f"data{{sim}}{{{x_num}}}({int(idx1)+1 if idx1 else 1})"
                    else:
                        replacement = f"data(sim,{x_num})"

                    # Build original string to replace
                    original    = f"mapVars[X{x_num}]" + (f"[{idx1}]" if idx1 else "")
                    expr        = expr.replace(original, replacement)  # Replace in expression

                # ---------- Handle other mdlVars references in derived expression ----------

                dep_pattern = r"mdlVars(\[['\"].*?['\"]\])+"  # Regex for remaining mdlVars

                def replace_dep(match):
                    dep_path    = match.group(0)
                    dep_parts   = re.findall(r"\[['\"](.*?)['\"]\]", dep_path)
                    return 'simStruct.ModelVars.' + '.'.join(dep_parts)

                expr = re.sub(dep_pattern, replace_dep, expr)

                # Save the final mapping in the dictionary with sequential key
                mappings[mapping_counter]    = f"{octave_path} = {expr}"
                mapping_counter             += 1

            # ---------- Handle simple mapVars assignments ----------

            else:
                mapvar_pattern  = r"mapVars\[X(\d+)\](?:\[(\d+)\])?"
                all_matches     = list(re.finditer(mapvar_pattern, right))

                if not all_matches  : continue  # Skip if no mapVars found

                expr = right                    # Start with RHS
                expr = expr.replace('**', '^')  # Convert Python exponent '**' to Octave '^'

                # Replace all mapVars references with Octave data access
                for match in all_matches:

                    x_num   = match.group(1)
                    idx1    = match.group(2)

                    if mapvars_dim == 3:
                        replacement = f"data{{sim}}{{{x_num}}}({int(idx1)+1 if idx1 else 1})"
                    else:
                        replacement = f"data(sim,{x_num})"

                    original    = f"mapVars[X{x_num}]" + (f"[{idx1}]" if idx1 else "")
                    expr        = expr.replace(original, replacement)

                # Save mapping to dictionary
                mappings[mapping_counter]    = f"{octave_path} = {expr}"
                mapping_counter             += 1

        return mappings

    def dict_to_struct(self,d):
        """
        Recursively converts a nested dictionary to Octave struct syntax.

        *Args:
            d  (dict) : A nested dictionary representing the structure

        !Returns:
                (str) : A string containing Octave struct creation code
        """

        # Initialize list to store key-value pairs for struct creation
        items           = []

        # Iterate through all key-value pairs in the dictionary
        for key, value in d.items():

            # Check if the value is another dictionary (nested structure)
            if isinstance(value, dict):

                # Recursively convert nested dictionary to struct syntax
                nested  = self.dict_to_struct(value)

                # Add the nested struct to items list
                items.append(f"'{key}', {nested}")

            elif isinstance(value, str):

                # Handle string values (wrap in quotes)
                items.append(f"'{key}', '{value}'")

            else:

                # Leaf node with numeric value (or other type)
                items.append(f"'{key}', {value}")

        # Check if there are no items in the dictionary
        if not items:

            # Return empty struct for empty dictionary
            return 'struct()'

        # Return complete struct creation string with all items
        return f"struct({', '.join(items)})"

    def inject_octave(self,plecs_file_path, output_file_path, m_file_path,solveropts):
        """
        Reads Octave code from an .m file and injects it into the PLECS file.

        *Args:
            plecs_file_path     (str)  : Path to the source .plecs file
            output_file_path    (str)  : Path to the output .plecs file
            m_file_path         (str)  : Path to the .m file containing the Octave script
            solveropts          (dict) : SolverOpts dictionary
        """

        # Read the entire content of the PLECS file into a string
        with open(plecs_file_path, 'r') as f: content   = f.read()

        # Read the entire Octave script code into a string
        with open(m_file_path, 'r') as f:octave_code    = f.read()

        # Read the entire content of the PLECS file
        with open(plecs_file_path, 'r') as f:
            content = f.read()

        #? SolverOpts injection sub-routine-------------------------------------------
        key_map = {
            #* SolverOpts(key)  : plecs(key)
            #*--------------------------------
            'StartTime'         : 'StartTime'           ,
            'TimeSpan'          : 'TimeSpan'            ,
            'Timeout'           : 'Timeout'             ,
            'MaxStep'           : 'MaxStep'             ,
            'FixedStep'         : 'FixedStep'           ,
            'RelTol'            : 'RelTol'              ,
            'Refine'            : 'Refine'              ,
            'ZeroCross'         : 'MaxConsecutiveZCs'   , #! this is not originally in SolverOpts but it is added in input_vars.json

        }

        for key, plecs_key in key_map.items():

            if key not in solveropts    :   continue

            # Format the value: strings get quotes
            formatted                   =   f'"{solveropts[key]}"'

            # Replace existing parameter line
            pattern                     =   rf'({plecs_key}\s+)(".*?"|\S+)'
            replacement                 =   rf'\g<1>{formatted}'

            if re.search(pattern, content):
                content     = re.sub(pattern, replacement, content)
            else:
                print("solver parameter not found in model ")

        # Write the modified content to the output file
        with open(output_file_path, 'w') as f:  f.write(content)

        #? Octave script injection sub-routine-------------------------------------------
        # Replace backslashes with double backslashes and double quotes with escaped double quotes
        escaped_code        = octave_code.replace('\\', '\\\\').replace('"', '\\"')

        # Create the new script section in PLECS XML-like format
        new_script_section  = f'''  Script {{
        Name          "{dp.JSON["scriptName"]}"
        Script        "{escaped_code}"
    }}'''

        # CASE 1: Check for empty script section pattern : Script { Name "Script" Script "" }
        empty_script_pattern = r'Script\s*{\s*Name\s+"Script"\s*Script\s+""\s*}'

        # Search for empty script pattern in the content
        if re.search(empty_script_pattern, content, re.DOTALL):

            # Replace the empty script section with the new populated script section
            new_content = re.sub(empty_script_pattern, new_script_section, content, flags=re.DOTALL)

        # CASE 2: Check for any existing script section
        elif re.search(r'Script\s*{.*?}', content, re.DOTALL):

            # Find all script sections in the content
            script_sections = list(re.finditer(r'Script\s*{.*?}', content, re.DOTALL))

            # Get the last script section found
            last_script     = script_sections[-1]

            # Get the end position of the last script section
            insert_pos      = last_script.end()

            # Insert new script section after the last existing script section
            new_content     = content[:insert_pos] + '\n' + new_script_section + content[insert_pos:]

        # CASE 3: No script section found at all in the file
        else:

            # Find the position of the last closing brace in the file
            last_brace_pos  = content.rfind('}')

            # Check if a closing brace was found
            # Insert new script section before the final closing brace
            new_content     = content[:last_brace_pos] + '\n' + new_script_section + content[last_brace_pos:]

        # Write the modified content back to the output PLECS file
        with open(output_file_path, 'w') as f: f.write(new_content)

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------