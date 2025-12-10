# GitHub Actions Status Badges

Add these to your main README.md to show CI/CD status:

## Markdown Code

```markdown
## Status Badges

![Tests](https://github.com/NathanielWilcox/plant_journal/workflows/Test%20Suite/badge.svg)
![Code Quality](https://github.com/NathanielWilcox/plant_journal/workflows/Code%20Quality/badge.svg)
![Security](https://github.com/NathanielWilcox/plant_journal/workflows/Security%20Checks/badge.svg)
```

## How to customize

Replace `NathanielWilcox` with your GitHub username
Replace `plant_journal` with your repo name

## Where to place

Add to top of README.md after the title, like:

```markdown
# Plant Journal

![Tests](https://github.com/NathanielWilcox/plant_journal/workflows/Test%20Suite/badge.svg)
![Code Quality](https://github.com/NathanielWilcox/plant_journal/workflows/Code%20Quality/badge.svg)

Your project description here...
```

## Badge meaning

- **Green** = Latest run passed ✅
- **Red** = Latest run failed ❌
- **Gray** = No runs yet (newly added)

When users see green badges, they know:
- ✅ Tests are passing
- ✅ Code quality is good
- ✅ No known vulnerabilities

## Optional: Codecov Badge

```markdown
[![codecov](https://codecov.io/gh/NathanielWilcox/plant_journal/branch/main/graph/badge.svg)](https://codecov.io/gh/NathanielWilcox/plant_journal)
```

This shows test coverage percentage!
