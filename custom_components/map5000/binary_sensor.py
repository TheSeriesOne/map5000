import asyncio
import logging

from homeassistant.const import EVENT_LOGBOOK_ENTRY

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DATA_API, DOMAIN

_LOGGER = logging.getLogger(__name__)


SUPPORTED_TYPES = (
    ".Point.",
    ".PowerSupply.",
    ".Gateway.",
    ".SystemKeypad.",
)


def find_devices(value):
    """Unterstützte MAP-Objekte rekursiv aus /config lesen."""
    devices = []

    if isinstance(value, dict):
        siid = value.get("siid")

        if isinstance(siid, str) and any(
            marker in siid for marker in SUPPORTED_TYPES
        ):
            devices.append(value)

        for child in value.values():
            devices.extend(find_devices(child))

    elif isinstance(value, list):
        for child in value:
            devices.extend(find_devices(child))

    return devices


def get_device_type(siid):
    if ".Point." in siid:
        return "Point"

    if ".PowerSupply." in siid:
        return "PowerSupply"

    if ".Gateway." in siid:
        return "Gateway"

    if ".SystemKeypad." in siid:
        return "SystemKeypad"

    return "Unknown"


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.warning("MAP5000: automatische Geräteerkennung gestartet")

    api = hass.data[DOMAIN][entry.entry_id][DATA_API]

    config = await api.get_config()
    device_configs = find_devices(config)

    unique_devices = {}

    for device in device_configs:
        siid = device.get("siid")

        if siid:
            unique_devices[siid] = device

    _LOGGER.warning(
        "MAP5000: %s unterstützte Objekte gefunden",
        len(unique_devices),
    )

    entities = []
    entities_by_url = {}

    for siid, device_config in unique_devices.items():
        device_url = "/" + siid
        name = device_config.get("name") or siid
        device_type = get_device_type(siid)

        try:
            state = await api.get_point(device_url)

        except Exception:
            _LOGGER.exception(
                "MAP5000: %s (%s) konnte nicht gelesen werden",
                name,
                siid,
            )
            continue

        entity = Map5000Device(
            name=name,
            siid=siid,
            device_url=device_url,
            device_type=device_type,
            state=state,
            api=api,
        )

        entities.append(entity)
        entities_by_url[device_url] = entity

        _LOGGER.warning(
            "MAP5000: %s gefunden: %s | %s | opState=%r active=%r",
            device_type,
            name,
            siid,
            state.get("opState"),
            state.get("active"),
        )

    if not entities:
        _LOGGER.error("MAP5000: Keine unterstützten Objekte gefunden")
        return

    async_add_entities(entities)

    urls = list(entities_by_url)

    # Auch Bereiche über dieselbe MAP-Live-Subscription überwachen.
    area_data = await api.get_point("/areas")
    for area_state in area_data.get("list", []):
        area_url = area_state.get("@self")
        if (
            isinstance(area_url, str)
            and (".Area." in area_url or ".ControlPanelArea." in area_url)
            and area_url not in urls
        ):
            urls.append(area_url)

    await api.create_subscription(urls)

    _LOGGER.warning(
        "MAP5000: Live-Subscription für %s Objekte erstellt",
        len(urls),
    )

    async def event_loop():
        _LOGGER.warning("MAP5000: Live Event Loop gestartet")

        while True:
            try:
                data = await api.fetch_events()

                for event in data.get("evts", []):
                    evt = event.get("evt", {})
                    device_url = evt.get("@self")

                    # MAP-Ereignis auch anderen Plattformen bereitstellen.
                    hass.bus.async_fire(
                        "map5000_object_changed",
                        {
                            "url": device_url,
                            "state": evt,
                        },
                    )

                    entity = entities_by_url.get(device_url)

                    if entity is None:
                        continue

                    entity.update_from_event(evt)

                    _LOGGER.warning(
                        "MAP5000 LIVE: %s | Zustand=%s",
                        entity.name,
                        entity.map_state,
                    )

            except asyncio.CancelledError:
                _LOGGER.warning("MAP5000: Event Loop beendet")
                raise

            except Exception:
                _LOGGER.exception("MAP5000: Fehler im Event Loop")
                await asyncio.sleep(5)

                try:
                    await api.create_subscription(urls)

                except Exception:
                    _LOGGER.exception(
                        "MAP5000: Subscription konnte nicht erneuert werden"
                    )
                    await asyncio.sleep(5)

    task = hass.async_create_background_task(
        event_loop(),
        "map5000_event_listener",
    )

    entry.async_on_unload(lambda: (task.cancel(), None)[1])


