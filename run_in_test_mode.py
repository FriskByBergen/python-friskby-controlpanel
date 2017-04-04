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

    iface.device_id = 'mydevice'
    iface.sampler_status = 'active'
    iface.sampler_journal = 'Doesn\'t look like anything to me.'

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
