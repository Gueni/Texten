
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
    rawDataPath     : str   = ""
    data            : list  = field(default_factory=lambda: lambda: np.array([]))
    header          : list  = field(default_factory=list)
    headerLen       : int   = 0

class IReader(ABC):
    """
    _summary_

    *Args:
        ABC (_type_)    : _description_
    """
    @abstractmethod
    def read(self, context: InputContext):
        """
        _summary_

        *Args:
            context (InputContext)  : _description_
        """
        pass

class CSVReader(IReader):
    """
    _summary_

    *Args:
        IReader (_type_)    : _description_
    """

    def read(self, context: InputContext):
        """
        _summary_

        *Args   :
            context (InputContext)  : _description_

        !Returns:
            _type_                  : _description_
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
    _summary_

    *Args:
        IReader (_type_)    : _description_
    """

    def read(self, context: InputContext):
        """
        _summary_

        *Args   :
            context (InputContext)  : _description_

        !Returns:
            _type_                  : _description_
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
    _summary_

    *Args:
        IReader (_type_)    : _description_
    """
    def read(self, context):
        """
        _summary_

        *Args   :
            context (_type_)    : _description_

        !Returns:
            _type_              : _description_
        """
        if ".csv" not in  context.rawDataPath   : ending = ".csv"
        else                                    : ending = ""

        # Read the CSV file header.
        context.header      = [ re.sub(r'[^a-zA-Z0-9]', '_', c) for c in pd.read_csv(context.rawDataPath+ending, nrows=0).columns]
        context.headerLen   = len(context.header)-1
        return context
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
