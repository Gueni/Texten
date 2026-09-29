
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                           ___ _   _ _____ _____ ____  _____ _    ____ _____ ____
#?                                          |_ _| \ | |_   _| ____|  _ \|  ___/ \  / ___| ____/ ___|
#?                                           | ||  \| | | | |  _| | |_) | |_ / _ \| |   |  _| \___ \
#?                                           | || |\  | | | | |___|  _ <|  _/ ___ \ |___| |___ ___) |
#?                                          |___|_| \_| |_| |_____|_| \_\_|/_/   \_\____|_____|____/
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from abc import ABC, abstractmethod
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class IProcessor(ABC):
    """
    Processor interface: the thing that actually runs a set of processes against a context.
    LinearProcessor is the concrete (and currently only) implementation -- it just runs every
    registered IProcess in order. Never instantiated directly.
    """
    @abstractmethod
    def process(self, context):
        """
        Run every process this processor knows about against the given context.

        *Args:
            context (ProcessContext) : Unified context carrying the raw data to process and the
                                       result repository each process writes its output into.
        """
        pass

class IProcess(ABC):
    """
    Process interface: one individual calculation step (e.g. absolute max, FFT, dissipation).
    Concrete processes implement execute() and self-register into ProcessRegistry via a
    @ProcessRegistry.register("NAME") decorator -- see post_process.py for the concrete processes.
    Never instantiated directly.
    """
    @abstractmethod
    def execute(self, context):
        """
        Run this one process's calculation against the given context, writing its result into
        context.result_repository under this process's own result name.

        *Args:
            context (ProcessContext) : Unified context carrying the raw data to read from and the
                                       result repository to write this process's output into.
        """
        pass
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------