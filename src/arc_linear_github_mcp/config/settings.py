"""Application settings using Pydantic Settings."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the path to the .env file relative to this module
_ENV_FILE = Path(__file__).parent.parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Linear API Configuration
    linear_api_key: str | None = Field(
        default=None,
        description="Linear API key (lin_api_xxxxx). Required if linear_workspaces is not set.",
    )
    linear_workspaces: dict[str, str] | None = Field(
        default=None,
        description=(
            "JSON dict mapping workspace names to API keys. "
            'Example: {"ios": "lin_api_xxx", "backend": "lin_api_yyy"}'
        ),
    )
    linear_api_url: str = Field(
        default="https://api.linear.app/graphql",
        description="Linear GraphQL API endpoint",
    )

    # GitHub API Configuration
    github_token: str = Field(
        ...,
        description="GitHub Personal Access Token (ghp_xxxxx)",
    )
    github_api_url: str = Field(
        default="https://api.github.com",
        description="GitHub REST API endpoint",
    )
    github_org: str = Field(
        ...,
        description="GitHub organization name",
    )

    # Default Project Settings
    default_project: str = Field(
        ...,
        description="Default Linear project key",
    )
    default_repo: str = Field(
        ...,
        description="Default GitHub repository name",
    )

    # Request Timeouts
    request_timeout: float = Field(
        default=30.0,
        description="HTTP request timeout in seconds",
    )

    @model_validator(mode="before")
    @classmethod
    def parse_linear_workspaces(cls, data: Any) -> Any:
        """Parse LINEAR_WORKSPACES from JSON string if needed."""
        if isinstance(data, dict):
            raw = data.get("linear_workspaces") or data.get("LINEAR_WORKSPACES")
            if isinstance(raw, str):
                data["linear_workspaces"] = json.loads(raw)
        return data

    @model_validator(mode="after")
    def validate_linear_config(self) -> "Settings":
        """Ensure at least one of linear_api_key or linear_workspaces is set."""
        if not self.linear_api_key and not self.linear_workspaces:
            raise ValueError("At least one of LINEAR_API_KEY or LINEAR_WORKSPACES must be set.")
        return self

    @property
    def resolved_workspaces(self) -> dict[str, str]:
        """Return workspace name -> API key mapping.

        If linear_workspaces is set, returns it directly.
        Otherwise, wraps the single linear_api_key as {"default": key}.
        """
        if self.linear_workspaces:
            return self.linear_workspaces
        return {"default": self.linear_api_key}  # type: ignore[dict-item]


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: Application settings instance
    """
    return Settings()
