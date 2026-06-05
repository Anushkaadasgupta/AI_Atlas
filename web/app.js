const state = {
  messages: [
    {
      role: "assistant",
      content:
        "Hi, I’m AI Atlas — a premium AI assistant for projects, careers, health topics, and image prompts.",
      context: "",
      provider: "fallback",
      model: "chat-latest",
      note: false,
    },
  ],
};

const elMessages = document.getElementById("messages");
const elForm = document.getElementById("chatForm");
const elInput = document.getElementById("chatInput");
const elProvider = document.getElementById("provider");
const elModel = document.getElementById("model");
const elStyle = document.getElementById("style");
const elTopk = document.getElementById("topk");
const elTopkValue = document.getElementById("topkValue");
const elClear = document.getElementById("clearChat");

function timeLabel() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function avatar(role) {
  return role === "user" ? "🤖" : "✦";
}

function fallbackReply(question) {
  const model = elModel.value || "chat-latest";
  return {
    answer:
      `Here’s a helpful fallback response for: "${question}".\n\n` +
      "I can help with planning, explaining concepts, writing prompts, and organizing ideas.",
    context:
      "Fallback mode is active because OPENAI_API_KEY is not set. The app is still responsive and ready for live model integration.",
    provider: "fallback",
    model,
  };
}

async function sendMessage(question) {
  const payload = {
    question,
    messages: state.messages.slice(-10),
    provider: elProvider.value,
    model: elModel.value || "chat-latest",
    style: elStyle.value,
    top_k: Number(elTopk.value),
  };

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("Request failed");
    return await response.json();
  } catch (error) {
    return fallbackReply(question);
  }
}

function render() {
  elMessages.innerHTML = "";
  state.messages.forEach((message) => {
    const row = document.createElement("div");
    row.className = "message";

    const avatarEl = document.createElement("div");
    avatarEl.className = `avatar ${message.role === "user" ? "user" : "ai"}`;
    avatarEl.textContent = avatar(message.role);

    const bubble = document.createElement("div");
    bubble.className = `bubble ${message.role === "user" ? "user" : "ai"}`;

    const text = document.createElement("p");
    text.textContent = message.content;
    bubble.appendChild(text);

    if (message.role === "assistant" && message.note) {
      const note = document.createElement("p");
      note.style.marginTop = "10px";
      note.style.color = "#a8b0bc";
      note.textContent = "Note: using fallback mode";
      bubble.appendChild(note);
    }

    if (message.role === "assistant" && message.context) {
      const details = document.createElement("details");
      details.className = "knowledge";
      const summary = document.createElement("summary");
      summary.textContent = "Knowledge used";
      const pre = document.createElement("pre");
      pre.textContent = message.context;
      details.append(summary, pre);
      bubble.appendChild(details);
    }

    const meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = `${timeLabel()} • ${message.model || "chat-latest"}`;
    bubble.appendChild(meta);

    row.append(avatarEl, bubble);
    elMessages.appendChild(row);
  });
  elMessages.scrollTop = elMessages.scrollHeight;
}

function clearChat() {
  state.messages = [
    {
      role: "assistant",
      content:
        "Hi, I’m AI Atlas — a premium AI assistant for projects, careers, health topics, and image prompts.",
      context: "",
      provider: "fallback",
      model: elModel.value || "chat-latest",
      note: false,
    },
  ];
  render();
}

elTopk.addEventListener("input", () => {
  elTopkValue.textContent = elTopk.value;
});

elClear.addEventListener("click", clearChat);

elForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = elInput.value.trim();
  if (!question) return;

  state.messages.push({ role: "user", content: question, model: elModel.value || "chat-latest" });
  elInput.value = "";
  render();

  const loadingId = `loading-${Date.now()}`;
  state.messages.push({
    role: "assistant",
    content: "Thinking…",
    context: "",
    model: elModel.value || "chat-latest",
    note: false,
    loading: true,
    id: loadingId,
  });
  render();

  const result = await sendMessage(question);
  state.messages = state.messages.filter((msg) => msg.id !== loadingId);
    state.messages.push({
      role: "assistant",
      content: result.answer,
      context: result.context || "",
      provider: result.provider || "fallback",
      model: result.model || elModel.value || "chat-latest",
      note: (result.provider || "fallback") === "fallback",
    });
  render();
});

render();
