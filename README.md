# 🔄 ARCLinearGitHub-MCP

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

MCP Server that integrates Linear and GitHub for seamless development workflows across all ARC Labs Studio projects.

- **Multi-Project Support** - Works with any Linear workspace and GitHub repository
- **Convention Enforcement** - Automatic branch, commit, and PR naming validation
- **Workflow Automation** - Create issues and branches in one command
- **AI-Native** - Designed for Claude Desktop and Claude Code integration

---

## 🎯 Overview

ARCLinearGitHub-MCP is a Model Context Protocol (MCP) Server that bridges Linear (issue tracking) and GitHub (repository management) for ARC Labs Studio. It enables AI assistants like Claude to manage your development workflow while enforcing consistent naming conventions.

### Key Capabilities

- **Linear Integration**: Create, list, update, and search issues across any workspace
- **GitHub Integration**: Manage branches and pull requests with proper naming
- **Workflow Automation**: Combined tools for end-to-end feature development
- **Naming Validation**: Ensure branch names and commit messages follow standards
- **Multi-Project**: Dynamically work with any project without reconfiguration

---

## 📋 Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| uv | Latest |
| Linear API Key | `lin_api_*` |
| GitHub Token | `ghp_*` with repo access |

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/arclabs-studio/ARCLinearGitHub-MCP.git
cd ARCLinearGitHub-MCP
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Linear API
LINEAR_API_KEY=lin_api_xxxxxxxxxxxxx

# GitHub API
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
GITHUB_ORG=arclabs-studio

# Default Project (used when no project/repo is specified)
DEFAULT_PROJECT=FAVRES
DEFAULT_REPO=FavRes
```

### 4. Integrate with Claude

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ARC Workflow": {
      "command": "/absolute/path/to/ARCLinearGitHub-MCP/.venv/bin/python",
      "args": ["-m", "arc_linear_github_mcp.server"],
      "cwd": "/absolute/path/to/ARCLinearGitHub-MCP"
    }
  }
}
```

#### Claude Code

The MCP is automatically available when working within the project directory, or configure it globally in your Claude Code settings.

---

## 📖 Usage

### Multi-Project Configuration

The MCP is designed to work with **any Linear project and GitHub repository**. You have two ways to specify which project to use:

#### Option 1: Environment Defaults

Set `DEFAULT_PROJECT` and `DEFAULT_REPO` in your `.env` file. All tools will use these when no explicit project is provided.

```bash
# For FavRes iOS project
DEFAULT_PROJECT=FAVRES
DEFAULT_REPO=FavRes

# For internal tools
DEFAULT_PROJECT=TOOLS
DEFAULT_REPO=internal-tools
```

#### Option 2: Explicit Parameters

Pass `project` and `repo` parameters to any tool to work with a specific project, regardless of defaults.

```
# List issues from a different project
linear_list_issues(project="WEBDEV")

# Create branch in a different repo
github_create_branch(repo="company-website", branch_name="feature/WEB-1-homepage")
```

---

## 🛠️ Use Cases

### Use Case 1: Starting a New Feature

**Scenario**: You're starting work on a new feature and need to create a Linear issue and matching GitHub branch.

**With Claude**:
```
"Start a new feature called 'User Authentication' for the FAVRES project"
```

**What happens**:
1. Creates a Linear issue titled "User Authentication" in FAVRES
2. Creates a GitHub branch `feature/FAVRES-XXX-user-authentication`
3. Returns next steps for local checkout

**Manual tool call**:
```python
workflow_start_feature(
    title="User Authentication",
    description="Implement OAuth2 login flow",
    project="FAVRES",
    repo="FavRes",
    priority=2
)
```

---

### Use Case 2: Working Across Multiple Projects

**Scenario**: You manage several projects (iOS app, web app, internal tools) and need to switch between them.

**With Claude**:
```
"Show me all in-progress issues for the WEBDEV project"
"Now create a bugfix branch for TOOLS-42 in the internal-tools repo"
```

**What happens**:
- Each command targets the specified project/repo
- No need to change environment variables
- Works seamlessly in a single conversation

