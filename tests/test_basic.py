# Copyright (C) 2023 Leandro Lisboa Penz <lpenz@lpenz.org>
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.

# type: ignore

import os
import tempfile
import unittest

import ptvertmenu


class TestView(unittest.TestCase):
    def test_chdir(self):
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as d:
            with ptvertmenu.chdir(d):
                self.assertEqual(os.getcwd(), d)
