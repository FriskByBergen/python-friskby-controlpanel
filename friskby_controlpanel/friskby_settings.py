ROOT_URL           = 'https://friskby.herokuapp.com'
SENSOR_PATH        = '/sensor/api/device'
DEVICE_CONFIG_PATH = '/usr/local/friskby/etc/config.json'

def config_url(device_id):
    return ROOT_URL + "%s/%s/" % (SENSOR_PATH, device_id)
