
        self.copyfiles()

    def copy_model_folder_files(self, model_folder):
        """
        Copies the model file and every file generated alongside it in model_folder -- the .plecs
        model itself, plus whatever PLECS Coder / the A2L-INCA merge produced there (.elf, .a2l,
        .c/.h if codegen_only, the INCA-adapted .a2l, ...) -- into resultfolder/RT_BOX_CODEGEN.

        ?NOTE:
            Flat, one level only: every entry in model_folder that's a file gets copied, but
            subfolders are skipped entirely, not recursed into -- deliberately not
            shutil.copytree(), which would pull in subfolders too.

            model_folder can hold other models' .plecs files too (a shared folder, not one
            dedicated to just this model) -- those are specifically excluded by name, compared
            case-insensitively against dp.cp_mdl's own filename, same as Open_Model()'s own
            matching. Only .plecs files are filtered this way: every non-.plecs file is assumed to
            be this run's own generated output (named after this model, e.g. Boost_integrated.elf)
            and is copied regardless of name.

        *Args:
            model_folder (str) : Folder to copy files from -- the model's own folder,
                                 i.e. os.path.dirname(dp.cp_mdl).
        """
        dest                =   os.path.join(self.resultfolder, "RT_BOX_CODEGEN")
        os.makedirs(dest, exist_ok=True)

        current_model_name  =   os.path.basename(dp.cp_mdl).lower()

        for name in os.listdir(model_folder):
            src = os.path.join(model_folder, name)
            if not os.path.isfile(src):
                continue
            if name.lower().endswith(".plecs") and name.lower() != current_model_name:
                continue  # a different model's .plecs file sharing this folder -- skip it
            shutil.copy(src, os.path.join(dest, name))

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

        # Copy all directories (dirs_exist_ok=True: a re-run/retry during testing shouldn't fail
        # just because the destination already exists from a previous attempt)
        for src, dst ,cond  in dirs_to_copy    :
            if cond :   shutil.copytree(src, dst, dirs_exist_ok=True)

        # RT Box codegen run: the model file itself plus whatever PLECS Coder (and the A2L/INCA
        # merge) generated alongside it -- .elf, .c/.h if codegen_only, .a2l and its INCA-adapted
        # copy, etc. Flat copy only: files directly in the model's folder, no subfolders recursed
        # into (unlike the shutil.copytree() dirs above).
        if dp.JSON.get("RT", False):
            self.copy_model_folder_files(os.path.dirname(dp.cp_mdl))

        # Fix headers : replace spaces with _ ...
        self.fix_json_strings(os.path.join(self.resultfolder, "Headers"))
