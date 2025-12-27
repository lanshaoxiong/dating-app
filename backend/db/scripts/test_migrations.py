"""Test Alembic migrations up and down

This script tests that migrations can be applied and rolled back successfully.
"""

import asyncio
import sys
import subprocess
from pathlib import Path

# Change to backend directory (parent of parent of this file)
backend_dir = Path(__file__).parent.parent.parent
import os
os.chdir(backend_dir)


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ {description} succeeded")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def test_migrations():
    """Test migration up and down"""
    
    print("=" * 60)
    print("Testing Alembic Migrations")
    print("=" * 60)
    
    # Check current revision
    if not run_command(
        ["alembic", "-c", "db/migrations/alembic.ini", "current"],
        "Checking current revision"
    ):
        return False
    
    # Upgrade to head
    if not run_command(
        ["alembic", "-c", "db/migrations/alembic.ini", "upgrade", "head"],
        "Applying migrations (upgrade head)"
    ):
        return False
    
    # Check current revision after upgrade
    if not run_command(
        ["alembic", "-c", "db/migrations/alembic.ini", "current"],
        "Verifying current revision"
    ):
        return False
    
    # Downgrade one step
    if not run_command(
        ["alembic", "-c", "db/migrations/alembic.ini", "downgrade", "-1"],
        "Rolling back one migration (downgrade -1)"
    ):
        return False
    
    # Upgrade back to head
    if not run_command(
        ["alembic", "-c", "db/migrations/alembic.ini", "upgrade", "head"],
        "Re-applying migrations (upgrade head)"
    ):
        return False
    
    # Show migration history
    if not run_command(
        ["alembic", "-c", "db/migrations/alembic.ini", "history"],
        "Showing migration history"
    ):
        return False
    
    print("\n" + "=" * 60)
    print("✅ All migration tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_migrations()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
