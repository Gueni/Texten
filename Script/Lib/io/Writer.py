
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                      __        ______  ___ _____ _____ ____
#?                                                      \ \      / /  _ \|_ _|_   _| ____|  _ \
#?                                                       \ \ /\ / /| |_) || |  | | |  _| | |_) |
#?                                                        \ V  V / |  _ < | |  | | | |___|  _ <
#?                                                         \_/\_/  |_| \_\___| |_| |_____|_| \_\
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from    abc         import  ABC         , abstractmethod
from    dataclasses import  dataclass   , field
import  pandas      as      pd
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class OutputContext:
    """
    _summary_

    """
    path    : str   = ""
    data    : list  = field(default_factory=list)
    mode    : str   = "w"

class IWriter(ABC):
    """
    _summary_

    *Args:
        ABC (_type_)    : _description_
    """
    @abstractmethod
    def write(self, context: OutputContext):
        """
        _summary_

        *Args:
            context (OutputContext) : _description_
        """
        pass

class CSVWriter(IWriter):
    """
    _summary_

    *Args:
        IWriter (_type_)    : _description_
    """
    def write(self, context: OutputContext):
        """
        Append the provided ND data array as a row to the specified CSV file.

        *Args   :
            fileName    (str)       :   The name of the CSV file to which the data will be appended.
            data        (list)      :   The ND data array to be appended.
            save_mode   (str)       :   Optional argument specifying the file open mode. Default value is 'a'
                                        which appends data to the end of the file. To overwrite the file, set save_mode to 'w'.

        !Raises :
            TypeError               : If the provided data is not a list.
            ValueError              : If the provided data is an empty list.
        """

        # Validate that 'data' is a list; raise an error if not.
        if not isinstance(context.data, list)   :   raise TypeError("data should be a list.")

        # Validate that the list is not empty; raise an error if it is.
        if len(context.data) == 0               :   raise ValueError("data list cannot be empty.")

        # Check if all elements in the data list are themselves lists.
        # If so, create a DataFrame directly from the list of lists.
        # Otherwise, transpose the data to align it as columns in the DataFrame.
        if all(isinstance(i, list) for i in context.data)   :   df = pd.DataFrame(list(context.data))
        else                                                :   df = pd.DataFrame(context.data).T

        # Write the DataFrame to a CSV file with the specified mode, without headers or index.
        df.to_csv(context.path+f".csv", mode=context.mode, index=False, header=False)
        return context

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
