# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-27

### Breaking Changes

- `GITHUB_ORG`, `DEFAULT_PROJECT`, and `DEFAULT_REPO` are now **required** environment variables
  - Previously defaulted to ARC Labs values (`arclabs-studio`, `FAVRES`, `FavRes`)
  - Users must explicitly set these in `.env` or environment — missing values produce a clear Pydantic validation error at startup

### Changed

- `.env.example` now uses generic placeholders instead of ARC Labs-specific values
- Settings tests use `_env_file=None` to prevent local `.env` contamination

## [1.3.0] - 2026-02-26

### Added

- Multi-workspace support via `LINEAR_WORKSPACES` environment variable
  - `WorkspaceRegistry` lazily creates and caches clients per workspace
  - Automatic team-key-to-workspace resolution across all workspaces
  - Fully backward compatible with single `LINEAR_API_KEY` setups
- ARC Labs security patterns to `.gitignore`

### Fixed

- CI: Update Claude GitHub Actions workflow permissions to `contents: write`

### Changed

- `LinearClient` now accepts `api_key` directly instead of full `Settings`
- Linear tools use `WorkspaceRegistry` for automatic workspace routing
- Workflow tools updated to work with multi-workspace architecture

## [0.1.0] - 2025-12-22

### Added

- Initial release of ARCLinearGitHub-MCP
- Linear API integration with GraphQL client
  - `linear_list_issues` - List issues from a project
  - `linear_get_issue` - Get issue details
  - `linear_create_issue` - Create new issues
  - `linear_update_issue` - Update existing issues
  - `linear_list_states` - List workflow states
  - `linear_list_labels` - List project labels
- GitHub API integration with REST client
  - `github_list_branches` - List repository branches
  - `github_create_branch` - Create branches with ARC naming
  - `github_list_prs` - List pull requests
  - `github_create_pr` - Create PRs with ARC template
  - `github_get_pr` - Get PR details
  - `github_get_default_branch` - Get default branch
- Workflow automation tools
  - `workflow_start_feature` - Create issue + branch combo
  - `workflow_validate_branch_name` - Validate branch names
  - `workflow_validate_commit_message` - Validate commits
  - `workflow_generate_branch_name` - Generate valid branch names
  - `workflow_generate_commit_message` - Generate valid commits
  - `workflow_get_conventions` - Get naming conventions reference
- ARC Labs naming convention enforcement
  - Branch naming: `<type>/<issue-id>-<description>`
  - Commit messages: `<type>(<scope>): <subject>`
  - PR titles: `<Type>/<Issue-ID>: <Title>`
- Pydantic models for type-safe API interactions
- Comprehensive test suite for validators
- Full documentation with README.md and CLAUDE.md
