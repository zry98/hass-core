"""
The rest binary sensor will consume responses sent by an exposed REST API.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/binary_sensor.rest/
"""
import logging

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.components.sensor.rest import RestData
from homeassistant.const import CONF_VALUE_TEMPLATE
from homeassistant.util import template

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'REST Binary Sensor'
DEFAULT_METHOD = 'GET'


# pylint: disable=unused-variable
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup REST binary sensors."""
    resource = config.get('resource', None)
    method = config.get('method', DEFAULT_METHOD)
    payload = config.get('payload', None)
    verify_ssl = config.get('verify_ssl', True)

    rest = RestData(method, resource, payload, verify_ssl)
    rest.update()

    if rest.data is None:
        _LOGGER.error('Unable to fetch Rest data')
        return False

    add_devices([RestBinarySensor(
        hass, rest, config.get('name', DEFAULT_NAME),
        config.get(CONF_VALUE_TEMPLATE))])


# pylint: disable=too-many-arguments
class RestBinarySensor(BinarySensorDevice):
    """A REST binary sensor."""

    def __init__(self, hass, rest, name, value_template):
        """Initialize a REST binary sensor."""
        self._hass = hass
        self.rest = rest
        self._name = name
        self._state = False
        self._value_template = value_template
        self.update()

    @property
    def name(self):
        """Name of the binary sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self.rest.data is None:
            return False

        if self._value_template is not None:
            self.rest.data = template.render_with_possible_json_value(
                self._hass, self._value_template, self.rest.data, False)
        return bool(int(self.rest.data))

    def update(self):
        """Get the latest data from REST API and updates the state."""
        self.rest.update()
