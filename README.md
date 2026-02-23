# BabelBeam

**BabelBeam** is a polished Streamlit translation application designed for fast, readable, and practical multilingual translation.

> **Tagline:** Beam your words across languages.

## Overview

BabelBeam provides a focused translation workflow with strong usability for both left-to-right and right-to-left languages. It combines a primary Google-based translation path with optional fallback support and in-app text-to-speech playback.

## Key Features

- Professional Streamlit interface with a custom galaxy theme
- Source language auto-detection support
- Right-to-left (RTL) rendering for Urdu and Arabic
- Translation quality improvements for long text (normalization + chunking)
- Retry handling for transient translation failures
- Optional fallback translation engine when primary translation fails
- Optional text-to-speech playback using gTTS

## Supported Languages

| Language | Code | Notes |
|---|---|---|
| Auto Detect | `auto` | Source only |
| English | `en` | Source/Target |
| Hindi | `hi` | Source/Target |
| French | `fr` | Source/Target |
| German | `de` | Source/Target |
| Spanish | `es` | Source/Target |
| Urdu | `ur` | Source/Target, RTL output |
| Arabic | `ar` | Source/Target, RTL output |

## Tech Stack

- Python 3.10+
- [Streamlit](https://streamlit.io/)
- [deep-translator](https://pypi.org/project/deep-translator/)
- [gTTS](https://pypi.org/project/gTTS/)

## Project Structure

```text
BabelBeam/
+- app.py
+- README.md
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/zahram456/BabelBeam.git
cd BabelBeam
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install streamlit deep-translator gTTS
```

### 3. Run the app

```bash
python -m streamlit run app.py
```

## Usage

1. Select source and target languages.
2. Enter or paste text in the input panel.
3. Click **Translate**.
4. (Optional) Enable backup translator if the primary service fails.
5. (Optional) Enable audio playback for translated output.

## Reliability Notes

- For best quality, keep backup translation disabled unless needed.
- For long paragraphs, BabelBeam automatically splits text into safer chunks to reduce API truncation issues.
- If source language is known, selecting it manually often improves accuracy versus auto-detect.

## Troubleshooting

- **`ModuleNotFoundError`**: install missing packages with pip.
- **Translation failure**: retry, then enable backup translator.
- **Audio unavailable**: some language/voice combinations may be limited by gTTS; text translation remains available.

## License

This project is available for educational and personal use.
