# -*- coding: utf-8 -*-
"""
    Friskby Controlpanel

    A webapp that allows for configuration of a friskby system on a device.

    (c) 2017 FriskbyBergen.
    (c) 2015 by Armin Ronacher.

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
from friskby_interface import FriskbyInterface
from flask import (Flask, request, redirect, g, url_for, render_template)  # noqa

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    FRISKBY_ROOT_URL='https://friskby.herokuapp.com',
    FRISKBY_SENSOR_PATH='/sensor/api/device',
    FRISKBY_DEVICE_CONFIG_PATH='/usr/local/friskby/etc/config.json',
    FRISKBY_INTERFACE=FriskbyInterface()
))
app.config.from_envvar('FRISKBY_CONTROLPANEL_SETTINGS', silent=True)


@app.context_processor
def inject_device_id():
    filename = app.config['FRISKBY_DEVICE_CONFIG_PATH']
    try:
        device_id = app.config['FRISKBY_INTERFACE'].get_device_id(filename)
    except IOError:
        device_id = None
    return dict(device_id=device_id)


@app.context_processor
def inject_statuses():
    fby_iface = app.config['FRISKBY_INTERFACE']
    sampler_status = fby_iface.get_service_status('sampler')
    return {
        'sampler_status': sampler_status,
        'submitter_status': 'n/a',
        'friskby_status': 'n/a'
    }


# @app.teardown_appcontext
# def close_db(error):
#     """Closes the database again at the end of the request."""
#     if hasattr(g, 'sqlite_db'):
#         g.sqlite_db.close()


@app.route('/', methods=['GET', 'POST'])
def dashboard():
    fby_iface = app.config['FRISKBY_INTERFACE']
    config_path = app.config['FRISKBY_DEVICE_CONFIG_PATH']

    try:
        device_id = fby_iface.get_device_id(config_path)
    except IOError:
        device_id = None

    register_device = device_id is None

    error = None

    if request.method == 'POST' and register_device:
        if request.form['deviceid'] == "":
            error = 'No device id'
        else:
            device_id = request.form['deviceid']
            sensor_path = app.config['FRISKBY_SENSOR_PATH']
            root_url = app.config['FRISKBY_ROOT_URL']
            config_url = root_url + "%s/%s/" % (sensor_path, device_id)
            print("Fetching config for device %s from: %s" % (device_id,
                                                              config_url))
            try:
                fby_iface.download_and_save_config(config_url, config_path)
                return redirect(url_for('registered'))
            except Exception as e:
                error = "Failed to download configuration: %s" % e
                print(error)
                register_device = True

    sys.stdout.flush()
    return render_template('dashboard.html',
                           error=error,
                           register_device=register_device)


@app.route('/registered')
def registered():
    return render_template('registered.html')


@app.route('/service/<string:service_name>')
def status(service_name):
    iface = app.config['FRISKBY_INTERFACE']
    error = None
    service_status = None
    service_journal = None

    try:
        service_status = iface.get_service_status(service_name)
        service_journal = iface.get_service_journal(service_name)
    except ValueError as e:
        print(e)
        error = 'No such service: %s.' % service_name

    return render_template(
        'service.html',
        error=error,
        name=service_name,
        status=service_status,
        journal=service_journal
    )
