# CLAUDE.md - AI Agent Context

This file provides context for Claude Code and other AI agents when working with the LinearGitHub-MCP project.

---

## Project Overview

LinearGitHub-MCP is an MCP (Model Context Protocol) Server that integrates Linear (issue tracking) and GitHub (repository management). It enforces naming conventions and automates development workflows.

**Key principle**: This MCP works with **any Linear project and GitHub repository** in your organization. Projects are specified dynamically via parameters or environment defaults.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12+ |
| MCP Framework | FastMCP (`mcp[cli]`) |
| Package Manager | uv |
| Linear API | GraphQL via `gql[httpx]` |
| GitHub API | REST via `httpx` |
| Validation | Pydantic v2 |

---

## Key Files

### Entry Point
- `src/arc_linear_github_mcp/server.py` - FastMCP server initialization and tool registration

### Configuration
- `src/arc_linear_github_mcp/config/settings.py` - Pydantic Settings for environment variables
- `src/arc_linear_github_mcp/config/standards.py` - Naming conventions and constants

### API Clients
- `src/arc_linear_github_mcp/clients/linear.py` - Async GraphQL client for Linear API
- `src/arc_linear_github_mcp/clients/github.py` - Async REST client for GitHub API

### MCP Tools
- `src/arc_linear_github_mcp/tools/linear.py` - Linear-specific MCP tools
- `src/arc_linear_github_mcp/tools/github.py` - GitHub-specific MCP tools
- `src/arc_linear_github_mcp/tools/workflow.py` - Combined workflow tools

### Validators
- `src/arc_linear_github_mcp/validators/branch.py` - Branch name validation
- `src/arc_linear_github_mcp/validators/commit.py` - Commit message validation

### Models
- `src/arc_linear_github_mcp/models/linear.py` - Pydantic models for Linear entities
- `src/arc_linear_github_mcp/models/github.py` - Pydantic models for GitHub entities

---

## Common Commands

```bash
# Install dependencies
uv sync

# Run in development mode with inspector
uv run mcp dev src/arc_linear_github_mcp/server.py

# Run directly
uv run python -m arc_linear_github_mcp.server

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=arc_linear_github_mcp

# Lint and format
uv run ruff check .
uv run ruff format .
```

---

## Environment Variables

Required in `.env` (all are **required** — no hardcoded defaults):

```bash
# Linear API
LINEAR_API_KEY=lin_api_xxxxx

# GitHub API
GITHUB_TOKEN=ghp_xxxxx
GITHUB_ORG=your-github-org

# Default project/repo (used when parameters are omitted)
DEFAULT_PROJECT=YOUR_PROJECT_KEY
DEFAULT_REPO=your-repo-name
```

### Multi-Project Configuration

The MCP works with **any Linear project and GitHub repository**. The `DEFAULT_PROJECT` and `DEFAULT_REPO` serve as fallback defaults when no explicit project/repo is provided.

**Usage patterns:**
- **Explicit project/repo**: Pass `project` or `repo` parameters to any tool to work with a specific project
- **Default fallback**: Omit `project`/`repo` parameters to use the configured defaults

**Example configurations:**

```bash
# For an iOS project
DEFAULT_PROJECT=MYAPP
DEFAULT_REPO=my-ios-app

# For internal tools
DEFAULT_PROJECT=TOOLS
DEFAULT_REPO=internal-tools

# For web projects
DEFAULT_PROJECT=WEBDEV
DEFAULT_REPO=company-website
```

All tools accept optional `project` and `repo` parameters, allowing you to work with multiple projects in the same session without changing environment variables.

---

## Naming Conventions

### Branch Names

**Format**: `<type>/<issue-id>-<description>`

| Type | When to use |
|------|-------------|
| `feature` | New functionality |
| `bugfix` | Bug fixes |
| `hotfix` | Urgent production fixes |
| `docs` | Documentation only |
| `spike` | Research/exploration |
| `release` | Release preparation |

**Examples**:
- `feature/PROJ-123-user-authentication`
- `bugfix/PROJ-456-login-crash`
- `docs/update-readme`

### Commit Messages

**Format**: `<type>(<scope>): <subject>`

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting |
| `refactor` | Code restructuring |
| `perf` | Performance |
| `test` | Tests |
| `chore` | Maintenance |
| `build` | Build system |
| `ci` | CI/CD |
| `revert` | Revert changes |

**Examples**:
- `feat(search): add restaurant filtering`
- `fix(map): resolve annotation crash`
- `docs(readme): update installation steps`

### PR Titles

**Format**: `<Type>/<Issue-ID>: <Title>`

**Examples**:
- `Feature/PROJ-123: User Authentication`
- `Bugfix/PROJ-456: Login Crash Fix`

