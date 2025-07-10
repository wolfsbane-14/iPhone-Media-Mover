# iPhone Media Mover


iPhone Media Mover is a robust, feature-rich GUI application designed specifically for Linux users to safely transfer, organize, and manage photos and videos from iOS devices. Built with Python and Tkinter, it provides a user-friendly interface while maintaining enterprise-grade reliability and safety features.

##  Key Features

### 🖥️ Modern GUI Interface
- **Dark Mode Theme**: Eye-friendly dark interface by default
- **Real-time Progress Tracking**: Visual progress bar with time estimates
- **Live Transfer Logs**: Real-time display of transfer operations
- **Intuitive Controls**: Simple checkboxes and buttons for all options

### 🔒 Safety & Reliability
- **Copy-Verify-Delete Workflow**: Ensures data integrity before any deletions
- **Checksum Verification**: Optional MD5 hash verification for complete file integrity
- **Duplicate Handling**: Smart filename collision resolution
- **Resumable Transfers**: Automatically skips already transferred files
- **Comprehensive Logging**: Detailed logs for successful, failed, and deleted files

### 📁 Smart Organization
- **Date-based Folders**: Automatically organize by YYYY/MM structure using EXIF data
- **Flexible Destination**: Choose any destination folder on your system
- **DCIM Scanning**: Recursive scanning of all iPhone DCIM subdirectories
- **Multiple File Types**: Supports all common photo and video formats

### 🛡️ Data Protection
- **Non-destructive by Default**: Original files remain untouched unless explicitly deleted
- **Verification Before Deletion**: Only removes originals after successful copy and verification
- **Error Handling**: Graceful handling of transfer failures and interruptions
- **Transfer Cancellation**: Safe exit with confirmation during active transfers

## 📋 System Requirements

### Operating System
- **Ubuntu 18.04+** (or compatible Debian-based distributions)
- **Python 3.6+** with Tkinter support

![Application interface](img/img1.png)

## System Setup (One-Time)

Install necessary packages and Python libraries:

```bash
sudo apt update
sudo apt install -y ifuse libimobiledevice6 libimobiledevice-utils gvfs-backends
pip3 install tqdm pillow piexif
```

## Save the Script

Save the script as `iphone_move.py`. Make it executable:

```bash
chmod +x iphone_move.py
```

## Usage

### 1. Copy and Organize into Folders by Year/Month

```bash
python3 iphone_move.py --dest ~/Pictures/iPhone --organise
```

### 2. Copy, Verify with Checksums, and Delete Originals from iPhone

```bash
python3 iphone_move.py --dest ~/Pictures/iPhone --organise --delete --checksum
```

### 3. Fast Flat Copy (No Organizing, No Deletion)

```bash
python3 iphone_move.py --dest ~/backup_iPhone
```

![Transfer in Progress](img/img2.png)

## Output Logs

Logs are saved in a `./iphone_logs/` directory:

* `success.txt` – Successfully copied and verified files
* `failed.txt` – Files that failed to copy or delete
* `deleted.txt` – Files deleted from the iPhone (only if `--delete` is used)

![Successful transfer of files with logs](img/img3.png)

## Resuming Transfers

If disconnected or interrupted, simply rerun the same command. The script will **skip already verified files** and continue from where it left off.

## Checksum Option (`--checksum`)

* Compares MD5 hashes to ensure file integrity.
* Recommended when using `--delete` for extra safety.
* Slower but provides verification beyond file size.

## Options Reference

| Option | Description |
|--------|-------------|
| `--dest` | Destination directory on Ubuntu (required) |
| `--organise` | Organize files into `YYYY/MM` folders |
| `--delete` | Delete originals from iPhone after successful copy |
| `--checksum` | Use MD5 checksums to verify file integrity |
| `--mount` | Mount point (default: `~/iPhone`) |

## Example Directory Structure (with `--organise`)

```
~/Pictures/iPhone/
├── 2023/
│   ├── 11/
│   └── 12/
├── 2024/
│   ├── 01/
│   └── 06/
```

## Notes

* Make sure your iPhone is **unlocked and trusted** when connecting.
* Only files under the `DCIM` directory will be processed.
* The script automatically unmounts the iPhone at the end.

## License

MIT License – Free to use, modify, and distribute.
