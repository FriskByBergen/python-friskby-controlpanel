# -*- coding: utf-8 -*-
"""
    Friskby Interface

    In interface between Friskby Control panel, and everything required from
    the rest of the friskby universe.

    Note that this fake interface only considers the 'submitter' service to
    be worthy mocking. It also will only consider the 'restart' action.

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


class FakeFriskbyInterface():

    def __init__(self):
        self.fails = False
        self.device_id = None

        self.uploaded_samples_count = 0
        self.all_samples_count = 0

        self.most_recently_uploaded = None
        self.most_recently_sampled = None

        self.sampler_status = None
        self.sampler_journal = []
        self.socket = None

        self.settings = dict()

    def _check_service(self, service_name):
        services = ['sampler', 'submitter', 'friskby', 'friskby_controlpanel']
        if service_name not in services:
            raise KeyError("No such service")

    def download_and_save_config(self, url, filename):
        if self.fails:
            raise ValueError("Was asked to fail for url %s -> %s." % (
                url, filename
            ))

    def get_device_id(self, _):
        return self.device_id

    def get_service_status(self, service):
        if service == 'sampler':
            return self.sampler_status

        self._check_service(service)

    def get_service_journal(self, service):
        if service == 'sampler':
            return self.sampler_journal
        else:
            return []

        self._check_service(service)

    def manage_service(self, service, action):
        self._check_service(service)

        if action != 'restart':
            raise KeyError('%s is not an action I know of...' % action)

    def get_uploaded_samples_count(self):
        return self.uploaded_samples_count

    def get_all_samples_count(self):
        return self.all_samples_count

    def get_most_recently_uploaded(self):
        return self.most_recently_uploaded

    def get_most_recently_sampled(self):
        return self.most_recently_sampled

    def get_socket_iface_name(self):
        return self.socket

    def get_recent_samples(self):
        limit = 10
        data = []
        for i in range(limit):
            row = (42+i, 42+i/10.0, 'PM10' if i % 2 else 'PM25', dt.now(), 0 if i < 2 else 1)
            data.append(row)
        return data

    def get_settings(self):
        return self.settings

    def set_settings(self, settings):
        self.settings = settings
