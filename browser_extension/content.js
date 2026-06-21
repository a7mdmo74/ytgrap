(function() {
    'use strict';

    let mainVideo = null;
    let detectedInfo = null;
    let serverConnected = false;
    let lastUrl = '';

    function getPlatform() {
        const host = window.location.hostname;
        if (host.includes('youtube.com') || host.includes('youtu.be')) return 'youtube';
        if (host.includes('instagram.com')) return 'instagram';
        if (host.includes('facebook.com')) return 'facebook';
        if (host.includes('twitter.com') || host.includes('x.com')) return 'twitter';
        if (host.includes('tiktok.com')) return 'tiktok';
        if (host.includes('vimeo.com')) return 'vimeo';
        if (host.includes('dailymotion.com')) return 'dailymotion';
        if (host.includes('twitch.tv')) return 'twitch';
        if (host.includes('reddit.com')) return 'reddit';
        if (host.includes('bilibili.com')) return 'bilibili';
        if (host.includes('soundcloud.com')) return 'soundcloud';
        return 'unknown';
    }

    function getActiveVideo() {
        const platform = getPlatform();

        if (platform === 'youtube') {
            const player = document.querySelector('#movie_player') || document.querySelector('.html5-video-player');
            if (player) {
                const video = player.querySelector('video.html5-main-video') || player.querySelector('video');
                if (video) return video;
            }
            const video = document.querySelector('video.html5-main-video');
            if (video) return video;
        }

        if (platform === 'tiktok') {
            const video = document.querySelector('[data-e2e="video-player"] video') ||
                         document.querySelector('.tiktok-1no72h2-DivVideoPlayerContainerV2 video') ||
                         document.querySelector('video[xvideo]');
            if (video) return video;
        }

        if (platform === 'instagram') {
            const video = document.querySelector('video[playsinline]') ||
                         document.querySelector('article video');
            if (video) return video;
        }

        if (platform === 'twitter' || platform === 'x') {
            const video = document.querySelector('video[playsinline]') ||
                         document.querySelector('[data-testid="videoPlayer"] video');
            if (video) return video;
        }

        if (platform === 'facebook') {
            const selectors = [
                'video[data-testid="fbvideo"]',
                'div[role="presentation"] video',
                'video[style*="width"]',
                'div[data-pagelet] video',
                'div[aria-label*="video" i] video',
                'video'
            ];
            for (const sel of selectors) {
                const videos = document.querySelectorAll(sel);
                for (const video of videos) {
                    const rect = video.getBoundingClientRect();
                    if (rect.width > 100 && rect.height > 100) {
                        return video;
                    }
                }
            }
        }

        const allVideos = document.querySelectorAll('video');
        for (const video of allVideos) {
            const rect = video.getBoundingClientRect();
            const isVisible = rect.width > 200 && rect.height > 150;
            if (isVisible) {
                return video;
            }
        }

        return null;
    }

    function getVideoInfo(video) {
        const platform = getPlatform();
        const info = {
            platform: platform,
            url: window.location.href.split('&')[0],
            title: document.title.replace(' - YouTube', '').trim(),
            thumbnail: document.querySelector('meta[property="og:image"]')?.content || null
        };
        return info;
    }

    function updatePanel() {
        const countEl = document.getElementById('ytgrab-count');
        const titleEl = document.getElementById('ytgrab-video-title');
        const btnEl = document.getElementById('ytgrab-download-all');

        if (countEl) {
            countEl.textContent = detectedInfo ? '1' : '0';
        }
        if (titleEl) {
            titleEl.textContent = detectedInfo ? detectedInfo.title.substring(0, 40) : 'No video detected';
        }
        if (btnEl) {
            btnEl.style.opacity = detectedInfo ? '1' : '0.4';
            btnEl.style.pointerEvents = detectedInfo ? 'auto' : 'none';
        }
    }

    function createDownloadButton(video) {
        removeDownloadButton();

        const container = document.createElement('div');
        container.id = 'ytgrab-btn-container';
        container.className = 'ytgrab-download-container';

        const btn = document.createElement('button');
        btn.className = 'ytgrab-download-btn';
        btn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>Download with YTGrab</span>
        `;

        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (detectedInfo) startDownload(detectedInfo);
        });

        container.appendChild(btn);

        let parent = video.parentElement;
        for (let i = 0; i < 5 && parent; i++) {
            if (parent.tagName === 'YTD-PLAYER' ||
                parent.tagName === 'YTD-WATCH-FLEXY' ||
                parent.classList?.contains('html5-video-player') ||
                parent.getAttribute('data-e2e') === 'video-player' ||
                parent.querySelector('video') === video) {
                break;
            }
            parent = parent.parentElement;
        }

        if (parent) {
            if (getComputedStyle(parent).position === 'static') {
                parent.style.position = 'relative';
            }
            parent.appendChild(container);
        }
    }

    function removeDownloadButton() {
        const existing = document.getElementById('ytgrab-btn-container');
        if (existing) existing.remove();
    }

    async function startDownload(info) {
        try {
            const response = await fetch('http://127.0.0.1:19850/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(info)
            });
            if (response.ok) {
                showNotification('Download started!', 'success');
                return;
            }
        } catch {}

        showNotification('Make sure YTGrab app is running!', 'error');
    }

    function showNotification(message, type) {
        const existing = document.querySelector('.ytgrab-notification');
        if (existing) existing.remove();

        const notification = document.createElement('div');
        notification.className = `ytgrab-notification ytgrab-${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    function scan() {
        const video = getActiveVideo();
        const currentUrl = window.location.href;

        if (currentUrl !== lastUrl) {
            lastUrl = currentUrl;
            mainVideo = null;
            detectedInfo = null;
            removeDownloadButton();
        }

        if (video && video !== mainVideo) {
            mainVideo = video;
            detectedInfo = getVideoInfo(video);
            createDownloadButton(video);
            updatePanel();
        } else if (!video && mainVideo) {
            mainVideo = null;
            detectedInfo = null;
            removeDownloadButton();
            updatePanel();
        }
    }

    function addFloatingPanel() {
        const existing = document.getElementById('ytgrab-panel');
        if (existing) existing.remove();

        const panel = document.createElement('div');
        panel.id = 'ytgrab-panel';
        panel.innerHTML = `
            <div class="ytgrab-panel-header">
                <span class="ytgrab-logo">YT</span>
                <span class="ytgrab-title">Grab</span>
                <span class="ytgrab-status" id="ytgrab-status">●</span>
            </div>
            <div class="ytgrab-panel-content">
                <div class="ytgrab-panel-item">
                    <span>Active video:</span>
                    <span id="ytgrab-count">0</span>
                </div>
                <div class="ytgrab-video-title" id="ytgrab-video-title">No video detected</div>
                <button class="ytgrab-panel-btn" id="ytgrab-download-all">
                    Download Active Video
                </button>
            </div>
        `;

        document.body.appendChild(panel);

        let isDragging = false;
        let offsetX, offsetY;

        panel.querySelector('.ytgrab-panel-header').addEventListener('mousedown', (e) => {
            isDragging = true;
            offsetX = e.clientX - panel.getBoundingClientRect().left;
            offsetY = e.clientY - panel.getBoundingClientRect().top;
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            panel.style.left = `${e.clientX - offsetX}px`;
            panel.style.top = `${e.clientY - offsetY}px`;
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        document.getElementById('ytgrab-download-all').addEventListener('click', () => {
            if (detectedInfo) startDownload(detectedInfo);
        });

        chrome.runtime.sendMessage({ type: 'CHECK_SERVER' }, (response) => {
            const status = document.getElementById('ytgrab-status');
            if (status) {
                status.style.color = response?.connected ? '#22c55e' : '#ef4444';
                serverConnected = response?.connected;
            }
        });

        updatePanel();
    }

    function init() {
        addFloatingPanel();
        scan();
        setInterval(scan, 1000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
