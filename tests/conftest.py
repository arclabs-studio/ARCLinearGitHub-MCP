"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set mock environment variables for testing (single-key mode)."""
    monkeypatch.setenv("LINEAR_API_KEY", "lin_api_test_key")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
    monkeypatch.setenv("GITHUB_ORG", "test-org")
    monkeypatch.setenv("DEFAULT_PROJECT", "TEST")
    monkeypatch.setenv("DEFAULT_REPO", "TestRepo")
    # Ensure multi-workspace is not set by default
    monkeypatch.delenv("LINEAR_WORKSPACES", raising=False)


@pytest.fixture
def mock_multi_workspace_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set mock environment variables for multi-workspace mode."""
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)
    monkeypatch.setenv(
        "LINEAR_WORKSPACES",
        '{"ios": "lin_api_ios_key", "backend": "lin_api_backend_key"}',
    )
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
    monkeypatch.setenv("GITHUB_ORG", "test-org")
    monkeypatch.setenv("DEFAULT_PROJECT", "TEST")
    monkeypatch.setenv("DEFAULT_REPO", "TestRepo")


@pytest.fixture(autouse=True)
def clear_caches() -> None:
    """Clear all LRU caches between tests."""
    from arc_linear_github_mcp.clients.workspace_registry import get_workspace_registry
    from arc_linear_github_mcp.config.settings import get_settings

    get_settings.cache_clear()
    get_workspace_registry.cache_clear()
