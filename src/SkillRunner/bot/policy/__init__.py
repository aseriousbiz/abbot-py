"""
Implements skill sandboxing policies.
"""

import logging

from typing import Optional, Protocol
from .restrictive import RestrictivePolicy
from .permissive import PermissivePolicy

class Policy(Protocol):
    """
    Protocol class (https://peps.python.org/pep-0544/)
    that defines the interface for a sandboxing policy.
    """

    def name(self) -> str:
        """Returns the name of this policy."""

    def exec(self, code: str, script_locals: dict) -> None:
        """
        Executes the provided Python code under the policy defined by this type,
        using the provided locals as top-level variables available to the script.
        """

def get_policy(name: str, logger: Optional[logging.Logger] = None) -> Policy:
    """Retrieves the policy with the provided name."""
    if name == "none":
        return PermissivePolicy(logger)
    elif name == "permissive":
        return PermissivePolicy(logger)
    else:
        # Default to "restrictive" with the default set of allowed modules
        policy = RestrictivePolicy(logger)
        policy.allow_modules(DEFAULT_ALLOWED_MODULES)
        return policy

DEFAULT_DENIED_MODULES = [
    # Modules that are explicitly disallowed

    # Built-in modules
    "atexit", # process-level stuff we don't want to permit
    "ctypes", # no native-interop for skills
    "importlib", # don't mess with Python modules bro
    "inspect", # seems risky, we'll see if customers want it
    "logging", # don't want skills writing to our logs
    "mailbox", # file I/O
    "marshal", # serialization is risky in general, wait for customer demand
    "mmap", # memory-mapped files, kinda sketchy for skills to use
    "modulefinder", # don't mess with Python modules bro
    "msvcrt", # Windows only and C-interop is a no-no
    "multiprocessing", # no starting processes please
    "os", # customers can request that we add some info in, but in general there isn't anything we want to expose in that
    "pdb", # no debuggers
    "pickle", # binary serialization is dangerous
    "pkgutil", # see C-interop
    "platform", # we could bring in a fake one if customers need it
    "runpy", # no running python
    "sched", # no threading
    "shelve", # binary serialization
    "signal", # process management
    "sqlite3", # wait for customer need
    "stat", # file I/O
    "struct", # binary serialization
    "subprocess", # process management
    "symtable", # compiler internals
    "sys",
    "sysconfig",
    "syslog", # I/O
    "threading", # threading
    "venv", # no development-time tomfoolery
   	"warnings", # Why would they need to do this?
    "webbrowser",	# We don't provide access to a browser, for now.
    "winreg", # We don't run on windows.
    "winsound", # We don't run on windows.

    # External modules
    # These are modules that the runner has access to because our dependencies need them,
    # But we don't want skills messing with.

    "cffi", # skills using FFI is bad news
]

DEFAULT_ALLOWED_MODULES = [
    # === Built-in modules ===
    # From https://docs.python.org/3/py-modindex.html
    # Some things may be missing from this list, either by omission or intentionally
    # Intentionally-missing items will usually have a comment explaining why.
    # Deprecated modules are not allowed by default (we can add them if there's customer demand)

    # all "_"-prefixed modules are explicitly disallowed.

    "abc",
    "argparse",
    "array",
    "ast", # It's OK to parse Python if you really want, just no compilers/debuggers
    "asyncio",

    "base64",
    "binascii",
    "binhex",
    "bisect",

    "calendar",
    "cmath",
    "collections",
    "colorsys",
    "contextlib",
    "copy",
    "copyreg",
    "csv",

    "dataclasses",
    "datetime",
    "decimal",
    "difflib",

    "email",
    "enum",
    "errno",

    "fractions",
    "functools",

    "getopt",
    "gettext",
    "glob",
    "graphlib",

    "hashlib",
    "heapq",
    "hmac",
    "html",
    "http",

    "io",
    "ipaddress",
    "itertools",

    "json",

    "keyword",

    "locale",

    "math",
    "mimetypes",

    "netrc", # Sure, it's just a file format.
    "numbers",

    "pathlib", # Path manipulation is fine
    "plistlib",
    "pprint",
    # Python compilers and stuff, NOT allowed

    "queue",
    "quopri",

    "random",
    "re",
    "reprlib",

    "secrets",
    "statistics", # Math Is Fundamental(TM)
    "string",
    "stringprep",

    "textwrap",
    "time",
    "timeit",
    "types", "typing", # Types Are Good(TM)

    "unicodedata",
    "urllib", # Technically this allows FTP as well as HTTP, but I'm OK with that
    "uuid",

    # The 'w's are just all kinds of sketchy

    "xml",

    "zoneinfo",

    # Dependency modules
    "azure",
    "boto3",
    "bs4",
    "cryptography",
    "dns",
    "ecdsa",
    "google",
    "grpc",
    "isodate",
    "jmespath",
    "jsonpickle",
    "kubernetes",
    "msal",
    "mysql",
    "mysqlx",
    "nltk",
    "nludb",
    "numpy",
    "octokit_routes",
    "octokit",
    "pandas_gbq",
    "pandas",
    "pyarrow",
    "PyYAML",
    "regex",
    "requests_oauthlib",
    "requests",
    "rsa",
    "soupsieve",
    "sqlalchemy",
    "toml",
    "twilio",
    "websocket",
    "urllib",
]
