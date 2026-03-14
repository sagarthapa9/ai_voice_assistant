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

# ─── Config ──────────────────────────────────────────────────────────────────

CONFIG = {
    # Ollama / LLM settings
    "ollama_url": "http://localhost:11434/api/generate",
    "model": "qwen2.5:1.5b",           # Ollama model tag for Qwen2.5 1.5B
    "num_predict": 80,


    # Whisper STT settings
    "whisper_model": "tiny",          # tiny | base | small | medium
    "whisper_device": "cpu",          # cpu or cuda (use cpu on Radxa)
    "language": "en",                 # STT language

    # Audio recording settings
    "sample_rate": 16000,
    "channels": 1,
    "silence_threshold": 0.01,        # RMS threshold to detect silence
    "silence_duration": 0.8,          # seconds of silence before stopping
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
        "/no_think"
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

# ─── STT: Whisper ─────────────────────────────────────────────────────────────

class WhisperSTT:
    def __init__(self, model_name="base", device="cpu"):
        console.print(f"[cyan]Loading Whisper [{model_name}] on {device}...[/cyan]")
        self.model = whisper.load_model(model_name, device=device)
        console.print("[green]✓ Whisper loaded[/green]")

    def transcribe(self, audio_path: str, language="en") -> str:
        # result = self.model.transcribe(
        #     audio_path,
        #     language=language,
        #     fp16=False,
        #     condition_on_previous_text=False,
        # )
        result = self.model.transcribe(
            audio_path,
            language="en",
            fp16=False,
            condition_on_previous_text=False,
            temperature=0,
            best_of=1,
            beam_size=1,
   )
        return result["text"].strip()


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

    def _rms(self, data):
        return np.sqrt(np.mean(data.astype(np.float32) ** 2))

    def record_until_silence(self) -> str:
        """Record until silence detected, return path to wav file."""
        console.print("[yellow]🎙  Listening... (speak now)[/yellow]")

        audio_chunks = []
        silent_chunks = 0
        chunk_size = int(self.sample_rate * 0.1)   # 100 ms chunks
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
        parts = [f"<|im_start|>system\n{self.system_prompt}/no_think<|im_end|>"]
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
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 256,
                "stop": ["<|im_end|>", "<|im_start|>"],
            },
        }

        try:
            resp = requests.post(self.url, json=payload, timeout=30)
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

# class TextToSpeech:
#     def __init__(self, rate=175, volume=0.9):
#         self.engine = pyttsx3.init()
#         self.engine.setProperty("rate", rate)
#         self.engine.setProperty("volume", volume)
#         # Try to pick a natural voice
#         voices = self.engine.getProperty("voices")
#         if voices:
#             # Prefer English voices
#             for v in voices:
#                 if "english" in v.name.lower() or "en" in v.id.lower():
#                     self.engine.setProperty("voice", v.id)
#                     break

#     def speak(self, text: str):
#         console.print(f"[green]🔊 Speaking:[/green] {text}")
#         self.engine.say(text)
#         self.engine.runAndWait()

class TextToSpeech:
    def __init__(self):
        from piper import PiperVoice
        self.voice = PiperVoice.load(
            "/home/sagar/piper-voices/en_US-lessac-medium.onnx",
            config_path="/home/sagar/piper-voices/en_US-lessac-medium.onnx.json",
        )

    # def speak(self, text: str):
    #     console.print(f"[green]🔊 Speaking:[/green] {text}")
    #     import wave, io
    #     with io.BytesIO() as buf:
    #         with wave.open(buf, 'wb') as wav:
    #             self.voice.synthesize(text, wav)
    #         buf.seek(0)
    #         data, samplerate = sf.read(buf)
    #     sd.play(data, samplerate)
    #     sd.wait()

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
            "[dim]Radxa Dragon Q6A · Whisper STT · Qwen2.5 7B · pyttsx3 TTS[/dim]",
            border_style="cyan",
        ))

        self.stt = WhisperSTT(
            model_name=CONFIG["whisper_model"],
            device=CONFIG["whisper_device"],
        )
        self.llm = QwenLLM(
            ollama_url=CONFIG["ollama_url"],
            model=CONFIG["model"],
            system_prompt=CONFIG["system_prompt"],
        )
        # self.tts = TextToSpeech(
        #     rate=CONFIG["tts_rate"],
        #     volume=CONFIG["tts_volume"],
        # )
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
        self.tts.speak("Voice assistant ready. How can I help you?")

        while self.running:
            try:
                # 1. Record
                audio_path = self.recorder.record_until_silence()
                if not audio_path:
                    continue

                # 2. Transcribe
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
