# 🛡️ Bosch MAP 5000 – Home Assistant Integration

Custom Home Assistant integration for **Bosch MAP 5000** intrusion
detection systems using the **Open Intrusion Interface (OII)**.

The integration communicates **locally** with the MAP 5000 via HTTPS
and does not require a cloud service.

> [!IMPORTANT]
> This is an independent community project and is **not an official
> Bosch integration**.

---

## ✨ Features

### 🔎 Automatic discovery

MAP 5000 objects are discovered automatically from the OII
configuration.

Supported objects include:

- Points / detectors
- Doors and windows
- Power supplies
- Gateways
- System keypads
- Modules / couplers
- Outputs
- Areas / control panel areas
- Internal programs

---

### ⚡ Live OII communication

The integration uses the MAP 5000 OII subscription mechanism for
live state updates.

Supported MAP objects are monitored through a central OII
subscription and their changes are distributed inside Home Assistant.

The integration also provides a dedicated **MAP5000 connectivity
binary sensor** to indicate whether communication with the panel is
online.

If communication is interrupted, the integration attempts to recreate
the OII subscription automatically.

---

## 🚪 Points, doors and windows

MAP points are exposed as Home Assistant binary sensors.

Available information can include:

- Open / closed state
- Enabled / disabled state
- Bypass state
- OII operating state
- MAP SIID

### Automatic door/window classification

Starting with **v0.3.0**, point names are used to select a more useful
Home Assistant device class:

- Names containing `Tür` or `Tuer` → Door
- Names containing `Fenster` → Window
- Other points → Opening

This provides more appropriate icons and state presentation in
Home Assistant.

### 🔒 Disable / enable points

Points can be disabled and enabled from Home Assistant using:

- `map5000.sperren`
- `map5000.entsperren`

The enabled state is synchronized with the MAP.

---

## 🔌 Outputs

Starting with **v0.3.0**, MAP outputs are exposed as native
Home Assistant **switch entities**.

Supported operations:

- Read actual output state
- Turn output ON
- Turn output OFF
- Live output state updates
- Read enabled / disabled state
- Read OII operating state
- Disable output
- Enable output

Output switching uses the native MAP OII `ON` and `OFF` commands.

Output locking uses:

- `map5000.sperren`
- `map5000.entsperren`

### ⚠️ Output configuration

For disable / enable operations, the output should be assigned to an
appropriate MAP area according to the configuration and permissions of
the installation.

Available functions may depend on the MAP configuration and OII user
permissions.

---

## ⚙️ Internal programs

Starting with **v0.3.0**, configured MAP internal programs are
discovered automatically.

Each discovered internal program is exposed as a Home Assistant
switch.

Supported operations:

- Read active / inactive state
- Activate internal program
- Deactivate internal program

The integration uses the native MAP OII:

- `ACTIVATE`
- `DEACTIVATE`

commands.

Internal-program URLs are also included in the central OII
subscription so state-change events can be received by the
integration.

If the MAP does not provide a descriptive program name through the
used OII resource, Home Assistant uses a fallback name such as:

`Internprogramm 1`

---

## 🛡️ Areas

MAP areas are exposed as Home Assistant **alarm control panel**
entities.

Supported functions include:

- Armed / disarmed state
- Arm area
- Disarm area
- Immediate arming without exit delay
- Ready-to-arm information
- Ready-to-disarm information
- Number of bypassed devices
- Live state updates

> [!CAUTION]
> Arming and disarming are security-critical operations. Test the
> behavior carefully on the actual MAP installation before using
> Home Assistant automations.

---

## 🚨 MAP incidents

The integration processes native MAP 5000 OII incidents instead of
deriving alarms from detector states.

A new incident generates the Home Assistant event:

`map5000_incident`

Information can include:

- Incident type
- Category
- Triggering detector
- Related area
- Incident time
- Handling state
- Silenced state
- Incident counter

Recognized categories currently include:

- Intrusion alarm
- Tamper alarm
- Battery trouble
- Other / unknown MAP incidents

Example native MAP incident type:

`Alarm.Intrusion.General`

When an incident is no longer referenced by MAP objects, the
integration generates:

`map5000_incident_cleared`

This allows Home Assistant automations and notifications to react to
actual alarm decisions made by the MAP panel.

---

## 🎛️ MAP control buttons

The integration provides Home Assistant button entities for:

- Reset / handle incidents
- Silence active incident signalers
- Start walk test
- Stop walk test

Availability and behavior can depend on the MAP configuration and OII
permissions.

---

## 🧰 Technical MAP devices

Technical MAP objects such as:

- Power supplies
- Gateways
- Modules / couplers
- System keypads

are exposed with their OII operating state.

This makes technical MAP faults visible inside Home Assistant.

---

# 📦 Installation

## HACS

This integration can be installed through HACS as a **custom
repository**.

1. Open **HACS** in Home Assistant.
2. Open the menu for **Custom repositories**.
3. Add this GitHub repository.
4. Select **Integration** as repository type.
5. Install **MAP 5000 - by MK**.
6. Restart Home Assistant.

After the restart:

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **MAP 5000 - by MK**.
4. Enter the MAP 5000 OII connection information.

Required values:

- MAP 5000 host / IP address
- OII username
- OII password

No YAML configuration is required for the basic integration setup.

---

# 🔧 Requirements

A configured and reachable **Bosch MAP 5000 Open Intrusion Interface**
is required.

Communication is performed locally using:

- HTTPS
- HTTP Digest authentication
- Bosch MAP 5000 OII REST resources
- OII event subscriptions

The OII user must have the permissions required for the functions that
should be controlled from Home Assistant.

---

# 🔐 Security notes

The MAP 5000 is an intrusion detection system.

Before using Home Assistant for security-related automation:

- Test all required functions on the real installation.
- Verify OII user permissions.
- Verify area and output assignments.
- Do not assume that a detector state alone represents an alarm.
- Use native MAP incidents for alarm notifications where appropriate.

Home Assistant should not be treated as a replacement for the MAP
panel's certified alarm functionality.

---

# 🆕 What's new in v0.3.0

### 🚪 Better point presentation

- Automatic Door device class for point names containing `Tür` or
  `Tuer`.
- Automatic Window device class for point names containing `Fenster`.
- Other points continue to use the Opening device class.

### 🔌 Controllable MAP outputs

- Outputs are now native Home Assistant switches.
- ON / OFF control.
- Live state synchronization.
- Disable / enable support.
- Output status attributes.

### ⚙️ Internal programs

- Automatic internal-program discovery.
- Internal programs as Home Assistant switches.
- ACTIVATE / DEACTIVATE support.
- Active-state synchronization.
- Added internal-program resources to the central OII subscription.

### 🧹 Integration improvements

- Separated output entities from the binary-sensor platform.
- Outputs continue to use the existing central OII subscription.
- Removed obsolete output binary-sensor state handling.
- Cleaned up duplicate service registration.
- General v0.3.0 code cleanup.

---

# 🧪 Tested

The integration has been developed and tested against a real Bosch
MAP 5000 installation.

Tested functionality includes:

- Automatic device discovery
- Live detector state changes
- Door / window classification
- Point disable / enable
- Area arm / disarm
- Immediate area arming
- Output ON / OFF
- Output disable / enable
- Internal-program activation / deactivation
- Native intrusion incident handling
- Incident source and area identification
- Incident reset
- MAP OII connectivity monitoring
- Subscription recovery

Some functions depend on the configuration, firmware, permissions and
capabilities of the individual MAP installation.

---

# 📋 Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for the complete release history.

---

# 📄 License

MIT License
