// ============================================================================
// GENOX AUTONOMOUS OMNI-AGENT COMMAND CENTER — v3.1.0
// ============================================================================

let ws = null;
let isExecuting = false;
let voiceEnabled = true;
let currentAgentTurnEl = null;
let audioCtx = null;

// DOM Elements
const liveClock = document.getElementById("liveClock");
const liveDate = document.getElementById("liveDate");
const systemStatusLabel = document.getElementById("systemStatusLabel");
const statusCapsule = document.getElementById("statusCapsule");
const memoryMetricVal = document.getElementById("memoryMetricVal");
const engineMetricVal = document.getElementById("engineMetricVal");
const toolsCountBadge = document.getElementById("toolsCountBadge");

const btnModeSphere = document.getElementById("btnModeSphere");
const btnModeAvatar = document.getElementById("btnModeAvatar");
const coreSphereCanvas = document.getElementById("coreSphereCanvas");
const avatarFaceContainer = document.getElementById("avatarFaceContainer");
const coreTitleText = document.getElementById("coreTitleText");
const coreSubtitleText = document.getElementById("coreSubtitleText");

const wakeWordToggleBtn = document.getElementById("wakeWordToggleBtn");
const wakeWordLabel = document.getElementById("wakeWordLabel");
const wakeWordStationCard = document.getElementById("wakeWordStationCard");
const voiceToggleBtn = document.getElementById("voiceToggleBtn");
const voiceIcon = document.getElementById("voiceIcon");
const voiceLabel = document.getElementById("voiceLabel");
const voiceStation = document.getElementById("voiceStation");
const sidebarMicBtn = document.getElementById("sidebarMicBtn");
const speechStateLabel = document.getElementById("speechStateLabel");

const promptInput = document.getElementById("promptInput");
const sendBtn = document.getElementById("sendBtn");
const sendBtnText = document.getElementById("sendBtnText");
const micBtn = document.getElementById("micBtn");

const reasoningDrawer = document.getElementById("reasoningDrawer");
const drawerContent = document.getElementById("drawerContent");
const closeDrawerBtn = document.getElementById("closeDrawerBtn");
const clearDrawerBtn = document.getElementById("clearDrawerBtn");

