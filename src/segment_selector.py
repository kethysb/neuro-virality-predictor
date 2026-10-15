"""
Segment selector module for NeuroClip.
Identifies high-potential candidate clips from transcripts using narrative arc analysis,
hook strength detection, and optional local LLM / Antigravity orchestration.
"""

import json
import re
import urllib.request
from typing import List, Dict, Any, Optional

HOOK_KEYWORDS = [
    # Português
    "ninguém fala", "segredo", "o problema é", "o erro que", "como fazer", "você não sabia",
    "cuidado", "preste atenção", "a verdade sobre", "nunca faça", "pouca gente sabe",
    "mudou tudo", "em vez de", "em minutos", "funciona assim", "alguém criou", "de graça",
    # Inglês
    "never", "secret", "the problem is", "biggest mistake", "how to", "nobody talks about",
    "stop doing", "warning", "the truth about", "changed everything", "for free"
]

class SegmentSelector:
    def __init__(self, min_duration: float = 25.0, max_duration: float = 60.0):
        self.min_duration = min_duration
        self.max_duration = max_duration

    def _score_hook_sentence(self, text: str) -> float:
        score = 50.0
        text_lower = text.lower()

        # Quebra de padrão / Palavras-chave de gancho
        for kw in HOOK_KEYWORDS:
            if kw in text_lower:
                score += 15.0

        # Perguntas abrem loops de curiosidade
        if "?" in text:
            score += 10.0

        # Números concretos aumentam credibilidade (ex: "15 segundos", "1 milhão")
        if re.search(r"\b\d+\b", text):
            score += 10.0

        # Frases curtas e diretas nos primeiros 5s convertem melhor que rodeios
        word_count = len(text.split())
        if 4 <= word_count <= 18:
            score += 10.0
        elif word_count > 30:
            score -= 10.0

        return min(100.0, max(0.0, score))

    def find_candidates(self, transcript_data: Dict[str, Any], max_candidates: int = 5) -> List[Dict[str, Any]]:
        segments = transcript_data.get("segments", [])
        if not segments:
            return []

        candidates = []
        n_seg = len(segments)

        for i in range(n_seg):
            start_t = segments[i]["start"]
            hook_text = segments[i]["text"]
            hook_score = self._score_hook_sentence(hook_text)

            # Acumular sentenças até atingir min_duration <= duração <= max_duration
            curr_text_parts = [hook_text]
            end_t = segments[i]["end"]
            
            for j in range(i + 1, n_seg):
                dur = segments[j]["end"] - start_t
                if dur > self.max_duration:
                    break
                curr_text_parts.append(segments[j]["text"])
                end_t = segments[j]["end"]

                if dur >= self.min_duration:
                    full_clip_text = " ".join(curr_text_parts)
                    total_score = hook_score * 0.6 + (100.0 if dur <= 45.0 else 80.0) * 0.4
                    
                    candidates.append({
                        "start": start_t,
                        "end": end_t,
                        "duration": round(end_t - start_t, 2),
                        "hook_text": hook_text,
                        "full_text": full_clip_text,
                        "preliminary_score": round(total_score, 1),
                        "start_segment_idx": i,
                        "end_segment_idx": j
                    })

        # Ordenar por pontuação e remover sobreposições excessivas (> 60%)
        candidates.sort(key=lambda x: x["preliminary_score"], reverse=True)
        
        filtered = []
        for cand in candidates:
            overlaps = False
            for accepted in filtered:
                overlap_start = max(cand["start"], accepted["start"])
                overlap_end = min(cand["end"], accepted["end"])
                overlap_dur = max(0.0, overlap_end - overlap_start)
                if overlap_dur > (cand["duration"] * 0.5):
                    overlaps = True
                    break
            if not overlaps:
                filtered.append(cand)
                if len(filtered) >= max_candidates:
                    break

        print(f"🎯 {len(filtered)} candidatos selecionados com base no potencial narrativo.")
        return filtered
