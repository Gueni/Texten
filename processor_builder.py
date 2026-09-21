
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
    Builds a ready-to-run processor for one simulation run: reads the JSON process config for
    the active model, assembles a ProcessorConfig, pre-allocates the result arrays, and hands
    back a LinearProcessor loaded with the concrete IProcess instances it needs to run.
    """
    _factory        = ProcessorFactory()
    _process_dict   : dict

    def _build_processor_config(self, dp:dp, mode:str = "NONE", plecs_model:str = "", process_filter:list[str] = []) -> ProcessorConfig:
        """
        Initializes the processor config based on mode, plecs_model, process_filter and various dp values.
        Currently the standard process config is loaded from process_config_dcdc_s.json or
        process_config_standalone.json depending on which model is used.

        *Args   :
            dp              (module)      : The Dependencies module, read here for JSON/mdlVars and the handful
                                            of run-state indices (current_idx, Rail_idx, Common_idx, Pout_idx, phase, std_length).
            mode            (str)         : The current simulaton mode, defaults to "NONE".
            plecs_model     (str)         : The simulation model, defaults to ""
            process_filter  (list[str])   : A list of process types which will be removed from standard process config. !currently only FFT supported

        !Returns:
            ProcessorConfig               : The initialized processor configuration
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
        Initializes the mat dictionary which holds all results of all processes, where the key is the
        process name and the value is a numpy array (pre-allocated with np.zeros()) that each process
        writes its per-iteration result into.

        *Args:
            res_dict        (dict)            : Empty dict to populate in place, keyed by process name.
            processor_cfg   (ProcessorConfig) : Initialized processor config (process_dict + slice_map).
            iterations      (int)             : Total number of iterations.

        !Returns:
            None normally. Returns the ValueError class itself (not raised, not instantiated) if any
            process's configured slice has length 0 -- see build_processor(), which checks this
            return value for truthiness and calls exit() on it.
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
        Adds a sensitivity process for each process already in processor_cfg's process dict, named
        as the original process name plus post_fix, sharing the same slice but processed as "SENSITIVITY".

        *Args:
            processor_cfg     (ProcessorConfig)     : The processor config including the process dict, updated in place.
            post_fix          (str)                 : Suffix appended to each original process name to build the new sensitivity process's name.
        """
        additional_process_dict = {}

        for current_process_name, info in processor_cfg.process_dict.items():
            additional_process_dict[current_process_name+post_fix] = dict(slice=info["slice"], processor="SENSITIVITY")
        processor_cfg.process_dict.update(additional_process_dict)

    def build_processor(self, MAT_dict: dict, dp: dp, iterations: int = 0, mode: str = "") -> tuple[IProcessor, dict]:
        """
        Builds the processor and the process dict end to end: reads the process config, adds
        sensitivity processes if mode is "SENSITIVITY", pre-allocates the result arrays, and
        builds the concrete process instances via ProcessorFactory.

        ?NOTE:
            If _init_mat_dict finds a misconfigured (zero-length) slice, this calls exit(err) --
            the print(err) line right after it is unreachable, since exit() already raises SystemExit.

        *Args:
            MAT_dict    (dict)   : Empty dict to be populated with one pre-allocated numpy array per process.
            dp          (module) : The Dependencies module, forwarded to _build_processor_config().
            iterations  (int)    : The total number of simulation iterations.
            mode        (str)    : The simulation mode, e.g. "WCA" or "SENSITIVITY".

        !Returns:
            tuple[IProcessor, dict] : (processor, process_dict) -- the ready-to-run LinearProcessor,
                                      and the final process dict (including any sensitivity processes added).
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