const settingsBtn = document.getElementById("settingsBtn");
const configModal = document.getElementById("configModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const saveConfigBtn = document.getElementById("saveConfigBtn");
const apiKeyInput = document.getElementById("apiKeyInput");
const modelSelect = document.getElementById("modelSelect");

const filePreviewModal = document.getElementById("filePreviewModal");
const previewFileName = document.getElementById("previewFileName");
const previewFileContent = document.getElementById("previewFileContent");
const closePreviewBtn = document.getElementById("closePreviewBtn");
const missionTimelineList = document.getElementById("missionTimelineList");

// Drawer Panes & Dynamic Lists
const drawerFilesList = document.getElementById("drawerFilesList");
const drawerMemoryList = document.getElementById("drawerMemoryList");
const drawerToolsList = document.getElementById("drawerToolsList");
const drawerHistoryList = document.getElementById("drawerHistoryList");
const refreshFilesBtn = document.getElementById("refreshFilesBtn");
const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");
const addMemoryBtn = document.getElementById("addMemoryBtn");
const newMemKey = document.getElementById("newMemKey");
const newMemVal = document.getElementById("newMemVal");

/* ==========================================================================
   1. LIVE DIGITAL CLOCK & DATE TICKER
   ========================================================================== */
function updateClock() {
  const now = new Date();
  const timeStr = now.toLocaleTimeString("en-US", { hour12: true });
  const dateStr = now.toLocaleDateString("en-US", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  
  if (liveClock) liveClock.textContent = timeStr.toUpperCase();
  if (liveDate) liveDate.textContent = dateStr.toUpperCase();
}
setInterval(updateClock, 1000);
updateClock();

/* ==========================================================================
   2. 3D NEURAL PARTICLE WAVE BACKGROUND (REFERENCE 2 REPRODUCTION)
   ========================================================================== */
function initNeuralParticleWave() {
  const canvas = document.getElementById("particleCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener("resize", () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const cols = 26;
  const rows = 13;
  const spacingX = 85;
  const spacingZ = 75;
  let waveTime = 0;
  let mouseX = width / 2;
  let mouseY = height / 2;

  window.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  function renderWave() {
    if (document.hidden) {
      requestAnimationFrame(renderWave);
      return;
    }

    ctx.clearRect(0, 0, width, height);
    waveTime += 0.022;

    const centerX = width / 2;
    const centerY = height * 0.72;
    const fov = 340;
    const grid = [];

    // Compute 3D coords with multi-frequency undulating wave
    for (let r = 0; r < rows; r++) {
      grid[r] = [];
      const z3d = (r + 4) * spacingZ;
      const scale = fov / (fov + z3d);
      const alpha = Math.min(1, Math.max(0.1, (rows - r * 0.7) / rows));

      for (let c = 0; c < cols; c++) {
        const x3d = (c - cols / 2) * spacingX;
        const mouseEffect = Math.sin((x3d - (mouseX - centerX)) * 0.005) * 8;
        const y3d =
          Math.sin(c * 0.22 + waveTime) * 36 +
          Math.cos(r * 0.28 + waveTime * 0.8) * 28 +
          Math.sin((c + r) * 0.15 + waveTime * 0.6) * 18 +
          mouseEffect;

        const px = centerX + x3d * scale;
        const py = centerY + (y3d - 40) * scale;
        grid[r][c] = { x: px, y: py, alpha, scale };
      }
    }

    // Interconnect lines along wave rows
    ctx.lineWidth = 0.8;
    for (let r = 0; r < rows; r++) {
      ctx.beginPath();
      for (let c = 0; c < cols; c++) {
        const p = grid[r][c];
        if (c === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      }
      ctx.strokeStyle = `rgba(0, 180, 255, ${grid[r][0].alpha * 0.16})`;
      ctx.stroke();
    }

    // Column crest lines
    for (let c = 0; c < cols; c += 2) {
      ctx.beginPath();
      for (let r = 0; r < rows; r++) {
        const p = grid[r][c];
        if (r === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      }
      ctx.strokeStyle = `rgba(0, 240, 255, ${grid[0][c].alpha * 0.12})`;
      ctx.stroke();
    }

    // Crisp high-speed glowing nodes without shadowBlur lag
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const p = grid[r][c];
        const rad = Math.max(1.0, p.scale * 2.2);

        // Soft outer glow
        ctx.beginPath();
        ctx.arc(p.x, p.y, rad * 2.2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 240, 255, ${p.alpha * 0.22})`;
        ctx.fill();

        // Bright inner core
        ctx.beginPath();
        ctx.arc(p.x, p.y, rad * 0.9, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(200, 255, 255, ${p.alpha * 0.95})`;
        ctx.fill();
      }
    }

    requestAnimationFrame(renderWave);
  }

  renderWave();
}

/* ==========================================================================
   3. 3D HOLOGRAPHIC AI CORE SPHERE (CANVAS 3D MATH)
   ========================================================================== */
let sphereAngleX = 0;
let sphereAngleY = 0;

function init3DSphere() {
  if (!coreSphereCanvas) return;
  const ctx = coreSphereCanvas.getContext("2d");
  const size = (coreSphereCanvas.width = coreSphereCanvas.height = 220);
  const radius = 68;
  const cx = size / 2;
  const cy = size / 2;

  const points = [];
  const rings = 10;
  const segments = 18;

  for (let i = 0; i < rings; i++) {
    const theta = (i * Math.PI) / (rings - 1);
    for (let j = 0; j < segments; j++) {
      const phi = (j * 2 * Math.PI) / segments;
      const x = radius * Math.sin(theta) * Math.cos(phi);
      const y = radius * Math.sin(theta) * Math.sin(phi);
      const z = radius * Math.cos(theta);
      points.push({ x, y, z });
    }
  }

  function renderSphere() {
    ctx.clearRect(0, 0, size, size);

    sphereAngleX += 0.008;
    sphereAngleY += 0.012;

    const cosX = Math.cos(sphereAngleX);
    const sinX = Math.sin(sphereAngleX);
    const cosY = Math.cos(sphereAngleY);
    const sinY = Math.sin(sphereAngleY);

    const projected = [];

    for (const p of points) {
      const x1 = p.x * cosY + p.z * sinY;
      const z1 = -p.x * sinY + p.z * cosY;

      const y2 = p.y * cosX - z1 * sinX;
      const z2 = p.y * sinX + z1 * cosX;

      const scale = 240 / (240 + z2);
      const px = cx + x1 * scale;
      const py = cy + y2 * scale;
      const alpha = (z2 + radius) / (2 * radius);

      projected.push({ x: px, y: py, alpha: Math.max(0.1, alpha), z: z2 });
    }

    ctx.strokeStyle = "rgba(0, 240, 255, 0.16)";
    ctx.lineWidth = 0.8;
    for (let i = 0; i < projected.length; i++) {
      if ((i + 1) % segments !== 0 && projected[i + 1]) {
        ctx.beginPath();
        ctx.moveTo(projected[i].x, projected[i].y);
        ctx.lineTo(projected[i + 1].x, projected[i + 1].y);
        ctx.stroke();
      }
    }

    for (const p of projected) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, 1.4, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, 240, 255, ${p.alpha * 0.9})`;
      ctx.fill();
    }

    // Outer orbital ring
    ctx.beginPath();
    ctx.ellipse(cx, cy, radius * 1.25, radius * 0.45, sphereAngleX * 0.5, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(0, 240, 255, 0.35)";
    ctx.lineWidth = 1.2;
    ctx.stroke();

    if (!document.hidden) {
      requestAnimationFrame(renderSphere);
    } else {
      setTimeout(() => requestAnimationFrame(renderSphere), 1000);
    }
  }

  renderSphere();
}

/* ==========================================================================
   4. VIEWPORT MODE SWITCHER (3D CORE vs TALKING AVATAR FACE)
   ========================================================================== */
function setViewportMode(mode) {
  if (mode === "avatar") {
    btnModeAvatar.classList.add("active");
    btnModeSphere.classList.remove("active");
    coreSphereCanvas.style.display = "none";
    avatarFaceContainer.classList.add("active");
    coreTitleText.textContent = "GENOX AVATAR";
    if (coreSubtitleText) coreSubtitleText.textContent = "CYBERNETIC INTERFACE ONLINE";
  } else {
    btnModeSphere.classList.add("active");
    btnModeAvatar.classList.remove("active");
    coreSphereCanvas.style.display = "block";
    avatarFaceContainer.classList.remove("active");
    coreTitleText.textContent = "GENOX";
    if (coreSubtitleText) coreSubtitleText.textContent = "AI CORE v3.1";
  }
}

btnModeSphere.addEventListener("click", () => setViewportMode("sphere"));
btnModeAvatar.addEventListener("click", () => setViewportMode("avatar"));

/* ==========================================================================
   5. SCI-FI AUDIO CHIMES (WEB AUDIO API SYNTHESIZER)
   ========================================================================== */
function playAudioChime(type) {
  if (!voiceEnabled) return;
  try {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === "suspended") {
      audioCtx.resume();
    }

    const now = audioCtx.currentTime;

    if (type === "wake") {
      // High-tech Siri-style activation chime (D5 -> A5 rising dual tone)
      const osc1 = audioCtx.createOscillator();
      const osc2 = audioCtx.createOscillator();
      const gain = audioCtx.createGain();

      osc1.type = "sine";
      osc1.frequency.setValueAtTime(587.33, now); // D5
      osc1.frequency.setValueAtTime(880.0, now + 0.08); // A5

      osc2.type = "triangle";
      osc2.frequency.setValueAtTime(1174.66, now + 0.08); // Harmonic

      gain.gain.setValueAtTime(0.09, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(audioCtx.destination);

      osc1.start(now);
      osc2.start(now + 0.08);
      osc1.stop(now + 0.35);
      osc2.stop(now + 0.35);

    } else if (type === "dispatch") {
      // Pleasant futuristic dual-tone ping
      const osc1 = audioCtx.createOscillator();
      const osc2 = audioCtx.createOscillator();
      const gain = audioCtx.createGain();

      osc1.type = "sine";
      osc1.frequency.setValueAtTime(540, now);
      osc1.frequency.exponentialRampToValueAtTime(840, now + 0.12);

      osc2.type = "triangle";
      osc2.frequency.setValueAtTime(1080, now);
      osc2.frequency.exponentialRampToValueAtTime(1620, now + 0.14);

      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(audioCtx.destination);

      osc1.start(now);
      osc2.start(now);
      osc1.stop(now + 0.22);
      osc2.stop(now + 0.22);

    } else if (type === "complete") {
      // Harmonious affirmative chord
      const freqs = [523.25, 659.25, 783.99, 1046.5]; // C Major
      freqs.forEach((freq, idx) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, now + idx * 0.06);

        gain.gain.setValueAtTime(0.06, now + idx * 0.06);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35 + idx * 0.06);

        osc.connect(gain);
        gain.connect(audioCtx.destination);

        osc.start(now + idx * 0.06);
        osc.stop(now + 0.4 + idx * 0.06);
      });
    }
  } catch (err) {
    console.warn("Audio chime error:", err);
  }
}

/* ==========================================================================
   6. REAL-TIME MACOS SYSTEM TELEMETRY (CPU, RAM, DISK)
   ========================================================================== */
async function pollSystemStats() {
  try {
    const res = await fetch("/api/system-stats");
    if (!res.ok) return;
    const data = await res.json();

    const cpuVal = data.cpu || 0;
    const memVal = data.memory || 0;
    const diskVal = data.disk || 0;

    const gauges = document.querySelectorAll(".radial-gauge-item");
    if (gauges.length >= 3) {
      // CPU
      const cpuCircle = gauges[0].querySelector(".gauge-fill");
      const cpuText = gauges[0].querySelector(".gauge-val-text");
      if (cpuCircle) cpuCircle.style.strokeDashoffset = 150 - (150 * cpuVal) / 100;
      if (cpuText) cpuText.textContent = `${Math.round(cpuVal)}%`;

      // Memory
      const memCircle = gauges[1].querySelector(".gauge-fill");
      const memText = gauges[1].querySelector(".gauge-val-text");
      if (memCircle) memCircle.style.strokeDashoffset = 150 - (150 * memVal) / 100;
      if (memText) memText.textContent = `${Math.round(memVal)}%`;

      // Storage
      const diskCircle = gauges[2].querySelector(".gauge-fill");
      const diskText = gauges[2].querySelector(".gauge-val-text");
      if (diskCircle) diskCircle.style.strokeDashoffset = 150 - (150 * diskVal) / 100;
      if (diskText) diskText.textContent = `${Math.round(diskVal)}%`;
    }
  } catch (err) {
    // Non-blocking
  }
}
setInterval(() => {
  if (!document.hidden) pollSystemStats();
}, 7000);
pollSystemStats();

/* ==========================================================================
   7. WEBSOCKET REAL-TIME CONNECTION
   ========================================================================== */
function initWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("[Genox] Telemetry link established.");
    checkSystemStatus();
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleAgentEvent(data);
    } catch (err) {
      console.error("[Genox] Message parsing error:", err);
    }
  };

  ws.onclose = () => {
    console.warn("[Genox] Telemetry connection lost. Reconnecting in 3s...");
    setTimeout(initWebSocket, 3000);
  };
}

async function checkSystemStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    if (data.api_key_configured) {
      systemStatusLabel.textContent = "SYSTEM STATUS: OPTIMAL";
      if (statusCapsule) statusCapsule.style.borderColor = "var(--border-subtle)";
      if (engineMetricVal) engineMetricVal.textContent = data.model.toUpperCase();
      if (memoryMetricVal) memoryMetricVal.textContent = `${data.memories_count} STORED`;
      if (toolsCountBadge) toolsCountBadge.textContent = data.total_tools;
    } else {
      systemStatusLabel.textContent = "API KEY REQUIRED";
      if (statusCapsule) statusCapsule.style.borderColor = "var(--accent-crimson)";
      openConfigModal();
    }
  } catch (err) {
    console.error("Status check failed:", err);
  }
}

/* ==========================================================================
   8. TASK DISPATCH & REASONING DRAWER
   ========================================================================== */
function dispatchPrompt(text) {
  const prompt = text || promptInput.value.trim();
  if (!prompt || isExecuting) return;

  // Clear patient listening state and timers if active
  if (isPatientListening) {
    isPatientListening = false;
    if (patientSilenceTimer) clearTimeout(patientSilenceTimer);
    if (patientCountdownTimer) clearInterval(patientCountdownTimer);
  }
  accumulatedTranscript = "";
  patientListeningStartIndex = 0;

  // Reset speech recognition session cleanly to wipe continuous buffer
  if (wakeRecognition && wakeRecognitionActive) {
    try {
      wakeRecognition.stop();
    } catch (e) {}
    wakeRecognitionActive = false;
  }

  // Open drawer to Stream pane
  openDrawer();
  switchDrawerPane("paneStream");

  // Switch center view to Avatar Face
  setViewportMode("avatar");

  // Play dispatch sound
  playAudioChime("dispatch");

  // Visual feedback: Update subtitle and command dock
  if (coreSubtitleText) coreSubtitleText.textContent = `[ DISPATCHED: "${prompt.slice(0, 40)}" ]`;

  // Create Turn Container in Drawer
  currentAgentTurnEl = createDrawerTurnContainer(prompt);

  if (ws && ws.readyState === WebSocket.OPEN) {
    setExecutingState(true);
    ws.send(JSON.stringify({
      action: "execute",
      prompt: prompt,
      max_steps: 15
    }));
  } else {
    appendDrawerEvent(currentAgentTurnEl, "error", "COMMUNICATION FAILURE", "WebSocket disconnected.");
  }

  promptInput.value = "";
}

function openDrawer() {
  reasoningDrawer.classList.add("open");
}
function closeDrawer() {
  reasoningDrawer.classList.remove("open");
}

closeDrawerBtn.addEventListener("click", closeDrawer);
clearDrawerBtn.addEventListener("click", () => {
  drawerContent.innerHTML = "";
});

// Drawer Pane Switching Logic
function switchDrawerPane(paneId) {
  document.querySelectorAll(".drawer-tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.pane === paneId);
  });
  document.querySelectorAll(".drawer-pane").forEach(pane => {
    pane.classList.toggle("active", pane.id === paneId);
  });

  if (paneId === "paneFiles") loadWorkspaceFiles();
  else if (paneId === "paneMemory") loadMemories();
  else if (paneId === "paneTools") loadTools();
  else if (paneId === "paneHistory") loadHistory();
}

document.querySelectorAll(".drawer-tab-btn").forEach(btn => {
  btn.addEventListener("click", () => switchDrawerPane(btn.dataset.pane));
});

function handleAgentEvent(data) {
  if (!currentAgentTurnEl) return;

  switch (data.type) {
    case "status":
      break;

    case "thought":
      appendDrawerEvent(currentAgentTurnEl, "thought", "🧠 COGNITIVE REASONING", data.content);
      break;

    case "open_url":
      if (data.url) {
        console.log("[Genox] Opening URL in browser tab:", data.url);
        window.open(data.url, "_blank");
      }
      break;

    case "tool_call":
      triggerAgentSquadHighlight(data.tool);
      // Auto-launch target URL directly in user's browser client
      if (data.url) {
        console.log("[Genox] Auto-launching target URL:", data.url);
        window.open(data.url, "_blank");
      } else if (data.args && data.args.command && typeof data.args.command === "string") {
        const urlMatch = data.args.command.match(/open\s+"(https?:\/\/[^"]+)"/);
        if (urlMatch && urlMatch[1]) {
          console.log("[Genox] Auto-launching extracted URL:", urlMatch[1]);
          window.open(urlMatch[1], "_blank");
        }
      }
      appendDrawerEvent(
        currentAgentTurnEl,
        "tool-call",
        `⚙️ TOOL DISPATCH: ${data.tool.toUpperCase()}`,
        JSON.stringify(data.args, null, 2),
        true
      );
      break;

    case "tool_result":
      appendDrawerEvent(
        currentAgentTurnEl,
        "tool-result",
        `✓ OBSERVATION: ${data.tool.toUpperCase()}`,
        data.output,
        true
      );
      break;

    case "final_response":
      renderDrawerFinalResponse(currentAgentTurnEl, data.content);
      resetAgentSquadHighlights();
      playAudioChime("complete");
      if (voiceEnabled) {
        speakResponse(data.content);
      }
      break;

    case "error":
      appendDrawerEvent(currentAgentTurnEl, "error", "⚠️ ALERT", data.message);
      setExecutingState(false);
      resetAgentSquadHighlights();
      break;

    case "complete":
      setExecutingState(false);
      resetAgentSquadHighlights();
      checkSystemStatus();
      logMissionAudit(currentAgentTurnEl.dataset.prompt);
      break;
  }

  scrollDrawerToBottom();
}

function scrollDrawerToBottom() {
  if (drawerContent) drawerContent.scrollTop = drawerContent.scrollHeight;
  const pane = document.getElementById("paneStream");
  if (pane) pane.scrollTop = pane.scrollHeight;
}

function createDrawerTurnContainer(prompt) {
  const turn = document.createElement("div");
  turn.className = "agent-turn-wrapper";
  turn.dataset.prompt = prompt;
  turn.innerHTML = `
    <div style="background: rgba(0, 240, 255, 0.1); border: 1px solid var(--accent-cyan); padding: 12px 18px; border-radius: var(--radius-md); font-weight: 600; margin-bottom: 12px;">
      <span style="color: var(--accent-cyan); margin-right: 8px;">USER DISPATCH:</span> ${escapeHtml(prompt)}
    </div>
    <div class="turn-events-list"></div>
  `;
  drawerContent.appendChild(turn);
  scrollDrawerToBottom();
  return turn;
}

function appendDrawerEvent(turnEl, type, title, content, isCode = false) {
  const list = turnEl.querySelector(".turn-events-list");
  if (!list) return;

  const card = document.createElement("div");
  card.className = `event-card ${type}`;

  const bodyContent = isCode
    ? `<div class="code-box">${escapeHtml(content)}</div>`
    : `<div class="event-card-body">${escapeHtml(content)}</div>`;

  card.innerHTML = `
    <div class="event-card-header"><span>${escapeHtml(title)}</span></div>
    ${bodyContent}
  `;
  list.appendChild(card);
  scrollDrawerToBottom();
}

function renderDrawerFinalResponse(turnEl, markdownText) {
  const list = turnEl.querySelector(".turn-events-list");
  const finalCard = document.createElement("div");
  finalCard.className = "final-output-card";
  finalCard.innerHTML = window.marked ? marked.parse(markdownText) : `<p>${escapeHtml(markdownText)}</p>`;
  list.appendChild(finalCard);
  scrollDrawerToBottom();
}

function setExecutingState(executing) {
  isExecuting = executing;
  sendBtn.disabled = executing;
  sendBtnText.textContent = executing ? "PROCESSING..." : "DISPATCH";
  if (executing) {
    // While executing, stop mic listener to prevent feedback or audio loop
    if (wakeRecognition && wakeRecognitionActive) {
      try { wakeRecognition.stop(); } catch (e) {}
      wakeRecognitionActive = false;
    }
  } else {
    // Execution completed, restart a clean wake recognition session from index 0
    if (wakeWordEnabled && !wakeRecognitionActive && !isGenoxSpeaking) {
      setTimeout(startWakeRecognition, 400);
    }
  }
}

/* ==========================================================================
   9. AGENT SQUAD HIGHLIGHT SYNCHRONIZATION
   ========================================================================== */
function triggerAgentSquadHighlight(toolName) {
  resetAgentSquadHighlights();
  let cardId = null;

  if (toolName.includes("python")) cardId = "agentCardCoding";
  else if (toolName.includes("search")) cardId = "agentCardResearch";
  else if (toolName.includes("web") || toolName.includes("scrape")) cardId = "agentCardBrowser";
  else if (toolName.includes("bash") || toolName.includes("shell") || toolName.includes("terminal")) cardId = "agentCardSystem";
  else if (toolName.includes("screen") || toolName.includes("image")) cardId = "agentCardVision";
  else if (toolName.includes("memory")) cardId = "agentCardMemory";

  if (cardId) {
    const card = document.getElementById(cardId);
    if (card) card.classList.add("active-state");
  }
}

function resetAgentSquadHighlights() {
  document.querySelectorAll(".agent-squad-card").forEach(c => c.classList.remove("active-state"));
}

/* ==========================================================================
   10. VOICE SYNTHESIS & TALKING AVATAR SYNCHRONIZATION
   ========================================================================== */
let isGenoxSpeaking = false;

function speakResponse(text) {
  if (!window.speechSynthesis || !voiceEnabled) return;

  const clean = text
    .replace(/[*_#`[\]()]/g, "")
    .replace(/https?:\/\/\S+/g, "link")
    .slice(0, 360);

  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.rate = 1.05;
  utterance.pitch = 0.95;

  const voices = window.speechSynthesis.getVoices();
  const genoxVoice = voices.find(
    v => v.lang.startsWith("en") && (v.name.includes("Daniel") || v.name.includes("Alex") || v.name.includes("Google") || v.name.includes("Natural"))
  );
  if (genoxVoice) utterance.voice = genoxVoice;

  utterance.onstart = () => {
    isGenoxSpeaking = true;
    if (avatarFaceContainer) avatarFaceContainer.classList.add("speaking");
    if (voiceStation) voiceStation.classList.add("speaking");
    if (sidebarMicBtn) sidebarMicBtn.classList.add("speaking");
    if (coreSubtitleText) coreSubtitleText.textContent = "[ SPEAKING: GENOX ACTIVE ]";
  };

  utterance.onend = () => {
    if (avatarFaceContainer) avatarFaceContainer.classList.remove("speaking");
    if (voiceStation) voiceStation.classList.remove("speaking");
    if (sidebarMicBtn) sidebarMicBtn.classList.remove("speaking");
    if (coreSubtitleText) coreSubtitleText.textContent = "CYBERNETIC INTERFACE ONLINE";
    setTimeout(() => {
      isGenoxSpeaking = false;
      if (wakeWordEnabled && !wakeRecognitionActive && !isExecuting) {
        startWakeRecognition();
      }
    }, 350);
  };

  utterance.onerror = () => {
    if (avatarFaceContainer) avatarFaceContainer.classList.remove("speaking");
    if (voiceStation) voiceStation.classList.remove("speaking");
    if (sidebarMicBtn) sidebarMicBtn.classList.remove("speaking");
    if (coreSubtitleText) coreSubtitleText.textContent = "AI CORE v3.1";
    setTimeout(() => {
      isGenoxSpeaking = false;
      if (wakeWordEnabled && !wakeRecognitionActive && !isExecuting) {
        startWakeRecognition();
      }
    }, 350);
  };

  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

/* ==========================================================================
   11. REAL-TIME WAKE WORD ENGINE ("HEY GENOX" LIKE SIRI)
   ========================================================================== */
let wakeWordEnabled = true;
let isAwaitingFollowUp = false;
let wakeRecognition = null;
let manualRecognition = null;
let wakeDebounceTimer = null;
let wakeWatchdogTimer = null;
let wakeRecognitionActive = false;
let hearingResetTimer = null;

// Patient Listening Mode State (Replies "Yes", patiently accumulates speech, and runs after 5s silence)
let isPatientListening = false;
let patientSilenceTimer = null;
let patientCountdownTimer = null;
let silenceSecondsRemaining = 5;
let accumulatedTranscript = "";
let patientListeningStartIndex = 0;

// Audio visualizer variables
let micMediaStream = null;
let micAudioAnalyser = null;
let micDataBuffer = null;

// Elements
const voiceHearingPill = document.getElementById("voiceHearingPill");
const voiceHearingText = document.getElementById("voiceHearingText");

// Comprehensive phonetic variations of "Genox" across all accents and STT interpretations
const WAKE_WORD_REGEX = /(?:hey\s+|hi\s+|hello\s+|ok\s+|yo\s+|a\s+|the\s+|they\s+|day\s+)?\b(genox|gen[\s\-_]*ox|geox|ge[\s\-_]*ox|geo[\s\-_]*x|giox|gio[\s\-_]*x|geonox|geenox|gee[\s\-_]*nox|jenox|jen[\s\-_]*ox|janox|xenox|zenox|inox|ginox|gnox|g[\s\-_]*nox|gen[\s\-_]*x|genx|denox|danox|kenox|knox|knocks|knock|lenox|lennox|linux|djenox|djinox|janice|janis|giannis|genetics|genesis|dmx|d[\s\-_]*max|dmax|jarvis|genius|phoenix|onyx|geno|jeno|genie|jeenox|jay[\s\-_]*nox|jay[\s\-_]*knocks|j[\s\-_]*knocks|j[\s\-_]*nox|can[\s\-_]*ox|can[\s\-_]*knocks|next|locks|lock)\b/i;

const WAKE_WORD_GLOBAL_REGEX = new RegExp(WAKE_WORD_REGEX.source, "gi");

const ACTION_REGEX = /\b(open|launch|start|run|go\s+to|visit|search(?:\s+for)?|play|what\s+time|what'?s\s+the\s+time|today'?s\s+date|what\s+date|battery(?:\s+level)?|mute|unmute)\b/i;

function cleanSpokenTask(text) {
  if (!text || typeof text !== "string") return "";
  let raw = text.trim();

  // If text contains multiple wake words, extract the segment after the LAST wake word!
  const matches = [...raw.matchAll(WAKE_WORD_GLOBAL_REGEX)];
  if (matches.length > 1) {
    const lastMatch = matches[matches.length - 1];
    raw = raw.slice(lastMatch.index + lastMatch[0].length).trim();
  }

  // 1. Strip all wake words globally
  let cleaned = raw.replace(WAKE_WORD_GLOBAL_REGEX, "").trim();
  // 2. Remove leading polite fillers
  cleaned = cleaned.replace(/^(?:please|can\s+you|could\s+you|will\s+you|just|the)\s+/i, "");
  // 3. Deduplicate repeated consecutive phrases (e.g. "open youtube open youtube" -> "open youtube")
  cleaned = cleaned.replace(/\b([a-zA-Z0-9\s]{3,})\s+\1\b/gi, (match, p1) => p1.trim());
  return cleaned.trim();
}

function parseSpokenIntent(rawText) {
  if (!rawText || typeof rawText !== "string") return null;
  const text = rawText.trim();
  if (!text) return null;

  // 1. Check for wake word ("Genox" and all phonetic variants)
  const wakeMatch = text.match(WAKE_WORD_REGEX);
  if (wakeMatch) {
    const wakeIndex = wakeMatch.index;
    const wakeLength = wakeMatch[0].length;
    let after = text.slice(wakeIndex + wakeLength).replace(/^[,\.\:\-\s]+/, "").trim();
    let before = text.slice(0, wakeIndex).replace(/[,\.\:\-\s]+$/, "").trim();
    after = after.replace(/^(?:please|can\s+you|could\s+you|will\s+you|just|the)\s+/i, "");
    const command = after || (before.length > 3 ? before : "");
    return {
      type: "wake",
      isWake: true,
      matchedWord: wakeMatch[0],
      command: command,
      raw: text
    };
  }

  // 2. Direct action match anywhere in text (e.g. "open youtube", "can you open spotify")
  const actionMatch = text.match(ACTION_REGEX);
  if (actionMatch) {
    const actionIndex = actionMatch.index;
    let command = text.slice(actionIndex).trim();
    return {
      type: "action",
      isWake: false,
      matchedWord: actionMatch[0],
      command: command,
      raw: text
    };
  }

  return null;
}

function updateHearingHud(text, state = "normal") {
  if (!voiceHearingText) return;
  voiceHearingText.textContent = text;
  if (voiceHearingPill) {
    voiceHearingPill.classList.toggle("hearing", state === "hearing");
    voiceHearingPill.classList.toggle("wake-hit", state === "wake-hit");
  }

  if (hearingResetTimer) clearTimeout(hearingResetTimer);
  // Do NOT reset HUD if in patient listening mode
  if (state !== "normal" && !isPatientListening) {
    hearingResetTimer = setTimeout(() => {
      if (voiceHearingText && !isPatientListening) {
        voiceHearingText.textContent = 'MIC READY // Say "Genox" or give any command...';
      }
      if (voiceHearingPill && !isPatientListening) {
        voiceHearingPill.classList.remove("hearing", "wake-hit");
      }
    }, 3500);
  }
}

/* ==========================================================================
   PATIENT LISTENING ENGINE (Says "Yes", waits 5s silence, says "OK", executes)
   ========================================================================== */
function startPatientListening(initialCommand = "", startIndex = 0) {
  isPatientListening = true;
  patientListeningStartIndex = startIndex >= 0 ? startIndex : 0;
  accumulatedTranscript = (initialCommand || "").trim();
  promptInput.value = accumulatedTranscript;

  // 1. Play chime and light up avatar
  playAudioChime("wake");
  triggerWakeWordVisual(true);

  // 2. Speak immediate verbal acknowledgement: "Yes"
  speakResponse("Yes");

  if (speechStateLabel) speechStateLabel.textContent = "Listening (5s silence to run)...";
  if (coreSubtitleText) coreSubtitleText.textContent = "[ GENOX: 'YES' // PATIENTLY LISTENING... ]";
  updateHearingHud('🟢 GENOX: "Yes" // Patiently listening... (Speak your full task, starts after 5s silence)', "wake-hit");

  // 3. Start silence countdown timer
  resetPatientSilenceTimer();
}

function resetPatientSilenceTimer() {
  if (patientSilenceTimer) clearTimeout(patientSilenceTimer);
  if (patientCountdownTimer) clearInterval(patientCountdownTimer);

  silenceSecondsRemaining = 5;

  patientCountdownTimer = setInterval(() => {
    silenceSecondsRemaining--;
    if (isPatientListening && silenceSecondsRemaining > 0) {
      const textPreview = (promptInput.value || accumulatedTranscript).trim();
      const previewStr = textPreview ? `"${textPreview.slice(-40)}"` : "listening to your task...";
      if (speechStateLabel) speechStateLabel.textContent = `Listening... (${silenceSecondsRemaining}s silence)`;
      updateHearingHud(`🎙️ LISTENING: ${previewStr} (Silence for ${silenceSecondsRemaining}s to run)`, "hearing");
    }
  }, 1000);

  patientSilenceTimer = setTimeout(() => {
    onPatientSilenceExpired();
  }, 5000);
}

function onPatientSilenceExpired() {
  if (!isPatientListening) return;
  isPatientListening = false;
  if (patientSilenceTimer) clearTimeout(patientSilenceTimer);
  if (patientCountdownTimer) clearInterval(patientCountdownTimer);

  const rawCommand = (promptInput.value || accumulatedTranscript).trim();
  const finalCommand = cleanSpokenTask(rawCommand) || rawCommand;
  if (finalCommand.length > 1) {
    updateHearingHud(`⚡ TASK RECEIVED: "${finalCommand.slice(0, 45)}..."`, "wake-hit");
    if (speechStateLabel) speechStateLabel.textContent = "Starting task...";
    if (coreSubtitleText) coreSubtitleText.textContent = "[ GENOX: 'OK' // STARTING TASK... ]";

    // 3. Reply with "OK" then start doing the task!
    speakResponse("OK");

    setTimeout(() => {
      triggerWakeWordVisual(false);
      dispatchPrompt(finalCommand);
    }, 700);
  } else {
    // No task was spoken
    updateHearingHud('MIC READY // Say "Genox" or give any command...');
    if (speechStateLabel) speechStateLabel.textContent = 'Say "Genox"...';
    triggerWakeWordVisual(false);
    accumulatedTranscript = "";
    patientListeningStartIndex = 0;
  }
}

// 1. Microphone Hardware Audio Visualizer (modulated bars)
async function initMicAudioVisualizer() {
  if (micMediaStream) return;
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
    micMediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });

    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended") audioCtx.resume();

    const source = audioCtx.createMediaStreamSource(micMediaStream);
    micAudioAnalyser = audioCtx.createAnalyser();
    micAudioAnalyser.fftSize = 64;
    source.connect(micAudioAnalyser);
    micDataBuffer = new Uint8Array(micAudioAnalyser.frequencyBinCount);

    function updateWaveBars() {
      if (micAudioAnalyser && micDataBuffer) {
        micAudioAnalyser.getByteFrequencyData(micDataBuffer);
        let sum = 0;
        for (let i = 0; i < micDataBuffer.length; i++) sum += micDataBuffer[i];
        const avg = sum / micDataBuffer.length;

        const bars = document.querySelectorAll("#sidebarVoiceBars .voice-wave-bar");
        bars.forEach((bar, idx) => {
          const factor = Math.min(100, Math.max(15, (avg * 2.2) + ((idx * 8) % 20)));
          bar.style.height = `${factor}%`;
          if (avg > 14) {
            bar.style.background = "var(--accent-emerald)";
            bar.style.boxShadow = "0 0 8px var(--accent-emerald)";
          } else {
            bar.style.background = "rgba(0, 240, 255, 0.4)";
            bar.style.boxShadow = "none";
          }
        });
      }
      requestAnimationFrame(updateWaveBars);
    }
    updateWaveBars();
    console.log("[Genox] Real-time microphone audio visualizer initialized.");
  } catch (err) {
    console.warn("[Genox] Microphone hardware visualizer notice:", err);
  }
}

