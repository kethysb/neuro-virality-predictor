"""
Video editor module for NeuroClip.
Performs 9:16 vertical cropping with smart face-centering,
audio normalization (-16 LUFS), and kinetic subtitle burning via FFmpeg.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import cv2
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

class VideoEditor:
    def __init__(self, target_width: int = 1080, target_height: int = 1920):
        self.target_width = target_width
        self.target_height = target_height
        self.cascade_path = Path(__file__).parent / "haarcascade_frontalface_default.xml"

    def detect_face_center_x(self, video_path: Path, start_time: float, sample_duration: float = 3.0) -> float:
        """Amostra os primeiros segundos para encontrar a coordenada X central do rosto do orador."""
        if not self.cascade_path.exists():
            return 0.5

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return 0.5

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        orig_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920.0
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000.0)

        face_cascade = cv2.CascadeClassifier(str(self.cascade_path))
        if face_cascade.empty():
            cap.release()
            return 0.5

        centers = []
        max_frames = int(fps * sample_duration)
        
        for _ in range(max_frames):
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
            if len(faces) > 0:
                faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                x, y, w, h = faces[0]
                centers.append((x + w / 2.0) / orig_w)

        cap.release()
        if centers:
            centers.sort()
            return centers[len(centers) // 2]
        return 0.5

    def generate_srt(self, words: List[Dict[str, Any]], clip_start: float, output_srt: Path):
        """Gera arquivo SRT com legendas dinâmicas em amarelo neon na safe-zone inferior."""
        def fmt_time(seconds: float) -> str:
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

        chunks = []
        curr_chunk = []
        for w in words:
            curr_chunk.append(w)
            if len(curr_chunk) >= 4 or w.get("word", "").endswith((".", "!", "?", ",")):
                chunks.append(curr_chunk)
                curr_chunk = []
        if curr_chunk:
            chunks.append(curr_chunk)

        with open(output_srt, "w", encoding="utf-8") as f:
            idx = 1
            for chunk in chunks:
                if not chunk:
                    continue
                start_s = max(0.0, chunk[0]["start"] - clip_start)
                end_s = max(start_s + 0.3, chunk[-1]["end"] - clip_start)
                text = " ".join([c["word"] for c in chunk])

                f.write(f"{idx}\n")
                f.write(f"{fmt_time(start_s)} --> {fmt_time(end_s)}\n")
                f.write(f"<font color=\"#FACC15\"><b>{text.upper()}</b></font>\n\n")
                idx += 1

    def render_vertical_clip(
        self,
        input_video: str | Path,
        start_time: float,
        end_time: float,
        output_clip: str | Path,
        transcript_words: Optional[List[Dict[str, Any]]] = None
    ) -> Path:
        in_file = Path(input_video).resolve()
        out_file = Path(output_clip).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)

        duration = end_time - start_time
        print(f"🎬 Renderizando corte 9:16 [{start_time:.1f}s -> {end_time:.1f}s] ({duration:.1f}s)...")

        # Inspecionar dimensões originais do vídeo
        cap = cv2.VideoCapture(str(in_file))
        orig_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920.0
        orig_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080.0
        cap.release()

        aspect_ratio = orig_w / orig_h

        # Se já for vertical (~9:16, ex: 1080x1920), só redimensiona
        if aspect_ratio < 0.65:
            video_filter = "scale=1080:1920"
        else:
            # Vídeo horizontal (16:9 / podcast): Rastreia rosto e recorta 9:16 centralizado no orador
            face_x_ratio = self.detect_face_center_x(in_file, start_time)
            video_filter = f"scale=-1:1920,crop=1080:1920:'max(0, min(in_w-1080, in_w*{face_x_ratio:.3f}-540))':0"

        srt_file = None
        if transcript_words:
            srt_file = out_file.with_suffix(".srt")
            self.generate_srt(transcript_words, start_time, srt_file)
            srt_escaped = str(srt_file).replace("\\", "/").replace(":", "\\:")
            sub_filter = f",subtitles='{srt_escaped}':force_style='FontSize=18,PrimaryColour=&H0015CCFA&,OutlineColour=&H00000000&,BorderStyle=3,Outline=2,Shadow=2,Alignment=2,MarginV=140'"
            video_filter += sub_filter

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", str(in_file),
            "-t", str(duration),
            "-vf", video_filter,
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "21",
            "-c:a", "aac",
            "-b:a", "192k",
            str(out_file)
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        if srt_file and srt_file.exists():
            srt_file.unlink()

        print(f"✅ Corte 9:16 salvo com sucesso em: {out_file.name}")
        return out_file
