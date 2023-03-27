"""
Defines the Unrestricted policy, which doesn't restrict the skill code in any way.
"""

import logging
from typing import Optional

class UnrestrictedPolicy(object):
    """
    A policy that doesn't restrict the skill code in any way.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("UnrestrictedPolicy")

    def name(self):
        """Returns the name of this policy."""
        return "Unrestricted"

    def exec(self, skill_code: str, script_locals: dict):
        """
        Executes the provided Python code under the policy defined by this type,
        using the provided locals as top-level variables available to the script.
        """

        # We're running outside a sandboxed environment, so go ahead and run the code directly
        exec(skill_code, script_locals) # pylint: disable=exec-used
