
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                            ______   ______  _     _____ ____ ____        ____  ____   ____
#?                                           |  _ / / / /  _ /| |   | ____/ ___/ ___|      |  _ /|  _ / / ___|
#?                                           | |_) / V /| |_) | |   |  _|| |   /___ / _____| |_) | |_) | |
#?                                           |  __/ | | |  __/| |___| |__| |___ ___) |_____|  _ <|  __/| |___
#?                                           |_|    |_| |_|   |_____|_____/____|____/      |_| /_/_|    /____|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import assets.Dependencies as dp

#Calling on Enviromment variables
for key in ["HTTP_PROXY", "HTTPS_PROXY"]:
    if key in list(dict(dp.os.environ).keys()):dp.os.environ.pop(key)
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class PlecsRPC:
    def __init__(self,url,port,mdlVars,slvOpts,anlOpts,METHOD="JSON") :
        """
        PlecsRPC Constructor to initialize global variables.

        *Args:
            url         (string)        : Could be a local address, an ip adress  or a link : http//:127.0.0.1 for localhost.
            port        (string)        : Port to connect to the xmlrpc server over.
            path        (string)        : String leading to the path of the model.
            mdlVars     (dictionary)    : Dictionary to specify variable values.
            solverOpts  (dictionary)    : Dictionary to specify solver settings.
            METHOD      (string)        : RPC connection medium, XML or JSON.
        """

        self.url                        =   url                                  # Host Local address    : http://localhost
        self.port                       =   port                                 # Port to connect over  : exemple 61677, default is 1080
        self.mdlVars                    =   mdlVars                              # Assign Parameters Dictionary "Modelvars"
        self.slvOpts                    =   slvOpts                              # Assign Parameters Dictionary "SolverOpts"
        self.anlOpts                    =   anlOpts                              # Assign Parameters Dictionary "AnalysisOpts"
        self.OptStruct                  =   []                                   # Initialize simulation parameters vector
        self.METHOD			            =   METHOD				                 # Desired RPC connection medium. Default is JSON. Alternative is XML.
        self.path                       =   ''                                   # Path to the plecs model file

    def optStruct(self,instances=1,iteration_range=[0],parallel=False):
        """
        Reconstructs the simstruct for the model
        based on the modelvar and solveropt dictionaries
        passed in from the local dependecies.

        *Args:
            instances (int)       : Number of instances to be generated, default is 1.
            parallel  (bool)      : Flag to indicate if parallel simulations will be performed.
        """

        # if only one instance is required and parallel simulations are not needed
        # return a single dictionary containing the model variables, solver options, analysis options and name
        if (instances == 1 and not parallel):
            self.OptStruct  =   {'ModelVars':self.mdlVars, 'SolverOpts':self.slvOpts, 'AnalysisOpts':self.anlOpts, 'Name':'Iter_1'}
            return

        # if multiple instances are required or parallel simulations are needed
        # create a list of dictionaries containing the model variables, solver options, analysis options and name
        # each dictionary corresponds to one instance of the simulation
        mdl_list        =   [dp.copy.deepcopy(self.mdlVars) for _ in range(instances)]
        slv_list        =   [dp.copy.deepcopy(self.slvOpts) for _ in range(instances)]
        anl_list        =   [dp.copy.deepcopy(self.anlOpts) for _ in range(instances)]
        nms_list        =   ["Iter_"+str(iteration_range[i]+1) for i in range(len(iteration_range))]
        self.OptStruct  =   [{'ModelVars':mdl_list[x],'SolverOpts':slv_list[x],'AnalysisOpts':anl_list[x], 'Name':nms_list[x]} for x in range(instances)]

    def PlecsConnect(self):
        """
        Establishes a connection to a Plecs simulation running on a remote server
        using either XML-RPC or JSON-RPC protocol.

        *Args:
            url         (str)       : the URL of the remote server running the Plecs simulation
            port        (str)       : the port number used for the XML-RPC or JSON-RPC connection
            METHOD      (str)       : the protocol used for the connection, either "XML" or "JSON"
            server      (object)    : the server object used for the XML-RPC or JSON-RPC connection

        """

        # set connection parameters
        url           =   self.url
        port          =   self.port

        # import RPC module based on the desired connection method and
        # establish connection to the plecs server using the specified method
        # raise an exception if the connection cannot be established
        if self.METHOD == "JSON":
            #? Will be removed once python version upgraded above 3.10.8
            for _name in ("Mapping", "MutableMapping", "Callable", "Iterable","Iterator", "Sequence", "MutableSequence", "Set"):
                if not hasattr(dp.collections, _name): setattr(dp.collections, _name, getattr(dp.collections.abc, _name))

            self.server  = dp.jsonrpc_requests.Server(url + ":" + port)

        elif self.METHOD == "XML":
            self.server  = dp.xmlrpc.client.Server(url + ":" + port)

    def Open_Model(self, modelname):
        """
        this function takes the name of the model and searches for the
        corresponding Plecs model then opens it before the simulation.


        *Args:
            modelname (string)       : The name of the plecs model.
        """

        # get pyplecs root directory
        root_dir            = dp.os.getcwd()

        # folders to exclude from top-level folders parsing
        excluded_folders    = ["Script","Thermal Models","MyLibraries","FMU","wheelhouse","venv","build","PyPLECS.egg-info"]

        # Build allowed top-level paths with root project level folder included
        allowed_dirs        = [
                                # crawl project directory and list sub directories
                                dp.os.path.join(root_dir, d) for d in dp.os.listdir(root_dir)
                                # with the condition that it is an actual folder not a file and is not from the excluded folders
                                if dp.os.path.isdir(dp.os.path.join(root_dir, d)) and d not in excluded_folders
                                # add pyplecs root dir in case a loose model is added there
                                ] + [root_dir]

        # Flatten all matches into one list
        all_matches         = sum((dp.glob.glob(p, recursive=True) for p in [dp.os.path.join(d, "**", "*.plecs") for d in allowed_dirs]), [])

        # Case-insensitive filter to find matches
        model_path          = next((p for p in all_matches if dp.os.path.basename(p).lower() == modelname.lower()),None)

        if model_path:
            self.path       = model_path
            dp.cp_mdl       = model_path
            dp.os.startfile(model_path)
            dp.scopes       = self.PlecsScopes(self.path)
        else:
            print("Check the model name please.")
            dp.os._exit(0)

    def LoadModel(self,path):
        """
        Loads the PLECS model file specified by the path.

        *Args   :
            path (str)  :   string that represents the path to the PLECS model file.

        !Returns:
            If the path is valid and refers to a PLECS file, the model will be loaded over the XML-RPC server.Otherwise, it returns an error message.
        """

        # get the file extension of the path
        # if the path is valid and refers to a plecs file load it over the xmlrpc server otherwise print an error message
        ext = dp.os.path.splitext(path)[-1].lower()
        if (path is not None) and (ext == ".plecs"):
            try :
                self.server.plecs.load(path)
            except Exception as e:
                return e
        else:
            print('Simulation Path is invalid or Empty')

    def LaunchSim(self,instances,path,parallel=False,callback=""):
        """
        Launches a simulation using the given path to the simulation model file.

        *Args   :
            path (str)  : The path to the simulation model file.

        !Returns:
            dict        : A dictionary containing the results of the simulation, including the time values and the corresponding simulated values.
        """

        # Extract the model name from the given path and launch the simulation
        # if only one instance is required and parallel simulations are not needed
        # launch the simulation without a callback function
        # otherwise, launch the simulation with a callback function
        SIM_NAME     =  dp.os.path.split(path)
        modelname    =  (list(SIM_NAME)[-1]).split('.')[0]

        if (instances == 1 and not parallel)    :   results =   self.server.plecs.simulate(modelname,self.OptStruct)
        else                                    :   results =   self.server.plecs.simulate(modelname,self.OptStruct,callback)

        return results

    def LaunchAnalysis(self,instances,path,analysisName,parallel=False,callback=""):
        """
        Interfaces with Plecs and launches the analysis.

        *Args   :
            path            (str)           : the path to the Plecs simulation file to be analyzed.
            analysisName    (str, optional) : the name of the analysis to be launched. Defaults to 'Steady_State_Analysis'.

        !Returns:
            Any                             : the results of the analysis, which may vary depending on the type of analysis.

        """

        # Extract the model name from the given path and launch the analysis
        # and if only one instance is required and parallel simulations are not needed
        # launch the analysis without a callback function
        # otherwise, launch the analysis with a callback function
        SIM_NAME     =  dp.os.path.split(path)
        modelname    =  (list(SIM_NAME)[-1]).split('.')[0]

        if (instances == 1 and not parallel)    :   results =   self.server.plecs.analyze(modelname,analysisName,self.OptStruct)
        else                                    :   results =   self.server.plecs.analyze(modelname,analysisName,self.OptStruct,callback)

        return results

    def CloseModel(self,path):
        """
        Close a PLECS model file.

        *Args   :
            path (str)  : The path to the PLECS model file that should be closed.

        """

        # Close the plecs model specified by the path over the xmlrpc server
        self.server.plecs.close(path)

    def ClearTrace(self, modelname, scopes):
        """
        Clears the traces for specified scopes in a given model.

        *Args   :
            modelname   (str)   : The name of the model, which may include a file extension.
            scopes      (list)  : A list of scope names within the model whose traces should be cleared.
        """

        # Extract the base model name by removing any file extension
        # Attempt to clear traces for each specified scope
        # Silently ignore any errors that occur during the clearing process
        modelname = (modelname.split('.'))[0]

        try:
            for scope in scopes:
                self.server.plecs.scope(modelname+'/'+scope, 'ClearTraces')
        except:
            pass

    def SaveTraces(self, modelname, scopes, path):
        """
        Saves trace data from specified scopes to a designated directory.

        *Args   :
            modelname   (str)   : The name of the model, which may include a file extension.
            scopes      (list)  : A list of scope names within the model whose traces should be saved.
            path        (str)   : The base directory path where the trace files will be saved.
        """

        # Ensure the target directory exists
        # Create a subdirectory named 'Scopes_Traces' within the specified path
        # Extract the base model name by removing any file extension
        # Attempt to save traces for each specified scope to the designated directory
        # Silently ignore any errors that occur during the saving process
        modelname   = (modelname.split('.'))[0]
        path        = path + '/Scopes_Traces'

        try:
            for scope in scopes:
                self.server.plecs.scope(modelname+'/'+scope, 'SaveTraces', path+'/'+scope.replace("/", "_"))
        except:
            pass

    def holdTrace(self, modelname, scopes):
        """
        Holds (pauses) the tracing for specified scopes in a given model.

        *Args   :
            modelname   (str)   : The name of the model, which may include a file extension.
            scopes      (list)  : A list of scope names within the model whose tracing should be paused.

        """

        # Extract the base model name by removing any file extension
        # Attempt to hold traces for each specified scope
        # Silently ignore any errors that occur during the process
        modelname = (modelname.split('.'))[0]

        try:
            for scope in scopes:
                self.server.plecs.scope(modelname+'/'+scope, 'HoldTrace')
        except:
            pass

    def holdTraceCallback(self, scopes):
        """
        Generates a callback script for holding traces of specified scopes.

        *Args   :
            scopes (list)   : A list of scope names for which the hold trace callback should be generated.

        !Returns:
            str             : A string containing the PLECS callback script with commands to hold traces for all specified scopes.
        """

        # Generate a PLECS callback script to hold traces for the specified scopes
        # Return the generated script as a string
        # Each scope will have a command to hold its trace
        callback = """"""
        if not dp.scopes == [None] :
            for scope in scopes:
                callback = callback + f"plecs('scope', './{scope}', 'HoldTrace', name);"

        return callback

    def modelinit_opts(self,maxThreads=1,iteration_range=[0],parallel=False):
        """
        Initialize simulation options and prepare for parallel execution if enabled.

        This method configures the simulation environment by setting up thread structures
        for parallel processing, establishing connection to the PLECS model, and loading
        the model for simulation. It includes a brief delay to ensure proper initialization
        before attempting to connect.

        *Args   :
            maxThreads      (int)   : Maximum number of threads to use for parallel simulation.Defaults to 1
            iteration_range (list)  : Range of iterations to simulate. Defaults to [0].
            parallel        (bool)  : Flag indicating whether to enable parallel execution.Defaults to False.
        """

        # Set up thread structures for parallel execution if enabled
        # Establish connection to the PLECS model
        # Load the PLECS model for simulation
        # Include a brief delay to ensure proper initialization before connecting
        self.optStruct(maxThreads,iteration_range,parallel)
        dp.time.sleep(5)
        self.PlecsConnect()
        self.LoadModel(self.path)

    def PlecsScopes(self,model_path):
        """
        Get the list of scopes in a given plecs model.

        *Args   :
            model_path (str)    : path of the current plecs model.

        !Returns:
            List                : _description_
        """
        #?----------------------------------
        #? NO SCOPES
        #?----------------------------------
        if dp.JSON["scopes"] == [None]  :   scopes = []

        #?----------------------------------
        #? ALL SCOPES
        #?----------------------------------
        elif dp.JSON["scopes"] == [] :

            # get plecs model tree
            tree    = dp.json.loads(dp.base64.b64decode(self.server.plecs.getModelTree(model_path)).decode('utf-8'))

            # List to store the full paths of all scopes
            scopes  = []

            # Recursive scan function
            def scan(node, path=""):
                """
                Recursively scan nodes and build paths.

                *Args:
                    node (obj)          : node is a plecs xml dictionary block or property
                    path (str, optional): node or component kind path. Defaults to "".
                """
                if isinstance(node, dict):                      # If node is a dictionary (block or property)
                    name            = node.get("name", "")      # Get block name, default empty string
                    kind            = node.get("kind", "")      # Get kind of element :  'circuit', 'scope'

                    # Build full path by appending current node name
                    current_path    = f"{path}/{name}" if path else name

                    # If node represents a scope, add it to the scopes list
                    if kind.lower() == "scope" or node.get("type") == "Scope":scopes.append(current_path)

                    # Recursively scan all children nodes
                    for child in node.get("children", []):scan(child, current_path)

                # If node is a list of nodes
                elif isinstance(node, list):
                    # Recursively scan each item
                    for item in node    :   scan(item, path)

            # Start scanning from the root of the tree
            scan([tree] if isinstance(tree, dict) else tree)

            # Return collected scopes
            scopes = [s.replace("\\", "/").split("/")[-1] for s in scopes]

        #?----------------------------------
        #? SELECTED SCOPES
        #?----------------------------------
        else    :   scopes = dp.JSON["scopes"]

        return scopes

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------