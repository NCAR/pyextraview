# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import unittest
from .context import extraview

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_absolute_truth_and_meaning(self):
        assert True

if __name__ == '__main__':
    unittest.main()
