
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
    Shared, mutable context passed into every IWriter.write() call: where to write to, what to
    write, and how to open the target file.

    *Args:
        path (str)   :   Destination path, without its extension (writers append it themselves). Defaults to "".
        data (list)  :   The data to write out. Defaults to an empty list.
        mode (str)   :   File open mode passed straight through to the underlying writer, e.g. "w" to overwrite
                        or "a" to append. Defaults to "w".
    """
    path    : str   = ""
    data    : list  = field(default_factory=list)
    mode    : str   = "w"

class IWriter(ABC):
    """
    Writer interface: any concrete writer takes an OutputContext, writes context.data out to
    context.path, and returns the same context back. Never instantiated directly -- CSVWriter
    below is the concrete writer.
    """
    @abstractmethod
    def write(self, context: OutputContext):
        """
        Write context.data out to context.path and return the context unchanged.

        *Args:
            context (OutputContext) : Carries the data and destination path/mode to write with.
        """
        pass

class CSVWriter(IWriter):
    """
    Writes context.data out to a CSV file, one row per top-level element of context.data (or,
    if the elements aren't themselves lists, one column each, transposed into rows).
    """
    def write(self, context: OutputContext):
        """
        Append (or overwrite, depending on context.mode) the data in context to a CSV file at context.path.

        *Args   :
            context (OutputContext) :   data      -- the rows (or columns, if not already nested lists) to write.
                                        path      -- destination file, without its ".csv" extension (added here).
                                        mode      -- passed straight to pandas.DataFrame.to_csv, e.g. "a" to append or "w" to overwrite.

        !Returns:
            OutputContext            :   The same context, unchanged, once the CSV has been written.

        !Raises :
            TypeError                : If context.data is not a list.
            ValueError                : If context.data is an empty list.
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
