# 🧠 Neuro-Virality Predictor & NeuroClip AI

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kethysb/neuro-virality-predictor/blob/main/notebooks/neuro_virality_predictor.ipynb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Model: Meta TRIBE v2](https://img.shields.io/badge/Model-Meta_TRIBE_v2-purple.svg)](https://github.com/facebookresearch/tribev2)

> **O "OpusClip Neurocientífico": Transcreva, selecione momentos narrativos, audite a atenção cerebral humana via fMRI (Meta TRIBE v2) e renderize clipes verticais 9:16 com legendas kinéticas automáticas.**

---

## 🗺️ Visualização de Ativação Cortical (Resultado Real de 15s)

Abaixo está o resultado de inferência de um gancho de 15 segundos extraído de um Reel do Instagram, alinhando **vídeo frame a frame**, **onda acústica do áudio**, **transcrição fonética do Whisper** e o **mapa térmico 3D da superfície cerebral** (`fsaverage5`):

![Mapa de Ativação Cerebral fMRI](assets/gancho_cerebro_3d_15s.png)

---

## ⚡ Novo Módulo: NeuroClip AI (OpusClip Open Source + Neurociência)

O **NeuroClip** junta o melhor dos dois mundos:
1. **Ingestão Universal**: Baixa vídeos de links do YouTube, Instagram ou arquivos locais.
2. **Transcrição em Nível de Palavras**: Usa **Whisper** para mapear cada palavra e timestamp exato.
3. **Seleção de Melhores Momentos (Sem APIs Pagas)**: Analisa quebras de padrão, ganchos e narrativa sem depender de créditos caros da OpenAI.
4. **Auditoria Neurocientífica (TRIBE v2)**: Avalia o sinal BOLD dos primeiros 15s e só aprova o corte se a retenção biológica for alta.
5. **Renderizador 9:16 com Rastreio de Rosto**: Centraliza o orador dinamicamente, normaliza o áudio em -16 LUFS e queima legendas kinéticas em amarelo neon (`#FACC15`).

### 💻 Como rodar o NeuroClip no seu computador:

```bash
# Executar no vídeo baixado ou link direto
python src/neuroclip.py --input "https://www.youtube.com/watch?v=SEU_VIDEO" --max-clips 3
```

Saída gerada na pasta `outputs/`:
* `clip_01_nota_98.mp4` (Corte vertical 1080x1920 pronto para Reels/TikTok)
* `neuroclip_relatorio.json` (Diagnóstico completo de pontuação e segundo exato do pico de atenção)

---

## 🔬 Como Funciona a Ciência por Trás?

Diferente de métricas superficiais de "visualizações" ou "likes", este pipeline prevê a **física e a biologia da atenção humana**:

1. **Quebra do Piloto Automático (DMN)**: Ao rolar o feed, o espectador está na *Default Mode Network* (devaneio mental / gasto mínimo de energia). Um gancho forte nos primeiros 3 segundos desativa a DMN e recruta a **Rede de Saliência**.
2. **Sinal BOLD (*Blood-Oxygen-Level Dependent*)**: O modelo **TRIBE v2** (treinado em centenas de horas de exames de ressonância magnética funcional com humanos assistindo a vídeos) prevê exatamente para onde o sangue oxigenado corre no cérebro a cada segundo.
3. **Pico no Giro Temporal Superior (STG)**: O ápice de atenção aos **00:03 - 00:04 segundos** (mancha incandescente amarela/branca) corresponde à decodificação semântica imediata da promessa do vídeo.

---

## 🏗️ Arquitetura do Sistema

```
[ Vídeo Longo / Link ]
          │
          ▼
 [ Whisper Transcriber ] ──► [ Segment Selector (Antigravity Logic) ]
                                            │
                                            ▼
                               [ TRIBE v2 Neuro Validator ]
                               (Sinal BOLD > 80? Aprovado!)
                                            │
                                            ▼
                             [ Video Editor 9:16 (FFmpeg) ]
                             - Face-Centering & Auto-Crop
                             - Legendas Kinéticas (#FACC15)
                             - Loudnorm -16 LUFS
                                            │
                                            ▼
                               [ Clipes Campeões Prontos ]
```

---

## 🚀 Como Executar em 1 Clique (Google Colab)

A forma mais rápida de rodar a predição fMRI 3D completa em qualquer GPU T4 gratuita:

1. Clique no botão [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kethysb/neuro-virality-predictor/blob/main/notebooks/neuro_virality_predictor.ipynb)
2. Faça o upload do seu vídeo de até 15–30 segundos no Colab (ex: `gancho_teste_15s.mp4`).
3. Execute todas as células (`Ambiente de Execução > Executar tudo`).
4. O notebook gera e baixa automaticamente o mapa de ativação 3D (`gancho_cerebro_3d_15s.png`).

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

Feito com 🧠 por [Kethely Soriano](https://github.com/kethysb).
