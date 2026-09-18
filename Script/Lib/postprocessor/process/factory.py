
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                              _____ _    ____ _____ ___  ______   __
#?                                                             |  ___/ \  / ___|_   _/ _ \|  _ \ \ / /
#?                                                             | |_ / _ \| |     | || | | | |_) \ V /
#?                                                             |  _/ ___ \ |___  | || |_| |  _ < | |
#?                                                             |_|/_/   \_\____| |_| \___/|_| \_\|_|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from Lib.postprocessor.core.interfaces  import IProcess
from Lib.postprocessor.core.config      import ProcessorConfig, ProcessBaseConfig
from Lib.postprocessor.process.registry import ProcessRegistry
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class ProcessorFactory():
    """
    Process factory to build the process dict and assigning the correct configuration to each process

    ?Methods:
        build_process_list(self, config) -> list[IProcess]  :   Used to build the process list
    """
    def build_process_list(self, config: ProcessorConfig) -> list[IProcess]:
        """
        This method builds the process dict and returns it

        *Args   :
            config ProcessorConfig    : Config file containing all data to set up the processor

        !Returns:
            process_list              : The process list
        """
        process_list:list[IProcess] = []

        for current_process_name, info in config.process_dict.items():
            processor_type:str      = info["processor"]
            slice_string:str        = info["slice"]
            process_dataclass       = config.process_cfg.get(processor_type)

            if not process_dataclass:
                process_dataclass   = ProcessBaseConfig()

            process_dataclass.process_name = current_process_name
            if slice_string != "NONE":
                process_dataclass.data_slice = config.slice_map.get(slice_string)
                process_dataclass.data_slice = eval(process_dataclass.data_slice.get("slice", slice(None)))

            if processor_type != "NONE":
                initialized_process          = ProcessRegistry.create(processor_type, config = process_dataclass)
                process_list.append(initialized_process)

        return process_list
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
