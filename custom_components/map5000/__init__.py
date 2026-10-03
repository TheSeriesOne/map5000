from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import service

from .api import Map5000Api
from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    DATA_API,
    DOMAIN,
    PLATFORMS,
)

SERVICE_SPERREN = "sperren"
SERVICE_ENTSPERREN = "entsperren"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """MAP5000-Aktionen registrieren."""

    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_SPERREN,
        entity_domain=BINARY_SENSOR_DOMAIN,
        schema={},
        func="async_sperren",
    )

    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_ENTSPERREN,
        entity_domain=BINARY_SENSOR_DOMAIN,
        schema={},
        func="async_entsperren",
    )

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """MAP5000 Config Entry einrichten."""

    api = Map5000Api(
        entry.data[CONF_HOST],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_API: api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """MAP5000 Config Entry entladen."""

    unloaded = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)

        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)

    return unloaded