---

## Architecture Notes

### MCP Tool Pattern

Tools are registered via decorator functions that receive the FastMCP instance:

```python
def register_linear_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def linear_list_issues(
        project: str | None = None,  # Optional, falls back to settings
        state: str | None = None,
        limit: int = 50,
    ) -> dict:
        settings = get_settings()
        project = project or settings.default_project  # Fallback pattern
        ...
```

### Client Pattern

All API clients are async and should be properly closed:

```python
client = LinearClient(settings)
try:
    result = await client.list_issues(...)
finally:
    await client.close()
```

### Validation Pattern

Validators return result dataclasses with `is_valid`, parsed components, and error/suggestions:

```python
result = validate_branch_name("feature/PROJ-123-test")
if result.is_valid:
    print(result.branch_type, result.issue_id, result.description)
else:
    print(result.error, result.suggestions)
```

---

## Testing

- Tests use pytest with async support
- Mock environment variables are set in `conftest.py`
- Validators have comprehensive unit tests
- API clients would need mocking for integration tests

---

## Adding New Tools

1. Add the tool function in the appropriate `tools/*.py` file
2. Use `@mcp.tool()` decorator
3. Include proper type hints and docstrings
4. **Use optional parameters with settings fallback** for project/repo:
   ```python
   async def my_tool(project: str | None = None) -> dict:
       settings = get_settings()
       project = project or settings.default_project
   ```
5. Return a dictionary with `success` boolean and relevant data or `error`
6. Handle exceptions and always close clients

---

## Error Handling

All tools return dictionaries with:
- `success: bool` - Whether the operation succeeded
- `error: str` - Error message if failed
- Operation-specific data if succeeded

---

## API Notes

### Linear API
- GraphQL endpoint: `https://api.linear.app/graphql`
- Authentication: Bearer token in Authorization header
- Team key (e.g., "MYAPP", "TOOLS") is used to identify projects
- Issue identifiers are formatted as `TEAM-NUMBER` (e.g., PROJ-123)

### GitHub API
- REST API endpoint: `https://api.github.com`
- Authentication: Bearer token
- Repository paths use org/repo format
- Branch creation requires getting base branch SHA first

---

## Available MCP Tools Reference

### Linear Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `linear_list_issues` | List issues from a project | `project?`, `state?`, `limit?` |
| `linear_get_issue` | Get issue details | `issue_id` |
| `linear_create_issue` | Create a new issue | `title`, `project?`, `description?`, `priority?`, `labels?` |
| `linear_update_issue` | Update an existing issue | `issue_id`, `state?`, `assignee?`, `title?`, `priority?` |
| `linear_list_states` | List workflow states | `project?` |
| `linear_list_labels` | List available labels | `project?` |

### GitHub Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `github_list_branches` | List repository branches | `repo?`, `limit?` |
| `github_create_branch` | Create a new branch | `branch_name`, `repo?`, `base_branch?` |
| `github_list_prs` | List pull requests | `repo?`, `state?` |
| `github_create_pr` | Create a pull request | `title`, `head`, `repo?`, `base?`, `body?` |
| `github_get_pr` | Get PR details | `pr_number`, `repo?` |
| `github_get_default_branch` | Get default branch | `repo?` |

### Workflow Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `workflow_start_feature` | Create issue + branch | `title`, `project?`, `repo?`, `description?`, `priority?`, `branch_type?` |
| `workflow_validate_branch_name` | Validate branch name | `branch_name` |
| `workflow_validate_commit_message` | Validate commit message | `message` |
| `workflow_generate_branch_name` | Generate branch name | `branch_type`, `description`, `issue_id?` |
| `workflow_generate_commit_message` | Generate commit message | `commit_type`, `subject`, `scope?` |
| `workflow_get_conventions` | Get naming reference | - |

**Note**: Parameters marked with `?` are optional and fall back to environment defaults.

---

## Common AI Agent Tasks

### Starting a new feature
```
1. Use workflow_start_feature with title, project, and repo
2. Returns Linear issue and GitHub branch
3. Provide checkout instructions to user
```

### Working with multiple projects
```
1. Pass explicit project/repo parameters to override defaults
2. Example: linear_list_issues(project="TOOLS") for tools project
3. Example: github_create_branch(repo="web-app") for web repo
```

### Validating user input
```
1. Use workflow_validate_branch_name for branch names
2. Use workflow_validate_commit_message for commits
3. Return suggestions if invalid
```

### Generating correct names
```
1. Use workflow_generate_branch_name with type, description, and optional issue_id
2. Use workflow_generate_commit_message with type, subject, and optional scope
3. Names are automatically normalized and formatted
```
