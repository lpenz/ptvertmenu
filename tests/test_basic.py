"""ptvertmenu basic tests"""

import unittest

from ptvertmenu.vertmenu import VertMenu


class TestView(unittest.TestCase):
    def test_version(self) -> None:
        print(VertMenu)
