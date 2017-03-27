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
import dbus
import subprocess
from friskby import DeviceConfig

SYSTEMD_UNIT_IFACE = 'org.freedesktop.systemd1.Unit'
SYSTEMD_MANAGER_IFACE = 'org.freedesktop.systemd1.Manager'
DBUS_PROPERTIES_IFACE = 'org.freedesktop.DBus.Properties'


# See https://wiki.freedesktop.org/www/Software/systemd/dbus/ for how this was
# defined.
class ActiveState():
    ACTIVE = 1
    RELOADING = 2
    INACTIVE = 3
    FAILED = 4
    ACTIVATING = 5
    DEACTIVATING = 6


class SystemdDBus():

    def __init__(self):
        self.sysbus = dbus.SystemBus()
        systemd1 = self.sysbus.get_object('org.freedesktop.systemd1',
                                          '/org/freedesktop/systemd1')
        self.manager = dbus.Interface(systemd1, SYSTEMD_MANAGER_IFACE)

    def get_unit_status(self, unit):
        """Returns a UnitStatus or None if unit not installed.

            type UnitStatus struct {
                Name, Description, LoadState, ActiveState, SubState, Followed,
                Path, JobId, JobType, JobPath
            }
        """
        active_units = self.manager.ListUnitsFiltered(['active'])
        for ret in active_units:
            if ret[0] == unit:
                return ret
        return None


class FriskbyInterface():

    def __init__(self):
        self.systemd = SystemdDBus()

    def _service_to_unit(self, service):
        """Returns a unit or None if the service wasn't pertinent."""
        known_units = {
            'friskby': 'friskby.service',
            'sampler': 'rsyslog.service',
            'submitter': 'friskby-submitter.service',
        }
        return known_units.get(service, None)

    def download_and_save_config(self, url, filename):
        config = DeviceConfig.download(url)
        config.save(filename=filename)

    def get_service_status(self, service):
        unit = self._service_to_unit(service)

        if service is None:
            raise ValueError('%s is not a pertinent service.' % service)

        status = self.systemd.get_unit_status(unit)
        try:
            return status[3]
        except TypeError:
            return None

    def get_service_journal(self, service):
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
            print(e)

        return content

    def are_we_polling_yet(self):
        pass

    def get_device_id(self, filename):
        """Returns the device id, or None."""
        config = DeviceConfig(filename)
        device_id = config.getDeviceID()
        if device_id == "" or device_id is None:
            return None
        return device_id