// 2. Speech Recognition Engine
function initWakeWordDetection() {
  if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
    console.warn("[Genox] SpeechRecognition API not supported in this browser.");
    if (wakeWordLabel) wakeWordLabel.textContent = "WAKE: NOT SUPPORTED";
    updateHearingHud("Speech recognition not supported in this browser (use Chrome)");
    return;
  }

  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  wakeRecognition = new SpeechRec();
  wakeRecognition.continuous = true;
  wakeRecognition.interimResults = true;
  wakeRecognition.maxAlternatives = 10;
  wakeRecognition.lang = navigator.language || "en-US";

  wakeRecognition.onstart = () => {
    wakeRecognitionActive = true;
    patientListeningStartIndex = 0;
    console.log("[Genox] Wake Word listener active.");
    if (wakeWordStationCard) wakeWordStationCard.classList.add("wake-listening");
    if (wakeWordLabel) wakeWordLabel.textContent = 'WAKE: "GENOX" ON';
    if (speechStateLabel && !isAwaitingFollowUp) speechStateLabel.textContent = 'Say "Genox"...';
    updateHearingHud('MIC ACTIVE // Say "Genox" or give any command...');
  };

  wakeRecognition.onresult = (event) => {
    if (isGenoxSpeaking) return; // Suppress while Genox TTS is talking

    // =========================================================================
    // MODE A: PATIENT LISTENING (User called "Genox", Genox said "Yes", listening)
    // =========================================================================
    if (isPatientListening) {
      // Check if user re-invoked the wake word during patient listening (e.g. said "Geox" or "Genox" again)
      // If the user spoke a wake word at a new index, restart patient listening cleanly from that point!
      for (let i = event.results.length - 1; i > patientListeningStartIndex; i--) {
        const chunk = (event.results[i][0].transcript || "").trim();
        if (WAKE_WORD_REGEX.test(chunk)) {
          console.log("[Genox] Wake word re-invoked during patient listening at index:", i);
          patientListeningStartIndex = i;
          accumulatedTranscript = "";
          speakResponse("Yes");
          break;
        }
      }

      let fullTranscript = "";
      const startIdx = Math.max(0, Math.min(patientListeningStartIndex, event.results.length - 1));
      for (let i = startIdx; i < event.results.length; i++) {
        fullTranscript += event.results[i][0].transcript + " ";
      }
      fullTranscript = fullTranscript.trim();

      // Strip any repeated wake word calls if present and deduplicate repeated phrases
      const cleaned = cleanSpokenTask(fullTranscript);
      const currentTask = cleaned || cleanSpokenTask(accumulatedTranscript) || fullTranscript;

      promptInput.value = currentTask;
      accumulatedTranscript = currentTask;

      // Check for user explicit finish phrases: e.g. "start doing the job", "do it now", "start now", "that's all"
      if (/\b(start\s+(?:doing\s+the\s+job|the\s+task|now)|do\s+it\s+now|that'?s\s+all|that'?s\s+it)\b/i.test(currentTask)) {
        const cleanedTask = cleanSpokenTask(currentTask.replace(/\b(start\s+(?:doing\s+the\s+job|the\s+task|now)|do\s+it\s+now|that'?s\s+all|that'?s\s+it)\b/i, ""));
        promptInput.value = cleanedTask;
        accumulatedTranscript = cleanedTask;
        onPatientSilenceExpired();
        return;
      }

      // Reset the 5-second silence timer on every spoken word/chunk
      resetPatientSilenceTimer();
      updateHearingHud(`🎙️ LISTENING: "${currentTask.slice(-45)}" (Silence for 5s to run)`, "hearing");
      return;
    }

    // =========================================================================
    // MODE B: STANDBY LISTENING (Waiting for wake word "Genox" or direct command)
    // =========================================================================
    let bestTranscript = "";
    let matchedIntent = null;
    let anyFinal = false;

    // Scan all results and all 10 alternatives returned by Google STT
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const res = event.results[i];
      if (res.isFinal) anyFinal = true;

      for (let j = 0; j < res.length; j++) {
        const alt = (res[j].transcript || "").trim();
        if (!alt) continue;

        if (j === 0 && !bestTranscript) {
          bestTranscript = alt;
        }

        if (!matchedIntent) {
          const parsed = parseSpokenIntent(alt);
          if (parsed) {
            matchedIntent = { ...parsed, isFinal: res.isFinal, resultIndex: i };
          }
        }
      }
    }

    const currentText = bestTranscript || (matchedIntent ? matchedIntent.raw : "");
    if (!currentText && !matchedIntent) return;

    // Live HUD update
    if (matchedIntent && matchedIntent.type === "wake") {
      updateHearingHud(`🟢 WAKE: "GENOX" (Heard: "${matchedIntent.matchedWord}")`, "wake-hit");
    } else {
      updateHearingHud(`🎙️ HEARING: "${currentText || (matchedIntent && matchedIntent.raw)}"`, "hearing");
    }

    // When Wake Word is detected: Acknowledge with "Yes", start patient 5s listening!
    if (matchedIntent) {
      const triggerIndex = (matchedIntent.resultIndex !== undefined) ? matchedIntent.resultIndex : event.resultIndex;
      if (matchedIntent.type === "wake") {
        startPatientListening(cleanSpokenTask(matchedIntent.command || ""), triggerIndex);
        return;
      }

      if (matchedIntent.type === "action") {
        // Direct Action: Start patient listening so user can complete their thought or let 5s timer run
        startPatientListening(cleanSpokenTask(matchedIntent.command || ""), triggerIndex);
        return;
      }
    }
  };

  wakeRecognition.onerror = (e) => {
    wakeRecognitionActive = false;
    if (e.error === "not-allowed") {
      console.warn("[Genox] Microphone access not allowed.");
      if (wakeWordLabel) wakeWordLabel.textContent = "MIC: CLICK TO ALLOW";
      if (speechStateLabel) speechStateLabel.textContent = "Click to allow mic";
      updateHearingHud("⚠️ MIC BLOCKED: Click anywhere or click mic to allow access");
    } else if (e.error !== "no-speech" && e.error !== "aborted") {
      console.warn("[Genox] Wake listener notice:", e.error);
    }
  };

  wakeRecognition.onend = () => {
    wakeRecognitionActive = false;
    if (wakeWordEnabled && !isExecuting) {
      setTimeout(() => {
        try {
          if (wakeWordEnabled && !wakeRecognitionActive) wakeRecognition.start();
        } catch (e) {}
      }, 300);
    } else {
      if (wakeWordStationCard) wakeWordStationCard.classList.remove("wake-listening");
    }
  };

  startWakeRecognition();
  initMicAudioVisualizer();
}

