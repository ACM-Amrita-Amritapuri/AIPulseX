// Function to poll the server for new frame data
function pollServer() {
  fetch("http://127.0.0.1:5000/poll")
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
      throw new Error("Network response was not ok");
    })
    .then((data) => {
      // console.log('Data from server:', data);
      // Handle the new data from server
      // (e.g., process the frame data, update the UI, etc.)
    })
    .catch((error) => {
      console.error("Fetch error:", error);
    })
    .finally(() => {
      // Reinitiate the poll
      setTimeout(pollServer, 1000);
    });
}

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "frame") {
    sendFrameToServer(message.data);
  }
});

// Function to send frame data to the server
function sendFrameToServer(frameData) {
  fetch("http://127.0.0.1:5000/send", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(frameData),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data["action"]);
      if (data["action"] === "rs") {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (tabs.length > 0) {
            const currentTabIndex = tabs[0].index;
            chrome.tabs.query({ windowId: tabs[0].windowId }, (allTabs) => {
              if (allTabs.length > 0) {
                const nextTabIndex = (currentTabIndex + 1) % allTabs.length;
                chrome.tabs.update(allTabs[nextTabIndex].id, { active: true });
              }
            });
          }
        });
      }
      else if(data["action"] === "ls") {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs.length > 0) {
                const currentTabIndex = tabs[0].index;
                chrome.tabs.query({ windowId: tabs[0].windowId }, (allTabs) => {
                    if (allTabs.length > 0) {
                        const prevTabIndex = (currentTabIndex - 1 + allTabs.length) % allTabs.length;
                        chrome.tabs.update(allTabs[prevTabIndex].id, { active: true });
                    }
                });
            }
        });        
      }
      else if(data["action"] === "sd"){
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            var activeTab = tabs[0];
            chrome.scripting.executeScript({
                target: {tabId: activeTab.id},
                func: scrollPageDown
            });
        });
      }
      else if(data["action"] === "su"){
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            var activeTab = tabs[0];
            chrome.scripting.executeScript({
                target: {tabId: activeTab.id},
                func: scrollPageUp
            });
        });
      }
      else if(data["action"] === "zi"){
        chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            chrome.tabs.getZoom(tabs[0].id, function(zoomFactor) {
              chrome.tabs.setZoom(tabs[0].id, zoomFactor + 0.1);
            });
          });
      }
      else if(data["action"] === "zo"){
        chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            chrome.tabs.getZoom(tabs[0].id, function(zoomFactor) {
              chrome.tabs.setZoom(tabs[0].id, zoomFactor - 0.1);
            });
          });
      }
    })
    .catch((error) => {
      console.error("Send error:", error);
    });
}

pollServer();
function scrollPageDown() {
    window.scrollBy(0, 10);
}

function scrollPageUp() {
    window.scrollBy(0,-10);
}


// Optional: Create a new tab on installation or update
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === "install" || details.reason === "update") {
    chrome.tabs.create({ url: "options.html" });
  }
});
