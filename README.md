# YTGrab

A YouTube video and playlist downloader with a modern IDM-inspired dark UI.

Works on **Windows**, **macOS**, and **Linux**.

## Features

- Download YouTube videos in multiple qualities (up to 4K)
- Playlist support — auto-detects and downloads all videos
- Live progress, speed, ETA, and file size display
- Adjustable settings: output format (MP4/MKV/WebM), parallel fragments, retries
- Auto-merges video + audio streams
- Dark theme with amber accent (IDM-style)

## Prerequisites

- **Python 3.10+**
- **FFmpeg**

### Install FFmpeg

| Platform | Command |
|----------|---------|
| Windows | `winget install Gyan.FFmpeg` |
| macOS | `brew install ffmpeg` |
| Linux | `sudo apt install ffmpeg` |

## Installation

### Option 1: Run from source (all platforms)

```bash
git clone https://github.com/a7mdmo74/ytgrap.git
cd ytgrap
pip install -r requirements.txt
python youtube_downloader.py
```

### Option 2: Install via pip

```bash
pip install git+https://github.com/a7mdmo74/ytgrap.git
ytgrab
```

### Option 3: Windows installer

Download the latest release from [GitHub Releases](https://github.com/a7mdmo74/ytgrap/releases), extract, and run `install.bat` as administrator.

## Usage

1. Paste a YouTube video or playlist URL
2. Click **Fetch** to load available qualities
3. Select a quality from the dropdown
4. Choose a save location (default: Downloads)
5. Click **Start Download**

## License

MIT