function startWakeRecognition() {
  if (!wakeRecognition || wakeRecognitionActive || !wakeWordEnabled || isExecuting || isGenoxSpeaking) return;
  try {
    wakeRecognition.start();
  } catch (err) {
    if (err.name !== "InvalidStateError") {
      console.warn("[Genox] Speech recognition start error:", err);
    }
  }
}

// 1. Re-sync recognition when user switches back to Genox tab or window gains focus
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible" && wakeWordEnabled && !wakeRecognitionActive) {
    startWakeRecognition();
  }
});
window.addEventListener("focus", () => {
  if (wakeWordEnabled && !wakeRecognitionActive) {
    startWakeRecognition();
  }
});

// 2. Periodic heartbeat to keep speech recognition alive in continuous mode
setInterval(() => {
  if (wakeWordEnabled && !wakeRecognitionActive && !isExecuting && !isGenoxSpeaking) {
    startWakeRecognition();
  }
}, 2500);

// User-gesture click unlocker
window.addEventListener("click", () => {
  if (audioCtx && audioCtx.state === "suspended") {
    audioCtx.resume();
  }
  if (wakeWordEnabled && !wakeRecognitionActive) {
    startWakeRecognition();
    initMicAudioVisualizer();
  }
}, { once: false });

// Spacebar Push-To-Talk Shortcut
window.addEventListener("keydown", (e) => {
  if (e.code === "Space" && document.activeElement !== promptInput && document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA") {
    e.preventDefault();
    toggleManualMic();
  }
});

