document.addEventListener("DOMContentLoaded", () => {
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const chatHistory = document.getElementById("chat-history");
    const exampleBtns = document.querySelectorAll(".example-btn");

    const retrievalStatus = document.getElementById("retrieval-status");
    const retrievalText = document.getElementById("retrieval-text");
    const loadingTexts = ["Searching official documents...", "Retrieving factsheet...", "Preparing response..."];
    let loadingInterval = null;

    let currentSessionId = null;

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Session Management
    function loadSessions() {
        const sessionsStr = localStorage.getItem('groww_sessions');
        return sessionsStr ? JSON.parse(sessionsStr) : [];
    }

    function saveSessions(sessions) {
        localStorage.setItem('groww_sessions', JSON.stringify(sessions));
    }

    // Modal state for deletion
    const deleteModal = document.getElementById('delete-modal');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    let sessionToDelete = null;

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', () => {
            if (deleteModal) deleteModal.classList.add('hidden');
            sessionToDelete = null;
        });
    }

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', () => {
            if (sessionToDelete) {
                deleteSession(sessionToDelete);
                if (deleteModal) deleteModal.classList.add('hidden');
                sessionToDelete = null;
            }
        });
    }

    function deleteSession(sessionId) {
        let sessions = loadSessions();
        sessions = sessions.filter(s => s.id !== sessionId);
        saveSessions(sessions);
        
        if (currentSessionId === sessionId) {
            startNewChat();
        } else {
            renderRecentChats();
        }
    }

    function startNewChat() {
        currentSessionId = null;
        const heroSection = document.getElementById('hero-section');
        if (heroSection) heroSection.style.display = 'flex';
        
        Array.from(chatHistory.children).forEach(child => {
            if (child.id !== 'hero-section') {
                child.remove();
            }
        });
        renderRecentChats();
    }

    function addMessageToSession(sender, data) {
        const sessions = loadSessions();
        let session = sessions.find(s => s.id === currentSessionId);
        
        if (!session) {
            currentSessionId = Date.now().toString();
            session = {
                id: currentSessionId,
                title: sender === 'user' ? data : 'New Chat',
                messages: []
            };
            sessions.unshift(session);
        }
        
        session.messages.push({ sender, data });
        saveSessions(sessions);
        renderRecentChats();
    }

    function renderRecentChats() {
        const list = document.getElementById('recent-chats-list');
        const noMsg = document.getElementById('no-chats-msg');
        if (!list) return;
        
        const sessions = loadSessions();
        if (sessions.length === 0) {
            if (noMsg) noMsg.style.display = 'block';
            Array.from(list.children).forEach(child => {
                if (child.id !== 'no-chats-msg') child.remove();
            });
            return;
        }
        
        if (noMsg) noMsg.style.display = 'none';
        
        Array.from(list.children).forEach(child => {
            if (child.id !== 'no-chats-msg') child.remove();
        });
        
        sessions.forEach(session => {
            const btn = document.createElement('button');
            const isActive = session.id === currentSessionId;
            btn.className = `group flex items-center gap-sm p-sm w-full text-left rounded-lg transition-all truncate ${isActive ? 'bg-surface-container-high text-primary' : 'text-secondary hover:bg-surface-container-high'}`;
            btn.innerHTML = `
                <span class="material-symbols-outlined text-[16px]">chat_bubble</span>
                <span class="text-label-md font-label-md truncate flex-1">${escapeHtml(session.title)}</span>
                <div class="delete-btn hidden group-hover:flex items-center justify-center p-1 rounded-md hover:bg-surface-variant ml-auto text-tertiary hover:text-error transition-colors" title="Delete chat">
                    <span class="material-symbols-outlined text-[16px]">delete</span>
                </div>
            `;
            
            const deleteBtn = btn.querySelector('.delete-btn');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    sessionToDelete = session.id;
                    if (deleteModal) deleteModal.classList.remove('hidden');
                });
            }
            
            btn.addEventListener('click', () => {
                loadChat(session.id);
            });
            list.appendChild(btn);
        });
    }

    function loadChat(sessionId) {
        const sessions = loadSessions();
        const session = sessions.find(s => s.id === sessionId);
        if (!session) return;
        
        currentSessionId = sessionId;
        
        const heroSection = document.getElementById('hero-section');
        if (heroSection) heroSection.style.display = 'none';
        
        Array.from(chatHistory.children).forEach(child => {
            if (child.id !== 'hero-section') {
                child.remove();
            }
        });
        
        session.messages.forEach(msg => {
            if (msg.sender === 'user') {
                appendUserMessage(msg.data, false);
            } else {
                appendAssistantMessage(msg.data, false);
            }
        });
        
        renderRecentChats();
    }

    // Utility functions for UI Redesign
    function formatDate(isoString) {
        if (!isoString) return 'Unknown';
        const date = new Date(isoString);
        return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    }

    function getDocumentInfo(url) {
        if (!url) return { name: 'Unknown Document', type: 'Factsheet' };
        
        // Extract scheme name from URL
        const parts = url.split('/');
        let slug = parts[parts.length - 1] || parts[parts.length - 2];
        if (!slug) return { name: 'Official Document', type: 'Factsheet' };

        // Convert slug to Title Case
        let name = slug.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        return { name: name + " Factsheet", type: "Monthly Factsheet" };
    }

    function appendUserMessage(text, save=true) {
        const heroSection = document.getElementById('hero-section');
        if (heroSection) {
            heroSection.style.display = 'none';
        }
        const userHtml = `
            <div class="flex items-start gap-md flex-row-reverse fade-in w-full mb-2">
                <div class="bg-[#006C4F] text-white rounded-[24px] rounded-tr-[4px] px-5 py-3 shadow-sm max-w-[80%]">
                    <p class="text-body-md font-body-md leading-relaxed">${escapeHtml(text)}</p>
                </div>
            </div>
        `;
        chatHistory.insertAdjacentHTML("beforeend", userHtml);
        scrollToBottom();

        if (save) {
            addMessageToSession('user', text);
        }
    }

    function appendAssistantMessage(responseObj, save=true) {
        let contentHtml = '';

        if (responseObj.status === 'error' || (responseObj.type && responseObj.type !== 'factual')) {
            // Warning or Error state
            const title = responseObj.status === 'error' ? 'System Error' : 'Out of Scope Query';
            const icon = responseObj.status === 'error' ? 'error' : 'warning';
            let answerText = escapeHtml(responseObj.answer).replace(/\n/g, '<br>');
            
            contentHtml = `
                <div class="flex flex-col gap-sm max-w-[80%] w-full fade-in">
                    <div class="bg-[#FFF8E1] border-l-4 border-[#FFB300] p-md rounded-r-lg flex items-start gap-sm shadow-sm">
                        <span class="material-symbols-outlined text-[#F57C00] mt-1" style="font-variation-settings: 'FILL' 1;">${icon}</span>
                        <div>
                            <h3 class="text-label-md font-label-md font-bold text-[#E65100] mb-1">${title}</h3>
                            <p class="text-body-sm font-body-sm text-[#E65100]">${answerText}</p>
                        </div>
                    </div>
                </div>
            `;
        } else {
            // Factual state - Structured Card Redesign
            // Strip raw appended text from answer
            let rawAnswer = responseObj.answer;
            if (rawAnswer.includes("Source:")) {
                rawAnswer = rawAnswer.split("Source:")[0].trim();
            }
            let pureAnswerText = escapeHtml(rawAnswer).replace(/\n/g, '<br>');
            
            const docInfo = getDocumentInfo(responseObj.source_url);
            const dateStr = formatDate(responseObj.last_updated);
            
            let metadataHtml = '';
            if (responseObj.source_url) {
                metadataHtml = `
                    <div class="h-px w-full bg-outline-variant/40 my-3"></div>
                    <div class="flex justify-between items-center gap-4 text-[12px]">
                        <div class="flex flex-col gap-0.5 overflow-hidden">
                            <span class="text-secondary font-semibold uppercase tracking-wider text-[9px]">Official Source</span>
                            <a href="${responseObj.source_url}" target="_blank" class="text-primary hover:text-primary-fixed-dim font-semibold transition-colors flex items-center gap-1 group">
                                <span class="truncate" title="${docInfo.name}">${docInfo.name}</span>
                                <span class="material-symbols-outlined text-[13px] group-hover:-translate-y-0.5 group-hover:translate-x-0.5 transition-transform">arrow_outward</span>
                            </a>
                        </div>
                        <div class="flex flex-col gap-0.5 text-right shrink-0">
                            <span class="text-secondary font-semibold uppercase tracking-wider text-[9px]">Updated</span>
                            <span class="text-on-surface-variant font-medium">${dateStr}</span>
                        </div>
                    </div>
                `;
            }

            contentHtml = `
                <div class="bg-surface-container-lowest border border-outline-variant/40 rounded-[24px] rounded-tl-[4px] p-4 shadow-sm fade-in w-full max-w-[90%]">
                    <p class="text-body-md font-body-md text-on-surface leading-snug">${pureAnswerText}</p>
                    ${metadataHtml}
                </div>
            `;
        }

        const assistantHtml = `
            <div class="flex items-start gap-md w-full fade-in mb-4">
                <div class="w-8 h-8 rounded-full bg-primary-container flex-shrink-0 flex items-center justify-center shadow-sm mt-1">
                    <span class="material-symbols-outlined text-[18px] text-on-primary-container">smart_toy</span>
                </div>
                ${contentHtml}
            </div>
        `;
        chatHistory.insertAdjacentHTML("beforeend", assistantHtml);
        scrollToBottom();

        if (save) {
            addMessageToSession('assistant', responseObj);
        }
    }

    function showLoading() {
        if(retrievalStatus) {
            retrievalStatus.classList.remove('hidden');
            let idx = 0;
            retrievalText.innerText = loadingTexts[0];
            loadingInterval = setInterval(() => {
                idx = (idx + 1) % loadingTexts.length;
                retrievalText.innerText = loadingTexts[idx];
            }, 1500);
        }
    }

    function hideLoading() {
        if(retrievalStatus) {
            retrievalStatus.classList.add('hidden');
        }
        if (loadingInterval) {
            clearInterval(loadingInterval);
            loadingInterval = null;
        }
    }

    async function sendQuery(query) {
        if (!query.trim()) return;
        
        chatInput.value = "";
        appendUserMessage(query);
        showLoading();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            hideLoading();
            appendAssistantMessage(data);
        } catch (error) {
            hideLoading();
            appendAssistantMessage({
                status: "error",
                type: "internal_error",
                answer: "Failed to connect to the server."
            });
        }
    }

    sendBtn.addEventListener("click", () => {
        sendQuery(chatInput.value);
    });

    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            sendQuery(chatInput.value);
        }
    });

    exampleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const queryText = btn.querySelector('.truncate').innerText;
            sendQuery(queryText);
        });
    });

    document.querySelectorAll(".hero-chip-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            sendQuery(btn.innerText);
        });
    });

    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', startNewChat);
    }

    // Initialize sidebar
    renderRecentChats();

    // Utility
    function escapeHtml(unsafe) {
        if (!unsafe) return "";
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }

    // Add basic fade-in style
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 0.3s ease-out forwards;
        }
    `;
    document.head.appendChild(style);
});
