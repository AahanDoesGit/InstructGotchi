/**
 * Instructa-Gotchi Phone Companion Mobile Client
 * Real-time state polling, care commands, mode switching, and audio visualizer.
 */

const API_BASE = window.location.origin;

let currentState = {};
let activeTab = "tab-home";

async function fetchState() {
  try {
    const res = await fetch(`${API_BASE}/api/state`);
    const data = await res.json();
    if (data.status === "ok") {
      currentState = data.state;
      updateUI();
    }
  } catch (err) {
    console.warn("Connection to UNIHIKER lost, retrying...", err);
    document.getElementById("connection-status").textContent = "Offline (Retrying...)";
    document.getElementById("status-indicator").style.backgroundColor = "#ED735C";
  }
}

function updateUI() {
  if (!currentState) return;

  document.getElementById("connection-status").textContent = "UNIHIKER Online";
  document.getElementById("status-indicator").style.backgroundColor = "#83A978";

  // Level & XP
  document.getElementById("pet-level-badge").textContent = `LVL ${currentState.level || 1}`;
  document.getElementById("pet-name-display").textContent = currentState.name || "Instructa-Gotchi";
  document.getElementById("pet-status-display").textContent = `Mode: ${(currentState.mode || 'auto').toUpperCase()} • Mood: ${(currentState.mood || 'happy').toUpperCase()}`;
  document.getElementById("pet-speech-display").textContent = currentState.speech || "Ready to build!";

  // Avatar expression
  const mood = currentState.mood || "idle";
  const avatarImg = document.getElementById("hero-character-avatar");
  if (avatarImg) {
    avatarImg.src = `/assets/expressions/${mood}.png`;
  }

  // Stats progress bars
  const stats = [
    { id: "hunger", val: currentState.hunger, col: "#F28B24" },
    { id: "happiness", val: currentState.happiness, col: "#FFC928" },
    { id: "energy", val: currentState.energy, col: "#38BDF8" },
    { id: "cleanliness", val: currentState.cleanliness, col: "#83A978" },
    { id: "health", val: currentState.health, col: "#ED735C" }
  ];

  stats.forEach(s => {
    const fillEl = document.getElementById(`bar-${s.id}`);
    const textEl = document.getElementById(`val-${s.id}`);
    if (fillEl && textEl) {
      fillEl.style.width = `${s.val}%`;
      fillEl.style.backgroundColor = s.col;
      textEl.textContent = `${s.val}%`;
    }
  });
}

async function sendCareAction(action) {
  try {
    const res = await fetch(`${API_BASE}/api/care`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action })
    });
    const data = await res.json();
    if (data.status === "ok") {
      currentState = data.state;
      updateUI();
    }
  } catch (e) {
    console.error("Care action failed:", e);
  }
}

async function setMode(mode) {
  try {
    const res = await fetch(`${API_BASE}/api/mode`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode })
    });
    const data = await res.json();
    if (data.status === "ok") {
      currentState = data.state;
      updateUI();
    }
  } catch (e) {
    console.error("Mode switch failed:", e);
  }
}

async function loadMissions() {
  try {
    const res = await fetch(`${API_BASE}/api/missions`);
    const data = await res.json();
    const container = document.getElementById("missions-list");
    if (container && data.missions) {
      container.innerHTML = data.missions.map(m => `
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="card-title">${m.title}</div>
            <span style="font-size:11px; font-weight:700; color:#F28B24;">+${m.xp_reward} XP</span>
          </div>
          <div style="font-size:12px; color:#879099; margin-bottom:8px;">${m.description}</div>
          <div class="stat-bar-track">
            <div class="stat-bar-fill" style="width: ${Math.min(100, (m.progress / m.target) * 100)}%; background-color:#83A978;"></div>
          </div>
        </div>
      `).join("");
    }
  } catch (e) {
    console.error("Failed to load missions", e);
  }
}

async function loadDiary() {
  try {
    const res = await fetch(`${API_BASE}/api/diary`);
    const data = await res.json();
    const container = document.getElementById("diary-list");
    if (container && data.diary) {
      container.innerHTML = data.diary.map(entry => {
        const timeStr = new Date(entry.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        return `
          <div class="timeline-item">
            <div class="timeline-icon">⚙️</div>
            <div class="timeline-body">
              <div class="timeline-title">${entry.title}</div>
              <div class="timeline-desc">${entry.description || ''} • ${timeStr}</div>
            </div>
            ${entry.xp_gained ? `<span style="font-size:10px; color:#F28B24; font-weight:700;">+${entry.xp_gained} XP</span>` : ''}
          </div>
        `;
      }).join("");
    }
  } catch (e) {
    console.error("Failed to load diary", e);
  }
}

function switchNavTab(tabId) {
  document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(btn => btn.classList.remove("active"));

  const targetSection = document.getElementById(tabId);
  const targetNavBtn = document.getElementById(`nav-${tabId}`);
  if (targetSection) targetSection.classList.add("active");
  if (targetNavBtn) targetNavBtn.classList.add("active");

  if (tabId === "tab-explore") {
    loadMissions();
    loadDiary();
  }
}

// Initial boot
document.addEventListener("DOMContentLoaded", () => {
  fetchState();
  setInterval(fetchState, 1500); // Poll every 1.5s
});