function triggerWakeWordVisual(active) {
  if (active) {
    if (wakeWordToggleBtn) wakeWordToggleBtn.classList.add("wake-triggered");
    if (wakeWordStationCard) wakeWordStationCard.classList.add("wake-triggered");
    setViewportMode("avatar");
    if (avatarFaceContainer) avatarFaceContainer.classList.add("active");
  } else {
    setTimeout(() => {
      if (wakeWordToggleBtn) wakeWordToggleBtn.classList.remove("wake-triggered");
      if (wakeWordStationCard) wakeWordStationCard.classList.remove("wake-triggered");
    }, 1800);
  }
}

function toggleWakeWord() {
  wakeWordEnabled = !wakeWordEnabled;
  if (wakeWordToggleBtn) {
    wakeWordToggleBtn.classList.toggle("wake-active", wakeWordEnabled);
    if (wakeWordLabel) wakeWordLabel.textContent = wakeWordEnabled ? 'WAKE: "GENOX" ON' : "WAKE: OFF";
  }
  if (wakeWordEnabled) {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(() => {
          startWakeRecognition();
          initMicAudioVisualizer();
          if (wakeWordStationCard) wakeWordStationCard.classList.add("wake-listening");
          if (wakeWordLabel) wakeWordLabel.textContent = 'WAKE: "GENOX" ON';
          if (speechStateLabel) speechStateLabel.textContent = 'Say "Genox"...';
          updateHearingHud('MIC ACTIVE // Say "Genox" or give any command...');
        })
        .catch(err => {
          console.warn("Microphone access declined:", err);
          if (wakeWordLabel) wakeWordLabel.textContent = "MIC: CLICK TO ALLOW";
          if (speechStateLabel) speechStateLabel.textContent = "Click to allow mic";
          updateHearingHud("⚠️ MIC BLOCKED: Click anywhere or click mic to allow access");
        });
    } else {
      startWakeRecognition();
      if (wakeWordStationCard) wakeWordStationCard.classList.add("wake-listening");
      if (speechStateLabel) speechStateLabel.textContent = 'Say "Genox"...';
    }
  } else {
    try {
      if (wakeRecognition) wakeRecognition.stop();
    } catch (e) {}
    wakeRecognitionActive = false;
    if (wakeWordStationCard) wakeWordStationCard.classList.remove("wake-listening");
    if (speechStateLabel) speechStateLabel.textContent = "Standby";
    updateHearingHud("WAKE DETECTION OFF // Click to enable");
  }
}

