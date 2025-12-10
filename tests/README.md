# Plant Journal Test Suite - Developer Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Testing Project](#testing-project)
3. [Adding New Tests](#adding-new-tests)
4. [Verifying Changes](#verifying-changes)
5. [Test Structure](#test-structure)
6. [Running Specific Tests](#running-specific-tests)
7. [Debugging Tests](#debugging-tests)
8. [CI/CD Integration](#cicd-integration)

---

## Quick Start

### Prerequisites

Ensure these packages are installed in your virtual environment:

```bash
pip install pytest pytest-django pytest-cov factory-boy faker
```

Or install all from requirements:

```bash
pip install -r requirements.txt
```

### Running All Tests

Run the complete test suite:

```bash
pytest
```

### Running Tests with Coverage Report

Generate a coverage report showing which code is tested:

```bash
pytest --cov=. --cov-report=html
```

The HTML report will be generated in `htmlcov/index.html`. Open it in a browser to see detailed coverage.

### Running Tests Silently (Minimal Output)

```bash
pytest -q
```

### Running Tests with Verbose Output

```bash
pytest -v
```

---

---

## 📊 Current Test Status

**✅ All core tests passing** (with some UI tests intentionally skipped)

- ✅ Unit tests for models and serializers
- ✅ Integration tests for API endpoints and permissions
- ✅ Workflow tests for cross-layer processes
- ⏭️ UI tests (Gradio - separate integration layer, may be skipped)
- ✅ E2E tests for complete user journeys

**Key Implementation Details:**

- Fixtures use pytest-django `db` parameter for database access
- API client fixtures create new `APIClient()` instances per user (prevents auth bleed)
- Serializer validation properly returns 400 errors (not 500)
- Owner auto-assigned during model creation via `perform_create()`
- PlantCreateUpdateSerializer includes owner/id/added_at as read-only fields
- LogCreateSerializer validates sunlight_hours between 0-24

---

## Testing Project

This test suite is organized into **5 phases** with clear separation of concerns:

### Phase 1: Unit Tests (Models & Serializers)

**Location:** `plants/tests/test_models.py`, `users/tests.py`

Tests individual components in isolation:

- User model creation and password hashing
- Plant model validation and relationships (defaults: pot_size='medium', sunlight_preference='bright_indirect_light')
- Log model cascading deletes with owner tracking
- Serializer validation patterns:
  - `PlantCreateUpdateSerializer`: write operations with read-only owner/id/added_at
  - `PlantSerializer`: read operations with nested logs
  - `LogCreateSerializer`: write operations with writable plant field
  - `LogSerializer`: read operations with read-only plant, timestamp, owner

**Run Phase 1:**

```bash
pytest plants/tests/test_models.py users/tests.py -v
pytest -m unit  # All unit tests
```

### Phase 2: Integration Tests (API Endpoints)

**Location:** `plants/tests/test_views.py`, `users/tests.py`

Tests API endpoints with multi-user isolation:

- **PlantViewSet CRUD:** list (filters by owner), create (auto-assigns owner), retrieve (404 for non-owner), update (PATCH), delete
- **LogViewSet CRUD:** list (filters by owner), create (validates plant ownership + sunlight hours), retrieve, update, delete
- **Custom Routes:** `GET /plants/{id}/logs/` returns plant's logs ordered by timestamp
- **Authentication:** 401 for unauthenticated requests
- **Authorization:** 404 for accessing other users' data, 403 for creating logs on other users' plants
- **Serializer Routing:** POST/PATCH use *CreateSerializer (writable plant), GET uses*Serializer (read-only)

**Important:** API client fixtures create new instances per user to prevent authentication bleeding between tests

**Run Phase 2:**

```bash
pytest plants/tests/test_views.py -v
pytest -m integration  # All integration tests
```

### Phase 3: Workflow Integration Tests (Cross-Layer)

**Location:** `tests/test_auth_flow.py`

Tests complete workflows across multiple layers:

- **Authentication Flow:** Register → Login (JWT tokens) → Create Data → Logout
- **Plant Lifecycle:** Create → List (verify owner filter) → Retrieve → Update (PATCH) → Delete
- **Log Lifecycle:** Create (validates plant ownership) → List → Retrieve → Update → Delete
- **Multi-user Isolation Tests:**
  - User A cannot see User B's plants (404)
  - User A cannot update User B's plants (404)
  - User A cannot delete User B's plants (404)
  - User A cannot see User B's logs (404)
- **Cascade Deletes:** Deleting a plant cascades deletes to logs

**Key Test Classes:**

- `TestAuthenticationFlow`: Register/login/token generation
- `TestPlantLifecycleFlow`: Full CRUD with ownership verification
- `TestLogLifecycleFlow`: CRUD with plant dependency
- `TestMultiUserIsolation`: Permission enforcement across users

**Run Phase 3:**

```bash
pytest tests/test_auth_flow.py -v
pytest -m auth  # All auth-related tests
```

### Phase 4: Gradio UI Integration Tests

**Location:** `tests/test_gradio_ui.py`

Tests UI handlers and mocked API calls (some tests may be skipped for UI-specific setup):

- Authentication UI (login, register, logout)
- Plant management UI (create, update, delete)
- Log management UI (create, update, delete)
- Error handling and validation

**Skipped Tests:**

- `test_ui_register_success` - UI layer requires separate mock setup
- `test_ui_load_user_plants` - UI layer requires separate mock setup
- `test_ui_delete_plant` - UI layer requires separate mock setup

**Run Phase 4:**

```bash
pytest tests/test_gradio_ui.py -v
pytest tests/test_gradio_ui.py::TestGradioPlantUI::test_ui_create_plant -v  # Run non-skipped UI tests
```

### Phase 5: End-to-End Tests

**Location:** `tests/test_e2e_workflows.py`

Tests complete user journeys and error scenarios:

- **Full User Journey:** Register (foliage_plant category, biweekly schedule) → Create plant → Create log → Verify data
- **Multiple Users:** User A and User B create independent plants/logs, verify no cross-user visibility
- **Error Recovery:** Invalid data validation, cascade delete preservation
- **Validation Across Boundaries:** Sunlight validation returns 400 (not 500), plant ownership enforced

**Key Test Classes:**

- `TestCompleteApplicationWorkflow`: Full user journeys with valid data (foliage_plant, biweekly)
- `TestErrorRecoveryScenarios`: Invalid input handling, cascade deletes
- `TestDataValidationIntegration`: Sunlight hours bounds checking (0-24)

**Run Phase 5 (slow tests marked):**

```bash
pytest tests/test_e2e_workflows.py -v
pytest -m e2e  # All E2E tests
pytest -m "not slow"  # Skip slow E2E tests (faster verification)
```

---

## Adding New Tests

### 1. Create a New Test File

**For API endpoint tests:** Add to appropriate app's `tests/` directory:

```python
# plants/tests/test_new_feature.py
import pytest
from rest_framework import status

@pytest.mark.integration
class TestNewFeature:
    def test_new_endpoint(self, api_client_with_user):
        response = api_client_with_user.get('/api/plants/')
        assert response.status_code == status.HTTP_200_OK
```

**For workflow tests:** Add to `tests/` directory:

```python
# tests/test_new_workflow.py
import pytest

@pytest.mark.e2e
class TestNewWorkflow:
    def test_new_user_workflow(self, api_client):
        # Test implementation
        pass
```

### 2. Use Provided Fixtures

The test suite provides ready-to-use fixtures in `tests/conftest.py`:

```python
# Available fixtures:
api_client                    # Unauthenticated API client
api_client_with_user         # Authenticated as test_user
api_client_with_user_2       # Authenticated as test_user_2
test_user                    # User object
test_user_2                  # Second user object
test_plant                   # Plant owned by test_user
test_plant_2                 # Plant owned by test_user_2
test_log                     # Log for test_plant
test_logs                    # Multiple logs
valid_plant_data            # Valid plant creation dict
valid_log_data              # Valid log creation dict
valid_user_data             # Valid user registration dict
valid_login_data            # Valid login credentials dict
```

### 3. Example: Adding a New Plant Feature Test

```python
import pytest
from rest_framework import status

@pytest.mark.integration
@pytest.mark.plant
class TestNewPlantFeature:
    """Test new plant feature"""
    
    def test_new_plant_endpoint(self, api_client_with_user):
        """Test the new plant endpoint"""
        response = api_client_with_user.post(
            '/api/plants/',
            {
                'name': 'Test Plant',
                'category': 'succulent',
                'care_level': 'easy'
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test Plant'
    
    def test_new_plant_permission(self, api_client_with_user, api_client_with_user_2, test_plant):
        """Test that users can only access their own plants"""
        # test_plant is owned by test_user, try accessing as test_user_2
        response = api_client_with_user_2.get(f'/api/plants/{test_plant.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
```

### 4. Test Markers (Categories)

Use pytest markers to organize tests:

```python
@pytest.mark.unit              # Single component test
@pytest.mark.integration       # Multi-component test
@pytest.mark.e2e               # End-to-end workflow
@pytest.mark.slow              # Takes >1 second
@pytest.mark.auth              # Authentication related
@pytest.mark.plant             # Plant model/API
@pytest.mark.log               # Log model/API
@pytest.mark.user              # User model/API
```

### 5. Running Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only plant tests
pytest -m plant

# Run integration tests excluding slow tests
pytest -m "integration and not slow"

# Run all tests except end-to-end
pytest -m "not e2e"
```

---

## Verifying Changes

### 1. After Making Code Changes

**Always run tests to verify nothing broke:**

```bash
# Quick verification (unit + integration)
pytest -m "not e2e" --tb=short
```

**Check coverage for your changed code:**

```bash
pytest --cov=plants --cov=logs --cov=users --cov-report=term-missing
```

### 2. Test Your Specific Feature

```bash
# Run only tests for a specific file
pytest plants/tests/test_views.py -v

# Run only tests matching a pattern
pytest -k "plant_creation" -v

# Run specific test class
pytest plants/tests/test_views.py::TestPlantViewSet -v

# Run specific test method
pytest plants/tests/test_views.py::TestPlantViewSet::test_create_plant_authenticated -v
```

### 3. Continuous Verification During Development

Watch for test failures in real-time:

```bash
# Rerun tests on file changes (requires pytest-watch)
pip install pytest-watch
ptw
```

### 4. Pre-commit Verification Script

Create `.git/hooks/pre-commit` to run tests before commits:

```bash
#!/bin/bash
echo "Running tests before commit..."
pytest -m "not slow" --tb=short
if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi
```

Make executable:

```bash
chmod +x .git/hooks/pre-commit
```

---

## Test Structure

### Fixture Hierarchy

``` markdown
conftest.py (root fixtures)
├── api_client (base unauthenticated client)
├── api_client_with_user (authenticated)
├── test_user (User object)
├── test_plant (Plant owned by test_user)
└── valid_plant_data (dict for creating plants)

tests/
├── test_auth_flow.py (uses fixtures)
├── test_e2e_workflows.py
└── test_gradio_ui.py

plants/tests/
├── test_models.py (unit)
└── test_views.py (integration)
```

### Model Test Relationships

``` markdown
User
├── creates Plant (owner FK)
│   └── creates Log (plant FK, owner FK)
└── creates Log (owner FK)

Test Coverage:
- User.objects.create() → test_models.py::TestUserModel
- Plant CRUD → test_views.py::TestPlantViewSet
- Log CRUD → test_views.py::TestLogViewSet
- Permissions → test_auth_flow.py::TestMultiUserIsolation
```

---

## Running Specific Tests

### By Feature

```bash
# Authentication tests
pytest -m auth -v

# Plant management tests
pytest -m plant -v

# Log management tests
pytest -m log -v

# User account tests
pytest -m user -v
```

### By Type

```bash
# Only unit tests
pytest plants/tests/test_models.py -v

# Only integration tests
pytest -m integration -v

# Only end-to-end tests
pytest -m e2e -v
```

### By Pattern

```bash
# Tests matching "create"
pytest -k "create" -v

# Tests matching "plant" but not "delete"
pytest -k "plant and not delete" -v

# Tests in specific class
pytest plants/tests/test_views.py::TestPlantViewSet::test_create_plant_authenticated -v
```

### By Performance

```bash
# Quick tests only (skip slow)
pytest -m "not slow" --tb=short

# Only slow tests
pytest -m slow -v
```

---

## Debugging Tests

### 1. Verbose Output

See detailed assertion failures:

```bash
pytest -vv -s
```

### 2. Print Debug Output

Add `print()` statements in test:

```python
def test_something(self, api_client_with_user, test_plant):
    response = api_client_with_user.get(f'/api/plants/{test_plant.id}/')
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    assert response.status_code == 200
```

Run with:

```bash
pytest -s test_file.py::test_name
```

### 3. Stop on First Failure

```bash
pytest -x
```

### 4. Drop to Python Debugger on Failure

Add to test:

```python
import pdb
pdb.set_trace()
```

Or use pytest:

```bash
pytest --pdb
```

### 5. Check Database State

```python
def test_something(self, api_client_with_user, test_plant):
    from plants.models import Plant
    
    print(f"Plants before: {Plant.objects.count()}")
    response = api_client_with_user.post('/api/plants/', {...})
    print(f"Plants after: {Plant.objects.count()}")
    assert Plant.objects.count() == 2
```

### 6. View SQL Queries

```python
from django.test.utils import CaptureQueriesContext
from django.db import connection

def test_query_efficiency(self, api_client_with_user):
    with CaptureQueriesContext(connection) as ctx:
        response = api_client_with_user.get('/api/plants/')
    
    print(f"Queries executed: {len(ctx)}")
    for query in ctx:
        print(query['sql'])
```

---

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### Local Pre-commit Hook

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest -m "not slow"
        language: system
        types: [python]
        pass_filenames: false
        stages: [commit]
EOF

# Install hooks
pre-commit install
```

---

## Common Issues & Solutions

### Issue: `django.core.exceptions.ImproperlyConfigured`

**Cause:** Django settings not loaded

**Solution:**

```python
# In test file or conftest
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
```

### Issue: `psycopg2.OperationalError`

**Cause:** Database connection failed

**Solution:** pytest-django uses test database automatically. Make sure `INSTALLED_APPS` includes `'django_extensions'` if using custom commands.

### Issue: Tests pass locally but fail in CI

**Cause:** Timing issues or environment differences

**Solution:**

- Use fixtures instead of hardcoded values
- Avoid `time.sleep()` - use Django's `TestCase` or factory defaults
- Set `TIME_ZONE = 'UTC'` in test settings

### Issue: `fixture 'api_client_with_user' not found`

**Cause:** conftest.py not in right location

**Solution:** Ensure `tests/conftest.py` exists at project root level or in app directories.

---

## Performance Tips

### 1. Use Django Test Transactions

Tests automatically use transactions. Add `@pytest.mark.django_db`:

```python
@pytest.mark.django_db
def test_database_changes(self):
    User.objects.create(username='test')
```

### 2. Factory Boy for Bulk Creation

```python
# Slow
for i in range(100):
    user = UserFactory()

# Fast with batch_create
users = [UserFactory.build() for _ in range(100)]
User.objects.bulk_create(users)
```

### 3. Reuse Fixtures

```python
# Bad: creates new user for each test
def test_1(self):
    user = UserFactory()

def test_2(self):
    user = UserFactory()

# Good: share fixture
def test_1(self, test_user):
    assert test_user.username == 'testuser'

def test_2(self, test_user):
    assert test_user.email == 'testuser@example.com'
```

---

## Summary

**Testing workflow:**

1. **Write code** in models, views, or serializers
2. **Run tests** to verify: `pytest -m "not slow" --tb=short`
3. **Check coverage**: `pytest --cov-report=term-missing`
4. **Add new tests** if coverage < 80%
5. **Commit** with passing tests

**Key commands:**

```bash
pytest                              # Run all tests
pytest -v                          # Verbose output
pytest -m unit                     # Run by marker
pytest --cov                       # With coverage
pytest -k "test_name"              # By pattern
pytest tests/test_file.py::TestClass::test_method -vv  # Specific test
```

---

## Need Help?

- Check existing tests for examples: `plants/tests/test_views.py`
- Review fixtures: `tests/conftest.py`
- Read test docstrings for expected behavior
- Run with `-v` and `-s` flags for debugging

Happy testing! 🌿
