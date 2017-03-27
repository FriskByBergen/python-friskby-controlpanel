# -*- coding: utf-8 -*-
"""
    (c) 2017 FriskbyBergen.

    Licence
    =======
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from friskby_controlpanel import friskby_controlpanel as cp
from fake_friskby_interface import FakeFriskbyInterface
import unittest


class StatusTestCase(unittest.TestCase):

    def setUp(self):
        self.iface = FakeFriskbyInterface()
        cp.app.config['TESTING'] = True
        cp.app.config['FRISKBY_INTERFACE'] = self.iface
        self.app = cp.app.test_client()

    def test_that_header_reflects_sampler_status(self):
        self.iface.sampler_status = 'active'
        out = self.app.get('/')
        self.assertIn("Sampler <span>active</span>", out.data)

        self.iface.sampler_status = 'dead'
        out = self.app.get('/')
        self.assertIn("Sampler <span>dead</span>", out.data)


if __name__ == '__main__':
    unittest.main()