if (wakeWordToggleBtn) wakeWordToggleBtn.addEventListener("click", toggleWakeWord);

// Manual Dictation Button (Microphone click or Spacebar)
function toggleManualMic() {
  if (wakeWordEnabled && wakeRecognitionActive) {
    try { wakeRecognition.stop(); } catch (e) {}
    wakeRecognitionActive = false;
    setTimeout(() => {
      startWakeRecognition();
      startPatientListening(promptInput.value || "", 0);
    }, 150);
    return;
  }

  if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
    alert("Speech recognition not supported in this browser. Please use Google Chrome.");
    return;
  }

  initMicAudioVisualizer();

  if (!manualRecognition) {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    manualRecognition = new SpeechRec();
    manualRecognition.continuous = false;
    manualRecognition.interimResults = true;
    manualRecognition.lang = navigator.language || "en-US";

    manualRecognition.onstart = () => {
      micBtn.classList.add("listening");
      if (speechStateLabel) speechStateLabel.textContent = "Listening...";
      updateHearingHud("🎙️ LISTENING (DICTATION ACTIVE)...", "hearing");
      playAudioChime("wake");
    };

    manualRecognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      promptInput.value = transcript;
      updateHearingHud(`🎙️ HEARING: "${transcript}"`, "hearing");
      if (e.results[0].isFinal) {
        micBtn.classList.remove("listening");
        if (speechStateLabel) speechStateLabel.textContent = "Processed";
        updateHearingHud(`✓ DISPATCHING: "${transcript}"`, "wake-hit");
        dispatchPrompt(transcript);
      }
    };

    manualRecognition.onerror = () => {
      micBtn.classList.remove("listening");
      if (speechStateLabel) speechStateLabel.textContent = 'Say "Genox"...';
      updateHearingHud('MIC READY // Say "Genox" or give any command...');
    };
    manualRecognition.onend = () => {
      micBtn.classList.remove("listening");
      if (speechStateLabel) speechStateLabel.textContent = 'Say "Genox"...';
    };
  }

  try {
    manualRecognition.start();
  } catch (e) {
    manualRecognition.stop();
  }
}

