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
        self.assertIn('rpi_location', out.data)

        self.assertIn(
            'value="60.392990, 5.324150, 0.000000, Bergen By E Nydeli"',
            out.data
        )

    def test_changing_a_setting_successfully(self):
        out = self.app.post('/settings', data={
            'rpi_sample_time': 12,
            'rpi_control_panel_host': '0.0.0.0',
            'rpi_control_panel_port': 50,
            'rpi_sds011': '/dev/foo',
            'rpi_location': '5.0, 60, 0, Bergen E Fin',
        })
        self.assertIn('Settings saved.', out.data)
        self.assertEqual(12, self.iface.settings['rpi_sample_time'])

    def test_posting_form_with_bad_data(self):
        out = self.app.post('/settings', data={
            'rpi_control_panel_host': '0.0.0.0',
            'rpi_control_panel_port': 50,
            'rpi_sds011': '/dev/foo',
            'rpi_location': '5.0, 60, 0, Bergen E Fin',
        })
        self.assertIn('Form had errors', out.data)
        self.assertIn('This field is required', out.data)

    def test_bad_location(self):
        data = {
            'rpi_sample_time': 12,
            'rpi_control_panel_host': '0.0.0.0',
            'rpi_control_panel_port': 50,
            'rpi_sds011': '/dev/foo',
        }

        # Bad latitude.
        data['rpi_location'] = '-91, 60, 0, Bergen E Fin'
        out = self.app.post('/settings', data=data)
        self.assertIn('Form had errors', out.data)
        self.assertIn('Latitude must be a number between -90 and 90.',
                      out.data)

        # Bad longitude.
        data['rpi_location'] = '5, -181, 0, Bergen E Fin'
        out = self.app.post('/settings', data=data)
        self.assertIn('Form had errors', out.data)
        self.assertIn('Longitude must be a number between -180 and 180.',
                      out.data)

        # Bad altitude.
        data['rpi_location'] = '5, 60, x, Bergen E Fin'
        out = self.app.post('/settings', data=data)
        self.assertIn('Form had errors', out.data)
        self.assertIn('Altitude must be a number, or 0 if not known.',
                      out.data)

        # Bad name.
        data['rpi_location'] = '5, 60, 0, '
        out = self.app.post('/settings', data=data)
        self.assertIn('Form had errors', out.data)
        self.assertIn('A location needs a human readable name.',
                      out.data)

    def test_setting_location_successfully(self):
        out = self.app.post('/settings', data={
            'rpi_sample_time': 12,
            'rpi_control_panel_host': '0.0.0.0',
            'rpi_control_panel_port': 50,
            'rpi_sds011': '/dev/foo',
            'rpi_location': '50.0, 3.0, 0, Somewhere else',
        })
        self.assertIn('Settings saved.', out.data)

        loc = self.iface.device_info['location']
        self.assertEqual(50, loc['latitude'])
        self.assertEqual(3, loc['longitude'])
        self.assertEqual(0, loc['altitude'])
        self.assertEqual('Somewhere else', loc['name'])

    def test_adding_location_when_offline(self):
        # Make set_settings raise
        self.iface.fails = True
        data = {
            'rpi_sample_time': 12,
            'rpi_control_panel_host': '0.0.0.0',
            'rpi_control_panel_port': 50,
            'rpi_sds011': '/dev/foo',
            'rpi_location': '5, 60, 0, Bergen E Fin',
        }
        out = self.app.post('/settings', data=data)
        self.assertIn('Settings saved.', out.data)
        self.assertIn('Setting the location failed: Was asked to fail.',
                      out.data)

    def test_do_not_recreate_locations(self):
        self.iface.settings = dict(rpi_sample_time=2)
        loc = self.iface.device_info['location']
        data = {
            'rpi_sample_time': 12,
            'rpi_control_panel_host': '0.0.0.0',
            'rpi_control_panel_port': 50,
            'rpi_sds011': '/dev/foo',
            'rpi_location': '%f, %f, %f, %s' % (
                loc['latitude'], loc['longitude'], loc['altitude'],
                'some new name',
            ),
        }
        self.app.post('/settings', data=data)

        # Name should not have changed. This is a bad way to assert this,
        # but fine for now.
        self.assertEqual('Bergen By E Nydeli',
                         self.iface.device_info['location']['name'])

        # Other changed settings should change.
        self.assertEqual(12, self.iface.settings['rpi_sample_time'])

    def test_no_settings_without_device_id(self):
        self.iface.device_id = None
        out = self.app.get('/', follow_redirects=True)
        self.assertIn('Not registered', out.data)


if __name__ == '__main__':
    unittest.main()
