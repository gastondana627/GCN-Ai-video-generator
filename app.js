const video = document.getElementById('master-video');
const playToggle = document.getElementById('play-toggle');
const loopToggle = document.getElementById('loop-toggle');
const muteToggle = document.getElementById('mute-toggle');
const playState = document.getElementById('play-state');
const miniVideo = document.getElementById('mini-video');
const miniPlayToggle = document.getElementById('mini-play-toggle');
const miniMuteToggle = document.getElementById('mini-mute-toggle');
const miniState = document.getElementById('mini-state');
const form = document.getElementById('prompt-form');
const feedback = document.getElementById('feedback');
const submitBtn = document.getElementById('submit-btn');
const resetBtn = document.getElementById('reset-btn');
const generationOverlay = document.getElementById('generation-overlay');
const overlayVideo = document.getElementById('overlay-video');
const overlayCountdown = document.getElementById('overlay-countdown');
const overlayProgressFill = document.getElementById('overlay-progress-fill');
const overlayCopy = document.getElementById('overlay-copy');
const resultsPanel = document.getElementById('results-panel');
const promptInput = document.getElementById('prompt');
const modeSelect = document.getElementById('mode');
const routeInput = document.getElementById('seed');

let loopEnabled = false;
let muted = false;
let miniMuted = true;
let overlayFrame = null;

function updatePlayUI() {
  const playing = !video.paused;
  playToggle.textContent = playing ? '⏸ Pause' : '▶ Play';
  playToggle.classList.toggle('active', playing);
  playState.textContent = playing ? 'Playing' : 'Paused';
}

function updateMiniUI() {
  const playing = !miniVideo.paused;
  miniPlayToggle.textContent = playing ? '⏸ Pause' : '▶ Play';
  miniPlayToggle.classList.toggle('active', playing);
  miniState.textContent = playing ? 'Playing' : 'Paused';
}

function setFeedback(message, state = '') {
  feedback.className = `feedback ${state}`.trim();
  feedback.textContent = message;
}

