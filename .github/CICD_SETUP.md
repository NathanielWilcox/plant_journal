# CI/CD Pipeline Setup Guide

This document explains the GitHub Actions CI/CD pipeline for Plant Journal.

## Overview

The pipeline consists of 4 automated workflows:

1. **Test Suite** - Runs tests on every push and PR
2. **Code Quality** - Linting and formatting checks
3. **Security** - Vulnerability and secret scanning
4. **Deployment** - Builds and deploys to production (commented out until ready)

## Workflows

### 1. Test Suite (`test.yml`)

**Triggers:** Push to main/develop, Pull Requests

**What it does:**
- Tests against Python 3.10, 3.11, 3.12, 3.13 (matrix testing)
- Caches pip dependencies for speed
- Runs Django system checks
- Runs database migrations
- Executes full test suite with coverage reporting
- Uploads coverage to Codecov

**Key Features:**
- Matrix strategy tests multiple Python versions
- Pip caching for 5-10x faster builds
- Coverage reports automatically generated
- Integrates with Codecov for tracking coverage trends

**Status Requirement:** ✅ Must pass before merging to main

### 2. Code Quality (`lint.yml`)

**Triggers:** Push to main/develop, Pull Requests

**What it does:**
- Checks code formatting with Black
- Verifies import sorting with isort
- Lints with flake8 (catches errors and warnings)
- Type checking with pylint

**Key Features:**
- Non-blocking checks (continue-on-error: true)
- Helps maintain consistent code style
- Prevents common Python mistakes
- Runs in ~2 minutes

**Status Requirement:** ℹ️ Informational (doesn't block merges)

### 3. Security (`security.yml`)

**Triggers:** 
- Push to main/develop
- Pull Requests
- Daily schedule (2 AM UTC)

**What it does:**
- Security scanning with Bandit (finds common vulnerabilities)
- Checks for known package vulnerabilities with Safety
- Scans for secrets/credentials in code with TruffleHog

**Key Features:**
- Runs on schedule to catch new vulnerabilities
- Can detect accidentally committed secrets
- Protects against common security issues
- Non-blocking (continue-on-error: true)

**Status Requirement:** ℹ️ Informational (security issues flagged but won't block)

### 4. Deployment (`deploy.yml`)

**Triggers:** Push to main only (manual trigger available)

**What it does:**
- Builds and tests application
- Deploys to production (when uncommented)
- Posts deployment status to pull requests

**Currently:** Build and test only (deployment commented out)

**To Enable Deployment:**
1. Set up Heroku/Railway/Render account
2. Add `HEROKU_API_KEY` and `HEROKU_APP_NAME` to GitHub Secrets
3. Uncomment deployment steps in `deploy.yml`
4. Push to main to trigger auto-deployment

## Setup Instructions

### 1. Push to GitHub

```bash
git add .github/
git commit -m "Add GitHub Actions CI/CD pipeline"
git push origin main
```

### 2. Enable Actions (if needed)

Go to: `Settings → Actions → General` and ensure "Allow all actions and reusable workflows" is enabled

### 3. View Workflow Runs

Go to: `Actions` tab on your GitHub repository

You should see workflows running automatically.

### 4. Setup Code Coverage Tracking (Optional)

1. Go to https://codecov.io
2. Sign in with GitHub
3. Authorize codecov
4. Repository will be automatically tracked
5. Badge can be added to README

### 5. Setup Deployment (When Ready)

To enable automatic deployment:

#### For Heroku:
```bash
# Get your API key from Heroku settings
# Add to GitHub Secrets:
# - HEROKU_API_KEY: <your-api-key>
# - HEROKU_APP_NAME: <your-app-name>
```

#### For Railway:
```bash
# Similar setup but different secrets
# RAILWAY_TOKEN
```

#### For Render:
```bash
# Create deploy hook in Render dashboard
# Add RENDER_DEPLOY_HOOK_URL to GitHub Secrets
```

## GitHub Secrets

Secrets needed for deployments (add via `Settings → Secrets and variables → Actions`):

```
HEROKU_API_KEY=<your-heroku-api-key>
HEROKU_APP_NAME=<your-app-name>
```

## Branch Protection Rules (Recommended)

To enforce CI/CD checks:

1. Go to `Settings → Branches`
2. Add rule for `main` branch
3. Require status checks to pass:
   - test (all matrices must pass)
4. Require branches to be up to date
5. Dismiss stale reviews when new commits pushed

This ensures:
- ✅ All tests pass before merging
- ✅ No accidental force pushes
- ✅ Code review required (if set up)

## Monitoring & Alerts

### Check Status
- Dashboard: `Actions` tab shows all runs
- Badges: Can be added to README
- Email: GitHub emails on failures (configurable)

### Failure Notifications
- GitHub shows red ✗ on failed checks
- PR shows which checks failed
- Email notifications (by default)
- Slack integration available (via GitHub App)

## Common Issues & Fixes

### Tests failing locally but passing in CI
- Different Python version: Run locally with same version
- Missing dependencies: Check requirements.txt is up to date
- Database: CI creates fresh SQLite, yours might have old state

### CI taking too long
- Cache is helping: First run is slowest
- Can parallelize more: Add more matrix combinations
- Reduce test scope: Use `-m "not slow"` marker

### Secrets not working in deploy
- Double-check secret names match exactly
- Verify secret value is correct
- Redeploy workflow after adding secret

## Next Steps

1. ✅ Push workflows to GitHub
2. ✅ Verify workflows run successfully
3. ✅ Set up branch protection rules
4. ✅ When ready: Add deployment secrets and enable deploy workflow
5. ✅ Monitor runs and fix any issues

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Django Deployment Guides](https://docs.djangoproject.com/en/5.2/howto/deployment/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.io/)
