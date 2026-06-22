document.addEventListener('DOMContentLoaded', async () => {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const videoList = document.getElementById('videoList');
    const refreshBtn = document.getElementById('refreshBtn');
    const settingsBtn = document.getElementById('settingsBtn');

    // Check server connection
    async function checkConnection() {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({ type: 'CHECK_SERVER' }, (response) => {
                if (response?.connected) {
                    statusDot.className = 'status-dot connected';
                    statusText.textContent = 'Connected';
                    resolve(true);
                } else {
                    statusDot.className = 'status-dot disconnected';
                    statusText.textContent = 'Disconnected';
                    resolve(false);
                }
            });
        });
    }

    // Load detected videos
    async function loadVideos() {
        chrome.runtime.sendMessage({ type: 'GET_DETECTED_VIDEOS' }, (response) => {
            if (response?.videos?.length > 0) {
                renderVideos(response.videos);
            } else {
                videoList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">🎬</div>
                        <div>No videos detected yet.<br>Browse YouTube or social media to detect videos.</div>
                    </div>
                `;
            }
        });
    }

    // Render video list
    function renderVideos(videos) {
        videoList.innerHTML = videos.map(video => `
            <div class="video-item" data-url="${video.url}">
                <img class="video-thumb" src="${video.thumbnail || ''}" alt="" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 48 36%22><rect fill=%22%2322262f%22 width=%2248%22 height=%2236%22/></svg>'">
                <div class="video-info">
                    <div class="video-title">${escapeHtml(video.title || 'Untitled')}</div>
                    <div class="video-platform">${video.platform || 'Unknown'}</div>
                </div>
                <button class="video-download-btn" data-url="${video.url}" data-title="${escapeHtml(video.title || '')}">Download</button>
            </div>
        `).join('');

        // Add click handlers
        document.querySelectorAll('.video-download-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const url = btn.dataset.url;
                const title = btn.dataset.title;

                chrome.runtime.sendMessage({ type: 'START_DOWNLOAD', data: { url, title, platform: 'browser' } }, (response) => {
                    if (response?.success) {
                        btn.textContent = 'Started!';
                        btn.style.background = '#22c55e';
                        setTimeout(() => {
                            btn.textContent = 'Download';
                            btn.style.background = '';
                        }, 2000);
                    } else {
                        alert('Make sure YTGrab app is running on your computer!');
                    }
                });
            });
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Event listeners
    refreshBtn.addEventListener('click', () => {
        checkConnection();
        loadVideos();
    });

    settingsBtn.addEventListener('click', () => {
        chrome.runtime.openOptionsPage?.() || chrome.tabs.create({ url: 'chrome://extensions' });
    });

    // Initial load
    await checkConnection();
    loadVideos();

    // Auto-refresh every 5 seconds
    setInterval(() => {
        checkConnection();
        loadVideos();
    }, 5000);
});