function renderResult(payload, mode) {
  const placeholder = resultsPanel.querySelector('.results-placeholder');
  if (placeholder) placeholder.remove();
  resultsPanel.innerHTML = '';

  const mediaUrl = payload?.image_url || payload?.imageBase64 || payload?.video_url || payload?.videoBase64 || payload?.url || payload?.result?.image_url || payload?.result?.video_url || payload?.result?.image_base64 || payload?.result?.video_base64 || payload?.result?.url;
  const base64 = payload?.image_base64 || payload?.video_base64 || payload?.result?.image_base64 || payload?.result?.video_base64;
  const isVideo = mode === 'video' || payload?.video_url || payload?.video_base64 || payload?.result?.video_url || payload?.result?.video_base64 || payload?.result?.type === 'video';

  const container = document.createElement('div');
  container.style.cssText = 'display: flex; flex-direction: column; align-items: center; gap: 14px; width: 100%;';

  let finalSource = '';

  if (isVideo) {
    const videoEl = document.createElement('video');
    videoEl.controls = true;
    videoEl.autoplay = true;
    videoEl.loop = true;
    videoEl.playsInline = true;
    videoEl.muted = true;

    const sourceEl = document.createElement('source');
    if (base64) {
      finalSource = `data:video/mp4;base64,${base64}`;
      sourceEl.src = finalSource;
    } else {
      finalSource = mediaUrl;
      sourceEl.src = mediaUrl;
    }
    sourceEl.type = 'video/mp4';
    videoEl.appendChild(sourceEl);

    container.appendChild(videoEl);
    resultsPanel.appendChild(container);

    videoEl.load();
    videoEl.play().catch(err => console.warn("Video playback deferred by browser policy:", err));
  } else {
    const img = document.createElement('img');
    img.alt = 'Generated output';
    if (base64) {
      finalSource = `data:image/png;base64,${base64}`;
    } else if (mediaUrl) {
      finalSource = mediaUrl;
    } else {
      resultsPanel.innerHTML = '<div class="results-placeholder">No output available from backend.</div>';
      return;
    }
    img.src = finalSource;
    container.appendChild(img);
    resultsPanel.appendChild(container);
  }

  const downloadBtn = document.createElement('button');
  downloadBtn.className = 'ctrl-btn active';
  downloadBtn.type = 'button';
  downloadBtn.innerHTML = `📥 Download ${isVideo ? 'Clip' : 'Image'}`;
  downloadBtn.onclick = async () => {
    try {
      const response = await fetch(finalSource);
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `gcn-generation-${Date.now()}.${isVideo ? 'mp4' : 'png'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(blobUrl);
    } catch (e) {
      const a = document.createElement('a');
      a.href = finalSource;
      a.target = '_blank';
      a.download = `gcn-generation-${Date.now()}.${isVideo ? 'mp4' : 'png'}`;
      a.click();
    }
  };

  container.appendChild(downloadBtn);
}

function showGenerationOverlay() {
  return new Promise((resolve) => {
    generationOverlay.classList.remove('hidden');
    overlayCopy.textContent = 'Telemetry feed primed. The GCN skateboard loop will play through before the final reveal.';
    overlayProgressFill.style.width = '0%';
    overlayCountdown.textContent = '07s';
    overlayVideo.play().catch(() => {});
    const duration = 7;
    const start = performance.now();
    if (overlayFrame) cancelAnimationFrame(overlayFrame);

    const tick = () => {
      const elapsed = (performance.now() - start) / 1000;
      const progress = Math.min(100, (elapsed / duration) * 100);
      overlayProgressFill.style.width = `${progress}%`;
      const remaining = Math.max(0, Math.ceil(duration - elapsed));
      overlayCountdown.textContent = `${String(remaining).padStart(2, '0')}s`;
      if (elapsed < duration) {
        overlayFrame = requestAnimationFrame(tick);
      } else {
        generationOverlay.classList.add('hidden');
        overlayProgressFill.style.width = '0%';
        overlayCountdown.textContent = '07s';
        resolve();
      }
    };

    overlayFrame = requestAnimationFrame(tick);
  });
}

playToggle.addEventListener('click', async () => {
  if (video.paused) {
    try { await video.play(); } catch (error) { console.warn('Playback blocked', error); }
  } else {
    video.pause();
  }
  updatePlayUI();
});

loopToggle.addEventListener('click', () => {
  loopEnabled = !loopEnabled;
  video.loop = loopEnabled;
  loopToggle.classList.toggle('active', loopEnabled);
  loopToggle.textContent = loopEnabled ? '↺ Looping' : '↺ Loop';
});

muteToggle.addEventListener('click', () => {
  muted = !muted;
  video.muted = muted;
  muteToggle.classList.toggle('active', muted);
  muteToggle.textContent = muted ? '🔇 Muted' : '🔊 Mute';
});

miniPlayToggle.addEventListener('click', async () => {
  if (miniVideo.paused) {
    try { await miniVideo.play(); } catch (error) { console.warn('Mini playback blocked', error); }
  } else {
    miniVideo.pause();
  }
  updateMiniUI();
});

miniMuteToggle.addEventListener('click', () => {
  miniMuted = !miniMuted;
  miniVideo.muted = miniMuted;
  miniMuteToggle.classList.toggle('active', miniMuted);
  miniMuteToggle.textContent = miniMuted ? '🔊 Mute' : '🔇 Muted';
});

video.addEventListener('play', updatePlayUI);
video.addEventListener('pause', updatePlayUI);
video.addEventListener('ended', updatePlayUI);
miniVideo.addEventListener('play', updateMiniUI);
miniVideo.addEventListener('pause', updateMiniUI);
miniVideo.addEventListener('ended', updateMiniUI);

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const prompt = promptInput.value.trim();
  const mode = modeSelect ? modeSelect.value : 'image';
  const route = routeInput.value.trim() || 'copper-arc-01';
  const endpoint = mode === 'video' ? '/generate-video' : '/generate-image';

  setFeedback(`Routing “${prompt || 'your prompt'}” to ${route} via ${mode} generation...`, 'loading');
  submitBtn.disabled = true;
  const overlayPromise = showGenerationOverlay();

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, mode, route_tag: route })
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = data?.detail || data?.message || 'Generation request failed';
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }

    renderResult(data, mode);
    setFeedback(`Generation complete. ${mode === 'video' ? 'Clip' : 'Image'} ready.`, 'success');
  } catch (error) {
    console.error('Generation request failed', error);
    setFeedback(`Request failed: ${error.message}`, 'error');
  } finally {
    await overlayPromise;
    submitBtn.disabled = false;
  }
});

resetBtn.addEventListener('click', () => {
  form.reset();
  setFeedback('Awaiting your next prompt.');
  resultsPanel.innerHTML = '<div class="results-placeholder">No output yet. Submit a prompt to populate the telemetry console.</div>';
});

updatePlayUI();
updateMiniUI();
miniVideo.play().catch(() => {});