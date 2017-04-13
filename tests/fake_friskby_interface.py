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

    def get_service_journal(self, service):
        if service == 'sampler':
            return self.sampler_journal
        else:
            return []

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
