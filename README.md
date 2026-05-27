# 🏋️‍♀️ AI Real-time GYM Coach

An AI-powered personal fitness coach that uses your webcam to analyze exercise form in real time, count reps, track sets, and deliver live voice feedback — all inside a Streamlit web app.

🌐 **Landing Page:** [ai-fitness-coach-in.netlify.app](https://ai-fitness-coach-in.netlify.app/)
🚀 **Live App:** [ai-fitness-instructor.streamlit.app](https://ai-fitness-instructor.streamlit.app/)

> ⚠️ **Heads up before you launch the app:** The live app uses WebRTC for camera streaming. **Use mobile data (4G/5G)** for the best experience — Wi-Fi networks often block the UDP traffic WebRTC relies on. [See details below.](#-important-mobile-data-tcp-vs-wi-fi-udp)

---

## ✨ Features

- **Real-time Pose Detection** — MediaPipe-powered skeleton tracking via your camera
- **5 Supported Exercises** — Squats, Push-ups, Biceps Curls (Dumbbell), Shoulder Press, and Lunges
- **Automatic Rep & Set Counting** — Tracks current set reps, total reps, and sets completed
- **Per-exercise Form Metrics** — Knee angle, elbow angle, back alignment, depth status, shoulder stability, swing detection, and more
- **AI Voice Coaching** — Groq LLM generates contextual coaching cues; gTTS converts them to audio that autoplays in-browser
- **Workout Planning** — Set your exercise, target sets, and reps per set before starting
- **Session History** — Workout logs are persisted in a local SQLite database and shown as an aggregated table
- **User Login Wall** — Simple auth layer to keep sessions separated

---

## 📁 Project Structure

```
AI-GYM-COACH/
├── app.py                   # Main Streamlit app entry point
├── requirements.txt
├── packages.txt
├── core/                    # Core utilities
├── detectors/               # Exercise-specific rep/form detectors
├── ml_models/               # Pose estimation model wrappers
├── services/
│   ├── auth/                # Login wall
│   ├── coaching/            # LLM coach, TTS, and voice pipeline
│   ├── config/              # Exercise options config
│   ├── persistence/         # SQLite exercise repository
│   ├── state/               # Streamlit session defaults
│   ├── tracking/            # Metric sync between WebRTC context and session state
│   ├── ui/                  # CSS/font loaders and WebRTC style injectors
│   └── vision/              # VideoProcessor for WebRTC frame handling
└── static/                  # CSS and font assets
```

---

## ⚙️ Tech Stack

| Layer | Library |
|---|---|
| UI Framework | Streamlit 1.54 |
| Camera / Streaming | streamlit-webrtc 0.64.5 |
| Pose Estimation | MediaPipe 0.10.14 |
| Computer Vision | OpenCV (headless) 4.10 |
| LLM Coach | Groq API (`groq >= 0.12`) |
| Text-to-Speech | gTTS 2.5.3 |
| Data | Pandas 2.2.3 |
| Config | python-dotenv 1.2.2 |

---

## 📶 Important: Mobile Data (TCP) vs. Wi-Fi (UDP)

> **This app works best on mobile data and may not work on many Wi-Fi networks.**

This project uses **`streamlit-webrtc`** for real-time camera streaming, which relies on **WebRTC** under the hood.

WebRTC defaults to **UDP** for its media transport (via ICE/STUN). Many **corporate, university, and home Wi-Fi networks block or restrict UDP traffic** on non-standard ports, causing the camera stream to fail to connect or hang indefinitely.

**Mobile data (4G/5G)** uses **TCP-friendly NAT traversal** and is far more permissive with WebRTC connections, which is why the app connects reliably on mobile data.

### What this means for you

| Network | Expected Behaviour |
|---|---|
| 📱 Mobile data (4G/5G) | ✅ Camera connects and streams reliably |
| 🏠 Home Wi-Fi (most routers) | ⚠️ May work, depends on router/firewall UDP settings |
| 🏢 Corporate / University Wi-Fi | ❌ Likely to fail — UDP is typically blocked |
| 🔒 VPN | ❌ Often fails — VPN tunnels interfere with WebRTC UDP |

### Why not just fix it with a TURN server?

A TURN server relays WebRTC traffic over TCP/TLS and would solve the Wi-Fi issue. This is a planned improvement but is not yet implemented — it requires a hosted TURN server (e.g., Twilio, Metered, or self-hosted coturn). Contributions welcome!

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/sriKritarth/AI-GYM-COACH.git
cd AI-GYM-COACH
```

### 2. Install system dependencies

```bash
# Debian/Ubuntu (see packages.txt)
sudo apt-get install $(cat packages.txt)
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Or add it to your Streamlit secrets (`~/.streamlit/secrets.toml`):

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

### 5. Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser. **Use mobile data or a permissive network** for the camera feed to connect.

---

## 🏃 How to Use

1. Log in through the login wall
2. In the sidebar, choose your **exercise**, **sets**, and **reps per set**
3. Click **Start Session** — the camera activates and the AI coach greets you
4. Perform your reps — the app counts them, tracks form metrics, and speaks coaching cues
5. Click **End Workout** when done — the session is saved to your history
6. Scroll down to view your aggregated **Workout History** table

---

## 🤝 Contributing

Pull requests are welcome! If you want to add TURN server support to fix the Wi-Fi/UDP issue, add new exercises, or improve the form detection logic, please open an issue first to discuss the approach.

---

