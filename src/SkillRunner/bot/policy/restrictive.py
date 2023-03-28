"""
Defines the RestrictivePolicy, which uses RestrictedPython to strictly limit what the script can do.
"""

import logging
from typing import Optional

from .restricted_environment import RestrictedEnvironment

class RestrictivePolicy(object):
    """
    A policy that uses RestrictedPython to strictly limit what the script can do.
    """
    def __init__(self, logger: Optional[logging.Logger] = None, deny_underscore_attributes = True):
        self.logger = logger or logging.getLogger("RestrictivePolicy")
        self.allowed_modules = []
        self.denied_modules = []
        self.deny_underscore_attributes = deny_underscore_attributes

    def name(self) -> str:
        """Returns the name of this policy."""
        return "Restrictive"

    def exec(self, code: str, script_locals: dict) -> None:
        """Executes the provided code under the configured policy."""

        # TODO: We could use multiprocessing to run the code in a separate process
        # But we'd need a way to send results back to the main process
        # Might be better to just rearchitect to a more general-purpose skill runner instead.

        self._exec_inline(code, script_locals)
        
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

    def _exec_inline(self, code: str, script_locals: dict) -> None:
        restricted_env = RestrictedEnvironment(
            self.logger.getChild("RestrictedEnvironment"),
            self.allowed_modules,
            self.denied_modules,
            self.deny_underscore_attributes
        )

        restricted_env.exec(code, script_locals)
