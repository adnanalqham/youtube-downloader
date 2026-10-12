
import threading
import queue
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp

APP_DIR = Path(__file__).resolve().parent
FFMPEG_DIR = APP_DIR / "ffmpeg" / "bin"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def file_size(size):
    if size is None:
        return "Unknown size"

    size = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024


class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("780x650")
        self.minsize(700, 600)

        self.events = queue.Queue()
        self.qualities = []
        self.video_url = ""
        self.busy = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header
        header = ctk.CTkFrame(self, corner_radius=14)
        header.grid(row=0, column=0, padx=22, pady=(22, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="YOUTUBE DOWNLOADER",
            font=ctk.CTkFont(size=25, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(18, 3), sticky="w")

        ctk.CTkLabel(
            header,
            text="Download videos • Choose quality • Save to your PC",
            text_color="#A8B0C0",
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, padx=20, pady=(0, 18), sticky="w")

        # URL input
        url_frame = ctk.CTkFrame(self, corner_radius=14)
        url_frame.grid(row=1, column=0, padx=22, pady=8, sticky="ew")
        url_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            url_frame, text="YouTube URL",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(14, 5), sticky="w")

        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Paste a YouTube video link here...",
            height=42,
        )
        self.url_entry.grid(
            row=1, column=0, padx=16, pady=(0, 12), sticky="ew"
        )

        self.check_button = ctk.CTkButton(
            url_frame, text="Check Video", width=140,
            height=38, command=self.check_video
        )
        self.check_button.grid(
            row=2, column=0, padx=16, pady=(0, 15), sticky="w"
        )

        # Video information and quality
        self.info_frame = ctk.CTkFrame(self, corner_radius=14)
        self.info_frame.grid(
            row=2, column=0, padx=22, pady=8, sticky="ew"
        )
        self.info_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.info_frame, text="Video Information",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(14, 5), sticky="w")

        self.title_label = ctk.CTkLabel(
            self.info_frame, text="No video checked yet",
            anchor="w", justify="left", wraplength=680
        )
        self.title_label.grid(
            row=1, column=0, padx=16, pady=4, sticky="ew"
        )

        self.duration_label = ctk.CTkLabel(
            self.info_frame, text="Duration: —",
            text_color="#A8B0C0", anchor="w"
        )
        self.duration_label.grid(
            row=2, column=0, padx=16, pady=(0, 10), sticky="w"
        )

        self.quality_menu = ctk.CTkComboBox(
            self.info_frame,
            values=["Check a video first"],
            state="readonly",
            height=40,
        )
        self.quality_menu.grid(
            row=3, column=0, padx=16, pady=(0, 15), sticky="ew"
        )
        self.quality_menu.set("Check a video first")

        # Save folder and download
        bottom = ctk.CTkFrame(self, corner_radius=14)
        bottom.grid(
            row=3, column=0, padx=22, pady=8, sticky="nsew"
        )
        bottom.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            bottom, text="Save Location",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(14, 5), sticky="w")

        default_folder = str(Path.home() / "Downloads")
        self.folder_entry = ctk.CTkEntry(bottom, height=38)
        self.folder_entry.insert(0, default_folder)
        self.folder_entry.grid(
            row=1, column=0, padx=(16, 8), pady=(0, 12), sticky="ew"
        )

        self.browse_button = ctk.CTkButton(
            bottom, text="Browse", width=100, height=38,
            command=self.browse_folder
        )
        self.browse_button.grid(
            row=1, column=1, padx=(0, 16), pady=(0, 12)
        )

        self.download_button = ctk.CTkButton(
            bottom, text="Download Video", height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_download,
            state="disabled",
        )
        self.download_button.grid(
            row=2, column=0, columnspan=2,
            padx=16, pady=(2, 12), sticky="ew"
        )

        self.progress = ctk.CTkProgressBar(bottom, height=12)
        self.progress.grid(
            row=3, column=0, columnspan=2,
            padx=16, pady=(0, 8), sticky="ew"
        )
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            bottom, text="Ready",
            anchor="w", text_color="#A8B0C0"
        )
        self.status_label.grid(
            row=4, column=0, columnspan=2,
            padx=16, pady=(0, 14), sticky="ew"
        )

        self.after(150, self.process_events)

    def set_busy(self, busy):
        self.busy = busy
        state = "disabled" if busy else "normal"
        self.check_button.configure(state=state)
        self.browse_button.configure(state=state)
        self.url_entry.configure(state=state)

        if busy:
            self.download_button.configure(state="disabled")
        else:
            self.download_button.configure(
                state="normal" if self.qualities else "disabled"
            )

    def browse_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.folder_entry.get()
        )
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def check_video(self):
        url = self.url_entry.get().strip()

        if not url.startswith(("https://", "http://")):
            messagebox.showerror(
                "Invalid URL", "Please paste a valid video URL."
            )
            return

        if self.busy:
            return

        self.video_url = url
        self.qualities = []
        self.quality_menu.configure(values=["Checking video..."])
        self.quality_menu.set("Checking video...")
        self.download_button.configure(state="disabled")
        self.status_label.configure(text="Checking video formats...")
        self.set_busy(True)

        threading.Thread(
            target=self.inspect_worker, args=(url,), daemon=True
        ).start()

    def inspect_worker(self, url):
        try:
            options = {
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)

            formats = info.get("formats", [])
            audio_formats = [
                f for f in formats
                if f.get("vcodec") == "none"
                and f.get("acodec") not in (None, "none")
            ]
            audio_formats.sort(
                key=lambda f: f.get("abr") or 0, reverse=True
            )
            best_audio = audio_formats[0] if audio_formats else None

            by_height = {}

            for fmt in formats:
                height = fmt.get("height")
                if not height or fmt.get("vcodec") in (None, "none"):
                    continue

                current = by_height.get(height)
                score = fmt.get("tbr") or 0

                if current and score <= current["score"]:
                    continue

                video_size = fmt.get("filesize") or fmt.get("filesize_approx")
                has_audio = fmt.get("acodec") not in (None, "none")

                audio_size = None
                total_size = video_size

                if not has_audio and best_audio:
                    audio_size = (
                        best_audio.get("filesize")
                        or best_audio.get("filesize_approx")
                    )
                    if video_size is not None and audio_size is not None:
                        total_size = video_size + audio_size
                    else:
                        total_size = None

                if has_audio:
                    format_code = fmt["format_id"]
                elif best_audio:
                    format_code = (
                        f"{fmt['format_id']}+{best_audio['format_id']}"
                    )
                else:
                    format_code = fmt["format_id"]

                by_height[height] = {
                    "height": height,
                    "size": total_size,
                    "format": format_code,
                    "score": score,
                }

            qualities = [
                by_height[h] for h in sorted(by_height, reverse=True)
            ]

            self.events.put(("inspected", info, qualities))

        except Exception as exc:
            self.events.put(("error", str(exc)))

    def start_download(self):
        if self.busy or not self.qualities:
            return

        selected_text = self.quality_menu.get()
        selected = next(
            (
                item for item in self.qualities
                if item["label"] == selected_text
            ),
            None,
        )

        if selected is None:
            messagebox.showerror(
                "Choose Quality", "Please select an available resolution."
            )
            return

        folder = Path(self.folder_entry.get().strip().strip('"')).expanduser()

        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Save Folder Error", str(exc))
            return

        self.progress.set(0)
        self.status_label.configure(text="Starting download...")
        self.set_busy(True)

        threading.Thread(
            target=self.download_worker,
            args=(self.video_url, selected, folder),
            daemon=True,
        ).start()

    def download_worker(self, url, selected, folder):
        def hook(data):
            if data.get("status") == "downloading":
                percent = data.get("_percent_str", "").strip()
                speed = data.get("_speed_str", "Unknown").strip()
                eta = data.get("_eta_str", "Unknown").strip()
                downloaded = data.get("downloaded_bytes", 0)
                total = data.get("total_bytes") or data.get(
                    "total_bytes_estimate"
                )
                fraction = downloaded / total if total else 0

                self.events.put((
                    "progress", fraction,
                    f"Downloading: {percent} | Speed: {speed} | ETA: {eta}"
                ))

            elif data.get("status") == "finished":
                self.events.put((
                    "status", "Download part complete. Processing..."
                ))

        options = {
            "format": selected["format"],
            "ffmpeg_location": str(FFMPEG_DIR),
            "outtmpl": str(folder / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [hook],
            "windowsfilenames": True,
            "retries": 3,
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            self.events.put(("done",))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def process_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]

                if kind == "inspected":
                    info, qualities = event[1], event[2]
                    self.qualities = qualities

                    self.title_label.configure(
                        text=info.get("title", "Unknown title")
                    )
                    self.duration_label.configure(
                        text=f"Duration: {info.get('duration_string', 'Unknown')}"
                    )

                    if not qualities:
                        self.quality_menu.configure(
                            values=["No video formats found"]
                        )
                        self.quality_menu.set("No video formats found")
                        self.status_label.configure(
                            text="No downloadable video formats found."
                        )
                    else:
                        for item in qualities:
                            size = file_size(item["size"])
                            item["label"] = (
                                f"{item['height']}p  |  {size}"
                            )

                        labels = [q["label"] for q in qualities]
                        self.quality_menu.configure(values=labels)
                        self.quality_menu.set(labels[0])
                        self.status_label.configure(
                            text=f"Found {len(qualities)} available resolutions."
                        )

                    self.set_busy(False)

                elif kind == "progress":
                    fraction, status = event[1], event[2]
                    self.progress.set(max(0, min(1, fraction)))
                    self.status_label.configure(text=status)

                elif kind == "status":
                    self.status_label.configure(text=event[1])

                elif kind == "done":
                    self.progress.set(1)
                    self.status_label.configure(text="Download completed!")
                    self.set_busy(False)
                    messagebox.showinfo(
                        "Download Complete",
                        "The video has been downloaded successfully."
                    )

                elif kind == "error":
                    self.status_label.configure(text="An error occurred.")
                    self.set_busy(False)
                    messagebox.showerror("Download Error", event[1])

        except queue.Empty:
            pass

        self.after(150, self.process_events)


if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
