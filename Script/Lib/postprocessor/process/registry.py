
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
    A concrete class registry to register process classes with userdefinded names

    *Attributes:
        _registry (dict)                        :   Used to store the classes with name as key

    ?Methods:
        register(cls, name)                     :   Used to register classes with userdefined name

    Decorator
        @ProcessRegistry.register(cls, name)    :   Decorator to register class with userdefined name
    """
    _registry: Dict[str, IProcess] = {}
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
