from flask_wtf import FlaskForm
from wtforms import Field, IntegerField, StringField
from wtforms.validators import InputRequired, ValidationError
from wtforms.widgets import TextInput


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def validate_lat_lon_alt_name(_, field):
    lat, lon, altitude, name = field.data
    if not is_number(lat) or float(lat) < -90 or float(lat) > 90:
        raise ValidationError(
            'Latitude must be a number between -90 and 90.'
        )
    elif not is_number(lon) or float(lon) < -180 or float(lon) > 180:
        raise ValidationError(
            'Longitude must be a number between -180 and 180.'
        )
    elif not is_number(altitude):
        raise ValidationError(
            'Altitude must be a number, or 0 if not known.'
        )
    elif not name:
        raise ValidationError('A location needs a human readable name.')


class LocationField(Field):
    # A comma separated list of lat, lon, altitude, name.
    widget = TextInput()

    def __init__(self, label='', validators=None, **kwargs):
        super(LocationField, self).__init__(
            label, [InputRequired(), validate_lat_lon_alt_name], **kwargs
        )
        self.data = None
        self.location = None

    def _value(self):
        if self.data:
            lat, lon, alt, name = self.data
            try:
                lat = float(lat)
                lon = float(lon)
                alt = float(alt)
            except ValueError:
                return u''
            # Note the loss of precision here. The default precision for %f is
            # 6, but that is enough precision (11cm).
            return u'%f, %f, %f, %s' % (float(lat), float(lon), float(alt),
                                        name)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = tuple(map(unicode.strip, valuelist[0].split(',')))

            t = self.data
            self.location = (float(t[0]), float(t[1]), float(t[2]), t[3])
        else:
            self.data = (0.0, 0.0, 0.0, "")

    def get_latitude(self):
        return self.location[0]

    def get_longitude(self):
        return self.location[1]

    def get_altitude(self):
        return self.location[2]

    def get_name(self):
        return self.location[3]

    def get_location(self):
        return self.location


class SettingsForm(FlaskForm):
    rpi_sample_time = IntegerField(
        'rpi_sample_time',
        validators=[InputRequired()]
    )
    rpi_control_panel_host = StringField(
        'rpi_control_panel_host',
        validators=[InputRequired()]
    )
    rpi_control_panel_port = IntegerField(
        'rpi_control_panel_port',
        validators=[InputRequired()]
    )
    rpi_sds011 = StringField(
        'rpi_sds011',
        validators=[InputRequired()]
    )
    rpi_location = LocationField('rpi_location')
