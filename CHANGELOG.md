# Changelog

## 0.3.1

### Fixed
- Fixed a service registration conflict between MAP points and outputs.
- Point lock/unlock actions work correctly again.
- Output lock/unlock now use dedicated actions:
  - `map5000.ausgang_sperren`
  - `map5000.ausgang_entsperren`
- Prevented the output service registration from overriding the point service registration.

### Tested
- Point lock
- Point unlock
- Output lock
- Output unlock
- Output ON/OFF remains functional


All notable changes to the MAP 5000 Home Assistant integration
are documented in this file.

---

## v0.3.0

### New features

#### Doors and windows

- Added automatic Home Assistant device-class selection for MAP
  points.
- Point names containing `Tür` or `Tuer` are exposed as Door binary
  sensors.
- Point names containing `Fenster` are exposed as Window binary
  sensors.
- Other points continue to use the Opening device class.

#### MAP outputs

- MAP outputs are now exposed as native Home Assistant switch
  entities.
- Added output ON support using the OII `ON` command.
- Added output OFF support using the OII `OFF` command.
- Added live output state synchronization through the existing central
  OII subscription.
- Added enabled / disabled state information.
- Added output OII operating-state information.
- Added output support for:
  - `map5000.sperren`
  - `map5000.entsperren`
- Output disable / enable has been tested with outputs assigned to a
  MAP area.

#### Internal programs

- Added automatic discovery through `/internalprograms`.
- Added internal programs as Home Assistant switch entities.
- Added activation using the OII `ACTIVATE` command.
- Added deactivation using the OII `DEACTIVATE` command.
- Added active-state synchronization after Home Assistant commands.
- Added discovered internal-program URLs to the central OII
  subscription.
- Added handling for internal-program state-change events.
- Added fallback entity names such as `Internprogramm 1` when no
  descriptive name is available through the used OII resource.

### Architecture and stability

- Outputs are no longer created as binary-sensor entities.
- Output URLs remain part of the central MAP OII subscription.
- Output switches receive state changes through Home Assistant's
  internal MAP event distribution.
- Internal programs use the same central OII subscription instead of
  creating an additional subscription.
- Removed obsolete output state handling from the binary-sensor
  entity implementation.
- Removed duplicate switch service registration.
- Removed unused integration code.
- Preserved the existing incident lifecycle and subscription recovery
  architecture.

### Tested

v0.3.0 has been tested with a real Bosch MAP 5000 installation,
including:

- Point state changes
- Door / window device classes
- Point disable / enable
- Output ON / OFF
- Output disable / enable
- Internal-program activation / deactivation
- Area arm / disarm
- Existing central OII event subscription
- MAP integration startup after the v0.3.0 changes

Internal-program resources have been successfully added to the central

Some MAP functions depend on the configuration, permissions and
capabilities of the individual installation.

---

## v0.2.0

### New features

- Added native Bosch MAP 5000 OII incident handling.
- Added Home Assistant event `map5000_incident`.
- Added incident information including:
  - incident type
  - category
  - triggering detector
  - related area
  - incident time
  - handling state
- Added `map5000_incident_cleared` event for incident lifecycle tracking.
- Added recognition of intrusion alarms.
- Added recognition of tamper alarms.
- Added recognition of battery trouble incidents.
- Added generic handling for other MAP incidents.

### MAP connectivity

- Added dedicated `MAP5000` connectivity binary sensor.
- Detects loss of OII communication.
- Automatically reports the connection as online again after successful reconnect.
- Added automatic OII subscription recreation after communication failures.

### Areas

- Added MAP areas as Home Assistant alarm control panel entities.
- Added live armed/disarmed state updates.
- Added ARM support.
- Added DISARM support.
- Added immediate arming using zero exit delay.
- Added ready-to-arm and ready-to-disarm information.
- Added bypassed-device information.

### MAP control

Added Home Assistant button entities for:

- Reset / handle MAP incidents
- Silence active incident signalers
- Start walk test
- Stop walk test

### Device support

Extended automatic discovery with support for:

- MAP modules / couplers
- MAP outputs
- Additional technical MAP devices

Outputs now use the actual OII `on` property for their displayed
binary state.

Direct output switching is not included in v0.2.0.

### Points / detectors

- Improved live detector state updates.
- Added enabled/disabled status.
- Added bypass information.
- Added OII operating state.
- Added Home Assistant services for disabling and enabling points:
  - `map5000.sperren`
  - `map5000.entsperren`
- Added status events when the enabled state changes.

### Live communication

- Expanded the central MAP OII subscription.
- Device and area changes are distributed inside Home Assistant.
- Improved automatic subscription recovery after connection errors.

### Bug fixes and stability

- Fixed incident lifecycle handling.
- Fixed detection of newly created MAP incidents.
- Fixed handling of incidents referenced by multiple MAP objects.
- Fixed incident clearing so an incident is only considered cleared
  after it is no longer referenced by MAP objects.
- Fixed output state handling to use the OII `on` state instead of
  treating the technical operating state as the output state.
- Improved state synchronization after point enable/disable commands.
- Improved subscription recovery after temporary MAP communication loss.
- Improved handling of HTTP 202 responses with empty response bodies.
- Improved integration unload and background event-loop handling.
- Various discovery and state-handling stability improvements.

### Tested

v0.2.0 has been tested with a real Bosch MAP 5000 installation,
including:

- Automatic device discovery
- Live detector state changes
- Point disable / enable
- Area arm / disarm
- Immediate arming
- Native intrusion incident detection
- Incident source and area identification
- Home Assistant push automation triggered by a real
  `Alarm.Intrusion.General` MAP incident
- Incident reset
- MAP OII online/offline monitoring

Some MAP functions depend on the configuration and capabilities of
the individual installation.

---

## v0.1.0

Initial public release.

### Features

- Bosch MAP 5000 OII connection
- Home Assistant Config Flow
- Automatic point discovery
- Binary sensor entities
- Local HTTPS communication
- HTTP Digest authentication
- Initial live OII subscription support