**Tool calls**:
```python
# List issues from web project
linear_list_issues(project="WEBDEV", state="In Progress")

# Create branch in tools repo
github_create_branch(
    repo="internal-tools",
    branch_name="bugfix/TOOLS-42-fix-sync-issue"
)
```

---

### Use Case 3: Validating Branch Names and Commits

**Scenario**: You want to ensure your branch name and commit message follow ARC Labs conventions.

**With Claude**:
```
"Validate this branch name: feature/FAVRES-123-add-search"
"Is this commit message correct? 'Added new search feature'"
```

**What happens**:
- Validates against ARC Labs naming patterns
- Returns detailed feedback with suggestions if invalid
- Explains what's wrong and how to fix it

**Tool calls**:
```python
# Validate branch
workflow_validate_branch_name("feature/FAVRES-123-add-search")
# Returns: Valid feature branch for issue FAVRES-123

# Validate commit (this would fail)
workflow_validate_commit_message("Added new search feature")
# Returns: Invalid - missing type prefix, use "feat(search): add search feature"
```

---

### Use Case 4: Generating Correct Names

**Scenario**: You have a description and need to generate a properly formatted branch name or commit message.

**With Claude**:
```
"Generate a branch name for bugfix on issue FAVRES-456 about fixing the map crash"
"Generate a commit message for adding restaurant filtering to the search module"
```

**Tool calls**:
```python
# Generate branch name
workflow_generate_branch_name(
    branch_type="bugfix",
    issue_id="FAVRES-456",
    description="Fix map crash on annotation tap"
)
# Returns: bugfix/FAVRES-456-fix-map-crash-on-annotation-tap

# Generate commit message
workflow_generate_commit_message(
    commit_type="feat",
    scope="search",
    subject="Add restaurant filtering by cuisine type"
)
# Returns: feat(search): add restaurant filtering by cuisine type
```

---

### Use Case 5: Daily Workflow with Claude Code

**Scenario**: You're using Claude Code for your daily development workflow.

**Morning standup**:
```
"Show me my in-progress issues for FAVRES"
```

**Starting work**:
```
"Create a branch for FAVRES-123 about implementing the favorites feature"
```

**During development**:
```
"What's the correct commit message format for a refactor?"
"Validate my commit: refactor(storage): simplify data persistence layer"
```

**Creating PR**:
```
"Create a PR for the current branch linking to FAVRES-123"
```

---

### Use Case 6: Team Onboarding

**Scenario**: A new team member needs to understand ARC Labs conventions.

**With Claude**:
```
"Show me all the ARC Labs naming conventions"
```

**Tool call**:
```python
workflow_get_conventions()
```

**Returns**:
```json
{
  "branch_naming": {
    "format": "<type>/<issue-id>-<description>",
    "types": ["bugfix", "docs", "feature", "hotfix", "release", "spike"],
    "examples": [...]
  },
  "commit_format": {
    "format": "<type>(<scope>): <subject>",
    "types": ["build", "chore", "ci", "docs", "feat", "fix", ...],
    "rules": [...]
  },
  "pr_naming": {...}
}
```

---

## 🔧 Available Tools

### Linear Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `linear_list_issues` | List issues from a project | `project`, `state`, `limit` |
| `linear_get_issue` | Get issue details | `issue_id` |
| `linear_create_issue` | Create a new issue | `title`, `project`, `priority`, `labels` |
| `linear_update_issue` | Update an existing issue | `issue_id`, `state`, `assignee`, `title` |
| `linear_list_states` | List workflow states | `project` |
| `linear_list_labels` | List available labels | `project` |

### GitHub Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `github_list_branches` | List repository branches | `repo`, `limit` |
| `github_create_branch` | Create a new branch | `repo`, `branch_name`, `base_branch` |
| `github_list_prs` | List pull requests | `repo`, `state` |
| `github_create_pr` | Create a pull request | `repo`, `title`, `head`, `base`, `body` |
| `github_get_pr` | Get PR details | `pr_number`, `repo` |
| `github_get_default_branch` | Get default branch | `repo` |

