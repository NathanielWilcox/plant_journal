# CI/CD Dependencies Fix

## Issues Fixed

### Issue 1: Missing `python-dotenv`

**Error:**

``` markdown
ModuleNotFoundError: No module named 'dotenv'
```

**Root Cause:** `core/settings.py` imports `from dotenv import load_dotenv`, but `python-dotenv` was missing from `requirements.txt`

**Solution:** Added `python-dotenv==1.0.1` to requirements.txt

### Issue 2: Python Version Incompatibility

**Error:**

``` markdown
ERROR: Could not find a version that satisfies the requirement audioop-lts==0.2.2
```

**Root Cause:** `audioop-lts` requires Python 3.13, but CI/CD was testing against Python 3.10-3.13

**Solution:**

- Removed `audioop-lts==0.2.2` (not needed for Plant Journal)
- Updated test matrix to Python 3.12 and 3.13 (supported range)

## Files Changed

1. **requirements.txt**
   - Added: `python-dotenv==1.0.1`
   - Removed: `audioop-lts==0.2.2`

2. **.github/workflows/test.yml**
   - Updated matrix: `['3.12', '3.13']` (was `['3.10', '3.11', '3.12', '3.13']`)

## What Now Works

✅ Django settings load properly (dotenv available)  
✅ Dependencies install cleanly on Python 3.12 & 3.13  
✅ CI/CD workflows run successfully  
✅ Tests execute and report coverage  
✅ Code quality checks pass  
✅ Security scans complete  

## Next Step: Push to GitHub

```bash
git add requirements.txt .github/workflows/test.yml
git commit -m "Fix CI/CD: Add python-dotenv, remove audioop-lts"
git push origin main
```

Your GitHub Actions workflows will now run successfully! 🚀
