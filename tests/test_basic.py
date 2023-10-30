"""ptvertmenu basic tests"""

import unittest

from ptvertmenu import VertMenu


class TestView(unittest.TestCase):
    def test_version(self) -> None:
        print(VertMenu)
