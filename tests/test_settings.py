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
from tests.fake_friskby_interface import FakeFriskbyInterface
import unittest


class SettingsTestCase(unittest.TestCase):

    def setUp(self):
        self.iface = FakeFriskbyInterface()
        cp.app.config['TESTING'] = True
        cp.app.config['FRISKBY_INTERFACE'] = self.iface

        # Set device so that the dashboard does not redirect.
        self.iface.device_id = 'mydevice'

        self.app = cp.app.test_client()

    def test_looking_at_settings(self):
        out = self.app.get('/settings')
        self.assertIn('rpi_sample_time', out.data)
        self.assertIn('rpi_control_panel_host', out.data)
        self.assertIn('rpi_control_panel_port', out.data)
        self.assertIn('rpi_sds011', out.data)

    def test_changing_a_setting_successfully(self):
        out = self.app.post('/settings', data={
            'rpi_sample_time': 12,
            'rpi_control_panel_host': '0.0.0.0',
            'rpi_control_panel_port': 50,
            'rpi_sds011': '/dev/foo'
        })
        self.assertIn('Settings saved.', out.data)
        self.assertEqual(12, self.iface.settings['rpi_sample_time'])

    def test_posting_form_with_bad_data(self):
        out = self.app.post('/settings', data={
            'rpi_control_panel_host': '0.0.0.0',
            'rpi_control_panel_port': 50,
            'rpi_sds011': '/dev/foo'
        })
        self.assertIn('Form had errors', out.data)
        self.assertIn('This field is required', out.data)


if __name__ == '__main__':
    unittest.main()
