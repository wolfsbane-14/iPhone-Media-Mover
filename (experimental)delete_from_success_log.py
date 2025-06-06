#!/usr/bin/env python3
import subprocess
from pathlib import Path
import os

# --- Settings ---
MOUNT_POINT = Path.home() / "iPhone"
LOG_DIR = Path("iphone_logs")
SUCCESS_LOG = LOG_DIR / "success.txt"
DELETED_LOG = LOG_DIR / "deleted.txt"
FAILED_LOG = LOG_DIR / "delete_failed.txt"

# --- Ensure mount point exists ---
MOUNT_POINT.mkdir(parents=True, exist_ok=True)

def is_iphone_mounted():
    try:
        output = subprocess.check_output(["mount"]).decode()
        return str(MOUNT_POINT) in output
    except subprocess.CalledProcessError:
        return False

def mount_iphone():
    print("📱 Mounting iPhone...")
    try:
        subprocess.run(["ifuse", str(MOUNT_POINT)], check=True)
        print(f"✅ iPhone mounted at {MOUNT_POINT}")
    except subprocess.CalledProcessError:
        print("❌ Failed to mount iPhone. Make sure it's unlocked and trusted.")
        exit(1)

def delete_files_from_success_log():
    count_deleted = 0
    count_failed = 0

    with SUCCESS_LOG.open("r") as infile, \
         DELETED_LOG.open("a") as deleted_log, \
         FAILED_LOG.open("a") as failed_log:

        for line in infile:
            path = Path(line.strip())
            if not path.exists():
                continue
            try:
                path.unlink()
                deleted_log.write(f"{path}\n")
                count_deleted += 1
            except Exception as e:
                failed_log.write(f"{path}  # FAILED: {e}\n")
                count_failed += 1

    print(f"✅ Deleted: {count_deleted}")
    print(f"⚠️  Failed: {count_failed} (see {FAILED_LOG.name})")

# --- Main execution ---
if not is_iphone_mounted():
    mount_iphone()

if not SUCCESS_LOG.exists():
    print(f"❌ No success log found at {SUCCESS_LOG}")
    exit(1)

delete_files_from_success_log()

