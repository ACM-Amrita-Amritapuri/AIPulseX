document.getElementById('startButton').addEventListener('click', () => {
    // Send a message to the content script to start the camera
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'startCamera' });
    });
});
