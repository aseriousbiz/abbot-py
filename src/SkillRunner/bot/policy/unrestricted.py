import logging
import os
from typing import Optional

DEFAULT_ALLOWED_ENV_KEYS = [
    "PYTHON_VERSION",
    "LANG",
    "PATH",
    "PYTHON_GET_PIP_URL",
    "HOME",
    "PYTHON_SETUPTOOLS_VERSION",
    "PYTHON_PIP_VERSION",
    "NUM_CORES",
    "PYTHONPATH"
]

class UnrestrictedPolicy(object):
    """
    A policy that doesn't use Restricted Python.
    Some environment variables may be masked from the script, but no other restrictions are applied.
    """

    def __init__(self, logger: Optional[logging.Logger] = None, allow_all: bool = False, allowed_keys: Optional[list[str]] = None):
        self.logger = logger or logging.getLogger("Policy")
        self.allow_all = allow_all
        self.allowed_keys = allowed_keys or DEFAULT_ALLOWED_ENV_KEYS

    def allow_all_env_keys(self):
        """
        Allows all environment variables to be accessed by the script.
        """
        self.allow_all = True

    def allow_env_key(self, key: str):
        """
        Allows the specified environment variable to be accessed by the script.
        """
        self.allowed_keys.append(key);

    def name(self):
        """Returns the name of this policy."""
        return "Unrestricted"

    def exec(self, skill_code: str, script_locals: dict):
        """
        Executes the provided Python code under the policy defined by this type,
        using the provided locals as top-level variables available to the script.
        """

        # Clear out environment variables before calling the skill
        if self.allow_all is not True:
            for key, _ in os.environ.items():
                if key not in self.allowed_keys:
                    del os.environ[key]

        # We're running outside a sandboxed environment, so go ahead and run the code directly
        exec(skill_code, script_locals) # pylint: disable=exec-used