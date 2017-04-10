# -*- coding: utf-8 -*-
"""
    Parses journalctl json output.

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
from datetime import datetime as dt
from datetime import timedelta as td


KEYS = {
    '__REALTIME_TIMESTAMP': 'timestamp_realtime',
    '__MONOTONIC_TIMESTAMP': 'timestamp_monotonic',
    'MESSAGE': 'message',
    'SYSLOG_IDENTIFIER': 'executable',
    '_SYSTEMD_UNIT': 'service'
}
PIDKEY = '_PID'


def from_timestamp(stamp, monotonic=False):
    int_stamp = int(stamp) // 1000000  # remove micro second
    if not monotonic:
        time_stamp = dt.fromtimestamp(int_stamp)
        iso_format = '%Y-%m-%d %H:%M:%S'
        return time_stamp.strftime(iso_format)
    else:
        delta = td(seconds=int_stamp)
        return str(delta)


def parse_message(k, v):
    if 'timestamp' in k:
        mono = 'monotonic' in k
        return from_timestamp(v, monotonic=mono)
    return v
