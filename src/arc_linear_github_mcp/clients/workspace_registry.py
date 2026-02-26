"""Workspace registry for multi-workspace Linear support."""

import re
from functools import lru_cache

from arc_linear_github_mcp.clients.linear import LinearClient, LinearClientError
from arc_linear_github_mcp.config.settings import get_settings


class TeamNotFoundError(Exception):
    """Raised when a team key cannot be found in any workspace."""


class WorkspaceRegistry:
    """Registry that manages LinearClient instances across multiple workspaces.

    Lazily creates clients per workspace and caches team key -> workspace
    mappings for fast resolution.
    """

    def __init__(
        self,
        workspaces: dict[str, str],
        api_url: str = "https://api.linear.app/graphql",
        timeout: float = 30.0,
    ):
        """Initialize the workspace registry.

        Args:
            workspaces: Mapping of workspace name -> API key
            api_url: Linear GraphQL API endpoint
            timeout: HTTP request timeout in seconds
        """
        self._workspaces = workspaces
        self._api_url = api_url
        self._timeout = timeout
        self._clients: dict[str, LinearClient] = {}
        self._team_cache: dict[str, str] = {}

    @property
    def workspace_names(self) -> list[str]:
        """Return the list of configured workspace names."""
        return list(self._workspaces.keys())

    def get_client(self, workspace_name: str) -> LinearClient:
        """Get or create a LinearClient for the given workspace.

        Args:
            workspace_name: Name of the workspace

        Returns:
            LinearClient for the workspace

        Raises:
            KeyError: If workspace_name is not configured
        """
        if workspace_name not in self._workspaces:
            raise KeyError(
                f"Workspace '{workspace_name}' not configured. "
                f"Available: {', '.join(self._workspaces.keys())}"
            )
        if workspace_name not in self._clients:
            self._clients[workspace_name] = LinearClient(
                api_key=self._workspaces[workspace_name],
                api_url=self._api_url,
                timeout=self._timeout,
            )
        return self._clients[workspace_name]

    async def resolve_client_for_team(self, team_key: str) -> LinearClient:
        """Resolve which workspace contains the given team key.

        Checks the cache first, then probes each workspace.

        Args:
            team_key: Team key (e.g., 'FAVRES')

        Returns:
            LinearClient for the workspace containing the team

        Raises:
            TeamNotFoundError: If the team is not found in any workspace
        """
        team_key_upper = team_key.upper()

        # Check cache first
        if team_key_upper in self._team_cache:
            return self.get_client(self._team_cache[team_key_upper])

        # Probe each workspace
        for ws_name in self._workspaces:
            client = self.get_client(ws_name)
            try:
                team = await client.get_team_by_key(team_key_upper)
                if team:
                    self._team_cache[team_key_upper] = ws_name
                    return client
            except LinearClientError:
                continue

        available = ", ".join(self._workspaces.keys())
        raise TeamNotFoundError(
            f"Team '{team_key}' not found in any workspace. "
            f"Searched workspaces: {available}. "
            f"Use linear_list_workspaces to see available teams."
        )

    async def resolve_client_for_issue(self, identifier: str) -> LinearClient:
        """Resolve which workspace contains the issue by its identifier.

        Extracts the team key from the identifier (e.g., 'FAVRES' from 'FAVRES-123')
        and delegates to resolve_client_for_team.

        Args:
            identifier: Issue identifier (e.g., 'FAVRES-123')

        Returns:
            LinearClient for the workspace containing the issue's team

        Raises:
            TeamNotFoundError: If the team is not found
            ValueError: If the identifier format is invalid
        """
        match = re.match(r"^([A-Za-z]+)-(\d+)$", identifier)
        if not match:
            raise ValueError(
                f"Invalid issue identifier format: '{identifier}'. "
                f"Expected format: TEAM-123 (e.g., FAVRES-123)"
            )
        team_key = match.group(1)
        return await self.resolve_client_for_team(team_key)

    async def list_all_workspaces_with_teams(self) -> dict:
        """Query all workspaces and return their teams.

        Returns:
            Dictionary with workspace info and teams
        """
        result: list[dict] = []
        for ws_name in self._workspaces:
            client = self.get_client(ws_name)
            try:
                teams = await client.list_teams()
                team_list = []
                for team in teams:
                    self._team_cache[team.key.upper()] = ws_name
                    team_list.append({"key": team.key, "name": team.name, "id": team.id})
                result.append(
                    {
                        "workspace": ws_name,
                        "teams": team_list,
                    }
                )
            except LinearClientError as e:
                result.append(
                    {
                        "workspace": ws_name,
                        "error": str(e),
                        "teams": [],
                    }
                )
        return {"workspaces": result}

    async def close_all(self) -> None:
        """Close all client connections."""
        for client in self._clients.values():
            await client.close()
        self._clients.clear()


@lru_cache
def get_workspace_registry() -> WorkspaceRegistry:
    """Get cached workspace registry.

    Returns:
        WorkspaceRegistry configured from application settings
    """
    settings = get_settings()
    return WorkspaceRegistry(
        workspaces=settings.resolved_workspaces,
        api_url=settings.linear_api_url,
        timeout=settings.request_timeout,
    )
