#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  AI Voice Assistant — Setup Script for Radxa Dragon Q6A
#  Installs: Ollama + Qwen2.5:7B, Whisper, audio libs, TTS
# ═══════════════════════════════════════════════════════════════════

set -e
GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }

info "Starting Voice Assistant setup..."

# ── 1. System packages ────────────────────────────────────────────
info "Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    portaudio19-dev libsndfile1 \
    espeak-ng espeak-ng-data \
    ffmpeg libavcodec-extra \
    curl git build-essential \
    alsa-utils pulseaudio

success "System packages installed"

# ── 2. Ollama ─────────────────────────────────────────────────────
if ! command -v ollama &>/dev/null; then
    info "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    success "Ollama installed"
else
    success "Ollama already installed"
fi

# Start Ollama service
info "Starting Ollama service..."
sudo systemctl enable ollama 2>/dev/null || true
sudo systemctl start ollama  2>/dev/null || ollama serve &
sleep 3

# ── 3. Pull Qwen3.5:4b ───────────────────────────────────────────
info "Pulling Qwen3.5:4b model (this may take 5-15 minutes)..."
ollama pull qwen3.5:4b
success "Qwen3.5:4b ready"

# ── 4. Python virtual environment ─────────────────────────────────
info "Creating Python virtual environment..."
python3 -m venv ~/voice_env
source ~/voice_env/bin/activate
pip install --upgrade pip -q

# ── 5. Python dependencies (from requirements.txt) ───────────────
info "Installing Python packages from requirements.txt..."
 
if [ ! -f requirements.txt ]; then
    warn "requirements.txt not found in $(pwd) — make sure it is in the same folder as setup.sh"
    exit 1
fi
 
# Install PyTorch CPU build first (needs a custom index URL not in requirements.txt)
pip install -q torch --index-url https://download.pytorch.org/whl/cpu
 
# Install everything else from requirements.txt
pip install -q -r requirements.txt
 
success "Python packages installed"

# ── 6. Whisper model pre-download ────────────────────────────────
info "Pre-downloading Whisper base model..."
python3 -c "import whisper; whisper.load_model('base')"
success "Whisper base model cached"

# ── 7. Audio config check ─────────────────────────────────────────
info "Checking audio devices..."
python3 -c "
import sounddevice as sd
devices = sd.query_devices()
print('Available audio devices:')
for i, d in enumerate(devices):
    if d['max_input_channels'] > 0:
        print(f'  [{i}] INPUT:  {d[\"name\"]}')
    if d['max_output_channels'] > 0:
        print(f'  [{i}] OUTPUT: {d[\"name\"]}')
" || warn "Check audio hardware manually with: arecord -l"

# ── 8. Systemd service ────────────────────────────────────────────
info "Installing systemd service..."
SERVICE_DIR="$(pwd)"

sudo tee /etc/systemd/system/voice-assistant.service > /dev/null <<EOF
[Unit]
Description=AI Voice Assistant (Whisper + Qwen3.5)
After=network.target sound.target ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$SERVICE_DIR
Environment="HOME=/home/$USER"
ExecStart=/home/$USER/voice_env/bin/python3 $SERVICE_DIR/assistant.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
success "Systemd service installed → 'sudo systemctl start voice-assistant'"

# ── 9. Done ───────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo ""
echo "  To run manually:"
echo "    source ~/voice_env/bin/activate"
echo "    python3 assistant.py"
echo ""
echo "  To run as a service:"
echo "    sudo systemctl start voice-assistant"
echo "    sudo systemctl enable voice-assistant  # auto-start on boot"
echo ""
echo "  Logs:"
echo "    journalctl -u voice-assistant -f"
echo "    tail -f /tmp/voice_assistant.log"
echo ""
