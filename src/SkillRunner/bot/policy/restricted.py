import logging
import RestrictedPython
from typing import Optional

class RestrictivePolicy(object):
    """
    A policy that uses RestrictedPython to strictly limit what the script can do.
    """
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("Policy")
        self.allowed_modules = []
        self.denied_modules = []

        # Construct the restricted python environment
        self.restricted_env = RestrictedEnvironment(Delegate(self))

    def allow_module(self, module: str):
        self.allowed_modules.push(module)

    def allow_modules(self, modules: list[str]):
        for module in modules:
            self.allow_module(module)

    def deny_module(self, module: str):
        self.denied_modules.push(module)

    def deny_modules(self, modules: list[str]):
        for module in modules:
            self.deny_module(module)

    def name(self) -> str:
        """Returns the name of this policy."""
        return "Restrictive"

    def exec(self, code: str, script_locals: dict) -> None:
        self.restricted_env.exec(code, script_locals)

class Delegate(object):
    """
    Delegate that uses the provided policy to implement RestrictedPython built-in functionality.
    """
    def __init__(self, policy: RestrictivePolicy):
        self.policy = policy
    
    def handle_print(self, s: str) -> None:
        # Just drop anything a skill prints on the ground.
        # We _could_ forward these somewhere though 🤔
        pass

    def handle_getiter(self, obj: object) -> object:
        """
        Gets an iterator from an iterable object.
        """
        return iter(obj)

    def handle_getattr(self, obj: object, name: str) -> object:
        """
        Gets an attribute from an object.
        """
        return getattr(obj, name)

class PrintCollector:
    """Accepts prints and ignores them."""

    def __init__(self, _getattr_=None):
        pass

    def write(self, text):
        pass

    def __call__(self):
        pass

    def _call_print(self, *objects, **kwargs):
        pass

class RestrictedEnvironment(object):
    """
    Defines a RestrictedPython environment.
    Expected a "delegate" class that implements 'handle_*' methods for each of the built-in functions.
    Executing code in this environment will call back to the delegate to implement the built-in functionality.
    """
    def __init__(self, delegate):

        # Install those closures into the environment-provided locals.
        self.environment_locals = {
            "_print_": RestrictedPython.PrintCollector,
            "_getattr_": lambda obj, name : delegate.handle_getattr(obj, name),
            "_getiter_": lambda obj: delegate.handle_getiter(obj),
        }

    def exec(self, code: str, script_locals: dict) -> None:
        """
        Executes the provided Python code in the restricted environment, calling back to the delegate to implement Python built-in functionality.
        """

        l = {
            **script_locals,
            **self.environment_locals, # Environment locals override provided script locals.
        }

        # Compile the code with RestrictedPython
        compiled = RestrictedPython.compile_restricted(code, filename="skill.py", mode="exec")
        exec(compiled, l) # pylint: disable=exec-used