import os
from friskby_controlpanel import friskby_controlpanel as cp
from fake_friskby_interface import FakeFriskbyInterface
import unittest
import tempfile


class DeviceSetupTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, cp.app.config['DATABASE'] = tempfile.mkstemp()
        cp.app.config['FRISKBY_INTERFACE'] = FakeFriskbyInterface()
        cp.app.config['TESTING'] = True
        self.app = cp.app.test_client()
        with cp.app.app_context():
            cp.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(cp.app.config['DATABASE'])

    def test_the_dash(self):
        out = self.app.get('/')
        assert b'Device id' in out.data

    def test_trying_to_register_nulldevice(self):
        out = self.app.post('/', data=dict({
            "deviceid": ""
        }), follow_redirects=True)
        assert b'No device id' in out.data

    def test_successful_registering_of_device(self):
        out = self.app.post('/', data=dict({
            "deviceid": "my-device-id"
        }), follow_redirects=True)
        assert b'Device now registered' in out.data

    def test_registering_a_device_but_it_fails_miserably(self):
        cp.app.config['FRISKBY_INTERFACE'].fails = True
        out = self.app.post('/', data=dict({
            "deviceid": "my-device-id"
        }), follow_redirects=True)
        assert b'Error' in out.data


if __name__ == '__main__':
    unittest.main()
