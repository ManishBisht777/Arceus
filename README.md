# Arceus: AI-Powered Jira to Pull Request Automation

Arceus is an intelligent automation tool that transforms Jira tickets into working pull requests by orchestrating a multi-step workflow combining AI-assisted code investigation, implementation, and git operations.

## 🎯 What It Does

Arceus automates the entire software development lifecycle from issue to PR:

1. **Fetches Jira tickets** with full context (summary, description, comments, status)
2. **Performs AI-powered investigation** to understand the codebase and identify required changes
3. **Implements solutions** using Claude AI with write permissions
4. **Manages git operations** (worktrees, commits, pushes)
5. **Creates pull requests** with comprehensive documentation

The entire workflow runs end-to-end with minimal manual intervention, enabling teams to go from Jira ticket to ready-for-review PR in minutes.

## 🛠️ Architecture & Components

### Core Systems

```
┌─────────────────────────────────────────────────────────┐
│                    ARCEUS WORKFLOW                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. JIRA Ticket Fetcher → Retrieves ticket context    │
│  2. Git Worktree Manager → Creates/reuses branches    │
│  3. Investigation Agent → Analyzes codebase           │
│  4. Implementation Agent → Writes & tests code        │
│  5. Diff Reviewer → Validates changes                 │
│  6. Commit & Push → Stages changes to git             │
│  7. PR Creator → Generates pull request               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Tools

#### **Integration Tools**
- **Jira Tool** (`src/arceus/tools/jira.py`): Fetches tickets via Atlassian API, extracts descriptions in Atlassian Document Format (ADF), retrieves comments and status
- **GitHub Tool** (`src/arceus/tools/github.py`): Creates pull requests using the GitHub CLI (`gh`)
- **Git Tool** (`src/arceus/tools/git.py`): Manages git operations (worktrees, commits, pushes, branch management)
- **Filesystem Tool** (`src/arceus/tools/filesystem.py`): File operations for code inspection
- **Shell Tool** (`src/arceus/tools/shell.py`): Executes shell commands and test suites

#### **AI Agents**
- **Claude Agent** (`src/arceus/agents/claude.py`): Orchestrates Claude Code to perform investigation and implementation
- **Investigation Agent**: Read-only analysis phase that produces implementation plans
- **Coding Agent**: Write-enabled phase that implements solutions and tests

#### **State & Configuration**
- **AgentState** (`src/arceus/graph/state.py`): Tracks workflow state across all phases
- **Configuration** (`src/arceus/config.py`): Environment and project settings

## 🔄 Workflow Steps

### Phase 1: Ticket Retrieval
```
Input: Jira ticket key (e.g., DTP-3861)
Process:
  • Fetch ticket from Jira REST API
  • Extract summary, description, comments
  • Retrieve ticket status
Output: Ticket context with full metadata
```

### Phase 2: Branch & Worktree Setup
```
Input: Ticket key, summary, base branch
Process:
  • Generate branch keyword from ticket summary (e.g., "fix-login-validation")
  • Branch name: {TICKET_KEY}-{KEYWORD}
  • Create isolated git worktree OR reuse existing
  • Fetch latest remote base branch
  • Rebase worktree if reusing existing branch
Output: Dedicated worktree at `../worktrees/{BRANCH_NAME}`
```

### Phase 3: Investigation (Read-Only)
```
Input: Ticket context, codebase path
Process:
  • Claude Code inspects codebase (read-only)
  • No write permissions, no git commands
  • Produces structured analysis:
    - Relevant Files: Which files need changes
    - Current Implementation: How code currently works
    - Problem: Root cause analysis
    - Proposed Solution: Exact changes needed
    - Tests: Required test coverage
    - Risks: Potential regressions
Output: Investigation report used in implementation phase
```

### Phase 4: Implementation (Write-Enabled)
```
Input: Investigation report, ticket context, worktree
Process:
  • Claude Code has full write permissions
  • Modifies code in packages/sop-web/
  • Runs relevant tests
  • Fixes any test failures
  • Cannot commit/push (handled by Arceus)
Output: Implemented changes in worktree
```

### Phase 5: Diff & Validation
```
Input: Worktree with changes
Process:
  • Extract git diff for changed files
  • Verify changes exist
  • Display diff for transparency
Output: Validated changeset
```

### Phase 6: Git Operations
```
Process Steps:
  1. Stage all changes in packages/sop-web/
  2. Create commit with message: "{TICKET_KEY}: {SUMMARY}"
  3. Push branch to origin with upstream tracking (-u flag)
