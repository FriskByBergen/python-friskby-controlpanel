import os
import controlpanel
import unittest
import tempfile


class DeviceSetupTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, controlpanel.app.config['DATABASE'] = tempfile.mkstemp()
        controlpanel.app.config['TESTING'] = True
        self.app = controlpanel.app.test_client()
        with controlpanel.app.app_context():
            controlpanel.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(controlpanel.app.config['DATABASE'])


if __name__ == '__main__':
    unittest.main()
