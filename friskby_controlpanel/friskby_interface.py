# -*- coding: utf-8 -*-
"""
    Friskby Interface

    In interface between Friskby Control panel, and everything required from
    the rest of the friskby universe.

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

try:
    import dbus
except ImportError:
    raise ImportError('Please install python-dbus.')

import subprocess
import sys
from friskby import DeviceConfig, FriskbyDao
from rpiparticle import get_setting

SYSTEMD_NAME = 'org.freedesktop.systemd1'
SYSTEMD_OBJ = '/org/freedesktop/systemd1'
SYSTEMD_UNIT_IFACE = 'org.freedesktop.systemd1.Unit'
SYSTEMD_MANAGER_IFACE = 'org.freedesktop.systemd1.Manager'
DBUS_PROPERTIES_IFACE = 'org.freedesktop.DBus.Properties'


# Represents a systemd DBus proxy as needed by the control panel.
class SystemdDBus():

    def __init__(self):
        self.sysbus = dbus.SystemBus()
        systemd1 = self.sysbus.get_object(SYSTEMD_NAME, SYSTEMD_OBJ)
        self.manager = dbus.Interface(systemd1, SYSTEMD_MANAGER_IFACE)

    def get_unit_status(self, unit):
        """Returns a UnitStatus or None if unit not installed.

            type UnitStatus struct {
                Name, Description, LoadState, ActiveState, SubState, Followed,
                Path, JobId, JobType, JobPath
            }
        """
        active_units = self.manager.ListUnits()
        for ret in active_units:
            if ret[0] == unit:
                return ret
        return None


# Glues DBus, python-friskby and other pertinent things together so as to
# hide implementation details from the control panel.
class FriskbyInterface():

    def __init__(self):
        self.systemd = SystemdDBus()
        self.dao = FriskbyDao(get_setting("rpi_db"))

    def _service_to_unit(self, service):
        """Returns a unit or None if the service wasn't pertinent to the
        friskby system."""
        known_units = {
            'friskby': 'friskby.service',
            'sampler': 'friskby-sampler.service',
            'submitter': 'friskby-submitter.service',
        }
        return known_units.get(service, None)

    def download_and_save_config(self, url, filename):
        """Downloads config from url and saves it to the given filename."""
        config = DeviceConfig.download(url)
        config.save(filename=filename)

    def get_service_status(self, service):
        """Returns the unit status as defined by [1]. Only services pertinent
        to the friskby system will be considered.
        [1] https://www.freedesktop.org/wiki/Software/systemd/dbus/
        """
        unit = self._service_to_unit(service)

        if service is None:
            raise ValueError('%s is not a pertinent service.' % service)

        status = self.systemd.get_unit_status(unit)
        try:
            return status[3]
        except TypeError:
            return None

    def get_service_journal(self, service):
        """Returns the full output from journalctl where unit is the given
        service. Only services pertinent to the friskby system will be
        considered."""
        unit = self._service_to_unit(service)

        if service is None:
            raise ValueError('%s is not a pertinent service.' % service)

        content = None

        try:
            content = subprocess.check_output([
                "journalctl",
                "--unit=%s" % unit,
                "--catalog",
                "--full",
                "--all",
                "--no-pager"
            ])
        except subprocess.CalledProcessError as e:
            """This means we got a non-zero exit code from journalctl. We can
            do naught but log."""
            print("Failed to capture journalctl output for %s:"
                  " %s exited with %d.\nOutput:%s" % (e.cmd,
                                                      int(e.returncode),
                                                      e.output))
            sys.stdout.flush()

        return content

    def get_device_id(self, filename):
        """Returns the device id, or None."""
        config = DeviceConfig(filename)
        device_id = config.getDeviceID()
        if device_id == "" or device_id is None:
            return None
        return device_id

    def get_uploaded_samples_count(self):
        fetch_uploaded = True
        return self.dao.get_num_rows(fetch_uploaded)

    def get_all_samples_count(self):
        return self.dao.get_num_rows()

    def get_most_recently_uploaded(self):
        fetch_uploaded_entry = True
        return self.dao.last_entry(fetch_uploaded_entry)

    def get_most_recently_sampled(self):
        return self.dao.last_entry()
