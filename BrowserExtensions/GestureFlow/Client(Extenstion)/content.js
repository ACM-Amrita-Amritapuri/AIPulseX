// content.js

async function startCamera() {
    try {
        console.log("Starting camera");
        
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const videoElement = document.createElement('video');
        videoElement.srcObject = stream;
        videoElement.autoplay = true;

        const popupDiv = document.createElement('div');
        popupDiv.style.position = 'fixed';
        popupDiv.style.bottom = '10px';
        popupDiv.style.right = '10px';
        popupDiv.style.width = '320px';
        popupDiv.style.height = '240px';
        popupDiv.style.border = '2px solid #000';
        popupDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        popupDiv.style.zIndex = '9999';
        popupDiv.style.overflow = 'hidden';
        popupDiv.style.borderRadius = '8px';

        videoElement.style.width = '100%';
        videoElement.style.height = '100%';
        popupDiv.appendChild(videoElement);

        document.body.appendChild(popupDiv);

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        setInterval(() => {
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
            const frame = canvas.toDataURL('image/jpeg');
            chrome.runtime.sendMessage({ type: 'frame', data: frame });
        }, 33);

    } catch (error) {
        console.error('Error accessing camera:', error);
    }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'startCamera') {
        startCamera();
    } else if (message.action === 'scroll') {
        window.scrollBy(0, 500);
        console.log('scrolling');
    }
});