Output: Branch pushed to remote
```

### Phase 7: Pull Request Creation
```
Input: Branch name, ticket metadata, investigation, implementation
Process:
  • Generate PR title: "[ephemeral] {TICKET_SUMMARY}"
  • Build comprehensive PR body:
    - Link to Jira ticket
    - Original ticket description
    - Implementation summary from Claude
    - Investigation findings for context
  • Create PR against configured base branch
Output: Live GitHub PR with full context
```

## 📋 Configuration

### Environment Variables

```bash
# Jira Configuration
JIRA_BASE_URL=https://jira.company.com      # Jira instance URL
JIRA_EMAIL=user@company.com                  # Jira API user email
JIRA_API_TOKEN=xxxxxxxxxxxxxxxxxxxx         # Jira API token

# Git Configuration
ARCEUS_REPO_PATH=/path/to/repo              # Target repository path
ARCEUS_PROD_BRANCH=main                     # Base branch for PRs
ARCEUS_PR_BRANCH=staging-no-training        # (Optional) custom PR branch

# GitHub Configuration
GH_TOKEN=github_pat_xxxxxxxxxxxxxxx         # GitHub CLI authentication
```

### Project Settings

Configured in `src/arceus/config.py`:
- Repository path for cloning/worktrees
- Base branch for PR creation
- Scope: Only modifies `packages/sop-web/`

## 🚀 Usage

### Installation

```bash
# Clone repository
git clone <repo-url>
cd arceus

# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Running Arceus

```bash
# Basic usage with ticket key
uv run python -m arceus.main DTP-3861

# Output:
# 🎫 Fetching Jira ticket DTP-3861...
# ✅ DTP-3861: Fix login validation error
# 🌿 Worktree base: main
# 🏷️ Generated keyword: fix-login-validation
# 🌳 Creating/reusing worktree...
# 📁 Worktree: ../worktrees/DTP-3861-fix-login-validation
# 🔍 Claude investigation...
# [Investigation report...]
# 🤖 Claude implementing...
# [Implementation report...]
# 💾 Committing changes...
# 🚀 Pushing branch...
# 🔀 Creating PR...
# ================================================================================
# ARCEUS COMPLETE
# ================================================================================
# Ticket: DTP-3861
# Branch: DTP-3861-fix-login-validation
# PR: https://github.com/company/repo/pull/1234
```

## 🔍 How Claude AI Integration Works

### Investigation Phase (Read-Only)
- Claude Code runs in read-only mode (`allow_writes=False`)
- Access to full codebase inspection
- Cannot modify files or run git commands
- Produces detailed analysis and implementation plan

### Implementation Phase (Write-Enabled)
- Claude Code runs with write permissions (`allow_writes=True`)
- Can create/modify/delete files in scope
- Can run test suites
- Cannot commit/push (Arceus handles this)
- Provides summary of changes and test results

### Invocation
- Uses Claude Code CLI (`claude` command)
- Runs in isolated git worktree
- Inherits permissions via CLI flags
- Captures stdout for structured output

## 🔐 Safety & Isolation

### Git Worktree Isolation
- Each ticket gets its own worktree
- Changes are isolated from main repository
- Base branch is always fetched fresh
- Prevents accidental interference between parallel runs

### Scope Limitations
- Only `packages/sop-web/` can be modified
- Other directories protected from changes
- Prevents scope creep and unintended modifications

### Worktree Reuse Safety
- Detects existing worktrees by branch name
- Validates worktree is in Git's registry
- Rejects worktrees with uncommitted changes
- Rebases on latest base branch before reuse
- Prevents data loss from stale branches

### Commit Safety
- Uses `--no-verify` to skip pre-commit hooks (respects CI)
- Validates changes exist before committing
- Clear commit messages with ticket context
- Push includes upstream tracking setup

## 📊 Dependencies

### Core Libraries
- **LangChain** (≥1.3.15): AI agent orchestration framework
- **LangGraph** (≥1.2.11): Workflow state management and graph execution
- **LangChain Google GenAI** (≥4.3.4): Integration with Google Gemini models

### Integration Libraries
- **Requests** (≥2.34.2): HTTP client for Jira API
- **Slack Bolt** (≥1.30.0): Slack app framework for notifications
- **Python Dotenv** (≥1.2.3): Environment variable management

### External Requirements
- **Claude Code CLI**: Must be installed and available in PATH
- **Git**: Git 2.36+ with worktree support
- **GitHub CLI** (gh): For PR creation
- **Python** 3.12+

