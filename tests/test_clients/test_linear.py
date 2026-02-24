"""Tests for LinearClient primitive parameter initialization."""

from arc_linear_github_mcp.clients.linear import LinearClient


class TestLinearClientInit:
    def test_accepts_primitive_params(self) -> None:
        client = LinearClient(
            api_key="lin_api_test",
            api_url="https://api.linear.app/graphql",
            timeout=15.0,
        )
        assert client._api_key == "lin_api_test"
        assert client._api_url == "https://api.linear.app/graphql"
        assert client._timeout == 15.0

    def test_default_values(self) -> None:
        client = LinearClient(api_key="lin_api_test")
        assert client._api_url == "https://api.linear.app/graphql"
        assert client._timeout == 30.0

    def test_client_starts_as_none(self) -> None:
        client = LinearClient(api_key="lin_api_test")
        assert client._client is None
