const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");
const chatBox = document.getElementById("chatBox");
const typing = document.getElementById("typing");

function addMessage(message, type) {
    const div = document.createElement("div");
    div.className = "message";

    if (type === "user") {
        div.classList.add("user-message");

        div.innerHTML = `
            <div class="message-content">
                <strong>You</strong>
                <p>${escapeHTML(message)}</p>
            </div>
        `;
    } else {
        div.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="message-content">
                <strong>AI Assistant</strong>
                <p>${escapeHTML(message)}</p>
            </div>
        `;
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function sendMessage() {

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    addMessage(message, "user");

    messageInput.value = "";
    sendBtn.disabled = true;
    typing.style.display = "block";

    try {

        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        if (data.answer) {
            addMessage(data.answer, "bot");
        } else {
            addMessage(
                data.error || "AI se response nahi mila.",
                "bot"
            );
        }

    } catch (error) {

        console.error(error);

        addMessage(
            "Server se connection nahi ho raha.",
            "bot"
        );
    }

    typing.style.display = "none";
    sendBtn.disabled = false;
    messageInput.focus();
}

sendBtn.addEventListener("click", sendMessage);

messageInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        sendMessage();
    }
});
