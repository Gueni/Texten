
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
    Processor interface

    """
    @abstractmethod
    def process(self, context):
        """
        Used to execute the process code using the context data

        *Args:
            context (obj) : unified context for each prossess containing the data to be processed
        """
        pass

class IProcess(ABC):
    """
    Process interface

    """
    @abstractmethod
    def execute(self, context):
        """
        Used to execute the process code using the context data

        *Args:
            context (obj)   :   Unifyed context for each prossess containing the data to be processed
        """
        pass
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------