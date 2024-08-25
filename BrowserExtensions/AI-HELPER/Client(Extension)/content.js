chrome.runtime.onMessage.addListener(async function(request, sender, sendResponse) {
    if (request.action === "showPopup") {
        var question = request.text;
        const response = await fetch('https://ai-helper-server.onrender.com/getanswer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });
        data = await response.json();
        console.log(data.answer);
        showPopup(data.answer);
    }
});


function showPopup(text) {
    let existingPopup = document.getElementById("ai-helper-popup");
    if (existingPopup) {
        existingPopup.remove();
    }

    let popup = document.createElement("div");
    popup.id = "ai-helper-popup";
    popup.textContent = text;
    popup.style.position = "fixed";
    popup.style.bottom = "20px";
    popup.style.right = "20px";
    popup.style.padding = "10px";
    popup.style.backgroundColor = "#333";
    popup.style.color = "#fff";
    popup.style.borderRadius = "5px";
    popup.style.boxShadow = "0px 0px 10px rgba(0,0,0,0.5)";
    popup.style.zIndex = "1000";
    document.body.appendChild(popup);

    setTimeout(() => {
        popup.remove();
    }, 5000);
}
