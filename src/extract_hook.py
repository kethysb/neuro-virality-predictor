"""
Helper script to download and extract the first 15 seconds of any video hook.
Requirements: yt-dlp, ffmpeg
"""

import subprocess
import sys
from pathlib import Path

def extract_hook(video_url_or_path: str, output_path: str = "gancho_teste_15s.mp4", duration: int = 15):
    output_file = Path(output_path).resolve()
    print(f"🎬 Processando gancho de {duration} segundos para: {output_file}")
    
    if video_url_or_path.startswith("http://") or video_url_or_path.startswith("https://"):
        temp_video = Path("temp_download.mp4")
        print(f"📥 Baixando via yt-dlp: {video_url_or_path}")
        subprocess.run(["yt-dlp", "-f", "b", "-o", str(temp_video), video_url_or_path], check=True)
        input_source = temp_video
    else:
        input_source = Path(video_url_or_path)

    cmd = [
        "ffmpeg", "-y",
        "-ss", "00:00:00",
        "-i", str(input_source),
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        str(output_file)
    ]
    subprocess.run(cmd, check=True)
    
    if video_url_or_path.startswith("http") and temp_video.exists():
        temp_video.unlink()
        
    print(f"✅ Gancho de {duration}s extraído com sucesso: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python extract_hook.py <url_ou_caminho_do_video> [saida.mp4] [duracao_segundos]")
        sys.exit(1)
    
    url_or_path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "gancho_teste_15s.mp4"
    dur = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    extract_hook(url_or_path, out, dur)
