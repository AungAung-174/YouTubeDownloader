import customtkinter as ctk
from tkinter import ttk, filedialog
import threading
import os
import re
from yt_dlp import YoutubeDL


def sanitize_filename(title):
    """Remove characters that are invalid in file names"""
    return re.sub(r'[\\/*?:"<>|]', "", title)

def download_video():
    """Download YouTube video with progress tracking"""
    url = entry_url.get().strip()
    resolution = resolution_var.get()
    save_dir = save_dir_var.get()

    if not url:
        status_label.configure(text="Please enter a URL", fg_color="red")
        return
    if not save_dir:
        status_label.configure(text="Please select a folder", fg_color="red")
        return

    status_label.configure(text="Starting download...", fg_color="gray")
    progress_bar.set(0)
    progress_label.configure(text="0%")

    def run_download():
        try:
            # Setup yt-dlp options
            ydl_opts = {
                'format': f'bestvideo[height<={resolution[:-1]}]+bestaudio/best',
                'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = sanitize_filename(info.get('title', 'video'))
                status_label.configure(text=f"Downloaded: {title}", fg_color="green")
        except Exception as e:
            status_label.configure(text=f"Error: {str(e)}", fg_color="red")

    threading.Thread(target=run_download, daemon=True).start()

def progress_hook(d):
    """Update progress bar and label"""
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            percent = downloaded / total
            progress_bar.set(percent)
            progress_label.configure(text=f"{int(percent*100)}%")
    elif d['status'] == 'finished':
        progress_bar.set(1.0)
        progress_label.configure(text="100%")

def choose_directory():
    """Open folder dialog and set directory"""
    folder = filedialog.askdirectory()
    if folder:
        save_dir_var.set(folder)

# ----------------------------
# GUI Setup
# ----------------------------
root = ctk.CTk()
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
root.title("YouTube Downloader by Lewis")
root.geometry("720x480")
root.minsize(720, 480)

content_frame = ctk.CTkFrame(root)
content_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

# URL Entry
ctk.CTkLabel(content_frame, text="YouTube URL:").pack(pady=(10, 0))
entry_url = ctk.CTkEntry(content_frame, width=500, height=40)
entry_url.pack(pady=(0, 10))

# Resolution Dropdown
ctk.CTkLabel(content_frame, text="Resolution:").pack(pady=(5, 0))
resolution_var = ctk.StringVar(value="720")
resolution_combobox = ttk.Combobox(content_frame, values=["720", "480", "360", "240"], textvariable=resolution_var)
resolution_combobox.pack(pady=(0, 10))

# Save Directory
ctk.CTkLabel(content_frame, text="Save Folder:").pack(pady=(5, 0))
save_dir_var = ctk.StringVar(value=os.path.join(os.getcwd(), "Downloads"))
save_dir_entry = ctk.CTkEntry(content_frame, textvariable=save_dir_var, width=400)
save_dir_entry.pack(pady=(0, 5))
ctk.CTkButton(content_frame, text="Choose Folder", command=choose_directory).pack(pady=(0, 10))

# Download Button
download_button = ctk.CTkButton(content_frame, text="Download", command=download_video)
download_button.pack(pady=(10, 10))

# Progress
progress_label = ctk.CTkLabel(content_frame, text="0%")
progress_label.pack(pady=(5, 0))
progress_bar = ctk.CTkProgressBar(content_frame, width=500)
progress_bar.set(0)
progress_bar.pack(pady=(0, 10))

# Status Label
status_label = ctk.CTkLabel(content_frame, text="", fg_color="gray")
status_label.pack(pady=(5, 10))

# ----------------------------
# Start GUI
# ----------------------------
os.makedirs(save_dir_var.get(), exist_ok=True)
root.mainloop()
