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
import inspect
from . import ctljson
from .friskby_interface import FriskbyInterface
from flask import (Flask, request, redirect, url_for, render_template)  # noqa

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    FRISKBY_ROOT_URL='https://friskby.herokuapp.com',
    FRISKBY_SENSOR_PATH='/sensor/api/device',
    FRISKBY_DEVICE_CONFIG_PATH='/usr/local/friskby/etc/config.json',
    FRISKBY_INTERFACE=FriskbyInterface
))
app.config.from_envvar('FRISKBY_CONTROLPANEL_SETTINGS', silent=True)


@app.before_request
def before_request():
    """Initializes the friskby interface if it wasn't already."""
    iface = app.config['FRISKBY_INTERFACE']
    if inspect.isclass(iface):
        app.config['FRISKBY_INTERFACE'] = iface()


@app.context_processor
def inject_device_id():
    """Injects the device_id into the template context, or None if none."""
    filename = app.config['FRISKBY_DEVICE_CONFIG_PATH']
    try:
        device_id = app.config['FRISKBY_INTERFACE'].get_device_id(filename)
    except IOError:
        device_id = None
    return dict(device_id=device_id)


@app.context_processor
def inject_statuses():
    """Injects the friskby system service statuses into the template context.
    """
    fby_iface = app.config['FRISKBY_INTERFACE']
    sampler_status = fby_iface.get_service_status('sampler')
    submitter_status = fby_iface.get_service_status('submitter')
    friskby_status = fby_iface.get_service_status('friskby')
    return {
        'sampler_status': sampler_status,
        'submitter_status': submitter_status,
        'friskby_status': friskby_status
    }


@app.route('/')
def dashboard():
    """Renders the dashboard. Will redirect to device registration if no
    device_id was found."""
    fby_iface = app.config['FRISKBY_INTERFACE']
    config_path = app.config['FRISKBY_DEVICE_CONFIG_PATH']

    try:
        device_id = fby_iface.get_device_id(config_path)
    except IOError:
        device_id = None

    # No device, so redirect to the register page.
    if not device_id:
        return redirect(url_for('register'))

    sockname = fby_iface.get_socket_iface_name()
    return render_template(
        'dashboard.html',
        has_sampled=fby_iface.get_all_samples_count() > 0,
        has_uploaded=fby_iface.get_uploaded_samples_count() > 0,
        most_recent_sample=fby_iface.get_most_recently_sampled(),
        most_recent_upload=fby_iface.get_most_recently_uploaded(),
        socket_iface_address=sockname)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Renders a page whereon you can register a device."""
    fby_iface = app.config['FRISKBY_INTERFACE']
    config_path = app.config['FRISKBY_DEVICE_CONFIG_PATH']
    error = None

    try:
        device_id = fby_iface.get_device_id(config_path)
    except IOError:
        device_id = None

    if request.method == 'POST' and device_id:
        return redirect(url_for('dashboard'))
    elif request.method == 'POST' and not device_id:
        if request.form['deviceid'] == "":
            error = 'No device id'
        else:
            device_id = request.form['deviceid']
            sensor_path = app.config['FRISKBY_SENSOR_PATH']
            root_url = app.config['FRISKBY_ROOT_URL']
            config_url = root_url + "%s/%s/" % (sensor_path, device_id)
            print("Fetching config for device %s from: %s" % (device_id,
                                                              config_url))
            sys.stdout.flush()
            try:
                fby_iface.download_and_save_config(config_url, config_path)
                return redirect(url_for('registered'))
            except ValueError as e:
                error = "Failed to download configuration: %s" % e
                print(error)
                sys.stdout.flush()

    return render_template('register.html', error=error)


@app.route('/registered')
def registered():
    """Renders a “your device is registered template”."""
    return render_template('registered.html')


@app.route('/service/<string:service_name>')
def status(service_name):
    """Renders a service given a service_name."""
    iface = app.config['FRISKBY_INTERFACE']
    error = None
    service_status = None
    service_journal = []

    try:
        service_status = iface.get_service_status(service_name)
        service_journal = iface.get_service_journal(service_name)
    except KeyError as e:
        error = 'No such service: %s (%s).' % (service_name, e)
        print(error)
        sys.stdout.flush()
    else:  # There could be something in the journal at this point.
        for key in ctljson.KEYS:
            for entry in service_journal:
                if key in entry:
                    export_key = ctljson.KEYS[key]
                    entry[export_key] = ctljson.parse_message(
                        export_key, entry[key]
                    )

    return render_template(
        'service.html',
        error=error,
        name=service_name,
        status=service_status,
        journal=service_journal
    )
