import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.const import (
    ATTR_FRIENDLY_NAME, 
    ATTR_UNIT_OF_MEASUREMENT,
    ATTR_ICON, 
    CONF_ENTITIES, 
    CONF_ENTITY_ID,
    EVENT_HOMEASSISTANT_START, 
    STATE_UNKNOWN, 
    STATE_ON, 
    STATE_OFF
)

from .const import (
    DOMAIN,
    CONF_SENSOR_NAME,
    CONF_ENTITIES,
    DEFAULT_SENSOR_NAME
)

_LOGGER = logging.getLogger(__name__)


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema( 
            {
                vol.Required(CONF_ENTITIES): cv.entity_ids,
                vol.Optional(
                    CONF_SENSOR_NAME, default=DEFAULT_SENSOR_NAME
                ): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

## https://gist.github.com/balloob/3e8ae00a2354f4e889c0

def setup(hass, config):
    # Get the text from the configuration. Use DEFAULT_TEXT if no name is provided.
    entities = config[DOMAIN].get(CONF_ENTITIES)
    

    def build_sensors():
        real_lights_entitites = []
        real_lights_on_list = []

        for entity in entities:
            device_state = hass.states.get(entity)

            if device_state is not None:
                real_lights_entitites.append({ "entity_id": entity, "friendly_name": device_state.attributes.get(ATTR_FRIENDLY_NAME) })

            if hass.states.is_state(entity, STATE_ON):
                real_lights_on_list.append({ "entity_id": entity, "friendly_name": device_state.attributes.get(ATTR_FRIENDLY_NAME) })

        sensor_name = config[DOMAIN].get(CONF_SENSOR_NAME)
        hass.states.set("sensor.%s_total" % (sensor_name), len(real_lights_entitites), { "entities": ', '.join(map( lambda entity: entity["entity_id"], real_lights_entitites)), "friendly_names": ', '.join(map( lambda entity: entity["friendly_name"], real_lights_entitites )) })
        hass.states.set("sensor.%s_on" % (sensor_name), len(real_lights_on_list), { "entities": ', '.join(map( lambda entity: entity["entity_id"], real_lights_on_list)), "friendly_names": ', '.join(map( lambda entity: entity["friendly_name"], real_lights_on_list )) } )
        


    def state_changed(event):
        if event.data[CONF_ENTITY_ID] not in entities: return
        build_sensors()
    
    hass.bus.listen('state_changed', state_changed)


    def service_update(call):
        build_sensors()

    hass.services.register(DOMAIN, 'update', service_update)

    

    return True


