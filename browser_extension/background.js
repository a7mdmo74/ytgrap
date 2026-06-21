const LOCAL_SERVER = "http://127.0.0.1:19850";
let serverConnected = false;
let detectedVideos = new Map();

// Check server connection
async function checkServer() {
    try {
        const response = await fetch(`${LOCAL_SERVER}/ping`, {
            method: "GET",
            signal: AbortSignal.timeout(2000)
        });
        serverConnected = response.ok;
    } catch {
        serverConnected = false;
    }
    return serverConnected;
}

// Send video info to local server
async function sendToServer(videoInfo) {
    try {
        const response = await fetch(`${LOCAL_SERVER}/add`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(videoInfo)
        });
        return response.ok;
    } catch {
        return false;
    }
}

// Get download queue from server
async function getQueue() {
    try {
        const response = await fetch(`${LOCAL_SERVER}/queue`);
        if (response.ok) {
            return await response.json();
        }
    } catch {}
    return [];
}

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "VIDEO_DETECTED") {
        const videoId = generateVideoId(message.data);
        if (!detectedVideos.has(videoId)) {
            detectedVideos.set(videoId, {
                ...message.data,
                id: videoId,
                detectedAt: Date.now(),
                tabId: sender.tab?.id
            });

            // Update badge
            updateBadge();

            // Try to send to server
            sendToServer(message.data).then(ok => {
                if (ok) {
                    detectedVideos.get(videoId).sentToServer = true;
                }
            });
        }
        sendResponse({ success: true });
    }

    if (message.type === "CHECK_SERVER") {
        checkServer().then(connected => {
            sendResponse({ connected });
        });
        return true;
    }

    if (message.type === "GET_QUEUE") {
        getQueue().then(queue => {
            sendResponse({ queue });
        });
        return true;
    }

    if (message.type === "START_DOWNLOAD") {
        sendToServer(message.data).then(ok => {
            sendResponse({ success: ok });
        });
        return true;
    }

    if (message.type === "GET_DETECTED_VIDEOS") {
        sendResponse({ videos: Array.from(detectedVideos.values()) });
    }
});

function generateVideoId(data) {
    return `${data.url}_${data.quality || "auto"}`;
}

function updateBadge() {
    const count = detectedVideos.size;
    chrome.action.setBadgeText({ text: count > 0 ? String(count) : "" });
    chrome.action.setBadgeBackgroundColor({ color: "#f5a623" });
}

// Periodically check server connection
setInterval(checkServer, 5000);
checkServer();

// Handle tab updates to clear old video detections
chrome.tabs.onRemoved.addListener((tabId) => {
    for (const [id, video] of detectedVideos) {
        if (video.tabId === tabId) {
            detectedVideos.delete(id);
        }
    }
    updateBadge();
});
