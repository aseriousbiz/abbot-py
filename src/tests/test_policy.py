import unittest
from parameterized import parameterized

from SkillRunner.bot.policy import Policy, UnrestrictedPolicy, RestrictivePolicy

#pylint: disable=missing-docstring

def first_param_name_func(testcase_func, param_num, params):
    return "%s_%s" %(
        testcase_func.__name__,
        params[0]
    )

class PolicyTest(unittest.TestCase):
    @parameterized.expand([
        ("Unrestricted", UnrestrictedPolicy()),
        ("Restricted", RestrictivePolicy()),
    ], name_func=first_param_name_func)
    def test_list_iteration(self, name: str, policy: Policy):
        code = """
list = [1, 2, 3]
for i in list:
    output.append(i)
        """
        output = []
        policy.exec(code, { "output" : output })
        self.assertEqual([1, 2, 3], output)