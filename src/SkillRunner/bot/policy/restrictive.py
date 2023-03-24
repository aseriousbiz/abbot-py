"""
Defines the RestrictedPolicy, which uses RestrictedPython to strictly limit what the script can do.
"""

import logging
import warnings
from typing import Optional

import RestrictedPython
from RestrictedPython import Guards

class RestrictivePolicy(object):
    """
    A policy that uses RestrictedPython to strictly limit what the script can do.
    """
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("RestrictivePolicy")
        self.allowed_modules = []
        self.denied_modules = []

        # Construct the restricted python environment
        delegate = Delegate(self.logger.getChild("Delegate"), self)
        self.restricted_env = RestrictedEnvironment(
            self.logger.getChild("RestrictedEnvironment"),
            delegate)

    def allow_module(self, module: str):
        """
        Allows access to the provided module when executing code under this policy.
        If the same module is both allowed and denied, the deny will take precedence.
        """
        self.allowed_modules.append(module)

    def allow_modules(self, modules: list[str]):
        """
        Allows access to all the provided modules when executing code under this policy.
        If the same module is both allowed and denied, the deny will take precedence.
        """
        for module in modules:
            self.allow_module(module)

    def deny_module(self, module: str):
        """
        Denies access to the provided module when executing code under this policy.
        If the same module is both allowed and denied, the deny will take precedence.
        """
        self.denied_modules.append(module)

    def deny_modules(self, modules: list[str]):
        """
        Denies access to all the provided modules when executing code under this policy.
        If the same module is both allowed and denied, the deny will take precedence.
        """
        for module in modules:
            self.deny_module(module)

    def denies(self, module: str) -> bool:
        """
        Checks if the provided module is denied by policy.
        A module is denied by policy if it, or any dotted-prefix is denied (i.e. for 'a.b.c', we consider 'a', 'a.b', and 'a.b.c').
        """
        segments = module.split('.')
        for i in range(len(segments)):
            if ".".join(segments[0:i+1]) in self.denied_modules:
                return True

    def allows(self, module: str) -> bool:
        """
        Checks if the provided module is allowed by policy.
        A module is allowed by policy if it, or any dotted-prefix is allowed (i.e. for 'a.b.c', we consider 'a', 'a.b', and 'a.b.c').
        """
        segments = module.split('.')
        for i in range(len(segments)):
            if ".".join(segments[0:i+1]) in self.allowed_modules:
                return True

    def name(self) -> str:
        """Returns the name of this policy."""
        return "Restrictive"

    def exec(self, code: str, script_locals: dict) -> None:
        """Executes the provided code under the configured policy."""
        self.restricted_env.exec(code, script_locals)