### Workflow Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `workflow_start_feature` | Create issue + branch | `title`, `project`, `repo`, `branch_type` |
| `workflow_validate_branch_name` | Validate branch name | `branch_name` |
| `workflow_validate_commit_message` | Validate commit message | `message` |
| `workflow_generate_branch_name` | Generate branch name | `branch_type`, `description`, `issue_id` |
| `workflow_generate_commit_message` | Generate commit message | `commit_type`, `subject`, `scope` |
| `workflow_get_conventions` | Get naming reference | - |

---

## 📐 ARC Labs Naming Conventions

### Branch Naming

**Format**: `<type>/<issue-id>-<description>`

| Type | Purpose | Example |
|------|---------|---------|
| `feature` | New functionality | `feature/PROJ-123-user-auth` |
| `bugfix` | Bug fixes | `bugfix/PROJ-456-login-crash` |
| `hotfix` | Urgent production fixes | `hotfix/PROJ-789-security-patch` |
| `docs` | Documentation only | `docs/update-readme` |
| `spike` | Research/exploration | `spike/evaluate-swiftui` |
| `release` | Release preparation | `release/1.2.0` |

### Commit Messages

**Format**: `<type>(<scope>): <subject>`

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature | `feat(auth): add OAuth2 login` |
| `fix` | Bug fix | `fix(map): resolve annotation crash` |
| `docs` | Documentation | `docs(readme): update setup guide` |
| `style` | Formatting | `style: apply swiftformat rules` |
| `refactor` | Code refactoring | `refactor(storage): simplify persistence` |
| `perf` | Performance | `perf(search): optimize query caching` |
| `test` | Tests | `test(auth): add login unit tests` |
| `chore` | Maintenance | `chore: update dependencies` |
| `build` | Build system | `build: configure CI pipeline` |
| `ci` | CI changes | `ci: add test coverage step` |
| `revert` | Revert changes | `revert: undo auth changes` |

### PR Titles

**Format**: `<Type>/<Issue-ID>: <Title>`

**Examples**:
- `Feature/FAVRES-123: User Authentication`
- `Bugfix/FAVRES-456: Map Annotation Crash Fix`
- `Hotfix/FAVRES-789: Critical Security Patch`

---

## 🏗️ Project Structure

```
ARCLinearGitHub-MCP/
├── src/arc_linear_github_mcp/
│   ├── server.py              # FastMCP server entry point
│   ├── config/
│   │   ├── settings.py        # Pydantic settings (env vars)
│   │   └── standards.py       # Naming convention constants
│   ├── clients/
│   │   ├── linear.py          # Linear GraphQL client
│   │   └── github.py          # GitHub REST client
│   ├── tools/
│   │   ├── linear.py          # Linear MCP tools
│   │   ├── github.py          # GitHub MCP tools
│   │   └── workflow.py        # Combined workflow tools
│   ├── validators/
│   │   ├── branch.py          # Branch name validation
│   │   └── commit.py          # Commit message validation
│   └── models/
│       ├── linear.py          # Linear Pydantic models
│       └── github.py          # GitHub Pydantic models
├── tests/
│   └── test_validators/       # Validator unit tests
├── CLAUDE.md                  # AI agent context
├── .env.example               # Environment template
└── pyproject.toml             # Project configuration
```

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# With verbose output
uv run pytest -v

# With coverage report
uv run pytest --cov=arc_linear_github_mcp
```

---

## 🛠️ Development

### Running in Development Mode

```bash
# With MCP Inspector (recommended for debugging)
uv run mcp dev src/arc_linear_github_mcp/server.py

# Direct execution
uv run python -m arc_linear_github_mcp.server
```

### Linting and Formatting

```bash
# Check for issues
uv run ruff check .

# Auto-format code
uv run ruff format .
```

---

## 🤝 Contributing

1. Create a feature branch following naming conventions
2. Make changes with proper commit messages
3. Ensure all tests pass
4. Create a PR using the ARC Labs template

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">Made with 💛 by ARC Labs Studio</p>
