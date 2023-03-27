import logging
import warnings
import RestrictedPython
from RestrictedPython import Guards

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
    def __init__(self, logger: logging.Logger, allowed_modules: list[str], denied_modules: list[str], deny_underscore_attributes: bool):
        # Restricted Python works by translating the incoming Python code
        # into calls to well-known functions.
        # Then, we provide implementations of those functions as globals.
        # For example, `import foo` becomes `__import__("foo")`, and `foo.bar`
        # becomes `_getattr_(foo, "bar")`.
        # So, we build a dictionary of script globals to implement
        # the functionality RestrictedPython depends on.
        self.logger = logger
        self.allowed_modules = allowed_modules
        self.denied_modules = denied_modules
        self.deny_underscore_attributes = deny_underscore_attributes

        def _write_(obj):
            if self._is_writable(obj):
                return obj
            else:
                raise PermissionError("Attempted to write to an unwritable object.")

        self.env_globals = {
            **Guards.safe_globals,
            '_print_': PrintCollector,
            '_getiter_': self._handle_getiter,
            '_getitem_': self._handle_getitem,
            'getattr': self._handle_getattr,
            'setattr': self._handle_setattr,
            'delattr': self._handle_delattr,
            'hasattr': self._handle_hasattr,
            '_getattr_': self._handle_getattr,
            '_unpack_sequence_': Guards.guarded_unpack_sequence,
            '_iter_unpack_sequence_': Guards.guarded_iter_unpack_sequence,
            '_write_': _write_,

            # Necessary setup for classes to work in RP
            # https://restrictedpython.readthedocs.io/en/latest/usage/basic_usage.html#necessary-setup
            '__metaclass__': type,
            '__name__': '__abbot_skill__',
        }
        self.env_globals['__builtins__']['__import__'] = self._handle_import

    def exec(self, code: str, script_globals: dict) -> None:
        """
        Executes the provided Python code in the restricted environment,
        calling back to the delegate to implement Python built-in functionality.
        """

        # Compile the code with RestrictedPython
        with warnings.catch_warnings():
            # Ignore warnings when compiling the skill code
            warnings.filterwarnings("ignore", category=SyntaxWarning)
            compiled = RestrictedPython.compile_restricted(code, filename="skill.py", mode="exec")

            # Merge the environment globals with the script globals
            # Don't allow the provided globals to override our environment globals though.
            all_globals = {
                **script_globals,
                **self.env_globals,
            }

            exec(compiled, all_globals) # pylint: disable=exec-used

    def _denies(self, module: str) -> bool:
        """
        Checks if the provided module is denied by policy.
        A module is denied by policy if it, or any dotted-prefix is denied (i.e. for 'a.b.c', we consider 'a', 'a.b', and 'a.b.c').
        """
        segments = module.split('.')
        for i in range(len(segments)):
            if ".".join(segments[0:i+1]) in self.denied_modules:
                return True

    def _allows(self, module: str) -> bool:
        """
        Checks if the provided module is allowed by policy.
        A module is allowed by policy if it, or any dotted-prefix is allowed (i.e. for 'a.b.c', we consider 'a', 'a.b', and 'a.b.c').
        """
        segments = module.split('.')
        for i in range(len(segments)):
            if ".".join(segments[0:i+1]) in self.allowed_modules:
                return True

    def _handle_import(self, name, globals=None, locals=None, fromlist=(), level=0): # pylint: disable=redefined-builtin
        """
        Restricts access to modules based on the policy.
        If the policy denies the module, the import fails.
        If the policy allows the module, the import succeeds.
        If the policy doesn't specify the module, the import is logged.
        """
        if self._denies(name):
            raise PermissionError(f"Module '{name}' is not allowed in skill code. Use a self-hosted runner (https://docs.ab.bot/chatops/custom-runner/) if you need this module.")
        
        if not self._allows(name):
            self.logger.warning(f"Skill code is importing module '{name}'", extra={"imported_module": name})

        return __import__(name, globals, locals, fromlist, level)
    
    def _handle_getiter(self, obj: object) -> object:
        """
        Gets an iterator from an iterable object.
        """
        return iter(obj)
    
    def _handle_getitem(self, obj: object, index: object) -> object:
        """
        Gets an item from an object.
        """
        return obj[index]

    def _handle_getattr(self, obj: object, name: str, default=None, getattr=getattr) -> object: # pylint: disable=redefined-builtin
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
        if self.deny_underscore_attributes and name.startswith('_'):
            raise PermissionError(
                f'Cannot access "{name}" because it starts with "_"'
            )
        return getattr(obj, name, default)

    def _handle_setattr(self, obj: object, name: str, value: object):
        """
        Sets an attribute on an object.
        """
        if self.deny_underscore_attributes and name.startswith('_'):
            raise PermissionError(
                f'Cannot access "{name}" because it starts with "_"'
            )
        return setattr(obj, name, value)

    def _handle_delattr(self, obj: object, name: str):
        """
        Deletes an attribute on an object.
        """
        if self.deny_underscore_attributes and name.startswith('_'):
            raise PermissionError(
                f'Cannot access "{name}" because it starts with "_"'
            )
        return delattr(obj, name)

    def _handle_hasattr(self, obj: object, name: str) -> bool:
        """
        Checks if an object has an attribute.
        """
        if self.deny_underscore_attributes and name.startswith('_'):
            # Pretend it doesn't exist.
            return False
        return hasattr(obj, name)

    def _is_writable(self, _obj) -> bool:
        """
        Returns whether or not the provided object is writable.
        """
        return True
