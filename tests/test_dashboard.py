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
from datetime import datetime
import unittest


class DashboardTestCase(unittest.TestCase):

    def setUp(self):
        self.iface = FakeFriskbyInterface()
        cp.app.config['TESTING'] = True
        cp.app.config['FRISKBY_INTERFACE'] = self.iface
        self.app = cp.app.test_client()

    def test_when_registered_device(self):
        self.iface.device_id = 'mydevice'
        out = self.app.get('/')
        self.assertIn("mydevice", out.data)

    def test_no_sampling_nor_any_upload_has_happened(self):
        self.iface.device_id = 'mydevice'
        out = self.app.get('/')
        self.assertIn(
            """This device is neither sampling, nor uploading anything to the server.""",  # noqa
            out.data
        )

    def test_sampling_but_no_uploading(self):
        self.iface.device_id = 'mydevice'
        self.iface.all_samples_count = 1
        self.iface.most_recently_sampled = datetime(2007, 12, 5, 12, 0, 0)
        out = self.app.get('/')
        self.assertIn(
            """This device is sampling, but has not yet uploaded data to the server. The last sample was taken at 2007-12-05 12:00:00.""",  # noqa
            out.data
        )

    def test_sampling_and_uploading(self):
        self.iface.device_id = 'mydevice'
        self.iface.uploaded_samples_count = 1
        self.iface.all_samples_count = 1
        self.iface.most_recently_uploaded = datetime(2007, 12, 5, 12, 0, 0)
        out = self.app.get('/')
        self.assertIn(
            """This device is sampling, and has uploaded data to the server at 2007-12-05 12:00:00.""",  # noqa
            out.data
        )


    def test_socket_iface_name(self):
        self.iface.device_id = 'mydevice'
        self.assertIn('Could not obtain', self.app.get('/').data)
        self.iface.socket = '27.182.81.82'
        self.assertIn('27.182.81.82', self.app.get('/').data)


if __name__ == '__main__':
    unittest.main()
