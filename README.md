# BabelBeam

Beam your words across languages.

BabelBeam is a Streamlit-based translation app with a modern galaxy-themed UI, multi-language support, and optional text-to-speech playback.

## Features

- Translate text between supported languages
- Auto-detect source language option
- Urdu and Arabic support with right-to-left (RTL) output rendering
- Optional backup translator when the primary engine fails
- Optional audio playback of translated text (gTTS)
- Clean, responsive Streamlit interface

## Supported Languages

- Auto Detect (source only)
- English (`en`)
- Hindi (`hi`)
- French (`fr`)
- German (`de`)
- Spanish (`es`)
- Urdu (`ur`)
- Arabic (`ar`)

## Tech Stack

- Python
- Streamlit
- deep-translator
- gTTS

## Installation

1. Clone the repository:

```bash
git clone https://github.com/zahram456/BabelBeam.git
cd BabelBeam
```

2. Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install streamlit deep-translator gTTS
```

## Run the App

```bash
python -m streamlit run app.py
```

## Usage

1. Choose source and target languages.
2. Enter text in the input box.
3. Click **Translate**.
4. Optionally enable audio playback.

## Troubleshooting

- `ModuleNotFoundError`: install missing packages using pip.
- If translation fails temporarily, enable **Use backup translator if needed**.
- If audio fails for a language, translation still works and text output is shown.

## License

This project is open-source for educational and personal use.
