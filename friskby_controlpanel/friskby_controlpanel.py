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
import os
import sqlite3
from friskby_interface import FriskbyInterface
from flask import (Flask, request, redirect, g, url_for, render_template)

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'data.db'),
    FRISKBY_ROOT_URL='https://friskby.herokuapp.com',
    FRISKBY_SENSOR_PATH='/sensor/api/device',
    FRISKBY_INTERFACE=FriskbyInterface()
))
app.config.from_envvar('FRISKBY_CONTROLPANEL_SETTINGS', silent=True)


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['GET', 'POST'])
def dashboard():
    error = None
    device_id = None
    if request.method == 'POST':
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
                app.config['FRISKBY_INTERFACE'].download_and_save_config(
                    config_url,
                    os.path.join("/usr/local/friskby", "etc/config.json")
                )
                return redirect(url_for('registered'))
            except Exception as e:
                error = "Failed to download configuration: %s" % e
                return render_template('dashboard.html', error=error)
    return render_template('dashboard.html', error=error)


@app.route('/registered')
def registered():
    return render_template('registered.html')
