"""Tests for Settings multi-workspace configuration."""

import pytest
from pydantic import ValidationError

from arc_linear_github_mcp.config.settings import Settings


class TestResolvedWorkspaces:
    """Tests for the resolved_workspaces property."""

    def test_single_api_key_returns_default_workspace(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LINEAR_API_KEY", "lin_api_single")
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        monkeypatch.setenv("GITHUB_ORG", "test-org")
        monkeypatch.setenv("DEFAULT_PROJECT", "TEST")
        monkeypatch.setenv("DEFAULT_REPO", "TestRepo")
        monkeypatch.delenv("LINEAR_WORKSPACES", raising=False)

        settings = Settings(_env_file=None)

        assert settings.resolved_workspaces == {"default": "lin_api_single"}

    def test_multi_workspace_returns_parsed_dict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("LINEAR_API_KEY", raising=False)
        monkeypatch.setenv(
            "LINEAR_WORKSPACES",
            '{"ios": "lin_api_ios", "backend": "lin_api_backend"}',
        )
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        monkeypatch.setenv("GITHUB_ORG", "test-org")
        monkeypatch.setenv("DEFAULT_PROJECT", "TEST")
        monkeypatch.setenv("DEFAULT_REPO", "TestRepo")

        settings = Settings(_env_file=None)

        assert settings.resolved_workspaces == {
            "ios": "lin_api_ios",
            "backend": "lin_api_backend",
        }

    def test_both_set_workspaces_takes_precedence(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LINEAR_API_KEY", "lin_api_single")
        monkeypatch.setenv(
            "LINEAR_WORKSPACES",
            '{"ws1": "lin_api_ws1"}',
        )
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        monkeypatch.setenv("GITHUB_ORG", "test-org")
        monkeypatch.setenv("DEFAULT_PROJECT", "TEST")
        monkeypatch.setenv("DEFAULT_REPO", "TestRepo")

        settings = Settings(_env_file=None)

        assert settings.resolved_workspaces == {"ws1": "lin_api_ws1"}

    def test_neither_set_raises_validation_error(self) -> None:
        """Directly construct Settings without any Linear config to verify validation."""
        with pytest.raises(ValidationError, match="LINEAR_API_KEY or LINEAR_WORKSPACES"):
            Settings(
                linear_api_key=None,
                linear_workspaces=None,
                github_token="ghp_test",
                _env_file=None,
            )
