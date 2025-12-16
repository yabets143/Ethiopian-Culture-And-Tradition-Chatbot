
document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatContainer = document.getElementById('chat-container');

    const addMessage = (sender, text) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
        messageDiv.textContent = text;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to the bottom
    };

    const sendMessage = async () => {
        const question = userInput.value.trim();
        if (question === '') return;

        addMessage('user', question);
        userInput.value = ''; // Clear input field

        // Placeholder for sending question to Flask API
        // This part will be completed in a later subtask
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: question })
            });
            const data = await response.json();
            if (response.ok) {
                addMessage('bot', data.response);
            } else {
                addMessage('bot', `Error: ${data.error || 'Something went wrong'}`);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage('bot', 'Sorry, I am having trouble connecting to the server.');
        }
    };

    sendButton.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    addMessage('bot', 'Hello! How can I help you today?');
});
