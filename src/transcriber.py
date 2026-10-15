"""
Transcription module for NeuroClip.
Extracts audio and generates word-level timestamps using Whisper.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import whisper

class Transcriber:
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None

    @property
    def model(self):
        if self._model is None:
            print(f"🎙️ Carregando modelo Whisper ({self.model_size})...")
            self._model = whisper.load_model(self.model_size)
        return self._model

    def extract_audio(self, video_path: Path, output_audio: Path) -> Path:
        output_audio.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            str(output_audio)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_audio

    def transcribe(self, video_path: str | Path, language: str = "pt") -> Dict[str, Any]:
        video_file = Path(video_path).resolve()
        audio_file = video_file.with_suffix(".wav")
        
        print(f"🔊 Extraindo áudio de: {video_file.name}")
        self.extract_audio(video_file, audio_file)

        print(f"🧠 Transcrevendo com timestamps em nível de palavras ({language})...")
        result = self.model.transcribe(
            str(audio_file),
            language=language,
            word_timestamps=True,
            verbose=False
        )

        segments = []
        for seg in result.get("segments", []):
            words = []
            for w in seg.get("words", []):
                words.append({
                    "word": w.get("word", "").strip(),
                    "start": round(w.get("start", 0.0), 3),
                    "end": round(w.get("end", 0.0), 3),
                    "probability": round(w.get("probability", 1.0), 3)
                })
            segments.append({
                "id": seg.get("id"),
                "start": round(seg.get("start", 0.0), 3),
                "end": round(seg.get("end", 0.0), 3),
                "text": seg.get("text", "").strip(),
                "words": words
            })

        structured_data = {
            "video_path": str(video_file),
            "language": language,
            "full_text": result.get("text", "").strip(),
            "segments": segments
        }

        json_out = video_file.with_suffix(".transcript.json")
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Transcrição concluída: {len(segments)} blocos identificados.")
        return structured_data
