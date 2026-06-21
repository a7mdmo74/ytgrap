# YTGrab

A YouTube video and playlist downloader with a modern IDM-inspired dark UI.

## Features

- Download YouTube videos in multiple qualities (up to 4K)
- Playlist support — auto-detects and downloads all videos
- Live progress, speed, ETA, and file size display
- Adjustable settings: output format (MP4/MKV/WebM), parallel fragments, retries
- Auto-merges video + audio streams
- Dark theme with amber accent (IDM-style)

## Prerequisites

FFmpeg is required. Install it via:

```bash
winget install Gyan.FFmpeg
```

## Installation

### Download

Download the latest release from [GitHub Releases](https://github.com/a7mdmo74/ytgrap/releases).

Extract the zip and run `install.bat` as administrator.

### Build from source

Requires Python 3.10+ and FFmpeg.

```bash
pip install yt-dlp pyinstaller
pyinstaller YTGrab.spec
```

The built executable will be in `dist/YTGrab/`.

## Usage

1. Paste a YouTube video or playlist URL
2. Click **Fetch** to load available qualities
3. Select a quality from the dropdown
4. Choose a save location (default: Downloads)
5. Click **Start Download**

## Uninstall

Run `uninstall.bat` to remove the installation and shortcuts.

## License

MIT
