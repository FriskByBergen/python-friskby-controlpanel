#!/usr/bin/env python
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
import sys
from friskby_controlpanel import friskby_controlpanel as cp
from tests.fake_friskby_interface import FakeFriskbyInterface


def start_in_test_mode(host, port):
    iface = FakeFriskbyInterface()
    cp.app.config['TESTING'] = True
    cp.app.config['FRISKBY_INTERFACE'] = iface

    iface.device_id = 'test device'
    iface.settings = {
        "rpi_sample_time": 42,
        "rpi_control_panel_host": "example.org",
        "rpi_control_panel_port": "80",
        "rpi_sds011": "/dev/foo/bar/baz"
    }
    iface.sampler_status = 'active'
    iface.sampler_journal = [
        {
            "__REALTIME_TIMESTAMP": "1491213967810472",
            "__MONOTONIC_TIMESTAMP": "8281790",
            "MESSAGE_ID": "7d4958e842da4a758f6c1cdc7b36dcc5",
            "_PID": "1",
            "_COMM": "systemd",
            "_EXE": "/lib/systemd/systemd",
            "_CMDLINE": "/sbin/init splash",
            "UNIT": "rsyslog.service",
            "MESSAGE": "Starting System Logging Service...",
        },
        {
            "__REALTIME_TIMESTAMP": "1491213967813472",
            "__MONOTONIC_TIMESTAMP": "8381790",
            "MESSAGE_ID": "dd4958e842da5321233c13dcdd3cdccd",
            "_PID": "1",
            "_COMM": "systemd",
            "_EXE": "/lib/systemd/systemd",
            "_CMDLINE": "/sbin/init splash",
            "UNIT": "rsyslog.service",
            "MESSAGE": "Doesn't look like anything to me.",
        },
        {
            "__REALTIME_TIMESTAMP": "2491213967813472",
            "__MONOTONIC_TIMESTAMP": "8383790",
            "MESSAGE_ID": "aa4958e842da5321233c13dcdd3cdccd",
            "_PID": "1",
            "_COMM": "systemd",
            "_EXE": "/lib/systemd/systemd",
            "_CMDLINE": "/sbin/init splash",
            "UNIT": "rsyslog.service",
            "MESSAGE": "This is a really really really really really really really really really really really really really really really really really really really long line.",  # noqa
        }
    ]

    cp.app.run(
        debug=True,
        host=host,
        port=int(port)
    )


if __name__ == '__main__':
    port = 5003
    host = '0.0.0.0'
    if len(sys.argv) > 1:
        host = sys.argv[2]
    if len(sys.argv) > 2:
        port = sys.argv[3]

    start_in_test_mode(host, port)
