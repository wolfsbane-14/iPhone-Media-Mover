#!/usr/bin/env python3
"""
iphone_move.py  –  Move photos/videos off an iPhone  (copy ✚ verify ✚ optional delete)

USAGE EXAMPLES
--------------
# 1) Copy + organise, but keep originals on phone
python3 iphone_move.py --dest ~/Pictures/Mom_iPhone --organise

# 2) Copy + verify with checksums, then delete originals after success
python3 iphone_move.py --dest ~/Pictures/Mom_iPhone --organise --delete --checksum
"""
import argparse, hashlib, os, shutil, subprocess, sys, time
from datetime import datetime
from pathlib import Path
from shutil import copy2
from typing import Optional

from tqdm import tqdm

# -------- EXIF helpers ------------------------------------------------------
def exif_datetime(src: Path) -> datetime:
    """Return datetime the photo/video was taken (EXIF), else mtime."""
    try:
        from PIL import Image
        import piexif
        img = Image.open(src)
        exif_bytes = img.info.get("exif")
        if exif_bytes:
            exif = piexif.load(exif_bytes)
            raw = exif["0th"].get(piexif.ImageIFD.DateTime)
            if raw:
                return datetime.strptime(raw.decode(), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return datetime.fromtimestamp(src.stat().st_mtime)

# -------- mount helpers -----------------------------------------------------
def mount_iphone(mount_point: Path):
    mount_point.mkdir(parents=True, exist_ok=True)
    print("📱  Unlock iPhone and tap **Trust** …")
    res = subprocess.run(["ifuse", str(mount_point)])
    if res.returncode != 0 or not (mount_point / "DCIM").exists():
        sys.exit("❌  Mount failed (no DCIM found).")

def unmount_iphone(mount_point: Path):
    subprocess.run(["fusermount", "-u", str(mount_point)], stdout=subprocess.DEVNULL)
    print("📴  iPhone unmounted.")

# -------- verification helpers ----------------------------------------------
def md5sum(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk_data in iter(lambda: f.read(chunk), b""):
            h.update(chunk_data)
    return h.hexdigest()

def equal_file(src: Path, dest: Path, use_checksum: bool) -> bool:
    if not dest.exists():
        return False
    if dest.stat().st_size != src.stat().st_size:
        return False
    if use_checksum:
        return md5sum(src) == md5sum(dest)
    return True

# -------- core copy / move ---------------------------------------------------
def copy_verify(src: Path, dest: Path, checksum: bool, retries: int = 3) -> bool:
    for attempt in range(1, retries + 1):
        try:
            copy2(src, dest)
            # Verify size (and checksum if requested)
            if equal_file(src, dest, checksum):
                return True
            raise IOError("Verification failed")
        except Exception as e:
            if attempt == retries:
                return False
            print(f"⚠️  {src.name}: retry {attempt}/{retries} ({e})")
            time.sleep(1)
    return False  # should never reach

# -------- main routine ------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Move iPhone photos/videos to Ubuntu safely")
    ap.add_argument("--dest", required=True, type=Path, help="Destination folder on PC")
    ap.add_argument("--organise", action="store_true", help="Organise into YYYY/MM")
    ap.add_argument("--delete", action="store_true", help="Delete originals after successful copy")
    ap.add_argument("--checksum", action="store_true", help="Verify copies with MD5 (slower)")
    ap.add_argument("--mount", default=Path.home() / "iPhone", type=Path, help="Mount point (default ~/iPhone)")
    args = ap.parse_args()

    # --- prepare logs
    logdir = Path.cwd() / "iphone_logs"
    logdir.mkdir(exist_ok=True)
    success_log = (logdir / "success.txt").open("a")
    fail_log    = (logdir / "failed.txt").open("a")
    delete_log  = (logdir / "deleted.txt").open("a") if args.delete else None

    try:
        mount_iphone(args.mount)
        dcim = args.mount / "DCIM"
        files = [f for f in dcim.rglob("*") if f.is_file()]
        print(f"🔍  Found {len(files)} media files")

        for src in tqdm(files, unit="file", desc="Processing"):
            # ---------- decide destination path
            if args.organise:
                dt = exif_datetime(src)
                dest_dir = args.dest / f"{dt.year}/{dt.month:02}"
            else:
                dest_dir = args.dest
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / src.name

            # ---------- skip if already ok
            if equal_file(src, dest, args.checksum):
                continue

            # ---------- copy + verify
            ok = copy_verify(src, dest, args.checksum)
            if not ok:
                fail_log.write(f"{src}\n")
                continue
            success_log.write(f"{src}\n")
            success_log.flush()

            # ---------- optional delete
            if args.delete:
                try:
                    src.unlink()
                    delete_log.write(f"{src}\n")
                    delete_log.flush()
                except Exception as e:
                    print(f"⚠️  Couldn't delete {src}: {e}")
                    fail_log.write(f"{src}  # DELETE_FAIL {e}\n")

        print("\n✅  Finished.  Logs saved in ./iphone_logs/")
        if args.delete:
            print("   → Originals removed where copy verified.")

    finally:
        success_log.close(); fail_log.close()
        if delete_log: delete_log.close()
        unmount_iphone(args.mount)

if __name__ == "__main__":
    main()
