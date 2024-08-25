chrome.contextMenus.create({
    id: "1",
    title: "Take help from AI",
    contexts: ["selection"],
});

chrome.contextMenus.onClicked.addListener(function(info, tab) {
    if (info.menuItemId === "1") {
        chrome.tabs.sendMessage(tab.id, {
            action: "showPopup",
            text: info.selectionText
        });
    }
});
