"""
Implements skill sandboxing policies.
"""

import logging

from typing import Optional, Protocol
from .restricted import RestrictivePolicy
from .unrestricted import UnrestrictedPolicy

class Policy(Protocol):
    """
    Protocol class (https://peps.python.org/pep-0544/) that defines the interface for a sandboxing policy.
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
        return UnrestrictedPolicy(logger, allow_all=True)
    elif name == "permissive":
        return UnrestrictedPolicy(logger, allow_all=False)
    else:
        # Default to "restrictive" with the default set of allowed modules
        policy = RestrictivePolicy(logger)
        policy.allow_modules(DEFAULT_ALLOWED_MODULES)
        return policy

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
    # atexit NOT allowed (it's process-level stuff we don't want to permit)

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
    # ctypes NOT allowed (no native-interop for skills)

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

    # imaplib NOT allowed (no I/O except HTTP)
    # importlib NOT allowed (don't mess with Python modules bro)
    # inspect NOT allowed (seems risky, we'll see if customers want it)
    "io",
    "ipaddress",
    "itertools",

    "json",

    "keyword",

    "locale",
    # logging NOT allowed (don't want skills writing to our logs)

    # mailbox NOT allowed (file I/O)
    # marshal NOT allowed (serialization is risky in general, wait for customer demand)
    "math",
    "mimetypes",
    # mmap NOT allowed (memory-mapped files, kinda sketchy for skills to use)
    # modulefinder NOT allowed (don't mess with Python modules bro)
    # msvcrt NOT allowed (Windows only and C-interop is a no-no)
    # multiprocessing NOT allowed (no starting processes please)

    "netrc", # Sure, it's just a file format.
    "numbers",

    # os NOT allowed (customers can request that we add some info in, but in general there isn't anything we want to expose in that)

    "pathlib", # Path manipulation is fine
    # pdb NOT allowed (no debuggers)
    # pickle NOT allowed (binary serialization is dangerous)
    # pkgutil NOT allowed (see C-interop)
    # platform NOT allowed (we could bring in a fake one if customers need it)
    "plistlib",
    "pprint",
    # Python compilers and stuff, NOT allowed

    "queue",
    "quopri",

    "random",
    "re",
    "reprlib",
    # runpy NOT allowed (no running python)

    # sched NOT allowed (no threading)
    "secrets",
    # select, selectors NOT allowed (no I/O except HTTP)
    # shelve NOT allowed (binary serialization)
    # signal NOT allowed (process management)
    # socket, socketserver NOT allowed (no I/O except HTTP, for now)
    # sqlite3 NOT allowed (wait for customer need)
    # ssl NOT allowed (not needed for HTTPS, for lower-level usage)
    # stat NOT allowed (file I/O)
    "statistics", # Math Is Fundamental(TM)
    "string",
    "stringprep",
    # struct NOT allowed (binary serialization)
    # subprocess NOT allowed (process management)
    # symtable NOT allowed (compiler internals)
    # sys, sysconfig NOT allowed
    #   (customers could request this, we need to go through it and choose what we're OK allowing access to)
    # syslog NOT allowed (I/O)

    "textwrap",
    # threading NOT allowed (threading)
    "time",
    "timeit",
    "types", "typing", # Types Are Good(TM)

    "unicodedata",
    "urllib", # Technically this allows FTP as well as HTTP, but I'm OK with that
    "uuid",

    # venv NOT allowed (no development-time tomfoolery)

    # The 'w's are just all kinds of sketchy

    "xml",

    "zoneinfo",

    # Dependency modules
    "azure",
    "boto3",
    "bs4",
    # cffi NOT ALLOWED (skills using CFFI is bad news),
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
