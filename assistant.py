#!/usr/bin/env python3
"""
AI Voice Assistant - Radxa Dragon Q6A
Stack: Whisper (STT) → Qwen3.5 7B (LLM) → Kokoro/pyttsx3 (TTS)
"""

import os
import sys
import json
import time
import queue
import threading
import tempfile
import logging
import signal
from pathlib import Path
from datetime import datetime

import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper
import requests
import pyttsx3
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

# Suppress ONNX Runtime GPU warning
os.environ["ORT_DISABLE_GPU"] = "1"

# ─── Config ──────────────────────────────────────────────────────────────────

CONFIG = {
    # Ollama / LLM settings
    "ollama_url": "http://localhost:11434/api/generate",
    "model": "qwen3.5:0.8b",           # Ollama model tag for Qwen3.5 0.8B
    "num_predict": 80,

    # Wake word settings
    "wake_word_model": "/home/sagar/wake-models/alexa_v0.1.onnx",
    "wake_word_threshold": 0.5,        # 0.0 to 1.0 — higher = less sensitive

    # Whisper STT settings
    "whisper_model": "tiny",          # tiny | base | small | medium
    "whisper_device": "cpu",          # cpu or cuda (use cpu on Radxa)
    "language": "en",                 # STT language

    # Audio recording settings
    "sample_rate": 16000,
    "channels": 1,
    "silence_threshold": 0.005,        # RMS threshold to detect silence
    "silence_duration": 0.6,          # seconds of silence before stopping
    "max_record_seconds": 30,

    # TTS settings
    "tts_rate": 175,                   # words per minute
    "tts_volume": 0.9,

    # Conversation memory
    "max_history": 10,                 # max message pairs to keep

    # System prompt
    "system_prompt": (
        "You are a helpful, concise voice assistant running on a Radxa Dragon Q6A "
        "edge device. Keep responses short and natural for spoken conversation. "
        "Avoid markdown, bullet points, or special formatting — speak in plain sentences."
    ),
}

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/tmp/voice_assistant.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("VoiceAssistant")
console = Console()
# ─── Wake Word Detector ───────────────────────────────────────────────────────
 
class WakeWordDetector:
    def __init__(self, model_path: str, threshold: float = 0.5):
        from openwakeword.model import Model
        console.print("[cyan]Loading wake word model (Alexa)...[/cyan]")
        self.model = Model(
            wakeword_model_paths=[model_path],
            vad_threshold=0.0,
        )
        self.threshold = threshold
        self.chunk_size = 1280   # 80ms at 16000 Hz — required by openWakeWord
        console.print("[green]✓ Wake word model loaded — say 'Alexa' to activate[/green]")
 
    def listen_for_wake_word(self):
        """Block until 'Alexa' is detected. Returns when heard."""
        console.print("[dim]Waiting for wake word — say 'Alexa'...[/dim]")

        with sd.InputStream(
            samplerate=16000,
            channels=1,
            dtype="int16",
            blocksize=self.chunk_size,
        ) as stream:
            # Drain first 20 chunks (~1.6 seconds) to flush:
            # 1. Audio device buffer leftover from speaker playback
            # 2. openWakeWord internal sliding window from last detection
            # 3. Any room echo/reverb still decaying
            for _ in range(20):
                stream.read(self.chunk_size)

            # Reset model state after draining
            try:
                self.model.reset()
            except AttributeError:
                for key in self.model.prediction_buffer:
                    self.model.prediction_buffer[key].clear()

            console.print("[dim]Ready — say 'Alexa'[/dim]")

            # Now actually listen for wake word
            while True:
                chunk, _ = stream.read(self.chunk_size)
                prediction = self.model.predict(chunk.flatten())
                score = list(prediction.values())[0]
                if score >= self.threshold:
                    console.print(f"[green]✓ Alexa detected! (score={score:.2f})[/green]")
                    return
# ─── STT: Whisper ─────────────────────────────────────────────────────────────
class WhisperSTT:
    def __init__(self, model_name="tiny", device="cpu"):
        from faster_whisper import WhisperModel
        console.print(f"[cyan]Loading faster-whisper [{model_name}]...[/cyan]")
        self.model = WhisperModel(
            model_name,
            device=device,
            compute_type="int8",   # int8 quantisation — faster on CPU
        )
        console.print("[green]✓ faster-whisper loaded[/green]")

    def transcribe(self, audio_path: str, language="en") -> str:
        segments, _ = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=1,
            best_of=1,
            temperature=0,
            vad_filter=True,       # skips silent parts automatically
            vad_parameters=dict(
                min_silence_duration_ms=300,
            ),
        )
        return " ".join(s.text.strip() for s in segments)
# ─── Audio Recorder ──────────────────────────────────────────────────────────

