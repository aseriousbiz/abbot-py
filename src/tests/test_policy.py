import io
import unittest
import logging
from parameterized import parameterized

from SkillRunner.bot.policy import Policy, PermissivePolicy, RestrictivePolicy

#pylint: disable=missing-docstring,

class PolicyTest(unittest.TestCase):
    @parameterized.expand([
        ("unrestricted", PermissivePolicy()),
        ("restricted", RestrictivePolicy()),
    ])
    def test_classes_and_attrs(self, _name: str, policy: Policy):
        """
        Ensures the script can define and use classes and their attributes.
        """
        code = """
class Thing:
    def __init__(self):
        self.value = 0

t = Thing()
t.value = 1
output.append(getattr(t, 'value'))
setattr(t, 'value', 42)
output.append(t.value)

t.deleteme = 99
output.append(t.deleteme)
output.append(hasattr(t, 'deleteme'))
del t.deleteme
output.append(hasattr(t, 'deleteme'))
        """
        output = []
        policy.exec(code, { "output" : output })
        self.assertEqual([1, 42, 99, True, False], output)

    @parameterized.expand([
        ("unrestricted", PermissivePolicy(), True),
        ("restricted", RestrictivePolicy(), False),
    ])
    def test_private_attrs_in_script(self, _name: str, policy: Policy, success: bool):
        """
        Ensures that a class defined in a script cannot have private attributes.
        """
        # This is more of a side-effect than intentional.
        # The guarded get/set/del/hasattr methods don't have any context as to
        # where they are running, except for knowing that they're _within_ the script.
        # So we can't tell that '_value' is defined within the script itself.
        # Also, that's not really a thing anyway, because Python.
        code = """
class Thing:
    def __init__(self):
        self._value = 42
output.append(Thing()._value)
        """
        output = []
        if success:
            policy.exec(code, { "output" : output })
            self.assertEqual(output, [42])
        else:
            with self.assertRaises(SyntaxError) as context:
                policy.exec(code, { "output" : output })
            self.assertEqual(
                context.exception.msg,
                ('Line 4: "_value" is an invalid attribute name because it starts with "_".', 
                'Line 5: "_value" is an invalid attribute name because it starts with "_".'))

    @parameterized.expand([
        ("unrestricted", PermissivePolicy(), True),
        ("restricted", RestrictivePolicy(), False),
    ])
    def test_private_attrs_in_provided_object(self, _name: str, policy: Policy, success: bool):
        """
        Ensures that the script cannot access private attributes
        of an object provided to it from outside (such as via importing).
        """
        code = """
output.append(protected._value)
        """
        class Protected:
            def __init__(self):
                self._value = 42
        protected = Protected()
        output = []
        if success:
            policy.exec(code, { "output" : output, "protected": protected })
            self.assertEqual(output, [42])
        else:
            with self.assertRaises(SyntaxError) as context:
                policy.exec(code, { "output" : output })
            self.assertEqual(
                context.exception.msg,
                ('Line 2: "_value" is an invalid attribute name because it starts with "_".',))

    @parameterized.expand([
        ("unrestricted", PermissivePolicy()),
        ("restricted", RestrictivePolicy()),
    ])
    def test_private_attrs_within_provided_object(self, _name: str, policy: Policy):
        """
        Ensures that an object provided to the script
        _can_ access private attributes of itself.
        """
        code = """
protected.increment()
protected.increment()
protected.increment()
        """
        class Protected:
            def __init__(self):
                self._counter = 0
            def increment(self):
                self._counter += 1
        protected = Protected()
        policy.exec(code, { "protected": protected })
        self.assertEqual(protected._counter, 3)

    @parameterized.expand([
        ("unrestricted", PermissivePolicy()),
        ("restricted", RestrictivePolicy()),
    ])
    def test_lists(self, _name: str, policy: Policy):
        code = """
list = [1, 2, 3, 4, 5, 6, 7]
output.append(list[1])
output.append(list[2:4])
output.append(list[-1])
del list[3]
output.append(list)
        """
        output = []
        policy.exec(code, { "output" : output })
        self.assertEqual(output, [
            2,
            [3, 4],
            7,
            [1, 2, 3, 5, 6, 7],
        ])

    @parameterized.expand([
        ("unrestricted", PermissivePolicy()),
        ("restricted", RestrictivePolicy()),
    ])
    def test_dicts(self, _name: str, policy: Policy):
        code = """
dict = { 'a' : 1, 'b' : 2, 'c' : 3 }
output.append(dict['a'])
del dict['b']
output.append(dict)
        """
        output = []
        policy.exec(code, { "output" : output })
        self.assertEqual(output, [
            1,
            { 'a' : 1, 'c' : 3 },
        ])

    @parameterized.expand([
        ("unrestricted", PermissivePolicy()),
        ("restricted", RestrictivePolicy()),
    ])
    def test_list_iteration(self, _name: str, policy: Policy):
        code = """
list = [1, 2, 3]
for i in list:
    output.append(i)
        """
        output = []
        policy.exec(code, { "output" : output })
        self.assertEqual(output, [1, 2, 3])

    @parameterized.expand([
        ("unrestricted", PermissivePolicy()),
        ("restricted", RestrictivePolicy()),
    ])
    def test_sequence_unpack(self, _name: str, policy: Policy):
        code = """
list = [1, 2, 3]
a, b, c = list
output.append(f"a={a},b={b},c={c}")
        """
        output = []
        policy.exec(code, { "output" : output })
        self.assertEqual(output, ["a=1,b=2,c=3"])

    @parameterized.expand([
        ("unrestricted", PermissivePolicy()),
        ("restricted", RestrictivePolicy()),
    ])
    def test_list_comprehension(self, _name: str, policy: Policy):
        code = """
output.append([i*2 for i in [1, 2, 3]])
        """
        output = []
        policy.exec(code, { "output" : output })
        self.assertEqual(output, [[2, 4, 6]])

    @parameterized.expand([
        ("os"),
    ])
    def test_import_module_unrestricted(self, import_attempt: str):
        """
        Ensures that the script cannot import a module that is explictly denied.
        """
        code = f"""
import {import_attempt}
output.append(True)
        """
        policy = PermissivePolicy()

        output = []
        policy.exec(code, { "output" : output })
        self.assertEqual(output, [True])

    @parameterized.expand([
        ("os", "os"),
        ("os", "os.path"),
    ])
    def test_import_denied_module_restricted(self, denied: str, import_attempt: str):
        """
        Ensures that the script cannot import a module that is explictly denied.
        """
        code = f"""
import {import_attempt}
output.append(True)
        """
        policy = RestrictivePolicy()
        policy.deny_module(denied)

        output = []
        with self.assertRaises(PermissionError) as context:
            policy.exec(code, { "output" : output })
        self.assertEqual(
            f"Module '{import_attempt}' is not allowed in skill code. Use a self-hosted runner (https://docs.ab.bot/chatops/custom-runner/) if you need this module.",
            context.exception.args[0])

    @parameterized.expand([
        ("os", "os"),
        ("os", "os.path"),
    ])
    def test_import_allowed_module_restricted(self, allowed: str, import_attempt: str):
        """
        Ensures that the script cannot import a module that is explictly denied.
        """
        code = f"""
import {import_attempt}
output.append(True)
        """
        output = []

        with self.assertLogs("RestrictivePolicy") as context:
            # Log a dummy log message so assertLogs doesn't _fail_ because there are no logs
            # Later, we will assert this is the ONLY log message
            logging.getLogger("RestrictivePolicy").info("Dummy log")

            policy = RestrictivePolicy()
            policy.allow_module(allowed)
            policy.exec(code, { "output" : output })

        self.assertEqual(context.output, [
            'INFO:RestrictivePolicy:Dummy log'
        ])

    def test_import_warning_module_restricted(self):
        """
        Ensures that if a script imports a module that is neither allowed nor denied,
        a warning is logged and the import is allowed
        """
        code = """
import os.path
output.append(True)
        """
        output = []

        with self.assertLogs("RestrictivePolicy") as context:
            policy = RestrictivePolicy()
            policy.exec(code, { "output" : output })

        self.assertEqual(output, [True])
        self.assertEqual(context.output, [
            "WARNING:RestrictivePolicy.Delegate:Skill code is importing module 'os.path'"
        ])
