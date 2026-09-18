
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                           ____  ____   ___   ____ _____ ____ ____   ___  ____     ____  _   _ ___ _     ____  _____ ____
#?                          |  _ \|  _ \ / _ \ / ___| ____/ ___/ ___| / _ \|  _ \   | __ )| | | |_ _| |   |  _ \| ____|  _ \
#?                          | |_) | |_) | | | | |   |  _| \___ \___ \| | | | |_) |  |  _ \| | | || || |   | | | |  _| | |_) |
#?                          |  __/|  _ <| |_| | |___| |___ ___) |__) | |_| |  _ <   | |_) | |_| || || |___| |_| | |___|  _ <
#?                          |_|   |_| \_\\___/ \____|_____|____/____/ \___/|_| \_\  |____/ \___/|___|_____|____/|_____|_| \_\
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

from    dataclasses         import field
import  json
import  numpy               as np
import  assets.Dependencies as dp

from Lib.postprocessor.core.interfaces  import IProcessor
from Lib.postprocessor.process.factory  import ProcessorFactory
from Lib.postprocessor.engine.processor import LinearProcessor
from Lib.postprocessor.core.config      import ProcessorConfig, ProcessFFTConfig, ProcessDissipationsConfig, ProcessThermalStatsConfig, ProcessSensitivityConfig
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