class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1,
                 silence_threshold=0.01, silence_duration=1.5,
                 max_seconds=30):
        self.sample_rate = sample_rate
        self.channels = channels
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_seconds = max_seconds

    def _beep(self, style="start"):
        """
        Play a polished chime.
        style='start' — rising two-tone (like Alexa wake confirmation)
        style='stop'  — falling single tone with soft fade (like Google done)
        """
        sr = 48000

        if style == "start":
            # Rising two-tone chime — short low note then higher note
            def tone(freq, dur, fade=0.015):
                t = np.linspace(0, dur, int(sr * dur), endpoint=False)
                wave = np.sin(2 * np.pi * freq * t)
                # Smooth fade in and out
                fade_samples = int(sr * fade)
                wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
                wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
                return wave

            # Two notes: 880 Hz then 1174 Hz (a musical fifth apart)
            note1 = tone(880,  0.10) * 0.35
            gap   = np.zeros(int(sr * 0.02))   # 20ms gap between notes
            note2 = tone(1174, 0.14) * 0.40
            audio = np.concatenate([note1, gap, note2])

        elif style == "stop":
            # Falling tone with pitch sweep — smooth and satisfying
            dur = 0.18
            t = np.linspace(0, dur, int(sr * dur), endpoint=False)
            # Frequency glides down from 880 to 660 Hz
            freq = np.linspace(880, 660, len(t))
            wave = np.sin(2 * np.pi * np.cumsum(freq) / sr)
            # Bell-curve volume envelope — soft attack and decay
            envelope = np.exp(-((t - dur * 0.3) ** 2) / (2 * (dur * 0.25) ** 2))
            audio = (wave * envelope * 0.45)

        # Convert to stereo float32 and play
        stereo = np.column_stack([audio, audio]).astype(np.float32)
        sd.play(stereo, sr, device=0)
        sd.wait()

    def _rms(self, data):
        # Normalise int16 range (-32768 to 32767) to float (-1.0 to 1.0)
        normalised = data.astype(np.float32) / 32768.0
        return np.sqrt(np.mean(normalised ** 2))

    def record_until_silence(self) -> str:
        """Record until silence detected, return path to wav file."""
        console.print("[yellow]🎙  Listening... (speak now)[/yellow]")
        self._beep(style="start")   #start listening

        audio_chunks = []
        silent_chunks = 0
        #chunk_size = int(self.sample_rate * 0.1)   # 100 ms chunks
        chunk_size = int(self.sample_rate * 0.2) # 200 ms chunks for more stable silence detection
        silence_limit = int(self.silence_duration / 0.1)
        max_chunks = int(self.max_seconds / 0.1)
        recording_started = False

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            blocksize=chunk_size,
        ) as stream:
            for _ in range(max_chunks):
                data, _ = stream.read(chunk_size)
                rms = self._rms(data)

                if rms > self.silence_threshold:
                    recording_started = True
                    silent_chunks = 0
                elif recording_started:
                    silent_chunks += 1

                if recording_started:
                    audio_chunks.append(data.copy())

                if recording_started and silent_chunks >= silence_limit:
                    self._beep(style="stop")   #stopped listening
                    break

        if not audio_chunks:
            return None

        audio_np = np.concatenate(audio_chunks, axis=0)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sf.write(tmp.name, audio_np, self.sample_rate, subtype="PCM_16")
        return tmp.name


# ─── LLM: Qwen via Ollama ────────────────────────────────────────────────────

class QwenLLM:
    def __init__(self, ollama_url: str, model: str, system_prompt: str):
        self.url = ollama_url
        self.model = model
        self.system_prompt = system_prompt
        self.history = []   # list of {"role": "user"|"assistant", "content": "..."}

    def _build_prompt(self, user_msg: str) -> str:
        """Build Qwen chat-format prompt."""
        parts = [f"<|im_start|>system\n{self.system_prompt}<|im_end|>"]
        for turn in self.history:
            role = turn["role"]
            parts.append(f"<|im_start|>{role}\n{turn['content']}<|im_end|>")
        parts.append(f"<|im_start|>user\n{user_msg}<|im_end|>")
        parts.append("<|im_start|>assistant\n")
        return "\n".join(parts)

    def chat(self, user_msg: str) -> str:
        prompt = self._build_prompt(user_msg)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 256,
                "stop": ["<|im_end|>", "<|im_start|>"],
            },
        }

        try:
            resp = requests.post(self.url, json=payload, timeout=60) # longer timeout for first inference
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            answer = "Sorry, I cannot reach the language model. Please make sure Ollama is running."
        except Exception as e:
            log.error(f"LLM error: {e}")
            answer = "I encountered an error processing your request."

        # Update history
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": answer})
        if len(self.history) > CONFIG["max_history"] * 2:
            self.history = self.history[-CONFIG["max_history"] * 2:]

        return answer

    def reset(self):
        self.history = []


