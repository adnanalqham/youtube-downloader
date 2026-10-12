
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("yt-dlp is not installed.")
    print("Run: python -m pip install -U yt-dlp")
    input("Press Enter to exit...")
    sys.exit(1)

FFMPEG_DIR = Path(__file__).parent / "ffmpeg" / "bin"


def get_size(fmt):
    return fmt.get("filesize") or fmt.get("filesize_approx")


def format_size(size):
    if size is None:
        return "Unknown"
    size = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.2f} {unit}"
        size /= 1024
    return "Unknown"


def progress_hook(data):
    if data.get("status") == "downloading":
        percent = data.get("_percent_str", "").strip()
        speed = data.get("_speed_str", "Unknown").strip()
        eta = data.get("_eta_str", "Unknown").strip()
        print(
            f"\rProgress: {percent} | Speed: {speed} | ETA: {eta}   ",
            end="",
            flush=True,
        )
    elif data.get("status") == "finished":
        print("\nDownload part finished. Processing...")


def get_quality_options(info):
    formats = info.get("formats", [])

    videos = [
        f for f in formats
        if f.get("height")
        and f.get("vcodec") != "none"
        and f.get("format_id")
    ]

    audios = [
        f for f in formats
        if f.get("acodec") != "none"
        and f.get("vcodec") == "none"
        and f.get("format_id")
    ]

    # Prefer the highest-bitrate audio stream with a known size.
    audios.sort(
        key=lambda f: (
            f.get("abr") or 0,
            get_size(f) is not None,
        ),
        reverse=True,
    )
    best_audio = audios[0] if audios else None

    qualities = {}

    for video in videos:
        height = video["height"]
        video_has_audio = video.get("acodec") != "none"

        # Keep the strongest video candidate for each resolution.
        score = (
            video.get("tbr") or 0,
            get_size(video) is not None,
        )

        current = qualities.get(height)
        if current and current["score"] >= score:
            continue

        video_size = get_size(video)
        audio_size = (
            get_size(best_audio)
            if best_audio and not video_has_audio
            else None
        )

        if video_has_audio:
            total_size = video_size
            format_code = video["format_id"]
        elif best_audio:
            total_size = (
                video_size + audio_size
                if video_size is not None and audio_size is not None
                else None
            )
            format_code = (
                f"{video['format_id']}+{best_audio['format_id']}"
            )
        else:
            total_size = video_size
            format_code = video["format_id"]

        qualities[height] = {
            "height": height,
            "format": format_code,
            "size": total_size,
            "score": score,
        }

    return [
        qualities[h]
        for h in sorted(qualities, reverse=True)
    ]


def main():
    while True:
        print("\n" + "=" * 68)
        print("                    YOUTUBE DOWNLOADER")
        print("                         Version 2.0")
        print("=" * 68)
        print("  1. Download Video")
        print("  2. Exit")
        print("=" * 68)

        choice = input("Select an option: ").strip()

        if choice == "2":
            print("Goodbye!")
            break

        if choice != "1":
            print("Invalid option.")
            continue

        url = input("\nPaste YouTube URL: ").strip()

        if not url.startswith(("https://", "http://")):
            print("Invalid URL.")
            continue

        print("\nChecking video information...")
        inspect_options = {
            "noplaylist": True,
            "quiet": True,
        }

        try:
            with yt_dlp.YoutubeDL(inspect_options) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as exc:
            print(f"\nCould not read video information: {exc}")
            input("Press Enter to continue...")
            continue

        qualities = get_quality_options(info)

        print("\n" + "=" * 68)
        print("VIDEO INFORMATION")
        print("-" * 68)
        print(f"Title    : {info.get('title', 'Unknown')}")
        print(f"Duration : {info.get('duration_string', 'Unknown')}")
        print("=" * 68)

        if not qualities:
            print("No downloadable video formats were found.")
            input("Press Enter to continue...")
            continue

        print("\nAVAILABLE RESOLUTIONS")
        print("-" * 68)
        print(f"{'No.':<5}{'Quality':<14}{'Estimated Size':<22}{'Format'}")
        print("-" * 68)

        for index, item in enumerate(qualities, start=1):
            print(
                f"{index:<5}"
                f"{str(item['height']) + 'p':<14}"
                f"{format_size(item['size']):<22}"
                f"Video + Audio"
            )

        best_option = len(qualities) + 1
        print(
            f"{best_option:<5}"
            f"{'Best quality':<14}"
            f"{'Depends on format':<22}"
            f"Video + Audio"
        )
        print("-" * 68)
        print("Note: Sizes are estimates when exact sizes are unavailable.")

        selection = input("\nSelect resolution number: ").strip()

        if not selection.isdigit():
            print("Invalid selection.")
            continue

        selection = int(selection)

        if selection == best_option:
            format_code = "bestvideo*+bestaudio/best"
            selected_label = "Best Available Quality"
            selected_size = None
        elif 1 <= selection <= len(qualities):
            selected = qualities[selection - 1]
            format_code = selected["format"]
            selected_label = f"{selected['height']}p"
            selected_size = selected["size"]
        else:
            print("Invalid selection.")
            continue

        print(f"\nSelected quality: {selected_label}")
        print(f"Estimated size: {format_size(selected_size)}")

        folder = input(
            "\nSave folder (Enter for Downloads): "
        ).strip().strip('"')

        output_dir = (
            Path(folder).expanduser()
            if folder
            else Path.home() / "Downloads"
        )

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(f"Cannot create save folder: {exc}")
            continue

        options = {
            "format": format_code,
            "ffmpeg_location": str(FFMPEG_DIR),
            "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [progress_hook],
            "windowsfilenames": True,
            "retries": 3,
        }

        print("\n" + "=" * 68)
        print("DOWNLOAD")
        print("-" * 68)
        print(f"Quality      : {selected_label}")
        print(f"Estimated size: {format_size(selected_size)}")
        print(f"Save folder  : {output_dir}")
        print("=" * 68)
        print("Starting download...\n")

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            print("\nDownload completed successfully!")
        except KeyboardInterrupt:
            print("\nDownload cancelled.")
        except Exception as exc:
            print(f"\nDownload failed: {exc}")

        input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    main()
