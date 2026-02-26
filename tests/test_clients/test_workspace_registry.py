"""Tests for WorkspaceRegistry."""

from unittest.mock import AsyncMock

import pytest

from arc_linear_github_mcp.clients.workspace_registry import (
    TeamNotFoundError,
    WorkspaceRegistry,
)
from arc_linear_github_mcp.models.linear import Team


@pytest.fixture
def registry() -> WorkspaceRegistry:
    return WorkspaceRegistry(
        workspaces={"ios": "lin_api_ios", "backend": "lin_api_backend"},
        api_url="https://api.linear.app/graphql",
        timeout=10.0,
    )


@pytest.fixture
def single_registry() -> WorkspaceRegistry:
    return WorkspaceRegistry(
        workspaces={"default": "lin_api_single"},
    )


class TestWorkspaceNames:
    def test_returns_configured_names(self, registry: WorkspaceRegistry) -> None:
        assert registry.workspace_names == ["ios", "backend"]

    def test_single_workspace(self, single_registry: WorkspaceRegistry) -> None:
        assert single_registry.workspace_names == ["default"]


class TestGetClient:
    def test_lazy_creates_client(self, registry: WorkspaceRegistry) -> None:
        client = registry.get_client("ios")
        assert client is not None
        assert client._api_key == "lin_api_ios"

    def test_returns_same_client_on_second_call(self, registry: WorkspaceRegistry) -> None:
        client1 = registry.get_client("ios")
        client2 = registry.get_client("ios")
        assert client1 is client2

    def test_different_workspaces_get_different_clients(self, registry: WorkspaceRegistry) -> None:
        ios_client = registry.get_client("ios")
        backend_client = registry.get_client("backend")
        assert ios_client is not backend_client
        assert ios_client._api_key == "lin_api_ios"
        assert backend_client._api_key == "lin_api_backend"

    def test_unknown_workspace_raises_key_error(self, registry: WorkspaceRegistry) -> None:
        with pytest.raises(KeyError, match="Workspace 'unknown' not configured"):
            registry.get_client("unknown")


class TestResolveClientForTeam:
    @pytest.mark.asyncio
    async def test_found_in_first_workspace(self, registry: WorkspaceRegistry) -> None:
        mock_team = Team(id="team-1", name="iOS App", key="FAVRES")
        ios_client = registry.get_client("ios")
        ios_client.get_team_by_key = AsyncMock(return_value=mock_team)

        client = await registry.resolve_client_for_team("FAVRES")
        assert client._api_key == "lin_api_ios"

    @pytest.mark.asyncio
    async def test_found_in_second_workspace(self, registry: WorkspaceRegistry) -> None:
        ios_client = registry.get_client("ios")
        ios_client.get_team_by_key = AsyncMock(return_value=None)

        backend_client = registry.get_client("backend")
        backend_client.get_team_by_key = AsyncMock(
            return_value=Team(id="team-2", name="Backend", key="BACK"),
        )

        client = await registry.resolve_client_for_team("BACK")
        assert client._api_key == "lin_api_backend"

    @pytest.mark.asyncio
    async def test_uses_cache_on_second_call(self, registry: WorkspaceRegistry) -> None:
        mock_team = Team(id="team-1", name="iOS App", key="FAVRES")
        ios_client = registry.get_client("ios")
        ios_client.get_team_by_key = AsyncMock(return_value=mock_team)

        await registry.resolve_client_for_team("FAVRES")
        # Reset to verify cache is used (no more calls)
        ios_client.get_team_by_key.reset_mock()

        client = await registry.resolve_client_for_team("FAVRES")
        assert client._api_key == "lin_api_ios"
        ios_client.get_team_by_key.assert_not_called()

    @pytest.mark.asyncio
    async def test_not_found_raises_error(self, registry: WorkspaceRegistry) -> None:
        ios_client = registry.get_client("ios")
        ios_client.get_team_by_key = AsyncMock(return_value=None)

        backend_client = registry.get_client("backend")
        backend_client.get_team_by_key = AsyncMock(return_value=None)

        with pytest.raises(TeamNotFoundError, match="Team 'UNKNOWN' not found"):
            await registry.resolve_client_for_team("UNKNOWN")


class TestResolveClientForIssue:
    @pytest.mark.asyncio
    async def test_extracts_team_key(self, registry: WorkspaceRegistry) -> None:
        mock_team = Team(id="team-1", name="iOS App", key="FAVRES")
        ios_client = registry.get_client("ios")
        ios_client.get_team_by_key = AsyncMock(return_value=mock_team)

        client = await registry.resolve_client_for_issue("FAVRES-123")
        assert client._api_key == "lin_api_ios"

    @pytest.mark.asyncio
    async def test_invalid_format_raises_value_error(self, registry: WorkspaceRegistry) -> None:
        with pytest.raises(ValueError, match="Invalid issue identifier format"):
            await registry.resolve_client_for_issue("bad-format-here")

    @pytest.mark.asyncio
    async def test_no_dash_raises_value_error(self, registry: WorkspaceRegistry) -> None:
        with pytest.raises(ValueError, match="Invalid issue identifier format"):
            await registry.resolve_client_for_issue("NODASH")


class TestCloseAll:
    @pytest.mark.asyncio
    async def test_closes_all_clients(self, registry: WorkspaceRegistry) -> None:
        ios_client = registry.get_client("ios")
        backend_client = registry.get_client("backend")

        ios_client.close = AsyncMock()
        backend_client.close = AsyncMock()

        await registry.close_all()

        ios_client.close.assert_called_once()
        backend_client.close.assert_called_once()
        assert len(registry._clients) == 0
