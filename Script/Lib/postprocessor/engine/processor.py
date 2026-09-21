
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
    Simple linear processor: executes all processes in its process list one after another,
    against the same context, in the order they were given.

    *Args:
        processes (list[IProcess])  :   Ordered list of already-built IProcess instances to run, in order, on each process() call.
    """
    def __init__(self, processes: list[IProcess]):
        self.processes = processes

    def process(self,context):
        """
        Run every process in self.processes, in order, against the given context.

        *Args:
            context (ProcessContext)    :   Unified context carrying the raw data to process and the
                                            result repository each process writes its output into.
        """
        for process in self.processes:
            process.execute(context)
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
