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
from .fake_friskby_interface import FakeFriskbyInterface
import unittest


class DeviceSetupTestCase(unittest.TestCase):

    def setUp(self):
        cp.app.config['FRISKBY_INTERFACE'] = FakeFriskbyInterface()
        cp.app.config['TESTING'] = True
        self.app = cp.app.test_client()

    def test_the_dash_unregistered_device(self):
        out = self.app.get('/', follow_redirects=True)
        self.assertIn('Not registered', out.data)

    def test_trying_to_register_nulldevice(self):
        out = self.app.post('/register', data=dict({
            "deviceid": ""
        }))
        self.assertIn('No device id', out.data)

    def test_successful_registering_of_device(self):
        out = self.app.post('/register', data=dict({
            "deviceid": "my-device-id"
        }), follow_redirects=True)
        self.assertIn('Device now registered', out.data)

    def test_registering_a_device_but_it_fails_miserably(self):
        cp.app.config['FRISKBY_INTERFACE'].fails = True
        out = self.app.post('/register', data=dict({
            "deviceid": "my-device-id"
        }), follow_redirects=True)
        self.assertIn('Error', out.data)

    def test_device_registered(self):
        cp.app.config['FRISKBY_INTERFACE'].device_id = 'mydevice'
        out = self.app.get('/')
        self.assertIn('mydevice', out.data)


if __name__ == '__main__':
    unittest.main()
