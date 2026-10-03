# MAP 5000 - by MK

Home Assistant Custom Integration for Bosch MAP 5000 systems using the local OII interface.

## Features

- Local HTTPS communication with the MAP 5000
- Home Assistant Config Flow
- Automatic discovery of supported MAP objects
- Live state updates through the MAP subscription mechanism
- Alarm areas with arm/disarm control
- Point enable/disable actions
- Power supply, gateway and system keypad monitoring
- German and English configuration flow

## Installation via HACS

1. Open HACS in Home Assistant.
2. Open **Integrations**.
3. Add this repository as a custom repository.
4. Select **Integration** as the category.
5. Install **MAP 5000 - by MK**.
6. Restart Home Assistant.
7. Add **MAP 5000 - by MK** through **Settings → Devices & services**.
8. Enter the MAP 5000 IP address or hostname, username and password.

## Configuration

The integration requires:

- MAP 5000 IP address or hostname
- OII username
- OII password

Credentials are stored in the Home Assistant config entry and are not part of the source code.

## Supported entities

The integration currently provides:

- Binary sensors for supported MAP objects
- Alarm control panels for MAP areas

New MAP objects can be discovered after restarting Home Assistant.

## Services

The integration provides actions for:

- Locking / disabling a MAP point
- Unlocking / enabling a MAP point

## Requirements

The MAP 5000 must provide access to its local OII interface over HTTPS.

## Disclaimer

This is an independent Home Assistant community integration and is not affiliated with or endorsed by Bosch.

## License

MIT
