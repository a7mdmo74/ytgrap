const DEFAULT_SETTINGS = {
    serverUrl: 'http://127.0.0.1:19850',
    autoDownload: false,
    showButton: true,
    showPanel: true,
    showNotifications: true,
    platforms: ['youtube', 'instagram', 'facebook', 'twitter', 'tiktok', 'vimeo', 'dailymotion', 'twitch', 'reddit', 'bilibili', 'soundcloud']
};

let currentSettings = { ...DEFAULT_SETTINGS };

document.addEventListener('DOMContentLoaded', async () => {
    await loadSettings();
    setupEventListeners();
});

async function loadSettings() {
    const stored = await chrome.storage.local.get('settings');
    if (stored.settings) {
        currentSettings = { ...DEFAULT_SETTINGS, ...stored.settings };
    }
    applySettingsToUI();
}

function applySettingsToUI() {
    document.getElementById('serverUrl').value = currentSettings.serverUrl;
    document.getElementById('autoDownload').checked = currentSettings.autoDownload;
    document.getElementById('showButton').checked = currentSettings.showButton;
    document.getElementById('showPanel').checked = currentSettings.showPanel;
    document.getElementById('showNotifications').checked = currentSettings.showNotifications;

    document.querySelectorAll('input[name="platform"]').forEach(cb => {
        cb.checked = currentSettings.platforms.includes(cb.value);
    });
}

function setupEventListeners() {
    document.getElementById('saveSettings').addEventListener('click', saveSettings);
    document.getElementById('resetSettings').addEventListener('click', resetSettings);
    document.getElementById('testConnection').addEventListener('click', testConnection);
}

async function saveSettings() {
    const serverUrl = document.getElementById('serverUrl').value.trim().replace(/\/$/, '');
    const platforms = [];
    document.querySelectorAll('input[name="platform"]:checked').forEach(cb => {
        platforms.push(cb.value);
    });

    currentSettings = {
        serverUrl: serverUrl || DEFAULT_SETTINGS.serverUrl,
        autoDownload: document.getElementById('autoDownload').checked,
        showButton: document.getElementById('showButton').checked,
        showPanel: document.getElementById('showPanel').checked,
        showNotifications: document.getElementById('showNotifications').checked,
        platforms: platforms
    };

    await chrome.storage.local.set({ settings: currentSettings });
    showStatus('Settings saved successfully!', 'success');

    chrome.runtime.sendMessage({ type: 'SETTINGS_UPDATED', settings: currentSettings });
}

function resetSettings() {
    currentSettings = { ...DEFAULT_SETTINGS };
    applySettingsToUI();
    saveSettings();
}

async function testConnection() {
    const serverUrl = document.getElementById('serverUrl').value.trim().replace(/\/$/, '');
    const btn = document.getElementById('testConnection');
    const originalText = btn.textContent;

    btn.textContent = 'Testing...';
    btn.disabled = true;

    try {
        const response = await fetch(`${serverUrl}/ping`, {
            method: 'GET',
            signal: AbortSignal.timeout(3000)
        });

        if (response.ok) {
            const data = await response.json();
            showStatus(`Connected! Server version: ${data.version}`, 'success');
        } else {
            showStatus('Server responded with error', 'error');
        }
    } catch (error) {
        showStatus('Cannot connect to server. Is YTGrab app running?', 'error');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

function showStatus(message, type) {
    const el = document.getElementById('statusMessage');
    el.textContent = message;
    el.className = `status-message ${type} show`;

    setTimeout(() => {
        el.classList.remove('show');
    }, 3000);
}
