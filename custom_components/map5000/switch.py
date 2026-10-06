"""Switch platform for Bosch MAP 5000."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback

from .const import DATA_API, DOMAIN

_LOGGER = logging.getLogger(__name__)


def find_outputs(value):
    """MAP5000-Outputs rekursiv aus /config ermitteln."""
    outputs = []

    if isinstance(value, dict):
        siid = value.get("siid")

        if isinstance(siid, str) and ".Output." in siid:
            outputs.append(value)

        for child in value.values():
            outputs.extend(find_outputs(child))

    elif isinstance(value, list):
        for child in value:
            outputs.extend(find_outputs(child))

    return outputs


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up MAP 5000 output switches."""
    api = hass.data[DOMAIN][entry.entry_id][DATA_API]

    # MAP5000-Internprogramme ermitteln.
    internal_program_data = await api.get_internal_programs()
    internal_program_configs = internal_program_data.get("list", [])

    internal_program_entities = []
    internal_programs_by_url = {}

    for program_state in internal_program_configs:
        program_url = program_state.get("@self")

        if not isinstance(program_url, str):
            continue

        program_number = program_url.rsplit("/", 1)[-1]
        name = f"Internprogramm {program_number}"

        entity = Map5000InternalProgramSwitch(
            name=name,
            program_number=program_number,
            program_url=program_url,
            state=program_state,
            api=api,
        )

        internal_program_entities.append(entity)
        internal_programs_by_url[program_url] = entity

        _LOGGER.warning(
            "MAP5000: Internprogramm-Switch gefunden: %s | %s | active=%r",
            name,
            program_url,
            program_state.get("active"),
        )

    config = await api.get_config()
    output_configs = find_outputs(config)

    unique_outputs = {}

    for output in output_configs:
        siid = output.get("siid")

        if siid:
            unique_outputs[siid] = output

    entities = []
    entities_by_url = {}

    for siid, output_config in unique_outputs.items():
        output_url = "/" + siid
        name = output_config.get("name") or siid

        try:
            state = await api.get_point(output_url)
        except Exception:
            _LOGGER.exception(
                "MAP5000: Output %s (%s) konnte nicht gelesen werden",
                name,
                siid,
            )
            continue

        entity = Map5000OutputSwitch(
            name=name,
            siid=siid,
            output_url=output_url,
            state=state,
            api=api,
        )

        entities.append(entity)
        entities_by_url[output_url] = entity

        _LOGGER.warning(
            "MAP5000: Output-Switch gefunden: %s | %s | on=%r | enabled=%r | opState=%r",
            name,
            siid,
            state.get("on"),
            state.get("enabled"),
            state.get("opState"),
        )

    if not entities and not internal_program_entities:
        _LOGGER.warning("MAP5000: Keine Output- oder Internprogramm-Switches gefunden")
        return

    async_add_entities([*entities, *internal_program_entities])

    @callback
    def handle_map5000_event(event):
        """Output-Zustand aus dem zentralen MAP-Livestream übernehmen."""
        output_url = event.data.get("url")
        state = event.data.get("state", {})

        entity = entities_by_url.get(output_url)

        if entity is None:
            entity = internal_programs_by_url.get(output_url)

        if entity is None:
            return

        entity.update_from_event(state)

    unsubscribe = hass.bus.async_listen(
        "map5000_object_changed",
        handle_map5000_event,
    )
    entry.async_on_unload(unsubscribe)


class Map5000OutputSwitch(SwitchEntity):
    """MAP5000 Output as Home Assistant switch."""

    _attr_should_poll = False

    def __init__(self, name, siid, output_url, state, api):
        self._attr_name = name
        self._attr_unique_id = f"map5000_output_{siid}"

        self._siid = siid
        self._output_url = output_url
        self._api = api

        self._attr_is_on = bool(state.get("on", False))
        self._enabled = bool(state.get("enabled", True))
        self._op_state = state.get("opState", "OK")

    @property
    def extra_state_attributes(self):
        return {
            "Zustand": "Ein" if self._attr_is_on else "Aus",
            "Gesperrt": "Nein" if self._enabled else "Ja",
            "OII Zustand": self._op_state,
            "SIID": self._siid,
            "Typ": "Output",
        }

    def update_from_event(self, state):
        """MAP5000 Live-Event übernehmen."""
        changed = False

        if "on" in state:
            self._attr_is_on = bool(state["on"])
            changed = True

        if "enabled" in state:
            self._enabled = bool(state["enabled"])
            changed = True

        if "opState" in state:
            self._op_state = state["opState"]
            changed = True

        if changed and self.hass is not None:
            self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """MAP5000-Ausgang einschalten."""
        _LOGGER.warning("MAP5000: Output einschalten: %s", self._siid)

        await self._api.turn_on_output(self._output_url)

        state = await self._api.get_point(self._output_url)
        self.update_from_event(state)

    async def async_turn_off(self, **kwargs):
        """MAP5000-Ausgang ausschalten."""
        _LOGGER.warning("MAP5000: Output ausschalten: %s", self._siid)

        await self._api.turn_off_output(self._output_url)

        state = await self._api.get_point(self._output_url)
        self.update_from_event(state)

    async def async_sperren(self):
        """MAP5000-Ausgang sperren."""
        _LOGGER.warning("MAP5000: Output sperren: %s", self._siid)

        await self._api.send_command(self._output_url, "DISABLE")

        state = await self._api.get_point(self._output_url)
        self.update_from_event(state)

    async def async_entsperren(self):
        """MAP5000-Ausgang entsperren."""
        _LOGGER.warning("MAP5000: Output entsperren: %s", self._siid)

        await self._api.send_command(self._output_url, "ENABLE")

        state = await self._api.get_point(self._output_url)
        self.update_from_event(state)


class Map5000InternalProgramSwitch(SwitchEntity):
    """MAP5000 internal program as Home Assistant switch."""

    _attr_should_poll = False

    def __init__(
        self,
        name,
        program_number,
        program_url,
        state,
        api,
    ):
        self._attr_name = name
        self._attr_unique_id = (
            f"map5000_internal_program_{program_number}"
        )

        self._program_number = program_number
        self._program_url = program_url
        self._api = api

        self._attr_is_on = bool(state.get("active", False))

    @property
    def extra_state_attributes(self):
        return {
            "Aktiv": "Ja" if self._attr_is_on else "Nein",
            "Nummer": self._program_number,
            "Typ": "Internprogramm",
        }

    def update_from_event(self, state):
        """MAP5000 Live-Event des Internprogramms übernehmen."""
        if "active" not in state:
            return

        self._attr_is_on = bool(state["active"])

        if self.hass is not None:
            self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """MAP5000-Internprogramm aktivieren."""
        _LOGGER.warning(
            "MAP5000: Internprogramm aktivieren: %s",
            self._program_number,
        )

        await self._api.activate_internal_program(
            self._program_url
        )

        state = await self._api.get_internal_program(
            self._program_number
        )

        self._attr_is_on = bool(state.get("active", False))
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """MAP5000-Internprogramm deaktivieren."""
        _LOGGER.warning(
            "MAP5000: Internprogramm deaktivieren: %s",
            self._program_number,
        )

        await self._api.deactivate_internal_program(
            self._program_url
        )

        state = await self._api.get_internal_program(
            self._program_number
        )

        self._attr_is_on = bool(state.get("active", False))
        self.async_write_ha_state()
