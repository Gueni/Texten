
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                       ____  _____ ____ ___ ____ _____ ______   __
#?                                                      |  _ \| ____/ ___|_ _/ ___|_   _|  _ \ \ / /
#?                                                      | |_) |  _|| |  _ | |\___ \ | | | |_) \ V /
#?                                                      |  _ <| |__| |_| || | ___) || | |  _ < | |
#?                                                      |_| \_\_____\____|___|____/ |_| |_| \_\|_|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from typing                             import Type         , Dict
from Lib.postprocessor.core.interfaces  import IProcess
from Lib.common.generic_registry        import BaseRegistry
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class ProcessRegistry(BaseRegistry[IProcess]):
    """
    Concrete registry of IProcess classes, keyed by the short name each one registers under
    (e.g. "AMAX", "FFT", "DISSIPATIONS" -- see the @ProcessRegistry.register(...) decorators
    in post_process.py). ProcessorFactory looks processes up here by name when building a run.
    """
    _registry: Dict[str, IProcess] = {}
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
