# YTGrab

A YouTube video and playlist downloader with IDM-style browser integration.

Works on **Windows**, **macOS**, and **Linux**.

[**Live Page**](https://a7mdmo74.github.io/ytgrap/) | [العربية](README-ar.md)

## Features

- Download YouTube videos in multiple qualities (up to 4K)
- Playlist support — auto-detects and downloads all videos
- Live progress, speed, ETA, and file size display
- Adjustable settings: output format (MP4/MKV/WebM), parallel fragments, retries
- Auto-merges video + audio streams
- Dark theme with amber accent (IDM-style)

### NEW: Browser Extension (Like IDM!)

- Install the Chrome extension to detect videos automatically
- Browse YouTube, Instagram, TikTok, Twitter/X, Facebook, Vimeo, and more
- Click the download button that appears on any video
- Videos are queued in the app and download automatically
- Works with 12+ social media platforms
- Configurable settings page

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

## Browser Extension Setup

### Chrome / Edge / Brave

1. Open your browser and go to `chrome://extensions`
2. Enable **Developer mode** (toggle in top right)
3. Click **Load unpacked**
4. Select the `browser_extension` folder from this project
5. The YTGrab icon will appear in your toolbar

### Firefox

1. Open Firefox and go to `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on**
3. Select any file in the `browser_extension` folder

### How It Works

1. Start the YTGrab app (the local server starts automatically on port 19850)
2. Browse YouTube, Instagram, TikTok, or any supported platform
3. Click the "Download" button that appears on videos
4. The video is added to the Browser Queue in the app
5. Click the play button (▶) to start downloading

### Extension Settings

Right-click the YTGrab icon in your toolbar and select **Options** to configure:

**Server Connection**
- Set custom server address (default: `http://127.0.0.1:19850`)
- Test connection to verify app is running

**Download Behavior**
- Auto-download on detection — automatically start download when video is detected
- Show download button — toggle the download button overlay on videos
- Show floating panel — toggle the YTGrab panel on video pages
- Show notifications — toggle toast notifications

**Supported Platforms**
- Enable/disable detection for each platform individually
- YouTube, Instagram, Facebook, Twitter/X, TikTok, Vimeo, Dailymotion, Twitch, Reddit, Bilibili, SoundCloud

### Supported Platforms

- YouTube, YouTube Music
- Instagram (Reels, Stories, Posts)
- Facebook (Videos, Reels)
- Twitter/X (Videos)
- TikTok
- Vimeo
- Dailymotion
- Twitch (VODs)
- Reddit (Videos)
- Bilibili
- SoundCloud

## Usage

### Manual Download

1. Paste a YouTube video or playlist URL
2. Click **Fetch** to load available qualities
3. Select a quality from the dropdown
4. Choose a save location (default: Downloads)
5. Click **Start Download**

### Browser Extension Download

1. Install the browser extension (see above)
2. Start the YTGrab app
3. Browse any supported platform
4. Click the download button on videos
5. Monitor progress in the Browser Queue

## App Settings

- **Output Format**: MP4, MKV, or WebM
- **Parallel Fragments**: 1-8 (default: 3)
- **Max Retries**: 1-30 (default: 10)
- **Auto-clean**: Remove leftover .part/.temp files

## License

MIT