micBtn.addEventListener("click", toggleManualMic);
if (sidebarMicBtn) sidebarMicBtn.addEventListener("click", toggleManualMic);

voiceToggleBtn.addEventListener("click", () => {
  voiceEnabled = !voiceEnabled;
  voiceIcon.textContent = voiceEnabled ? "🔊" : "🔇";
  voiceLabel.textContent = voiceEnabled ? "SPEECH: ON" : "SPEECH: OFF";
  if (!voiceEnabled && window.speechSynthesis) {
    window.speechSynthesis.cancel();
    if (avatarFaceContainer) avatarFaceContainer.classList.remove("speaking");
    if (voiceStation) voiceStation.classList.remove("speaking");
  }
});

/* ==========================================================================
   12. WORKSPACE FILES LOADER & VIEWER
   ========================================================================== */
async function loadWorkspaceFiles() {
  if (!drawerFilesList) return;
  drawerFilesList.innerHTML = "<div style='color: var(--text-dim);'>Scanning workspace...</div>";
  try {
    const res = await fetch("/api/files");
    const files = await res.json();
    if (!files || files.length === 0) {
      drawerFilesList.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 24px; text-align: center; color: var(--text-dim); border: 1px dashed var(--border-subtle); border-radius: var(--radius-md);">
          No files generated in workspace yet. Ask Genox to generate code, reports, or data!
        </div>
      `;
      return;
    }

    drawerFilesList.innerHTML = files.map(f => `
      <div class="file-item-card" onclick="openFilePreview('${escapeHtml(f.name)}')">
        <div style="display: flex; align-items: center; gap: 10px; overflow: hidden;">
          <span style="font-size: 1.2rem;">${f.is_dir ? "📁" : getFileIcon(f.name)}</span>
          <div style="overflow: hidden;">
            <div style="font-size: 0.85rem; font-weight: 600; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">${escapeHtml(f.name)}</div>
            <div style="font-size: 0.7rem; color: var(--text-dim); font-family: var(--font-mono);">${formatBytes(f.size)}</div>
          </div>
        </div>
        <span style="font-size: 0.72rem; color: var(--accent-cyan); font-family: var(--font-mono);">VIEW ➔</span>
      </div>
    `).join("");
  } catch (err) {
    drawerFilesList.innerHTML = `<div style="color: var(--accent-crimson);">Error loading files: ${err.message}</div>`;
  }
}

function getFileIcon(name) {
  if (name.endsWith(".py")) return "🐍";
  if (name.endsWith(".json")) return "📋";
  if (name.endsWith(".md")) return "📝";
  if (name.endsWith(".txt")) return "📄";
  if (name.endsWith(".png") || name.endsWith(".jpg")) return "🖼️";
  return "📦";
}

function formatBytes(bytes) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

async function openFilePreview(filename) {
  try {
    const res = await fetch(`/api/file-content?filename=${encodeURIComponent(filename)}`);
    if (!res.ok) throw new Error("Could not read file");
    const data = await res.json();
    previewFileName.textContent = `WORKSPACE FILE: ${data.filename}`;
    previewFileContent.textContent = data.content;
    filePreviewModal.classList.add("open");
  } catch (err) {
    alert("Could not open file: " + err.message);
  }
}

closePreviewBtn.addEventListener("click", () => filePreviewModal.classList.remove("open"));
if (refreshFilesBtn) refreshFilesBtn.addEventListener("click", loadWorkspaceFiles);

/* ==========================================================================
   13. MEMORY BANK LOADER & STORE
   ========================================================================== */
async function loadMemories() {
  if (!drawerMemoryList) return;
  drawerMemoryList.innerHTML = "<div style='color: var(--text-dim);'>Recalling memory facts...</div>";
  try {
    const res = await fetch("/api/memory");
    const list = await res.json();
    if (!list || list.length === 0) {
      drawerMemoryList.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 24px; text-align: center; color: var(--text-dim); border: 1px dashed var(--border-subtle); border-radius: var(--radius-md);">
          No memories stored yet. Save any user preference, key fact, or project note!
        </div>
      `;
      return;
    }

    drawerMemoryList.innerHTML = list.map(m => `
      <div class="memory-item-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <strong style="color: var(--accent-cyan); font-family: var(--font-mono); font-size: 0.8rem;">${escapeHtml(m.key)}</strong>
          <span style="font-size: 0.65rem; background: rgba(0, 240, 255, 0.1); padding: 2px 6px; border-radius: 4px; color: var(--accent-cyan);">${escapeHtml(m.category || "general")}</span>
        </div>
        <div style="font-size: 0.82rem; color: var(--text-main); margin-top: 4px; line-height: 1.4;">${escapeHtml(m.value)}</div>
        <div style="display: flex; justify-content: flex-end; margin-top: 6px;">
          <button class="topbar-btn" style="padding: 2px 8px; font-size: 0.68rem; color: var(--accent-crimson);" onclick="deleteMemoryFact('${escapeHtml(m.key)}')">Delete</button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    drawerMemoryList.innerHTML = `<div style="color: var(--accent-crimson);">Error loading memory: ${err.message}</div>`;
  }
}

async function deleteMemoryFact(key) {
  if (!confirm(`Delete memory key '${key}'?`)) return;
  try {
    await fetch(`/api/memory/${encodeURIComponent(key)}`, { method: "DELETE" });
    loadMemories();
    checkSystemStatus();
  } catch (err) {
    alert("Delete failed: " + err.message);
  }
}

if (addMemoryBtn) {
  addMemoryBtn.addEventListener("click", async () => {
    const k = newMemKey.value.trim();
    const v = newMemVal.value.trim();
    if (!k || !v) {
      alert("Please enter both a key and a value.");
      return;
    }
    try {
      await fetch("/api/memory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: k, value: v, category: "user" })
      });
      newMemKey.value = "";
      newMemVal.value = "";
      loadMemories();
      checkSystemStatus();
    } catch (err) {
      alert("Save failed: " + err.message);
    }
  });
}

/* ==========================================================================
   14. TOOLS & SKILLS CATALOG LOADER
   ========================================================================== */
async function loadTools() {
  if (!drawerToolsList) return;
  drawerToolsList.innerHTML = "<div style='color: var(--text-dim);'>Inspecting tool registry...</div>";
  try {
    const res = await fetch("/api/tools");
    const tools = await res.json();
    drawerToolsList.innerHTML = tools.map(t => `
      <div class="tool-item-card">
        <div class="tool-item-header">
          <span class="tool-name-tag">${escapeHtml(t.name)}</span>
          <span style="font-size: 0.65rem; color: var(--accent-emerald); font-family: var(--font-mono);">READY</span>
        </div>
        <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.4; margin-top: 4px;">${escapeHtml(t.description)}</p>
        <div style="font-size: 0.7rem; font-family: var(--font-mono); color: var(--text-dim); margin-top: 6px;">
          Parameters: ${Object.keys(t.parameters || {}).join(", ") || "None"}
        </div>
      </div>
    `).join("");
  } catch (err) {
    drawerToolsList.innerHTML = `<div style="color: var(--accent-crimson);">Error loading tools: ${err.message}</div>`;
  }
}

/* ==========================================================================
   15. MISSION AUDIT TIMELINE & HISTORY LOADER
   ========================================================================== */
async function loadHistory() {
  if (!drawerHistoryList) return;
  drawerHistoryList.innerHTML = "<div style='color: var(--text-dim);'>Retrieving mission audit log...</div>";
  try {
    const res = await fetch("/api/history");
    const logs = await res.json();
    if (!logs || logs.length === 0) {
      drawerHistoryList.innerHTML = `
        <div style="padding: 24px; text-align: center; color: var(--text-dim); border: 1px dashed var(--border-subtle); border-radius: var(--radius-md);">
          No mission records found yet.
        </div>
      `;
      return;
    }

    drawerHistoryList.innerHTML = logs.map(h => `
      <div class="history-item-row">
        <div>
          <div style="font-size: 0.82rem; font-weight: 600;">${escapeHtml(h.prompt)}</div>
          <div style="font-size: 0.7rem; color: var(--text-dim); font-family: var(--font-mono); margin-top: 2px;">
            ${h.timestamp ? new Date(h.timestamp * 1000).toLocaleString() : "Just now"} • ${h.tool_calls_count || 0} tools used
          </div>
        </div>
        <span style="font-size: 0.7rem; color: var(--accent-emerald); font-family: var(--font-mono);">SUCCESS</span>
      </div>
    `).join("");
  } catch (err) {
    drawerHistoryList.innerHTML = `<div style="color: var(--accent-crimson);">Error loading history: ${err.message}</div>`;
  }
}

if (refreshHistoryBtn) refreshHistoryBtn.addEventListener("click", loadHistory);

function logMissionAudit(prompt) {
  if (!missionTimelineList || !prompt) return;
  const row = document.createElement("div");
  row.style.fontSize = "0.78rem";
  row.style.color = "var(--text-muted)";
  row.style.display = "flex";
  row.style.justifyContent = "space-between";
  row.innerHTML = `
    <span>• ${escapeHtml(prompt.slice(0, 36))}${prompt.length > 36 ? "..." : ""}</span>
    <span style="font-family: var(--font-mono); color: var(--accent-emerald);">DONE</span>
  `;
  missionTimelineList.prepend(row);
}

function escapeHtml(str) {
  if (typeof str !== "string") str = String(str);
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/* ==========================================================================
   16. CONFIG MODAL OPERATIONS
   ========================================================================== */
function openConfigModal() { configModal.classList.add("open"); }
function closeConfigModal() { configModal.classList.remove("open"); }

settingsBtn.addEventListener("click", openConfigModal);
closeModalBtn.addEventListener("click", closeConfigModal);

saveConfigBtn.addEventListener("click", async () => {
  const key = apiKeyInput.value.trim();
  const model = modelSelect.value;
  if (!key) {
    alert("Please enter a valid Google AI Studio API Key.");
    return;
  }

  saveConfigBtn.textContent = "SAVING...";
  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gemini_api_key: key, model_name: model })
    });
    const result = await res.json();
    if (result.success) {
      closeConfigModal();
      checkSystemStatus();
    }
  } catch (err) {
    alert("Failed to save config: " + err.message);
  } finally {
    saveConfigBtn.textContent = "SAVE CONFIG";
  }
});

/* ==========================================================================
   17. EVENT LISTENERS & NAVIGATION
   ========================================================================== */
sendBtn.addEventListener("click", () => dispatchPrompt());
promptInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    dispatchPrompt();
  }
});

// Quick action chips
document.querySelectorAll(".quick-pill").forEach(pill => {
  pill.addEventListener("click", () => {
    dispatchPrompt(pill.dataset.prompt);
  });
});

// Left Sidebar Navigation
document.querySelectorAll(".nav-item").forEach(item => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    item.classList.add("active");
    const view = item.dataset.view;

    if (view === "dashboard") {
      closeDrawer();
    } else if (view === "aicore") {
      closeDrawer();
      setViewportMode("avatar");
    } else if (view === "agents") {
      closeDrawer();
      const squad = document.querySelector(".agents-squad-grid");
      if (squad) squad.scrollIntoView({ behavior: "smooth" });
    } else if (view === "files") {
      openDrawer();
      switchDrawerPane("paneFiles");
    } else if (view === "memory") {
      openDrawer();
      switchDrawerPane("paneMemory");
    } else if (view === "tools") {
      openDrawer();
      switchDrawerPane("paneTools");
    } else if (view === "logs") {
      openDrawer();
      switchDrawerPane("paneHistory");
    }
  });
});

// Global Keyboard Shortcut: Cmd/Ctrl + K to focus command bar
window.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    if (promptInput) promptInput.focus();
  }
});

// Boot Genox System
window.addEventListener("DOMContentLoaded", () => {
  initNeuralParticleWave();
  init3DSphere();
  initWebSocket();
  initWakeWordDetection();
});