class ProcessorBuilder:
    """
    The processor builder is used to build the process dict as well as the processor.

    *Attributes :
        _factory        : ProcessorFactory Factory to build the process dict and assigning the correct configuration to each process
        _process_dict   : dict[IProcess]  The dict with all prcesses to be processed wher key is process name

    ?Methods    :
        _build_processor_config(dp, mode = "NONE", plecs_model = "", process_filter = []) : Internally used to build the processor config
        _init_mat_dict(res_dict, processor_cfg, iterations)                               : Internally used to pre allocate np.arrays and collect them in the mat dict
        _add_sensitivity_processes(processor_cfg, post_fix)                               : Internally used to add the sensitivity processes to the process dict
        build_processor(MAT_dict, dp, iterations, mode) -> tuple[IProcessor, dict]        : Used to build the processor and the final process dict (+ sensitivity processes)
    """
    _factory        = ProcessorFactory()
    _process_dict   : dict

    def _build_processor_config(self, dp:dp, mode:str = "NONE", plecs_model:str = "", process_filter:list[str] = []) -> ProcessorConfig:
        """
        This method initializes the porcessor config based on mode, plecs_model, process_filter and various dp parameter.
        Currently the standard process config is loaded from process_config_dcdc_s or process_config_standalone depending which model is used.

        *Args   :
            mode            (str)        : The current simulaton mode, defaults to "NONE".
            plecs_model     (str)        : The simulation model, defaults to ""
            process_filter  (list[str])  : A list of process types which will be removed from standard process config. !currently only FFT supported

        !Returns:
            ProcessorConfig              : The initialized processor configuration
        """
        process_config  = {}
        sens_pre_fix    = "_Sensitivity"

        #* Add FFT config to config dict if not filterd out
        if "FFT" not in process_filter:
            process_config.update(dict(FFT = ProcessFFTConfig(
                fund_freq  = dp.JSON["FundFreq"],
                hrmcs      = dp.JSON["hrmcs"],
                to_file_ts = dp.mdlVars['Common']['ToFile']['Ts'])))
            fft_cfg = process_config["FFT"] # temporal save for sensitivity
        else:
            fft_cfg = field(default_factory = ProcessFFTConfig) #* Temporal save for sensitivity with default value if FFT not used

        #* Add sensitivity config to config dict
        if mode == "SENSITIVITY":
            process_config.update(dict(SENSITIVITY = ProcessSensitivityConfig(
            perturbation    = dp.JSON["perturbation"],
            post_fix        = sens_pre_fix,
            fft_cfg         = fft_cfg)))

        if plecs_model == "DCDC_S" or plecs_model == "DCDC_D":
            #* Add dissipation config to config dict
            process_config.update(dict(DISSIPATIONS = ProcessDissipationsConfig(
                res_list    = [], # todo: update to give res_list as config. Currently workaround via context
                current_idx = dp.current_idx)))

            #* Add thermal stats config to config dict
            process_config.update(dict(THERMALSTATS = ProcessThermalStatsConfig(
                dcdc_d      = False,
                rail_idx    = dp.Rail_idx,
                common_idx  = dp.Common_idx,
                pout_idx    = dp.Pout_idx,
                p_aux       = 0, # todo: update to give p_aux as config. Currently workaround via context. TBC if p_aux sweep
                phase       = dp.phase)))

            #* Load process config from json for DCDC
            with open("Script\Lib\postprocessor\config\process_config_dcdc_s.json", "r") as f       :  content = f.read()
            json_config                 = json.loads(content)
            slicing                     = json_config["Slicing"]

        if plecs_model == "":
            #* Load process config from json for Standalone
            with open("Script\Lib\postprocessor\config\process_config_standalone.json", "r") as f   :   content = f.read()
            json_config                 = json.loads(content)
            slicing                     = json_config["Slicing"]
            slicing["all"]["length"]    = dp.std_length

        cfg_name            = json_config["Config_Name"]
        self.process_dict   = json_config["Processes"]

        #* Delete filter processes from process dict
        for filter in process_filter:
            process_to_remove = [k for k in self.process_dict if filter in k]
            for process in process_to_remove:
                self.process_dict.pop(process)

        return ProcessorConfig(
            sim_type     = cfg_name,
            slice_map    = slicing,
            process_dict = self.process_dict,
            process_cfg  = process_config)

    def _init_mat_dict(self, res_dict: dict, processor_cfg: ProcessorConfig, iterations: int = 0) -> ValueError:
        """
        This method initializes the mat dictionary wich holds all results of all processes
        where the key is the process name and the data is a reference to a numpy array. The numpy arrays are initialized with np.zeros()

        *Args:
            res_dict        (dict)  : Referene to an empty dict
            processor_cfg   ()      : Initialized processor config
            iterations      (int)   : Total number of itterations

        !Returns:
            ValueError              : If slice length == 0
        """
        sensitivity_len     = iterations - 1

        for current_process_name, info in processor_cfg.process_dict.items():
            processor_type  = info["processor"]
            slice_string    = info["slice"]

            if processor_type == "SENSITIVITY"  : len   = sensitivity_len
            else                                : len   = iterations

            if slice_string != "NONE":
                data_slice          = processor_cfg.slice_map.get(slice_string)
                data_slice_length   = data_slice.get("length")

                if data_slice_length != 0:
                    if "FFT" not in current_process_name:
                        res_dict[current_process_name] = np.zeros((len, data_slice_length))
                    else:
                        res_dict[current_process_name] = np.zeros((len * (processor_cfg.process_cfg["FFT"].hrmcs+1), data_slice_length))
                else:
                    print(f"Slice length not initialized in; {current_process_name}")
                    return ValueError

    def _add_sensitivity_processes(self, processor_cfg: ProcessorConfig, post_fix: str = ""):
        """
        This method adds a sensitivity process for each process in the process dict in the processor config.
        Each process is named as the original one + the post fix string

        *Args:
            processor_cfg     (ProcessorConfig)     : The processor config including the process dict.
            post_fix          (str)                 : A post fix wich is used to build the new process name.
        """
        additional_process_dict = {}

        for current_process_name, info in processor_cfg.process_dict.items():
            additional_process_dict[current_process_name+post_fix] = dict(slice=info["slice"], processor="SENSITIVITY")
        processor_cfg.process_dict.update(additional_process_dict)

    def build_processor(self, MAT_dict: dict, dp: dp, iterations: int = 0, mode: str = "") -> tuple[IProcessor, dict]:
        """
        This method builds the processor and the process dict.
        In case the mode is sesnitivity it adds the sensitivity processes to the process dict

        *Args:
            MAT_dict    (dict)  : A dictionary to store the result data
            dp          ()      : The dependency modul
            iterations  (int)   : The total number of simulation iterations
            mode        (str)   : The simulation mode like WCA or SENSITIVITY
        """
        process_filter          = []
        if not dp.JSON["FFT"]   : process_filter.append("FFT")

        processor_cfg           = self._build_processor_config(dp= dp, mode = mode, plecs_model = dp.JSON["model"], process_filter = process_filter)

        if mode == "SENSITIVITY": self._add_sensitivity_processes(processor_cfg= processor_cfg, post_fix="_Sensitivity")

        err                     = self._init_mat_dict(res_dict= MAT_dict, processor_cfg= processor_cfg, iterations= iterations)
        if err:
            exit(err)
            print(err)

        process_list            = self._factory.build_process_list(processor_cfg)

        return LinearProcessor(process_list), self.process_dict
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
