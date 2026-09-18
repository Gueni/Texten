
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from rich.console import Console
from rich.panel import Panel
import contextlib
import functools
import os
import sys
import traceback
import  assets.Dependencies         as        dp
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
error_log = (os.getcwd()).replace("\\","/") + "/Script/" + "D".upper() + "ata/Log/" + "error_log.log"

with open(error_log , "w"):pass

def suppress_tracebacks_to_file(exc_type, exc_value, exc_traceback):
    with open(error_log, "w", encoding="utf-8") as f:
        f.write("="*40 + " Unhandled Exception " + "="*40 +"\n")
        f.write("*" * 80 + "\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
        f.write("*" * 80 + "\n")
        f.write("\n")

sys.excepthook   = suppress_tracebacks_to_file
console             = Console()
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class ErrorHint:
    def __init__(self):
        self._function_hints = {}
        self._shown_messages = set()

    def add_hint(self, func_name, message):
        self._function_hints[func_name] = message

    def get_hint(self, func_name):
        return self._function_hints.get(func_name)

    def mark_shown(self, func_name, message):
        self._shown_messages.add(f"{func_name}:{message}")

    def was_shown(self, func_name, message):
        return f"{func_name}:{message}" in self._shown_messages

def hint(message):
    def decorator(func):
        func._hint_message = message

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self_obj = args[0] if args else None
            if self_obj and hasattr(self_obj, 'hint'):
                self_obj.hint.add_hint(func.__name__, message)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def safe_function(func):
    """Wraps a function with error handling and hint display."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self_obj = args[0] if args else None

        if not self_obj or not hasattr(self_obj, 'hint'):
            return func(*args, **kwargs)

        try:
            return func(*args, **kwargs)

        except Exception as e:
            custom_message = self_obj.hint.get_hint(func.__name__)

            # Always show Rich panel for user clarity
            if custom_message and not self_obj.hint.was_shown(func.__name__, custom_message):
                console.print(Panel.fit(
                    f"[white]{custom_message}[/white]",
                    title=f"[bright_red]Exception in {func.__name__}[/bright_red]",
                    border_style="red",
                ))
                self_obj.hint.mark_shown(func.__name__, custom_message)
            # else:
            #     console.print(Panel.fit(
            #         f"[white]{type(e).__name__}: {e}[/white]",
            #         title=f"[bright_red]Exception in {func.__name__}[/bright_red]",
            #         border_style="red",
            #     ))

            # Always log the error quietly
            with open(error_log, "a", encoding="utf-8") as f:
                traceback.print_exception(type(e), e, e.__traceback__, file=f)
                f.write("\n")

            # If we’re inside a user try/except, re-raise
            # otherwise, swallow it to keep program running
            exc_type, _, _ = sys.exc_info()
            if exc_type and dp.flag:
                # inside a user try/except, re-raise normally
                raise
            else:
                # outside try/except -> swallow safely
                return None

    return wrapper

def safe_class():
    def decorator(cls):
        if getattr(cls, "_already_wrapped", False):
            return cls

        # Patch original __init__ to include the hint manager
        original_init = getattr(cls, '__init__', lambda self: None)

        def new_init(self, *args, **kwargs):
            self.hint = ErrorHint()
            original_init(self, *args, **kwargs)

        cls.__init__ = new_init

        # Wrap all methods (except __init__)
        for attr_name in dir(cls):
            if attr_name.startswith('__'):
                continue

            attr_value = getattr(cls, attr_name)

            if callable(attr_value):
                setattr(cls, f"__orig_{attr_name}", attr_value)
                setattr(cls, attr_name, safe_function(attr_value))

        cls._already_wrapped = True
        return cls
    return decorator
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

@contextlib.contextmanager
def allow_exceptions():
    """Temporarily allow exceptions to propagate through the error handler."""
    original_flag = getattr(dp, 'flag', False)
    dp.flag = True
    try:
        yield
    finally:
        dp.flag = original_flag
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