class Map5000Device(BinarySensorEntity):
    _attr_should_poll = False

    def __init__(
        self,
        name,
        siid,
        device_url,
        device_type,
        state,
        api,
    ):
        self._attr_name = name
        self._attr_unique_id = f"map5000_{siid}"
        self._siid = siid
        self._device_url = device_url
        self._device_type = device_type
        self._api = api

        self._active = bool(state.get("active", False))
        self._enabled = bool(state.get("enabled", True))
        self._bypassed = bool(state.get("bypassed", False))
        self._activated = state.get("activated")
        self._op_state = state.get("opState", "OK")

        self._update_binary_state()

    @property
    def map_state(self):
        if self._device_type == "Point":
            return "Offen" if self._active else "Geschlossen"

        return "Ruhe" if self._op_state == "OK" else "Störung"

    @property
    def extra_state_attributes(self):
        attributes = {
            "Zustand": self.map_state,
            "Gesperrt": "Nein" if self._enabled else "Ja",
            "SIID": self._siid,
            "Typ": self._device_type,
        }

        if self._bypassed:
            attributes["Bypass"] = "Ja"

        if self._activated is not None:
            attributes["Aktiviert"] = (
                "Ja" if self._activated else "Nein"
            )

        return attributes

    def _update_binary_state(self):
        if self._device_type == "Point":
            self._attr_is_on = self._active
        else:
            # ON bedeutet bei technischen Geräten: Störung vorhanden
            self._attr_is_on = self._op_state != "OK"

    def _log_sperrstatus(self):
        """Sperrstatus im Home-Assistant-Aktivitätsverlauf protokollieren."""
        if self.hass is None:
            return

        status = "Entsperrt" if self._enabled else "Gesperrt"

        self.hass.bus.async_fire(
            EVENT_LOGBOOK_ENTRY,
            {
                "name": self.name,
                "message": status,
                "domain": "map5000",
                "entity_id": self.entity_id,
            },
        )

    def update_from_event(self, evt):
        changed = False

        if "active" in evt:
            self._active = bool(evt["active"])
            changed = True

        if "enabled" in evt:
            old_enabled = self._enabled
            self._enabled = bool(evt["enabled"])
            changed = True

            if old_enabled != self._enabled and self.hass is not None:
                self.hass.bus.async_fire(
                    "map5000_sperrstatus",
                    {
                        "entity_id": self.entity_id,
                        "name": self.name,
                        "siid": self._siid,
                        "status": "Entsperrt" if self._enabled else "Gesperrt",
                        "enabled": self._enabled,
                    },
                )
                self._log_sperrstatus()

        if "bypassed" in evt:
            self._bypassed = bool(evt["bypassed"])
            changed = True

        if "activated" in evt:
            self._activated = bool(evt["activated"])
            changed = True

        if "opState" in evt:
            self._op_state = evt["opState"]
            changed = True

        if changed:
            self._update_binary_state()

            if self.hass is not None:
                self.async_write_ha_state()

    async def async_sperren(self):
        """MAP-Melder sperren."""
        if self._device_type != "Point":
            raise ValueError("Sperren ist nur für MAP-Points verfügbar")

        _LOGGER.warning("MAP5000: Melder sperren: %s", self._siid)

        await self._api.disable_point(self._device_url)

        state = await self._api.get_point(self._device_url)
        old_enabled = self._enabled
        self._enabled = bool(state.get("enabled", False))

        if old_enabled != self._enabled and self.hass is not None:
            self.hass.bus.async_fire(
                "map5000_sperrstatus",
                {
                    "entity_id": self.entity_id,
                    "name": self.name,
                    "siid": self._siid,
                    "status": "Gesperrt",
                    "enabled": self._enabled,
                },
            )

        self.async_write_ha_state()

    async def async_entsperren(self):
        """MAP-Melder entsperren."""
        if self._device_type != "Point":
            raise ValueError("Entsperren ist nur für MAP-Points verfügbar")

        _LOGGER.warning("MAP5000: Melder entsperren: %s", self._siid)

        await self._api.enable_point(self._device_url)

        state = await self._api.get_point(self._device_url)
        old_enabled = self._enabled
        self._enabled = bool(state.get("enabled", True))

        if old_enabled != self._enabled and self.hass is not None:
            self.hass.bus.async_fire(
                "map5000_sperrstatus",
                {
                    "entity_id": self.entity_id,
                    "name": self.name,
                    "siid": self._siid,
                    "status": "Entsperrt",
                    "enabled": self._enabled,
                },
            )

        self.async_write_ha_state()
