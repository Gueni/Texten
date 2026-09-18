
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                   ____  ____   ___   ____ _____ ____ ____   ___  ____
#?                                                  |  _ \|  _ \ / _ \ / ___| ____/ ___/ ___| / _ \|  _ \
#?                                                  | |_) | |_) | | | | |   |  _| \___ \___ \| | | | |_) |
#?                                                  |  __/|  _ <| |_| | |___| |___ ___) |__) | |_| |  _ <
#?                                                  |_|   |_| \_\\___/ \____|_____|____/____/ \___/|_| \_\
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from Lib.postprocessor.core.interfaces import IProcess, IProcessor
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

class LinearProcessor(IProcessor):
    """
    Simple linear processor. Executes all processes in its process dict one after another.

    *Attributes:
        self.processes (dict)   :   List of processes to be processed

    ?Methods   :
        process(self, context)  :   Used to run the processor, runs each process in self.processes one after another
    """
    def __init__(self, processes: list[IProcess]):
        self.processes = processes

    def process(self,context):
        """
        Method to executes all processes in its process dict one after another.

        *Args:
            context (ProcessContext)    :   Unified context for each prossess containing the data to be processed
        """
        for process in self.processes:
            process.execute(context)
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
