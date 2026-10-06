# MAP 5000 v0.3.1

Bugfix release for MAP point and output locking.

## Fixed

Home Assistant entity-service registration caused `map5000.sperren` and
`map5000.entsperren` for MAP points to be overridden by the corresponding
output service registration.

MAP points and outputs now use separate actions.

### MAP points

- `map5000.sperren`
- `map5000.entsperren`

### MAP outputs

- `map5000.ausgang_sperren`
- `map5000.ausgang_entsperren`

Point lock/unlock and output lock/unlock have been tested successfully
against a real Bosch MAP 5000 system.

Normal output ON/OFF control remains unchanged.
