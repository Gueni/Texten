
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                           ____  _____    _    ____  _____ ____
#?                                                          |  _ \| ____|  / \  |  _ \| ____|  _ \
#?                                                          | |_) |  _|   / _ \ | | | |  _| | |_) |
#?                                                          |  _ <| |___ / ___ \| |_| | |___|  _ <
#?                                                          |_| \_\_____/_/   \_\____/|_____|_| \_\
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from    abc            import  ABC         , abstractmethod
from    dataclasses    import  dataclass   , field
import  pandas         as      pd
import  numpy          as      np
import  csv
import  decimal
import  re
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
@dataclass(init=True)
class InputContext:
    """
    Shared, mutable context passed into every IReader.read() call: where to read from, and where
    the loaded data lands. One instance is built per file to read and passed straight through.

    *Args:
        rawDataPath (str)   :   Path to the input file, without its extension (readers append it themselves). Defaults to "".
        data        (list)  :   The data read from rawDataPath, populated by whichever reader is used. Defaults to an empty array.
        header      (list)  :   Column header names, populated only by CSVReaderHeader. Defaults to an empty list.
        headerLen   (int)   :   Number of header columns minus one, populated only by CSVReaderHeader. Defaults to 0.
    """
    rawDataPath     : str   = ""
    data            : list  = field(default_factory=lambda: np.array([]))
    header          : list  = field(default_factory=list)
    headerLen       : int   = 0

class IReader(ABC):
    """
    Reader interface: any concrete reader takes an InputContext, fills in its .data (and,
    depending on the reader, .header/.headerLen), and returns the same context back. Never
    instantiated directly -- CSVReader/CSVReaderNP/CSVReaderHeader below are the concrete readers.
    """
    @abstractmethod
    def read(self, context: InputContext):
        """
        Read whatever rawDataPath points to and populate the context in place.

        *Args:
            context (InputContext)  : Carries the path to read from; populated with the loaded data on return.
        """
        pass

class CSVReader(IReader):
    """
    Reads a CSV file, auto-detecting whether it has a header row, and converts every value to
    a Decimal for precise numerical operations (falls back to raw strings if Decimal conversion fails).
    """

    def read(self, context: InputContext):
        """
        Auto-detect a header row via csv.Sniffer, read the CSV as strings, convert to Decimal,
        and store the result (transposed, so each row of context.data is one column of the CSV).

        *Args   :
            context (InputContext)  :   rawDataPath is the CSV file, without its ".csv" extension (added here if missing).

        !Returns:
            InputContext             :   The same context, with .data populated as a list of Decimal columns.
        """

        if ".csv" not in  context.rawDataPath   : ending = ".csv"
        else                                    : ending = ""

        #Check first rows for header
        with open(context.rawDataPath+ending, "r", encoding="utf-8") as f:
            sample  = "".join([f.readline() for _ in range(5)])

        try:
            has_header = csv.Sniffer().has_header(sample)
        except csv.Error:
            has_header = False

        if has_header:
            header      = 0
            skip_row    = 1 # todo: why in standalone one row blank?
        else:
            header      = None
            skip_row    = 0

        # Read the CSV file into a pandas DataFrame with no headers, treat all data as strings, and transpose it.
        dataFrame   = pd.read_csv(context.rawDataPath+ending, skiprows=skip_row, header=header, dtype=str).transpose()

        # Attempt to convert all elements of the DataFrame to Decimal for precise numerical operations.
        # If conversion fails for any reason, catch the exception, print a warning, and continue without interruption.
        try:
            context.data   = (dataFrame.apply(lambda col: col.map(decimal.Decimal))).values.tolist()
        except Exception:
            print("Could not apply Decimal.")
            pass

        return context

class CSVReaderNP(IReader):
    """
    Reads a CSV file straight into a numpy float64 array, skipping the header row unconditionally.
    Faster than CSVReader, but assumes the file is already purely numeric with exactly one header row.
    """

    def read(self, context: InputContext):
        """
        Read the CSV (skipping row 0 as the header), transpose it, and store it as a numpy float64
        array so each row of context.data is one column of the CSV.

        *Args   :
            context (InputContext)  :   rawDataPath is the CSV file, without its ".csv" extension (added here if missing).

        !Returns:
            InputContext             :   The same context, with .data populated as a numpy float64 array.
        """
        if ".csv" not in  context.rawDataPath   : ending = ".csv"
        else                                    : ending = ""

        # Read the CSV file into a pandas DataFrame with no headers, treat all data as strings, and transpose it.
        dataFrame       = pd.read_csv(
                                        context.rawDataPath+ending  ,
                                        header      =   None        ,
                                        skiprows    =   1
                                     ).transpose()

        context.data   = dataFrame.to_numpy(dtype=np.float64)
        return context

class CSVReaderHeader(IReader):
    """
    Reads only the header row of a CSV file, sanitizing each column name to be a valid identifier
    (non-alphanumeric characters replaced with underscores). Does not touch context.data at all.
    """
    def read(self, context):
        """
        Read just the column names from row 0, sanitize them, and store the count (minus one) alongside.

        *Args   :
            context (InputContext)  :   rawDataPath is the CSV file, without its ".csv" extension (added here if missing).

        !Returns:
            InputContext             :   The same context, with .header (sanitized column names) and .headerLen populated.
        """
        if ".csv" not in  context.rawDataPath   : ending = ".csv"
        else                                    : ending = ""

        # Read the CSV file header.
        context.header      = [ re.sub(r'[^a-zA-Z0-9]', '_', c) for c in pd.read_csv(context.rawDataPath+ending, nrows=0).columns]
        context.headerLen   = len(context.header)-1
        return context
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
