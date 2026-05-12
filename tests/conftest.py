"""Fixtures partagées pour les tests ALLIN I/O 8."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.allin_io_8.const import (
    CONF_HOSTNAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
)

# pytest-homeassistant-custom-component requiert ce flag pour autoriser
# le chargement des intégrations custom depuis `custom_components/`.
pytest_plugins = ["pytest_homeassistant_custom_component"]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Activer le chargement des custom components pour tous les tests."""
    yield


# ─── Mocks pykmtronic ────────────────────────────────────────────────


class MockRelay:
    """Représente un relais KMTronic mocké."""

    def __init__(self, relay_id: int, is_energised: bool = False) -> None:
        self.id = relay_id
        self.is_energised = is_energised
        self.energise = AsyncMock(side_effect=self._energise)
        self.de_energise = AsyncMock(side_effect=self._de_energise)

    async def _energise(self) -> None:
        self.is_energised = True

    async def _de_energise(self) -> None:
        self.is_energised = False


class MockHub:
    """Représente un KMTronicHubAPI mocké."""

    def __init__(self, name: str = "KMTronic Hub", relay_count: int = 8) -> None:
        self.name = name
        self.relays = [MockRelay(i) for i in range(1, relay_count + 1)]
        # AsyncMock pour await hub.async_update_relays() / async_get_relays()
        self.async_update_relays = AsyncMock(return_value=None)
        self.async_get_relays = AsyncMock(return_value=None)


@pytest.fixture
def mock_relay():
    """Un relais isolé pour les tests switch."""
    return MockRelay(1)


@pytest.fixture
def mock_hub():
    """Un hub KMTronic mocké avec 8 relais."""
    return MockHub()


@pytest.fixture
def mock_kmtronic(mock_hub):
    """Patcher KMTronicHubAPI dans tous les modules qui l'importent.

    L'intégration importe la classe à deux endroits : __init__.py et
    config_flow.py. On patche chaque référence pour qu'elles retournent
    le même MockHub.
    """
    with patch(
        "custom_components.allin_io_8.KMTronicHubAPI", return_value=mock_hub
    ) as init_mock, patch(
        "custom_components.allin_io_8.config_flow.KMTronicHubAPI",
        return_value=mock_hub,
    ) as cf_mock:
        yield {"hub": mock_hub, "init": init_mock, "config_flow": cf_mock}


# ─── Données de config standard ──────────────────────────────────────


@pytest.fixture
def user_input():
    """Données utilisateur valides pour le config flow."""
    return {
        CONF_HOSTNAME: "192.168.1.42",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "secret",
    }


@pytest.fixture
def mock_config_entry(user_input):
    """Une ConfigEntry mockée prête à l'emploi.

    Utilise MockConfigEntry de pytest-homeassistant-custom-component
    pour rester compatible avec hass.config_entries.
    """
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    return MockConfigEntry(
        domain=DOMAIN,
        title=user_input[CONF_HOSTNAME],
        data=user_input,
        options={},
        unique_id=user_input[CONF_HOSTNAME],
    )


# ─── Helpers ─────────────────────────────────────────────────────────


def make_client_response_error(status: int = 401):
    """Construire une aiohttp.ClientResponseError avec status donné."""
    import aiohttp

    request_info = MagicMock()
    request_info.real_url = "http://192.168.1.42"
    return aiohttp.ClientResponseError(
        request_info=request_info,
        history=(),
        status=status,
        message="error",
    )
