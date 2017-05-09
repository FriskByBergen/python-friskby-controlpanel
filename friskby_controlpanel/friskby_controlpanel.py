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
from flask import (Flask, request, redirect, flash, url_for, render_template)  # noqa
from .friskby_interface import FriskbyInterface
from .forms import SettingsForm
from .friskby_settings import DEVICE_CONFIG_PATH, config_url

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    FRISKBY_ROOT_URL='https://friskby.herokuapp.com',
    FRISKBY_SENSOR_PATH='/sensor/api/device',
    FRISKBY_DEVICE_CONFIG_PATH=DEVICE_CONFIG_PATH,
    FRISKBY_INTERFACE=FriskbyInterface,
    CONFIG_URL=config_url,
    WTF_CSRF_ENABLED=False,
    SUPPORT_URL='https://github.com/FriskByBergen/python-friskby-controlpanel'
))
app.config.from_envvar('FRISKBY_CONTROLPANEL_SETTINGS', silent=True)
app.secret_key = 'we actually do not care too much'


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
    iface = app.config['FRISKBY_INTERFACE']
    (device_id, _) = iface.get_device_id_and_api_key(filename)
    return dict(device_id=device_id)


@app.context_processor
def inject_meta():
    # Injects meta stuff (about the controlpanel) into the context.
    support_url = app.config['SUPPORT_URL']
    return dict(support_url=support_url)


@app.context_processor
def inject_statuses():
    """Injects the friskby system service statuses into the template context.
    """
    fby_iface = app.config['FRISKBY_INTERFACE']
    sampler_status = fby_iface.get_service_status('sampler')
    submitter_status = fby_iface.get_service_status('submitter')
    friskby_status = fby_iface.get_service_status('friskby')
    friskby_controlpanel_status = fby_iface.get_service_status(
        'friskby_controlpanel'
    )
    return {
        'sampler_status': sampler_status,
        'submitter_status': submitter_status,
        'friskby_status': friskby_status,
        'friskby_controlpanel_status': friskby_controlpanel_status,
    }


@app.route('/')
def dashboard():
    """Renders the dashboard. Will redirect to device registration if no
    device_id was found."""
    fby_iface = app.config['FRISKBY_INTERFACE']
    config_path = app.config['FRISKBY_DEVICE_CONFIG_PATH']

    (device_id, _) = fby_iface.get_device_id_and_api_key(config_path)

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
        get_recent_samples=fby_iface.get_recent_samples(),
        socket_iface_address=sockname)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Renders a page whereon you can register a device."""
    fby_iface = app.config['FRISKBY_INTERFACE']
    config_path = app.config['FRISKBY_DEVICE_CONFIG_PATH']
    error = None

    (device_id, _) = fby_iface.get_device_id_and_api_key(config_path)

    if request.method == 'POST' and device_id:
        return redirect(url_for('dashboard'))
    elif request.method == 'POST' and not device_id:
        if request.form['deviceid'] == "":
            error = 'No device id'
        else:
            device_id = request.form['deviceid']
            url = app.config['CONFIG_URL'](device_id)
            print("Fetching config for device %s from: %s" % (device_id, url))
            sys.stdout.flush()
            try:
                fby_iface.download_and_save_config(url, config_path)
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
        flash(error)
        return redirect(url_for('dashboard'))
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


@app.route('/service/<string:service_name>/<string:action_name>',
           methods=['POST'])
def status_manage(service_name, action_name):
    """Manages a service."""
    iface = app.config['FRISKBY_INTERFACE']

    try:
        iface.manage_service(service_name, action_name)
    except KeyError:
        error = 'No such service (%s) or action (%s).' % (service_name,
                                                          action_name)
        print(error)
        sys.stdout.flush()
        flash(error)
        return redirect(url_for('dashboard'))

    flash('Requested %s on service %s.' % (action_name, service_name))
    return redirect(url_for('status', service_name=service_name))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Displays and allows changing of settings."""
    iface = app.config['FRISKBY_INTERFACE']
    config_path = app.config['FRISKBY_DEVICE_CONFIG_PATH']
    (device_id, api_key) = iface.get_device_id_and_api_key(config_path)

    # No device, so redirect to the register page.
    if not device_id:
        flash('Please register your device before tuning settings.')
        return redirect(url_for('register'))

    # Get location from friskby.
    device_info_uri = "%s/%s/%s" % (app.config['FRISKBY_ROOT_URL'],
                                    app.config['FRISKBY_SENSOR_PATH'],
                                    device_id)
    device_info = iface.get_device_info(device_info_uri)
    location = None
    try:
        loc = device_info['location']
        location = (loc['latitude'], loc['longitude'], 0, loc['name'])
    except TypeError:
        print("Failed to get location of device from friskby.")
        sys.stdout.flush()

    form = None

    if request.method == 'GET':
        data = iface.get_settings()
        data['rpi_location'] = location
        form = SettingsForm(data=data)
    else:
        form = SettingsForm()  # defaults to flask.request.form
        if form.validate_on_submit():
            flash('Settings saved.')
            iface.set_settings(form.data)

            # Attempts to set the location only if it has changed.
            if not _compare_locations(location,
                                      form.rpi_location.get_location()):
                try:
                    field = form.rpi_location
                    api_uri = "%s/%s/%s/" % (
                        app.config['FRISKBY_ROOT_URL'],
                        'sensor/api/location/create',
                        device_id
                    )
                    iface.set_location(
                        field.get_latitude(), field.get_longitude(),
                        field.get_altitude(), field.get_name(), api_uri,
                        api_key)
                except RuntimeError as e:
                    flash('Setting the location failed: %s' % e)

        else:
            flash('Form had errors.')

    return render_template(
        'settings.html', form=form, errors=form.errors
    )


def _compare_locations(a, b):
    # Returns true if strictly equal. Name is ignored.
    return a[0] == b[0] and a[1] == b[1] and a[2] == b[2]
