
document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatContainer = document.getElementById('chat-container');
    const statusIndicator = document.getElementById('status-indicator');
    const settingsBtn = document.getElementById('settings-btn');
    const settingsPanel = document.getElementById('settings-panel');
    const apiBaseInput = document.getElementById('api-base');
    const saveSettingsBtn = document.getElementById('save-settings');
    const closeSettingsBtn = document.getElementById('close-settings');

    const getApiBase = () => localStorage.getItem('API_BASE') || 'http://localhost:5000';
    const setApiBase = (url) => localStorage.setItem('API_BASE', url);

    apiBaseInput.value = getApiBase();

    const setBusy = (busy) => {
        chatContainer.setAttribute('aria-busy', busy ? 'true' : 'false');
        userInput.disabled = !!busy;
        sendButton.disabled = !!busy;
    };

    const addMessage = (sender, text, withMeta = true) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
        messageDiv.textContent = text;
        if (withMeta) {
            const meta = document.createElement('span');
            meta.className = 'meta';
            meta.textContent = new Date().toLocaleTimeString();
            messageDiv.appendChild(meta);
        }
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return messageDiv;
    };

    const setStatus = (state, title) => {
        statusIndicator.classList.remove('ok', 'bad');
        if (state === 'ok') statusIndicator.classList.add('ok');
        if (state === 'bad') statusIndicator.classList.add('bad');
        statusIndicator.title = title || '';
    };

    const checkHealth = async () => {
        setStatus(null, 'Checking...');
        try {
            const res = await fetch(`${getApiBase()}/health`, { method: 'GET' });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            const loaded = data?.model_loaded === true;
            setStatus('ok', loaded ? 'API OK • Model loaded' : 'API OK • Model not loaded');
        } catch (e) {
            setStatus('bad', 'API not reachable');
        }
    };

    const sendMessage = async () => {
        const question = userInput.value.trim();
        if (!question) return;

        addMessage('user', question);
        userInput.value = '';

        const typing = addMessage('bot', '…');
        setBusy(true);
        try {
            const response = await fetch(`${getApiBase()}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });
            const data = await response.json().catch(() => ({}));
            typing.remove();
            if (response.ok && typeof data.response !== 'undefined') {
                addMessage('bot', String(data.response));
            } else {
                addMessage('bot', `Error: ${data.error || 'Something went wrong'}`);
            }
        } catch (error) {
            typing.remove();
            addMessage('bot', 'ለሰርቨሩ መገናኘት አልተቻለም። (Connection error)');
        } finally {
            setBusy(false);
            checkHealth();
        }
    };

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    settingsBtn.addEventListener('click', () => {
        settingsPanel.classList.toggle('hidden');
        settingsPanel.setAttribute('aria-hidden', settingsPanel.classList.contains('hidden') ? 'true' : 'false');
        apiBaseInput.value = getApiBase();
    });
    closeSettingsBtn.addEventListener('click', () => {
        settingsPanel.classList.add('hidden');
        settingsPanel.setAttribute('aria-hidden', 'true');
    });
    saveSettingsBtn.addEventListener('click', () => {
        const url = apiBaseInput.value.trim();
        if (url) setApiBase(url);
        settingsPanel.classList.add('hidden');
        settingsPanel.setAttribute('aria-hidden', 'true');
        checkHealth();
    });

    addMessage('bot', 'ሰላም! እንዴት ልርዳዎት እችላለሁ?');
    checkHealth();
});
