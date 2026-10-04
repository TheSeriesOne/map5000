"""Button platform for Bosch MAP 5000."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_API, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MAP 5000 buttons."""
    api = hass.data[DOMAIN][entry.entry_id][DATA_API]

    async_add_entities(
        [
            Map5000ResetButton(api=api, entry_id=entry.entry_id),
            Map5000SilenceButton(api=api, entry_id=entry.entry_id),
            Map5000WalktestStartButton(api=api, entry_id=entry.entry_id),
            Map5000WalktestStopButton(api=api, entry_id=entry.entry_id),
        ]
    )


class Map5000ResetButton(ButtonEntity):
    """Button to handle/reset open MAP 5000 incidents."""

    _attr_has_entity_name = True
    _attr_name = "Zurücksetzen"
    _attr_icon = "mdi:restore-alert"

    def __init__(self, api, entry_id: str) -> None:
        """Initialize reset button."""
        self._api = api
        self._attr_unique_id = f"{entry_id}_reset"

    async def async_press(self) -> None:
        """Handle/reset open MAP 5000 incidents."""
        _LOGGER.warning("MAP5000: Zurücksetzen ausgelöst")
        await self._api.handle_incidents()


class Map5000SilenceButton(ButtonEntity):
    """Signalgeber aktiver MAP 5000 Incidents ausschalten."""

    _attr_has_entity_name = True
    _attr_name = "Signalgeber aus"
    _attr_icon = "mdi:volume-off"

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_silence"

    async def async_press(self) -> None:
        _LOGGER.warning("MAP5000: Signalgeber aus ausgelöst")
        await self._api.silence_incidents()


class Map5000WalktestStartButton(ButtonEntity):
    """MAP 5000 Begehtest starten."""

    _attr_has_entity_name = True
    _attr_name = "Begehtest starten"
    _attr_icon = "mdi:walk"

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_walktest_start"

    async def async_press(self) -> None:
        _LOGGER.warning("MAP5000: Begehtest starten")
        await self._api.start_walktest()


class Map5000WalktestStopButton(ButtonEntity):
    """MAP 5000 Begehtest beenden."""

    _attr_has_entity_name = True
    _attr_name = "Begehtest beenden"
    _attr_icon = "mdi:stop-circle-outline"

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_walktest_stop"

    async def async_press(self) -> None:
        _LOGGER.warning("MAP5000: Begehtest beenden")
        await self._api.stop_walktest()