class Delegate(object):
    """
    Delegate that uses the provided policy to implement RestrictedPython built-in functionality.
    """
    def __init__(self, logger: logging.Logger, policy: RestrictivePolicy):
        self.logger = logger
        self.policy = policy
    
    def handle_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """
        Restricts access to modules based on the policy.
        If the policy denies the module, the import fails.
        If the policy allows the module, the import succeeds.
        If the policy doesn't specify the module, the import is logged.
        """
        if self.policy.denies(name):
            raise PermissionError(f"Module '{name}' is not allowed in skill code. Use a self-hosted runner (https://docs.ab.bot/chatops/custom-runner/) if you need this module.")
        
        if not self.policy.allows(name):
            self.logger.warning(f"Skill code is importing module '{name}'", extra={"imported_module": name})

        return __import__(name, globals, locals, fromlist, level)
    
    def handle_getiter(self, obj: object) -> object:
        """
        Gets an iterator from an iterable object.
        """
        return iter(obj)
    
    def handle_getitem(self, obj: object, index: object) -> object:
        """
        Gets an item from an object.
        """
        return obj[index]

    def handle_getattr(self, obj: object, name: str, default=None, getattr=getattr) -> object:
        """
        Gets an attribute from an object.
        """
        # Restricted Python has a guard that prevents:
        #   * Access to attributes starting with '_'
        #   * Calling 'format' on a string because http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
        # The first of those rescrictions is fine,
        # but the second is a bit too restrictive.
        # It's designed for scenarios where you don't trust the input string,
        # but skills make that decision for themselves.
        if name.startswith('_'):
            raise PermissionError(
                f'Cannot access "{name}" because it starts with "_"'
            )
        return getattr(obj, name, default)

    def handle_setattr(self, obj: object, name: str, value: object):
        """
        Sets an attribute on an object.
        """
        if name.startswith('_'):
            raise PermissionError(
                f'Cannot access "{name}" because it starts with "_"'
            )
        return setattr(obj, name, value)

    def handle_delattr(self, obj: object, name: str):
        """
        Deletes an attribute on an object.
        """
        if name.startswith('_'):
            raise PermissionError(
                f'Cannot access "{name}" because it starts with "_"'
            )
        return delattr(obj, name)

    def handle_hasattr(self, obj: object, name: str) -> bool:
        """
        Checks if an object has an attribute.
        """
        if name.startswith('_'):
            # Pretend it doesn't exist.
            return False
        return hasattr(obj, name)

    def is_writable(self, _obj) -> bool:
        """
        Returns whether or not the provided object is writable.
        """
        return True

class PrintCollector:
    """Accepts prints and ignores them."""

    def __init__(self, _getattr_=None):
        pass

    def write(self, text): # pylint: disable=missing-function-docstring
        pass

    def __call__(self):
        pass

    def _call_print(self, *objects, **kwargs):
        pass

class RestrictedEnvironment(object):
    """
    Defines a RestrictedPython environment.
    Expected a "delegate" class that implements 'handle_*' methods
    for each of the built-in functions.
    Executing code in this environment will call back to the delegate
    to implement the built-in functionality.
    """
    def __init__(self, logger: logging.Logger, delegate):
        # Restricted Python works by translating the incoming Python code
        # into calls to well-known functions.
        # Then, we provide implementations of those functions as globals.
        # For example, `import foo` becomes `__import__("foo")`, and `foo.bar`

        # For completeness, we 
        # becomes `_getattr_(foo, "bar")`.
        # So, we build a dictionary of script globals to implement
        # the functionality RestrictedPython depends on.
        self.logger = logger

        def _write_(obj):
            if delegate.is_writable(obj):
                return obj
            else:
                raise PermissionError("Attempted to write to an unwritable object.")

        self.script_globals = {
            **Guards.safe_globals,
            '_print_': PrintCollector,
            '_getiter_': delegate.handle_getiter,
            '_getitem_': delegate.handle_getitem,
            'getattr': delegate.handle_getattr,
            'setattr': delegate.handle_setattr,
            'delattr': delegate.handle_delattr,
            'hasattr': delegate.handle_hasattr,
            '_getattr_': delegate.handle_getattr,
            '_unpack_sequence_': Guards.guarded_unpack_sequence,
            '_write_': _write_,

            # Necessary setup for classes to work in RP
            # https://restrictedpython.readthedocs.io/en/latest/usage/basic_usage.html#necessary-setup
            '__metaclass__': type,
            '__name__': '__abbot_skill__',
        }
        self.script_globals['__builtins__']['__import__'] = delegate.handle_import

    def exec(self, code: str, script_locals: dict) -> None:
        """
        Executes the provided Python code in the restricted environment,
        calling back to the delegate to implement Python built-in functionality.
        """

        # Compile the code with RestrictedPython
        with warnings.catch_warnings():
            # Ignore warnings when compiling the skill code
            warnings.filterwarnings("ignore", category=SyntaxWarning)
            compiled = RestrictedPython.compile_restricted(code, filename="skill.py", mode="exec")
            exec(compiled, self.script_globals, script_locals) # pylint: disable=exec-used
