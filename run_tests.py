#!/usr/bin/env python
"""Simple test runner to verify test suite setup"""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
    capture_output=True,
    text=True,
    cwd='.'
)

print("Test Collection Summary:")
print("-" * 60)
lines = result.stdout.split('\n')
for line in lines[-5:]:
    if line.strip():
        print(line)

print("\n" + "=" * 60)
print("Running quick test (non-e2e, non-slow)...")
print("=" * 60 + "\n")

result2 = subprocess.run(
    [sys.executable, '-m', 'pytest', '-m', 'not slow', '-q', '--tb=line'],
    capture_output=True,
    text=True,
    cwd='.'
)

print(result2.stdout)
if result2.stderr:
    print("STDERR:", result2.stderr)

sys.exit(result2.returncode)
