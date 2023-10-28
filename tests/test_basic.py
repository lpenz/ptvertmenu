"""ptvertmenu basic tests"""

# type: ignore

import unittest

import ptvertmenu


class TestView(unittest.TestCase):
    def test_version(self):
        ptvertmenu.version()
