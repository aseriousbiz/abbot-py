import logging
import os
from RestrictedPython import compile_restricted, safe_builtins, utility_builtins

# This defines the builtins scripts are allowed to use
script_builtins = safe_builtins.copy()

# Allow basic utilities (string, math, random, etc.)
# https://github.com/zopefoundation/RestrictedPython/blob/c1bc989e1fa060273594e39a86d3c4fb3ffe3a4b/src/RestrictedPython/Utilities.py
script_builtins.update(utility_builtins)

allowed_modules = [
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
]

# We allow any module that starts with any of these names followed by a '.' (like 'dns.resolver')
allowed_module_prefixes = [
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
    "requests",
    "rsa",
    "soupsieve",
    "sqlalchemy",
    "toml",
    "twilio",
    "websocket",
    "urllib",
]

def guarded_import(mname, *args, **kwargs):
    """
    Implementation of '__import__' used in scripts.
    Here we can filter to only allow certain modules and then pass through to the built-in '__import__'.
    For modules we disallow, we can raise a useful error
    """
    segments = mname.split('.')

    if mname in allowed_modules:
        logging.debug(f"Import of '{mname}' allowed (direct import)")
        return __import__(mname, *args, **kwargs)
    elif segments[0] in allowed_module_prefixes:
        logging.debug(f"Import of '{mname}' allowed (prefix '{segments[0]}' is allowed)")
        return __import__(mname, *args, **kwargs)
    else:
        logging.debug(f"Import of '{mname}' denied")
        raise PermissionError(f"Skills are not permitted to import the {mname} module. Contact 'support@ab.bot' if you have questions or want to add a module to the allowed list.")

script_builtins["__import__"] = guarded_import

def guarded_getitem(obj, index):
    return obj[index]

script_builtins["_getitem_"] = guarded_getitem

def guarded_getattr(obj, name, default=None):
    """
    Implementation of 'getattr' used in scripts.
    This can be used to ban access to certain properties of objects/modules
    """
    if name.startswith('_'):
        raise AttributeError(f'"{name} is an invalid attribute name because it starts with "_"')

    logging.debug(f"Getattr '{type(obj).__name__}#{name}' allowed")
    return getattr(obj, name, default)

script_builtins["_getattr_"] = guarded_getattr

def guarded_hasattr(obj, name):
    """
    Implementation of 'hasattr' used in scripts.
    We implement it by trying our guarded 'getattr'.
    If it raises a PermissionError, we say the attribute doesn't exist.
    """
    try:
        guarded_getattr(obj, name)
    except (AttributeError, PermissionError, TypeError):
        logging.debug(f"Hasattr '{type(obj).__name__}#{name}' denied")
        return 0
    logging.debug(f"Hasattr '{type(obj).__name__}#{name}' allowed")
    return 1

script_builtins["hasattr"] = guarded_hasattr

def guarded_getiter(*args):
    return iter(*args)

def guarded_any(seq):
    return any(guarded_getiter(seq))

script_builtins["any"] = guarded_any

script_globals = {
    '__builtins__': script_builtins,
    '_getattr_': guarded_getattr,
    '_getiter_': guarded_getiter,
    'getattr': guarded_getattr,
}

def exec_with_policy(skill_code, locals):
    """
    Executes the provided python skill code under our restriction policy.
    """

    if os.environ.get('ABBOT_SANDBOXED') == 'false':
        # We're running outside a sandboxed environment, so go ahead and run the code directly
        logging.info("executing skill code WITHOUT sandbox")
        exec(skill_code, locals)
    else:
        logging.info("executing skill code WITH sandbox")
        # We're running in a sandboxed environment. Run the code through RestrictedPython
        globals = {
            **script_globals,
            **locals
        }

        byte_code = compile_restricted(
            skill_code,
            filename='<skill code>',
            mode='exec')
        exec(byte_code, globals)
