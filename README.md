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

## 🚀 Installation

### Quick Setup
1. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y ifuse libimobiledevice6 libimobiledevice-utils gvfs-backends python3-tk
   ```

2. **Install Python dependencies**:
   ```bash
   pip3 install Pillow piexif
   ```

3. **Download and run**:
   ```bash
   # Download the application
   wget https://github.com/your-repo/iphone-media-mover/raw/main/iphone_move.py
   
   # Make it executable
   chmod +x iphone_move.py
   
   # Run the application
   python3 iphone_move.py
   ```

### Alternative Installation
You can also save the script manually and run it:
```bash
# Save as iphone_move.py
python3 iphone_move.py
```

## 💻 Usage Guide

### Getting Started
1. **Connect your iPhone** via USB cable
2. **Unlock your iPhone** and tap "Trust" when prompted
3. **Launch the application**:
   ```bash
   python3 iphone_move.py
   ```


![Transfer in Progress](img/img2.png)

### Main Controls
- **Browse Button**: Select destination folder for your media files
- **Organise into YYYY/MM**: Create date-based folder structure
- **Delete from iPhone**: Remove originals after successful transfer (marked as unstable)
- **Verify with checksum**: Enable MD5 verification (slower but more secure)
- **Open logs folder**: Automatically open log directory after transfer
- **Start Transfer**: Begin the transfer process

#### Progress Tracking
- **Visual Progress Bar**: Shows transfer completion percentage
- **File Counter**: Current file / Total files
- **Time Estimates**: Elapsed time and estimated remaining time
- **Live Log**: Real-time display of transfer operations

### Transfer Options

#### Basic Copy
- Select destination folder
- Click "Start Transfer"
- Files copied to destination maintaining original structure

#### Organized Copy
- ✅ Check "Organise into YYYY/MM"
- Files automatically sorted by date into year/month folders
- Uses EXIF data when available, falls back to file modification time

#### Verified Copy
- ✅ Check "Verify with checksum (slower)"
- Each file verified with MD5 hash after copy
- Recommended for critical transfers

#### Complete Migration
- ✅ Check "Organise into YYYY/MM"
- ✅ Check "Verify with checksum (slower)"
- ✅ Check "Delete from iPhone after copy"
- ⚠️ **Warning**: Only use delete option after testing


![Successful transfer of files with logs](img/img3.png)

## 📊 File Organization

### With Organization Enabled
```
~/Pictures/iPhone/
├── 2023/
│   ├── 11/          # November 2023 photos
│   │   ├── IMG_2847.JPG
│   │   ├── IMG_2848.AAE
│   │   └── VID_2849.MOV
│   └── 12/          # December 2023 photos
│       ├── IMG_2850.HEIC
│       └── IMG_2851.PNG
├── 2024/
│   ├── 01/          # January 2024 photos
│   ├── 06/          # June 2024 photos
│   └── 12/          # December 2024 photos
└── iphone_logs/     # Transfer logs
    ├── success_20241210_143052.txt
    ├── failed_20241210_143052.txt
    └── deleted_20241210_143052.txt
```

### Without Organization
```
~/Pictures/iPhone/
├── IMG_2847.JPG
├── IMG_2848.AAE
├── VID_2849.MOV
├── IMG_2850.HEIC
└── IMG_2851.PNG
```

## 📝 Logging System

### Log Files
All transfer operations are logged in `~/iphone_logs/` with timestamp:

- **`success_YYYYMMDD_HHMMSS.txt`**: Successfully transferred files
- **`failed_YYYYMMDD_HHMMSS.txt`**: Files that failed to transfer
- **`deleted_YYYYMMDD_HHMMSS.txt`**: Files deleted from iPhone (if applicable)

### Log Format
```
/home/user/iPhone/DCIM/100APPLE/IMG_2847.JPG
/home/user/iPhone/DCIM/100APPLE/IMG_2848.AAE
/home/user/iPhone/DCIM/101APPLE/VID_2849.MOV
```

## 🔧 Advanced Features

### Automatic File Detection
- **Recursive DCIM Scanning**: Finds all media files in iPhone's DCIM directory
- **Multiple Format Support**: JPEG, HEIC, PNG, AAE, MOV, MP4, and more
- **Smart Filtering**: Processes only actual media files

### Duplicate Handling
- **Intelligent Naming**: Automatically renames duplicates (e.g., `IMG_2847_1.JPG`)
- **Content Verification**: Checks file size and optionally MD5 hash
- **Skip Existing**: Automatically skips files that already exist and match

### Transfer Resumption
- **Automatic Resume**: Rerun the same command to continue interrupted transfers
- **Skip Verified Files**: Only processes new or failed files
- **Progress Preservation**: Maintains transfer state across sessions

## 🛡️ Safety Features

### Data Protection
- **Non-destructive Default**: Original files remain on iPhone unless explicitly deleted
- **Verification Required**: Files must be successfully copied and verified before deletion
- **Transfer Confirmation**: Dialog confirmation before allowing exit during transfers
- **Error Recovery**: Graceful handling of disconnections and errors

### Success Notifications
- **Complete Success**: All files transferred successfully
- **Partial Success**: Some files failed (details in logs)
- **Transfer Interrupted**: Operation cancelled or failed

### Post-Transfer Actions
- **Automatic Log Opening**: Optional automatic opening of log directory
- **Transfer Statistics**: Clear summary of successful and failed transfers
- **Error Details**: Specific error information for troubleshooting

## 📊 Supported File Types

### Photos
- **JPEG** (.jpg, .jpeg)
- **HEIC** (.heic) 
- **PNG** (.png)
- **AAE** (.aae) 

### Videos
- **MOV** (.mov) 
- **MP4** (.mp4)
- **M4V** (.m4v)

### Metadata
- **EXIF Date Extraction**: Uses photo metadata for accurate dating
- **Fallback Dating**: Uses file modification time when EXIF unavailable

## 🔒 Security & Privacy

### Local Processing
- **No Cloud Dependencies**: All processing done locally
- **No Data Transmission**: No data sent to external servers
- **Complete Control**: Full control over your media files

