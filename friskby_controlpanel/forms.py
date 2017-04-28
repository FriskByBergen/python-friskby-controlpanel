from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired


class SettingsForm(FlaskForm):
    rpi_sample_time = IntegerField(
        'rpi_sample_time',
        validators=[DataRequired()]
    )
    rpi_control_panel_host = StringField(
        'rpi_control_panel_host',
        validators=[DataRequired()]
    )
    rpi_control_panel_port = IntegerField(
        'rpi_control_panel_port',
        validators=[DataRequired()]
    )
    rpi_sds011 = StringField(
        'rpi_sds011',
        validators=[DataRequired()]
    )