## 🎯 Use Cases

### 1. Routine Bug Fixes
Small bugs that don't require complex architecture changes
```
Jira Ticket → Claude analyzes → Implements fix → Tests → Creates PR
Timeline: 5-10 minutes
```

### 2. Feature Implementation
Well-scoped features with clear requirements
```
Jira Ticket → Investigation → Implementation → Full test coverage → PR
Timeline: 15-30 minutes
```

### 3. Code Refactoring
Controlled refactoring of specific components
```
Jira Ticket → Code analysis → Refactor → Test verification → PR
Timeline: 10-20 minutes
```

### 4. Documentation Updates
Content changes and documentation improvements
```
Jira Ticket → Review docs → Update → Validation → PR
Timeline: 3-5 minutes
```

## 📈 Limitations & Considerations

### When Arceus Works Best
- ✅ Well-defined, scoped issues
- ✅ Issues within a single package (`packages/sop-web/`)
- ✅ Issues with clear acceptance criteria
- ✅ Non-critical features suitable for async implementation
- ✅ Routine maintenance and bug fixes

### When to Use Manual Process
- ❌ Issues requiring architecture decisions
- ❌ Cross-repository or cross-package changes
- ❌ Highly complex logic requiring design reviews
- ❌ Sensitive security-related changes
- ❌ Issues requiring stakeholder input during implementation

## 🛠️ Extending Arceus

### Adding Custom Tools
1. Create tool in `src/arceus/tools/`
2. Use `@tool` decorator from LangChain
3. Import in workflow.py
4. Integrate into workflow phase

### Customizing Prompts
- Edit `src/arceus/agents/prompts.py`
- Investigation prompt: Analysis strategy
- Implementation prompt: Implementation guidelines
- Customize for your codebase patterns

### Modifying Workflow Steps
- Edit `src/arceus/workflow.py`
- Reorder phases as needed
- Add validation steps
- Integrate additional tools

### Adding Notifications
- Slack integration prepared in `src/arceus/slack/`
- Configure Slack bot token
- Add notification calls to workflow

## 📝 Project Files Reference

```
arceus/
├── src/arceus/
│   ├── main.py                 # CLI entry point
│   ├── workflow.py             # Main workflow orchestration
│   ├── config.py               # Configuration management
│   ├── utils.py                # Utility functions
│   ├── tools/
│   │   ├── jira.py            # Jira API integration
│   │   ├── git.py             # Git worktree operations
│   │   ├── github.py          # GitHub PR creation
│   │   ├── filesystem.py       # File operations
│   │   └── shell.py           # Shell command execution
│   ├── agents/
│   │   ├── claude.py          # Claude Code CLI wrapper
│   │   ├── coding.py          # Coding agent configuration
│   │   └── prompts.py         # Investigation & implementation prompts
│   ├── graph/
│   │   ├── workflow.py        # LangGraph workflow definition
│   │   ├── nodes.py           # Workflow node definitions
│   │   └── state.py           # State type definitions
│   └── slack/
│       ├── app.py             # Slack app setup
│       └── __main__.py        # Slack bot entry point
├── pyproject.toml              # Project metadata & dependencies
└── README.md                   # This file
```

## 🤝 Contributing

To extend or modify Arceus:

1. Follow existing tool structure and patterns
2. Add type hints to all functions
3. Include docstrings for new tools
4. Test changes with real Jira tickets
5. Update this README for significant changes

## 📞 Support & Troubleshooting

### Common Issues

**"Jira ticket not found"**
- Verify ticket key is correct and capitalized
- Check JIRA_EMAIL and JIRA_API_TOKEN are valid
- Ensure JIRA_BASE_URL is correct

**"Git worktree error"**
- Check ARCEUS_REPO_PATH points to valid repository
- Verify git version supports worktrees (≥2.36)
- Remove stale worktree: `git worktree remove ../worktrees/OLD-KEY`

**"Claude Code failed"**
- Verify `claude` CLI is installed: `which claude`
- Check working directory permissions
- Review Claude Code output for specific errors

**"PR creation failed"**
- Verify GitHub CLI is installed: `which gh`
- Check GH_TOKEN is valid and has repo permissions
- Ensure ARCEUS_PROD_BRANCH exists on remote

## 📄 License

[Specify your project's license]

## 👤 Author

Manish Bisht (manish@delightree.com)

---

**Version**: 0.1.0  
**Last Updated**: August 2024