# ─── TTS ─────────────────────────────────────────────────────────────────────
class TextToSpeech:
    def __init__(self):
        from piper import PiperVoice
        self.voice = PiperVoice.load(
            "/home/sagar/piper-voices/en_US-lessac-medium.onnx",
            config_path="/home/sagar/piper-voices/en_US-lessac-medium.onnx.json",
        )

    def speak(self, text: str):
        console.print(f"[green]🔊 Speaking:[/green] {text}")
        import numpy as np
        from scipy.signal import resample_poly
        from math import gcd

        chunks = list(self.voice.synthesize(text))
        if not chunks:
            log.warning("Piper returned no audio chunks")
            return

        # Concatenate all sentence chunks into one array
        audio = np.concatenate([chunk.audio_float_array for chunk in chunks])
        samplerate = chunks[0].sample_rate  # 22050

        # Resample from 22050 to 48000 for Jabra
        target_rate = 48000
        if samplerate != target_rate:
            g = gcd(int(samplerate), target_rate)
            audio = resample_poly(audio, target_rate // g, int(samplerate) // g)

        # Mono to stereo for Jabra
        stereo = np.column_stack([audio, audio]).astype(np.float32)

        sd.play(stereo, target_rate, device=0)
        sd.wait()
# ─── Main Assistant Loop ──────────────────────────────────────────────────────

class VoiceAssistant:
    def __init__(self):
        console.print(Panel.fit(
            "[bold cyan]AI Voice Assistant[/bold cyan]\n"
            "[dim]Radxa Dragon Q6A · faster-whisper · Qwen3.5 2B · pyttsx3 TTS[/dim]",
            border_style="cyan",
        ))
        self.wake = WakeWordDetector(
            model_path=CONFIG["wake_word_model"],
            threshold=CONFIG["wake_word_threshold"],
        )

        self.stt = WhisperSTT(
            model_name=CONFIG["whisper_model"],
            device=CONFIG["whisper_device"],
        )
        self.llm = QwenLLM(
            ollama_url=CONFIG["ollama_url"],
            model=CONFIG["model"],
            system_prompt=CONFIG["system_prompt"],
        )

        self.tts = TextToSpeech()
        self.recorder = AudioRecorder(
            sample_rate=CONFIG["sample_rate"],
            channels=CONFIG["channels"],
            silence_threshold=CONFIG["silence_threshold"],
            silence_duration=CONFIG["silence_duration"],
            max_seconds=CONFIG["max_record_seconds"],
        )

        self.running = True
        signal.signal(signal.SIGINT, self._shutdown)

    def _shutdown(self, *_):
        self.running = False
        console.print("\n[red]Shutting down...[/red]")
        sys.exit(0)

    def run(self):
        #self.tts.speak("Voice assistant ready. How can I help you?")
        self.tts.speak("Voice assistant ready. Say Alexa to activate.")

        while self.running:
            try:
                # 1. Wait for wake word
                self.wake.listen_for_wake_word()

                # Short pause so the word "Alexa" is not captured in the recording
                time.sleep(0.5)

                # 2. Record
                audio_path = self.recorder.record_until_silence()
                if not audio_path:
                    continue

                # 3. Transcribe
                console.print("[cyan]Transcribing...[/cyan]")
                t0 = time.time()
                text = self.stt.transcribe(audio_path, language=CONFIG["language"])
                os.unlink(audio_path)

                if not text or len(text.strip()) < 2:
                    console.print("[dim]No speech detected.[/dim]")
                    continue

                console.print(f"[bold white]You:[/bold white] {text}  [dim]({time.time()-t0:.1f}s)[/dim]")

                # Handle special commands
                lower = text.lower().strip()
                if any(w in lower for w in ["reset", "clear history", "new conversation"]):
                    self.llm.reset()
                    self.tts.speak("Conversation history cleared.")
                    continue
                if any(w in lower for w in ["goodbye", "bye", "exit", "quit", "stop"]):
                    self.tts.speak("Goodbye!")
                    break

                # 3. LLM inference
                console.print("[cyan]Thinking...[/cyan]")
                t1 = time.time()
                response = self.llm.chat(text)
                console.print(f"[bold green]Assistant:[/bold green] {response}  [dim]({time.time()-t1:.1f}s)[/dim]")

                # 4. Speak
                self.tts.speak(response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                log.error(f"Loop error: {e}", exc_info=True)
                self.tts.speak("Sorry, something went wrong. Please try again.")


if __name__ == "__main__":
    VoiceAssistant().run()
