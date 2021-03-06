"""The tests for the Buienradar sensor platform."""
from homeassistant.setup import async_setup_component
from homeassistant.components import sensor


CONDITIONS = ["stationname", "temperature"]
BASE_CONFIG = {
    "sensor": [
        {
            "platform": "buienradar",
            "name": "volkel",
            "latitude": 51.65,
            "longitude": 5.7,
            "monitored_conditions": CONDITIONS,
        }
    ]
}


async def test_smoke_test_setup_component(hass):
    """Smoke test for successfully set-up with default config."""
    assert await async_setup_component(hass, sensor.DOMAIN, BASE_CONFIG)

    for cond in CONDITIONS:
        state = hass.states.get(f"sensor.volkel_{cond}")
        assert state.state == "unknown"
