# Bosch MAP 5000 – v0.3.2

## Automatic LSN PIR motion detector recognition

This release adds automatic classification of Bosch PIR motion detectors.

### Improvements

- Reads the Bosch device subtype from the OII configuration.
- Detects `POINT.PIR` devices automatically.
- Uses Home Assistant `motion` device class.
- No name-based detection required for PIR sensors.
- Preserves existing door, window and other Point classifications.
- Keeps the existing live OII event processing.

### Tested

- Bosch MAP 5000 LSN PIR motion detector
- SIID: `1.1.Point.1001.6`
- Live motion detection confirmed
- German HA states: `Frei` / `Erkannt`

### Upgrade

Update through HACS and restart Home Assistant.

No configuration changes required.
