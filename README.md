# Bosch MAP 5000 – Home Assistant Integration

Custom Home Assistant integration for Bosch MAP 5000 intrusion
detection systems using the Open Intrusion Interface (OII).

The integration communicates locally with the MAP 5000 and does
not require a cloud service.

## Version

Current release: **v0.2.0**

## Features

### Automatic device discovery

MAP 5000 objects are discovered automatically from the OII
configuration.

Currently supported object types include:

- Points / detectors
- Power supplies
- Gateways
- System keypads
- Modules / couplers
- Outputs
- Areas / control panel areas

### Live status updates

The integration uses the MAP 5000 OII subscription mechanism.

Changes from the MAP are transferred to Home Assistant without
normal polling.

### MAP 5000 connectivity

A dedicated **MAP5000** connectivity binary sensor shows whether
the OII communication with the panel is online or offline.

### Points / detectors

Points are represented as binary sensors.

Supported information includes:

- Open / closed state
- Enabled / disabled state
- Bypass state
- OII operating state

Points can also be disabled and enabled from Home Assistant using:

- `map5000.sperren`
- `map5000.entsperren`

### Areas

MAP areas are exposed as Home Assistant alarm control panel
entities.

Supported operations:

- Read armed / disarmed state
- Arm area
- Disarm area
- Immediate arming without exit delay
- Live state updates from the MAP

### MAP 5000 incidents

The integration processes native MAP 5000 OII incidents.

A new incident generates the Home Assistant event:

`map5000_incident`

The event can contain information such as:

- Incident type
- Category
- Triggering detector
- Related area
- Incident time
- Handling state

Currently recognized incident categories include:

- Intrusion alarm
- Tamper alarm
- Battery trouble
- Other / unknown MAP incidents

Example MAP incident type:

`Alarm.Intrusion.General`

Incident clearing is exposed through:

`map5000_incident_cleared`

This allows Home Assistant automations to send notifications based
on real alarm decisions made by the MAP panel instead of merely
reacting to detector state changes.

### MAP control buttons

The integration provides Home Assistant button entities for:

- Reset / handle incidents
- Silence active incident signalers
- Start walk test
- Stop walk test

### Technical devices

Technical MAP devices such as power supplies, gateways and modules
are exposed with their OII operating state.

### Outputs

MAP output objects are currently discovered and their actual
`on` state is displayed.

Direct output switching is not part of v0.2.0 yet.

## Installation with HACS

1. Open HACS in Home Assistant.
2. Add this repository as a custom repository.
3. Select **Integration** as repository type.
4. Install **MAP 5000 - by MK**.
5. Restart Home Assistant.
6. Add the integration through:

   **Settings → Devices & services → Add integration**

7. Search for:

   **MAP 5000 - by MK**

Enter the MAP 5000 OII host, username and password.

## Requirements

A configured and reachable Bosch MAP 5000 Open Intrusion Interface
is required.

Communication is performed locally via HTTPS using HTTP Digest
authentication.

## Important

This is an independent community project and is not an official
Bosch integration.

Alarm and security functions should always be tested carefully on
the actual installation before relying on Home Assistant
automations.

## Planned

Future development may include:

- Automatic door/window device classes based on point names
- MAP outputs as controllable Home Assistant switches

## License

MIT License

## Changelog

See `CHANGELOG.md` for release history, new features, improvements
and bug fixes.
