import logging

from homeassistant.core import callback

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)

from .const import DATA_API, DOMAIN

_LOGGER = logging.getLogger(__name__)



def find_area_names(value):
    """Bereichsnamen rekursiv aus /config ermitteln."""
    result = {}

    if isinstance(value, dict):
        siid = value.get("siid")
        name = value.get("name")

        if (
            isinstance(siid, str)
            and (".Area." in siid or ".ControlPanelArea." in siid)
        ):
            result[siid] = name or siid

        for child in value.values():
            result.update(find_area_names(child))

    elif isinstance(value, list):
        for child in value:
            result.update(find_area_names(child))

    return result


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.warning("MAP5000: Bereichserkennung über /areas gestartet")

    api = hass.data[DOMAIN][entry.entry_id][DATA_API]

    try:
        # Namen aus MAP-Konfiguration holen.
        config = await api.get_config()
        area_names = find_area_names(config)

        # Tatsächliche Bereiche + aktuelle Zustände direkt von /areas.
        area_data = await api.get_point("/areas")
        area_list = area_data.get("list", [])

        entities = []

        for state in area_list:
            area_url = state.get("@self")

            if not isinstance(area_url, str):
                continue


            if ".Area." not in area_url and ".ControlPanelArea." not in area_url:
                continue

            siid = area_url.lstrip("/")
            name = area_names.get(siid, siid)

            entity = Map5000Area(
                name=name,
                siid=siid,
                area_url=area_url,
                state=state,
                api=api,
            )

            entities.append(entity)

            _LOGGER.warning(
                "MAP5000: Bereich gefunden: %s | %s | armed=%s | "
                "readyToArm=%s | readyToDisarm=%s | oiiArmable=%s",
                name,
                siid,
                state.get("armed"),
                state.get("readyToArm"),
                state.get("readyToDisarm"),
                state.get("oiiArmable"),
            )

        if entities:
            async_add_entities(entities)

            entities_by_url = {
                entity._area_url: entity for entity in entities
            }

            @callback
            def handle_map5000_event(event):
                """Bereichszustände aus dem zentralen MAP-Livestream übernehmen."""
                area_url = event.data.get("url")
                state = event.data.get("state", {})
                entity = entities_by_url.get(area_url)

                if entity is None:
                    return

                entity._update_from_state(state)
                entity.async_write_ha_state()

                _LOGGER.warning(
                    "MAP5000 LIVE Bereich: %s | armed=%s",
                    entity.name,
                    entity._armed,
                )

            unsubscribe = hass.bus.async_listen(
                "map5000_object_changed",
                handle_map5000_event,
            )
            entry.async_on_unload(unsubscribe)

        _LOGGER.warning(
            "MAP5000: %d Bereich(e) in Home Assistant angelegt",
            len(entities),
        )

    except Exception:
        _LOGGER.exception("MAP5000: Fehler bei Bereichserkennung")


class Map5000Area(AlarmControlPanelEntity):
    _attr_should_poll = False
    _attr_code_arm_required = False

    # Noch keine Schaltbefehle freigeben.
    _attr_supported_features = AlarmControlPanelEntityFeature.ARM_AWAY

    def __init__(self, name, siid, area_url, state, api):
        self._attr_name = name
        self._attr_unique_id = f"map5000_area_{siid}"

        self._siid = siid
        self._area_url = area_url
        self._api = api

        self._armed = bool(state.get("armed", False))
        self._ready_to_arm = bool(state.get("readyToArm", False))
        self._ready_to_disarm = bool(state.get("readyToDisarm", False))
        self._oii_armable = bool(state.get("oiiArmable", False))
        self._transitional_state = state.get("transitionalState", "")
        self._bypassed = state.get("numberOfBypassedDevices", 0)

    @property
    def state(self):
        if self._transitional_state:
            return self._transitional_state

        return "armed_away" if self._armed else "disarmed"

    @property
    def extra_state_attributes(self):
        return {
            "SIID": self._siid,
            "MAP URL": self._area_url,
            "Zustand": "Scharf" if self._armed else "Unscharf",
            "Bereit zum Scharfschalten":
                "Ja" if self._ready_to_arm else "Nein",
            "Bereit zum Unscharfschalten":
                "Ja" if self._ready_to_disarm else "Nein",
            "OII schaltbar":
                "Ja" if self._oii_armable else "Nein",
            "Übergangszustand": self._transitional_state or "-",
            "Gesperrte Melder": self._bypassed,
        }

    async def async_alarm_arm_away(self, code=None):
        """Bereich sofort ohne Austrittsverzögerung scharfschalten."""
        _LOGGER.warning(
            "MAP5000: Scharfschalten angefordert: %s",
            self._siid,
        )

        await self._api.arm_area(self._area_url)

        state = await self._api.get_point(self._area_url)
        self._update_from_state(state)
        self.async_write_ha_state()

    async def async_alarm_disarm(self, code=None):
        """Bereich unscharfschalten."""
        _LOGGER.warning(
            "MAP5000: Unscharfschalten angefordert: %s",
            self._siid,
        )

        await self._api.disarm_area(self._area_url)

        state = await self._api.get_point(self._area_url)
        self._update_from_state(state)
        self.async_write_ha_state()

    def _update_from_state(self, state):
        """Aktuellen Bereichszustand von der MAP übernehmen."""
        if "armed" in state:
            self._armed = bool(state["armed"])

        if "readyToArm" in state:
            self._ready_to_arm = bool(state["readyToArm"])

        if "readyToDisarm" in state:
            self._ready_to_disarm = bool(state["readyToDisarm"])

        if "oiiArmable" in state:
            self._oii_armable = bool(state["oiiArmable"])

        if "transitionalState" in state:
            self._transitional_state = state["transitionalState"]

        if "numberOfBypassedDevices" in state:
            self._bypassed = state["numberOfBypassedDevices"]
