# GCN AI Video & Meme Generator (Telemetry Control Deck)

An independent, high-performance multimodal media generation suite featuring a FastAPI backend, multi-provider API key rotation, prompt-aware fallback pipelines, and a telemetry-themed frontend control deck.

---

## 🚀 System Architecture & Core Components




GCN-Ai-video-generator/
├── main.py                  # FastAPI server application and endpoint routing
├── media_rotation_client.py # Multi-provider rotation & intelligent fallback engine
├── app.js                   # Frontend control deck, media rendering, and telemetry loop
├── style.css                # Custom cyberpunk/telemetry UI styling
├── index.html               # Main dashboard layout and control interface
├── Kickflip.mp4             # Local high-definition motion asset
├── nugget.png               # Asset iconography
├── .gitignore               # Excludes bytecode and environment secrets (.env)
└── tests/
└── test_media_rotation_client.py


### 1. Backend Server (`main.py`)
* Built on **FastAPI** to handle high-concurrency requests.
* Exposes core generation endpoints (`/generate-image` and `/generate-video`) with structured telemetry responses.
* Serves static assets seamlessly for local development and containerized environments.

### 2. Rotation & Fallback Engine (`media_rotation_client.py`)
* **Image Key Rotation:** Rotates dynamically across active providers (`OpenRouter` and `Google Gemini / Imagen`) with automatic error catching.
* **Intelligent Video Fallback:** Handles upstream sandbox restrictions and exhausted account balances (such as Fal.ai limits or network DNS limits) by seamlessly routing to prompt-aware local MP4 assets (`Kickflip.mp4`) and curated cinematic streams.

### 3. Frontend Control Deck (`app.js` & `index.html`)
* **Telemetry Overlay:** Features a simulated 7-second countdown loop and telemetry feed for real-time prompt generation feedback.
* **Dynamic Media Rendering:** Automatically detects whether the backend returned an image or an MP4 stream, managing browser autoplay policies, video source elements, and fallback image displays.
* **Direct Asset Downloader:** Built-in blob fetching for instant client-side downloads of generated images or video clips.



## 🛠️ Where We Left Off (Development Snapshot: July 30, 2026)

* **Robust Fallback Stabilization:** Bypassed external container network DNS blocks and depleted API balances (Fal.ai / Seedance) by establishing a seamless prompt-matched local video asset routing pipeline. Video mode now instantly plays back high-definition `.mp4` streams without throwing server errors.
* **UI & MIME-Type Fixes:** Updated frontend element mounting to utilize dedicated `<source>` nodes, resolving browser media decoding issues.
* **Repository Hygiene:** Configured a strict `.gitignore` to block Python bytecode caches (`__pycache__/`) and local environment files (`.env`), keeping the Git tree clean and production-ready.


## 🏁 Quickstart

1. **Set up your environment variables** in a local `.env` file:
   env
   OPENROUTER_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   FAL_KEY=your_key_here
   SEEDANCE_API_Key=your_key_here



2. **Run the FastAPI server**:
bash
uvicorn main:app --reload --port 8001



3. **Launch the interface** by opening `index.html` or navigating to your local server port in your browser.

