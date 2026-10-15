"""
NeuroClip Master Orchestrator.
Combines Whisper transcription, narrative segment selection,
TRIBE v2 neuro-attention validation, and 9:16 vertical editing with kinetic captions.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from transcriber import Transcriber
from segment_selector import SegmentSelector
from neuro_validator import NeuroValidator
from video_editor import VideoEditor

class NeuroClip:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.transcriber = Transcriber(model_size="base")
        self.selector = SegmentSelector(min_duration=20.0, max_duration=60.0)
        self.validator = NeuroValidator()
        self.editor = VideoEditor()

    def download_if_url(self, source: str) -> Path:
        if source.startswith("http://") or source.startswith("https://"):
            dest = self.output_dir / "downloaded_source.mp4"
            print(f"📥 Baixando vídeo via yt-dlp: {source}")
            cmd = ["yt-dlp", "-f", "b", "-o", str(dest), source]
            subprocess.run(cmd, check=True)
            return dest
        return Path(source).resolve()

    def run(self, source: str, max_clips: int = 3, min_score: float = 70.0):
        print("\n" + "="*60)
        print("🧠 INICIANDO PIPELINE UNIFICADO NEUROCLIP AI")
        print("="*60)

        # 1. Ingestão
        video_file = self.download_if_url(source)
        if not video_file.exists():
            print(f"❌ Arquivo não encontrado: {video_file}")
            return

        # 2. Transcrição com Whisper
        transcript_data = self.transcriber.transcribe(video_file)
        all_words = []
        for seg in transcript_data.get("segments", []):
            all_words.extend(seg.get("words", []))

        # 3. Seleção de Candidatos Narrativos
        candidates = self.selector.find_candidates(transcript_data, max_candidates=max_clips * 2)
        if not candidates:
            print("⚠️ Nenhum candidato atendeu aos critérios de duração.")
            return

        # 4. Auditoria Neurocientífica de Gancho (TRIBE v2)
        print("\n🔬 Executando auditoria neurocientífica de ativação cerebral...")
        audited_candidates = []
        for cand in candidates:
            neuro_report = self.validator.evaluate_hook(cand, all_words)
            cand["neuro"] = neuro_report
            audited_candidates.append(cand)

        # Ordenar pelos clipes com maior BOLD Attention Score
        audited_candidates.sort(key=lambda c: c["neuro"]["bold_attention_score"], reverse=True)

        # Filtrar apenas os que superam o critério mínimo
        selected = [c for c in audited_candidates if c["neuro"]["bold_attention_score"] >= min_score][:max_clips]
        if not selected:
            print("⚠️ Nenhum clipe atingiu a nota mínima. Pegando os melhores disponíveis...")
            selected = audited_candidates[:max_clips]

        # 5. Renderização dos Clipes 9:16
        print(f"\n✂️ Renderizando os {len(selected)} melhores clipes campeões em 9:16...")
        results = []
        for idx, clip in enumerate(selected, start=1):
            clip_name = f"clip_{idx:02d}_nota_{int(clip['neuro']['bold_attention_score'])}.mp4"
            out_clip_path = self.output_dir / clip_name

            clip_words = [w for w in all_words if clip["start"] <= w["start"] <= clip["end"]]
            
            self.editor.render_vertical_clip(
                input_video=video_file,
                start_time=clip["start"],
                end_time=clip["end"],
                output_clip=out_clip_path,
                transcript_words=clip_words
            )

            results.append({
                "clip_path": str(out_clip_path),
                "duration": clip["duration"],
                "start": clip["start"],
                "end": clip["end"],
                "bold_score": clip["neuro"]["bold_attention_score"],
                "peak_second": clip["neuro"]["peak_second"],
                "grade": clip["neuro"]["grade"],
                "hook_text": clip["hook_text"],
                "full_text": clip["full_text"]
            })

        # Relatório Final
        summary_file = self.output_dir / "neuroclip_relatorio.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n" + "="*60)
        print("🏆 RELATÓRIO FINAL DOS CLIPES CAMPEÕES")
        print("="*60)
        for r in results:
            print(f"🎬 {Path(r['clip_path']).name} | Nota BOLD: {r['bold_score']}/100 [{r['grade']}]")
            print(f"   ⏱️ Intervalo: {r['start']:.1f}s -> {r['end']:.1f}s (Pico aos {r['peak_second']}s)")
            print(f"   💬 Gancho: \"{r['hook_text'][:60]}...\"\n")
        print(f"📁 Todos os vídeos e relatórios salvos em: {self.output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuroClip: OpusClip + TRIBE v2 NeuroAI Engine")
    parser.add_argument("--input", required=True, help="URL do YouTube/Instagram ou caminho local do vídeo (.mp4)")
    parser.add_argument("--max-clips", type=int, default=3, help="Número máximo de clipes a exportar")
    parser.add_argument("--min-score", type=float, default=65.0, help="Nota mínima de ativação cerebral (0-100)")
    parser.add_argument("--output-dir", default="outputs", help="Pasta de saída dos cortes")

    args = parser.parse_args()
    app = NeuroClip(output_dir=args.output_dir)
    app.run(source=args.input, max_clips=args.max_clips, min_score=args.min_score)
