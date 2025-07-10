import os, sys, shutil, hashlib, time, subprocess
from pathlib import Path
from datetime import datetime
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from PIL import Image
import piexif
import platform

class IPhoneMoverApp:
    def __init__(self, root):
        self.root = root
        root.title("📱 iPhone Media Mover")
        root.geometry("800x700")
        
        # Initialize destination path
        self.dest_path = None
        
        # Define Color Themes for Light and Dark Mode
        self.themes = {
            "dark": {
                "bg": "#2e2e2e",          # Dark background
                "fg": "white",            # Light text
                "button": "#4caf50",      # Green buttons
                "highlight": "#2196f3",   # Blue buttons
                "text_bg": "#121212",     # Dark text area
                "text_fg": "#e0e0e0",     # Light text area
                "selectcolor": "#2e2e2e", # Dark checkbox
                "progress_bg": "#333",    # Progress bar background
                "progress_fg": "#4caf50", # Progress bar foreground
            },
            "light": {
                "bg": "#f5f5f5",          # Light background
                "fg": "#1c1c1c",          # Dark text
                "button": "#4caf50",      # Green buttons
                "highlight": "#2196f3",   # Blue buttons
                "text_bg": "#ffffff",     # Light text area
                "text_fg": "#000000",     # Dark text area
                "selectcolor": "#f5f5f5", # Light checkbox
                "progress_bg": "#ccc",    # Progress bar background
                "progress_fg": "#4caf50", # Progress bar foreground
            }
        }

        self.theme = "dark"  # Set the default theme to dark
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._apply_theme()

        self._build_ui()

    def _apply_theme(self):
        """Apply the current theme to all elements."""
        t = self.themes[self.theme]
        self.root.configure(bg=t["bg"])
        self.style.configure("TProgressbar", thickness=20, troughcolor=t["progress_bg"], background=t["progress_fg"])
        
    def toggle_theme(self):
        """Toggle between light and dark modes."""
        self.theme = "light" if self.theme == "dark" else "dark"
        self._apply_theme()
        self._build_ui()  # Rebuild the UI with the new theme

    def _build_ui(self):
        """Rebuild UI elements according to the selected theme."""
        for widget in self.root.winfo_children():
            widget.destroy()

        t = self.themes[self.theme]

        # Title Label
        title = Label(self.root, text="📱 iPhone Media Mover", font=("Helvetica", 18, "bold"), bg=t["bg"], fg=t["fg"])
        title.pack(pady=10)

        # Folder selection
        Label(self.root, text="Choose Destination Folder", bg=t["bg"], fg=t["fg"]).pack()
        Button(self.root, text="Browse", command=self.pick_dest, bg=t["button"], fg="white").pack(pady=5)

        # Option Checkboxes
        self.organise = IntVar()
        self.delete = IntVar()  # Fixed: This was commented out but referenced later
        self.checksum = IntVar()
        self.open_logs = IntVar()

        Checkbutton(self.root, text="Organise into YYYY/MM", variable=self.organise, bg=t["bg"], fg=t["fg"], selectcolor=t["selectcolor"]).pack()
        Checkbutton(self.root, text="Delete from iPhone after copy (unstable)", variable=self.delete, bg=t["bg"], fg=t["fg"], selectcolor=t["selectcolor"]).pack()
        Checkbutton(self.root, text="Verify with checksum (slower)", variable=self.checksum, bg=t["bg"], fg=t["fg"], selectcolor=t["selectcolor"]).pack()
        Checkbutton(self.root, text="Open logs folder after transfer", variable=self.open_logs, bg=t["bg"], fg=t["fg"], selectcolor=t["selectcolor"]).pack()

        Button(self.root, text="Start Transfer", command=self.run_threaded, bg=t["highlight"], fg="white", font=("Helvetica", 12)).pack(pady=10)

        # Log area
        self.log_area = Text(self.root, wrap="word", bg=t["text_bg"], fg=t["text_fg"], height=14)
        self.log_area.pack(fill=BOTH, expand=True, padx=10)

        scrollbar = Scrollbar(self.log_area)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log_area.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_area.yview)

        # Loader section
        self.loader_frame = Frame(self.root, bg=t["bg"])
        self.loader_frame.pack(pady=10)

        self.progress = ttk.Progressbar(self.loader_frame, orient='horizontal', length=700, mode='determinate')
        self.progress.pack()

        self.counter_label = Label(self.loader_frame, text="Progress: 0 / 0", bg=t["bg"], fg=t["fg"])
        self.counter_label.pack()

        self.time_label = Label(self.loader_frame, text="⏱ Elapsed: 00:00:00   |   ⌛ Remaining: ~--:--:--", bg=t["bg"], fg=t["fg"])
        self.time_label.pack()

        self.start_time = None
        self.is_transferring = False
        self.success_list = []
        self.fail_list = []
        
        # Toggle Theme Button (uncommented if you want it)
        # Button(self.root, text="Toggle Theme", command=self.toggle_theme, bg=t["highlight"], fg="white", font=("Helvetica", 10)).pack(pady=10)

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def pick_dest(self):
        selected_path = filedialog.askdirectory()
        if selected_path:  # Only set if user didn't cancel
            self.dest_path = Path(selected_path)
            self.log(f"📂 Destination set to: {self.dest_path}")

    def log(self, message):
        self.log_area.insert(END, message + "\n")
        self.log_area.see(END)
        self.root.update_idletasks()  # Force GUI update

    def run_threaded(self):
        Thread(target=self.main, daemon=True).start()

    def update_loader(self, current, total):
        if self.start_time:
            elapsed = time.time() - self.start_time
            avg_time = elapsed / current if current > 0 else 0
            remaining = avg_time * (total - current) if current < total else 0
            elapsed_fmt = time.strftime("%H:%M:%S", time.gmtime(elapsed))
            remaining_fmt = time.strftime("%H:%M:%S", time.gmtime(remaining))
            self.counter_label.config(text=f"Progress: {current} / {total}")
            self.time_label.config(text=f"⏱ Elapsed: {elapsed_fmt}   |   ⌛ Remaining: ~{remaining_fmt}")
        
        self.progress["value"] = current
        self.root.update_idletasks()

    def set_transferring(self, status: bool):
        self.is_transferring = status

    def on_close(self):
        if self.is_transferring:
            if messagebox.askyesno("Confirm Exit", "⚠️ Transfer in progress.\nAre you sure you want to exit and cancel the operation?"):
                self.root.destroy()
        else:
            self.root.destroy()

    def main(self):
        if not self.dest_path:
            self.log("❌ Please select a destination folder first.")
            return

        mount_point = Path.home() / "iPhone"
        try:
            self.mount_iphone(mount_point)
        except Exception as e:
            self.log(f"❌ Mount failed: {e}")
            return

        try:
            dcim = mount_point / "DCIM"
            
            # Debug: Check if DCIM exists and analyze structure
            if not dcim.exists():
                self.log(f"❌ DCIM folder not found at {dcim}")
                return
            
            self.log(f"📂 DCIM folder found: {dcim}")
            
            # List all subdirectories in DCIM
            subdirs = [d for d in dcim.iterdir() if d.is_dir()]
            self.log(f"📁 Found {len(subdirs)} subdirectories in DCIM:")
            for subdir in subdirs:
                try:
                    subdir_files = [f for f in subdir.iterdir() if f.is_file()]
                    self.log(f"  📁 {subdir.name}: {len(subdir_files)} files")
                except PermissionError:
                    self.log(f"  📁 {subdir.name}: Permission denied")
                except Exception as e:
                    self.log(f"  📁 {subdir.name}: Error - {e}")
            
            # Get all files recursively
            self.log("🔍 Scanning for files recursively...")
            files = []
            for item in dcim.rglob("*"):
                if item.is_file():
                    files.append(item)
            
            total = len(files)
            
            # Debug: Show file extensions found
            extensions = {}
            for f in files:
                ext = f.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1
            
            self.log(f"📊 File types found: {extensions}")
            self.log(f"🔍 Total files found: {total}")
            
            # Sample some file paths for debugging
            if files:
                self.log("📄 Sample file paths:")
                for i, f in enumerate(files[:5]):  # Show first 5
                    try:
                        relative_path = f.relative_to(dcim)
                        self.log(f"  📄 {i+1}: {relative_path}")
                    except ValueError:
                        self.log(f"  📄 {i+1}: {f}")
                
                if total > 5:
                    self.log(f"  ... and {total - 5} more files")
            
            if total == 0:
                self.log("📭 No files found on device.")
                return

            self.log(f"🚀 Starting transfer of {total} media files")
            self.progress["value"] = 0
            self.progress["maximum"] = total
            self.start_time = time.time()
            self.set_transferring(True)

            processed = 0
            for src in files:
                try:
                    dt = self.get_date(src)
                    if self.organise.get():
                        dest_dir = self.dest_path / f"{dt.year}/{dt.month:02d}"
                    else:
                        dest_dir = self.dest_path
                    
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest = dest_dir / src.name

                    # Handle duplicate filenames
                    counter = 1
                    original_dest = dest
                    while dest.exists() and not self.same_file(src, dest):
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest = dest_dir / f"{stem}_{counter}{suffix}"
                        counter += 1

                    if self.same_file(src, dest):
                        self.success_list.append(str(src))
                        self.log(f"⏭️ Skipped (already exists): {src.name}")
                        processed += 1
                        self.update_loader(processed, total)
                        continue

                    if not self.copy_and_verify(src, dest):
                        self.fail_list.append(str(src))
                        self.log(f"❌ Failed to copy {src.name}")
                        processed += 1
                        self.update_loader(processed, total)
                        continue

                    self.success_list.append(str(src))
                    self.log(f"✅ Copied: {src.name}")

                    if self.delete.get():
                        try:
                            src.unlink()
                            self.log(f"🗑️ Deleted: {src.name}")
                        except Exception as e:
                            self.log(f"⚠️ Could not delete {src.name}: {e}")

                    processed += 1
                    self.update_loader(processed, total)
                    
                except Exception as e:
                    self.fail_list.append(str(src))
                    self.log(f"❌ Error processing {src.name}: {e}")
                    processed += 1
                    self.update_loader(processed, total)

            self.log("✅ All files processed.")
            self.write_logs()
            self.notify_user()

        except Exception as e:
            self.log(f"❌ Unexpected error: {e}")
            import traceback
            self.log(f"📋 Debug info: {traceback.format_exc()}")
            self.write_logs()
            self.notify_user(error=True)

        finally:
            self.set_transferring(False)
            self.unmount_iphone(mount_point)
            self.log("📴 Unmounted iPhone.")

    def write_logs(self):
        try:
            log_dir = Path.home() / "iphone_logs"
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with open(log_dir / f"success_{timestamp}.txt", "w") as sf:
                for line in self.success_list:
                    sf.write(line + "\n")
            
            with open(log_dir / f"failed_{timestamp}.txt", "w") as ff:
                for line in self.fail_list:
                    ff.write(line + "\n")
            
            self.log(f"📁 Logs saved in: {log_dir}")
            
            if self.open_logs.get():
                if platform.system() == "Linux":
                    subprocess.run(["xdg-open", str(log_dir)])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(log_dir)])
                elif platform.system() == "Windows":
                    subprocess.run(["explorer", str(log_dir)])
                    
        except Exception as e:
            self.log(f"⚠️ Could not write logs: {e}")

    def notify_user(self, error=False):
        success_count = len(self.success_list)
        fail_count = len(self.fail_list)
        
        if error:
            messagebox.showerror("Transfer Interrupted", 
                               f"⚠️ Transfer aborted.\n\n✅ Successful: {success_count} file(s)\n❌ Failed: {fail_count} file(s)\n\nLogs saved in ~/iphone_logs/")
        else:
            if fail_count == 0:
                messagebox.showinfo("Transfer Complete", 
                                  f"🎉 All files transferred successfully!\n\n✅ Successful: {success_count} file(s)\n\nLogs saved in ~/iphone_logs/")
            else:
                messagebox.showwarning("Transfer Finished with Issues",
                                     f"⚠️ Transfer completed with some issues.\n\n✅ Successful: {success_count} file(s)\n❌ Failed: {fail_count} file(s)\n\nLogs saved in ~/iphone_logs/")

    def mount_iphone(self, mount_point):
        mount_point.mkdir(parents=True, exist_ok=True)
        self.log("📱 Unlock iPhone and tap Trust if prompted…")
        
        # Check if already mounted
        if (mount_point / "DCIM").exists():
            self.log("📱 iPhone already mounted")
            return
        
        result = subprocess.run(["ifuse", str(mount_point)], capture_output=True, text=True)
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            raise RuntimeError(f"ifuse failed: {error_msg}")
        
        # Wait a moment for mount to complete
        time.sleep(2)
        
        if not (mount_point / "DCIM").exists():
            raise RuntimeError("Mount failed – DCIM folder not found. Make sure iPhone is unlocked and trusted.")
        
        self.log("✅ iPhone mounted successfully")

    def unmount_iphone(self, mount_point):
        try:
            result = subprocess.run(["fusermount", "-u", str(mount_point)], capture_output=True, text=True)
            if result.returncode != 0:
                # Try alternative unmount method
                subprocess.run(["umount", str(mount_point)], capture_output=True)
            self.log("✅ iPhone unmounted successfully")
        except Exception as e:
            self.log(f"⚠️ Unmount warning: {e}")

    def get_date(self, src: Path):
        """Get the date from EXIF data or file modification time"""
        try:
            # Try to get EXIF data first
            with Image.open(src) as img:
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                    if piexif.ImageIFD.DateTime in exif_dict["0th"]:
                        date_str = exif_dict["0th"][piexif.ImageIFD.DateTime].decode()
                        return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass  # Fall back to file modification time
        
        # Use file modification time as fallback
        return datetime.fromtimestamp(src.stat().st_mtime)

    def md5(self, path: Path, chunk_size=1024*1024):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_md5.update(chunk)
        except Exception:
            return None
        return hash_md5.hexdigest()

    def same_file(self, src: Path, dest: Path):
        """Check if two files are the same"""
        if not dest.exists():
            return False
        
        # Quick size check first
        if dest.stat().st_size != src.stat().st_size:
            return False
        
        # If checksum verification is enabled, compare MD5 hashes
        if self.checksum.get():
            src_hash = self.md5(src)
            dest_hash = self.md5(dest)
            if src_hash is None or dest_hash is None:
                return False
            return src_hash == dest_hash
        
        # If sizes match and no checksum verification, consider them the same
        return True

    def copy_and_verify(self, src: Path, dest: Path, max_retries=3):
        """Copy file with retry logic and verification"""
        for attempt in range(1, max_retries + 1):
            try:
                # Copy the file
                shutil.copy2(src, dest)
                
                # Verify the copy
                if self.same_file(src, dest):
                    return True
                else:
                    self.log(f"⚠️ {src.name} verification failed on attempt {attempt}")
                    
            except Exception as e:
                self.log(f"⚠️ {src.name} copy failed on attempt {attempt}: {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < max_retries:
                time.sleep(1)
        
        return False

def main():
    root = Tk()
    app = IPhoneMoverApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()
    

