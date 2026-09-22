/**
 * frontend/script.js
 *
 * Customer Support Agent — chat UI logic.
 *
 * Connects to the FastAPI backend at POST /chat.
 * Maintains thread_id across turns for multi-turn conversation.
 * Backend URL is configurable via the BACKEND_URL constant below.
 */

'use strict';

// ── Configuration ──────────────────────────────────────────────────────────────
const BACKEND_URL = 'http://localhost:8000';
const CHAT_ENDPOINT = `${BACKEND_URL}/chat`;

// ── State ──────────────────────────────────────────────────────────────────────
let threadId = null;      // persists conversation context across turns
let isLoading = false;    // prevents double-sends

// ── DOM references ─────────────────────────────────────────────────────────────
const chatWindow      = document.getElementById('chat-window');
const typingIndicator = document.getElementById('typing-indicator');
const errorBanner     = document.getElementById('error-banner');
const errorText       = document.getElementById('error-text');
const errorCloseBtn   = document.getElementById('error-close-btn');
const userInput       = document.getElementById('user-input');
const sendBtn         = document.getElementById('send-btn');
const suggestions     = document.getElementById('suggestions');
const suggestionChips = document.querySelectorAll('.suggestion-chip');

// ── Initialisation ─────────────────────────────────────────────────────────────
userInput.addEventListener('input', onInputChange);
userInput.addEventListener('keydown', onKeyDown);
sendBtn.addEventListener('click', handleSend);
errorCloseBtn.addEventListener('click', hideError);

suggestionChips.forEach(chip => {
  chip.addEventListener('click', () => {
    const question = chip.dataset.question;
    if (!question || isLoading) return;
    userInput.value = question;
    autoResize();
    updateSendButton();
    handleSend();
  });
});

// ── Input handling ─────────────────────────────────────────────────────────────

function onInputChange() {
  autoResize();
  updateSendButton();
}

function onKeyDown(e) {
  // Send on Enter; allow Shift+Enter for newline.
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!isLoading && userInput.value.trim()) handleSend();
  }
}

function autoResize() {
  userInput.style.height = 'auto';
  userInput.style.height = userInput.scrollHeight + 'px';
}

function updateSendButton() {
  sendBtn.disabled = isLoading || !userInput.value.trim();
}

// ── Send flow ──────────────────────────────────────────────────────────────────

async function handleSend() {
  const message = userInput.value.trim();
  if (!message || isLoading) return;

  // Clear input immediately.
  userInput.value = '';
  autoResize();
  setLoading(true);
  hideError();
  hideSuggestions();

  // Render user's message.
  appendMessage('user', message);

  try {
    const data = await sendMessage(message);

    // Persist thread for multi-turn conversation.
    if (data.thread_id) threadId = data.thread_id;

    appendMessage('agent', data.reply);

  } catch (err) {
    showError(err.message || 'Could not reach the support agent. Please try again.');
  } finally {
    setLoading(false);
  }
}

// ── API call ───────────────────────────────────────────────────────────────────

async function sendMessage(message) {
  const body = { message };
  if (threadId) body.thread_id = threadId;

  const response = await fetch(CHAT_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let detail = `Server error (${response.status})`;
    try {
      const err = await response.json();
      if (err.detail) detail = err.detail;
    } catch (_) { /* ignore */ }
    throw new Error(detail);
  }

  return response.json();
}

// ── Message rendering ──────────────────────────────────────────────────────────

function appendMessage(role, text) {
  const isUser  = role === 'user';
  const wrapper = document.createElement('div');
  wrapper.className = `message message--${isUser ? 'user' : 'agent'}`;

  // Avatar
  const avatar = document.createElement('div');
  avatar.className = 'message__avatar';
  avatar.setAttribute('aria-hidden', 'true');
  avatar.textContent = isUser ? '👤' : '✦';

  // Bubble
  const bubble = document.createElement('div');
  bubble.className = 'message__bubble';

  // Render text — convert newlines to <br> and simple markdown bold (**text**).
  bubble.innerHTML = formatText(text);

  // Timestamp
  const time = document.createElement('span');
  time.className = 'message__time';
  time.textContent = formatTime(new Date());
  bubble.appendChild(time);

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  chatWindow.appendChild(wrapper);

  scrollToBottom();
}

// ── Text formatting ────────────────────────────────────────────────────────────

function formatText(raw) {
  // Strip Foundry citation markers: private-use Unicode blocks \uE200…\uE201
  // These appear as raw tokens like \uE200cite\uE202turn6:0\uE201 in RAG replies.
  let clean = raw.replace(/\uE200[\s\S]*?\uE201/g, '');

  // Escape HTML entities first to prevent XSS.
  let safe = clean
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Basic markdown: **bold**
  safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Newlines → <br>
  safe = safe.replace(/\n/g, '<br>');

  return safe;
}

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ── Loading state ──────────────────────────────────────────────────────────────

function setLoading(loading) {
  isLoading = loading;
  typingIndicator.hidden = !loading;
  updateSendButton();
  if (loading) scrollToBottom();
}

// ── Error banner ───────────────────────────────────────────────────────────────

function showError(message) {
  errorText.textContent = message;
  errorBanner.hidden = false;
  scrollToBottom();
}

function hideError() {
  errorBanner.hidden = true;
}

// ── Suggestions ────────────────────────────────────────────────────────────────

function hideSuggestions() {
  // Hide after first user interaction.
  suggestions.classList.add('suggestions--hidden');
}

// ── Scroll ─────────────────────────────────────────────────────────────────────

function scrollToBottom() {
  requestAnimationFrame(() => {
    chatWindow.scrollTop = chatWindow.scrollHeight;
  });
}
