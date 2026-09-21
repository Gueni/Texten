
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                            ____ _____ _   _ _____ ____  ___ ____   ____  _____ ____ ___ ____ _____ ______   __
#?                           / ___| ____| \ | | ____|  _ \|_ _/ ___| |  _ \| ____/ ___|_ _/ ___|_   _|  _ \ \ / /
#?                          | |  _|  _| |  \| |  _| | |_) || | |     | |_) |  _|| |  _ | |\___ \ | | | |_) \ V /
#?                          | |_| | |___| |\  | |___|  _ < | | |___  |  _ <| |__| |_| || | ___) || | |  _ < | |
#?                           \____|_____|_| \_|_____|_| \_\___\____| |_| \_\_____\____|___|____/ |_| |_| \_\|_|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from typing import TypeVar, Generic, Type, Dict, Any, Callable
T   =   TypeVar('T')
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

class BaseRegistry(Generic[T]):

    """
    A generic, reusable registry: maps user-defined string names to classes, so callers can look
    a class up (and construct it) by name instead of hardcoding imports or long if/elif chains.
    Subclass this to build a registry for one specific interface (see ProcessRegistry for an example).

    ?NOTE:
        _registry is declared here only as a default/fallback. Every concrete subclass must redeclare
        its own `_registry: Dict[str, Type[T]] = {}` in its own class body -- otherwise it would
        silently inherit (and share) BaseRegistry's own dict with every other subclass that also
        forgot to redeclare it.
    """
    _registry: Dict[str, Type[T]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[Type[T]], Type[T]]:
        """
        Used to register classes with userdefined name

        *Args    :
            name (str)                  : Used to register classes with userdefined name

        !Returns :
            Callable[[Type[T]], Type[T]]: registered class and type
        """
        def decorator(sub_cls: Type[T]) -> Type[T]:
            """
            Decorator to register class with userdefined name

            *Args   :
                sub_cls (Type[T])   : Class the decorator is used on

            !Returns:
                Type[T]             : Class the decorator is used on
            """
            cls._registry[name] = sub_cls
            return sub_cls
        return decorator

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> T:
        """
        Used to create object from registered class

        *Args    :
            name    (str)       : Desired user defined class name
            **kwargs             : Additional keyword arguments, forwarded to the registered class's constructor.

        !Returns :
            T                    : A new instance of the class registered under name.

        !Raises  :
            KeyError If name is not registered in this registry.
        """
        if name not in cls._registry    :   raise KeyError(f"Name '{name}' is not registerd in this registry.")
        return cls._registry[name](**kwargs)

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------