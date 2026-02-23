import io
import re
import time
import unicodedata
from html import escape

import streamlit as st
from deep_translator import GoogleTranslator, MyMemoryTranslator
from gtts import gTTS
from gtts.lang import tts_langs

st.set_page_config(page_title="BabelBeam", page_icon="BB", layout="centered")

LANGUAGES = {
    "Auto Detect": "auto",
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Urdu": "ur",
    "Arabic": "ar",
}

RTL_LANGS = {"ur", "ar"}
TTS_OVERRIDES = {
    "ur": {"lang": "ur", "tld": "com.pk"},
    "ar": {"lang": "ar", "tld": "com"},
}


def normalize_text(value: str) -> str:
    """Normalize user text to improve model input consistency."""
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def split_for_translation(value: str, max_len: int = 3000) -> list[str]:
    """Split long text into sentence-aware chunks to avoid API truncation/quality drop."""
    if len(value) <= max_len:
        return [value]

    parts: list[str] = []
    paragraphs = value.split("\n")
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) <= max_len:
            parts.append(para)
            continue

        # Split by common sentence boundaries, including Arabic question mark (\u061F).
        sentences = re.split(r"(?<=[.!?\u061F])\s+", para)
        current = ""
        for sentence in sentences:
            if not sentence:
                continue
            candidate = f"{current} {sentence}".strip() if current else sentence
            if len(candidate) <= max_len:
                current = candidate
            else:
                if current:
                    parts.append(current)
                if len(sentence) <= max_len:
                    current = sentence
                else:
                    # Hard split for very long sentence.
                    for i in range(0, len(sentence), max_len):
                        parts.append(sentence[i : i + max_len])
                    current = ""
        if current:
            parts.append(current)
    return parts or [value]


def translate_google(value: str, source: str, target: str, retries: int = 2) -> str:
    last_exc = None
    for attempt in range(retries + 1):
        try:
            return GoogleTranslator(source=source, target=target).translate(value)
        except Exception as exc:  # pragma: no cover - network/API path
            last_exc = exc
            if attempt < retries:
                time.sleep(0.5)
    raise RuntimeError(str(last_exc))


if "source_name" not in st.session_state:
    st.session_state.source_name = "Auto Detect"
if "target_name" not in st.session_state:
    st.session_state.target_name = "English"
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "translated_lang" not in st.session_state:
    st.session_state.translated_lang = "en"

st.markdown(
    """
    <style>
    :root {
        --bb-bg: #04050b;
        --bb-panel: #0d1224;
        --bb-panel-alt: #0f1630;
        --bb-border: #2a3768;
        --bb-primary: #4f7cff;
        --bb-primary-strong: #7c4dff;
        --bb-text: #edf2ff;
        --bb-muted: #aab6e8;
        --bb-accent: #2dd4bf;
        --bb-glow: #22c55e;
    }
    .stApp {
        background:
            radial-gradient(75rem 34rem at -15% -25%, rgba(79, 124, 255, 0.35) 0%, transparent 58%),
            radial-gradient(58rem 30rem at 115% -18%, rgba(124, 77, 255, 0.30) 0%, transparent 62%),
            radial-gradient(34rem 20rem at 80% 80%, rgba(34, 197, 94, 0.20) 0%, transparent 65%),
            radial-gradient(24rem 14rem at 20% 78%, rgba(45, 212, 191, 0.16) 0%, transparent 68%),
            var(--bb-bg);
        color: var(--bb-text);
    }
    .bb-hero {
        background:
            linear-gradient(140deg, rgba(2, 6, 23, 0.92) 0%, rgba(20, 28, 58, 0.94) 45%, rgba(53, 24, 90, 0.94) 100%);
        color: #ffffff;
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 14px;
        border: 1px solid rgba(92, 119, 255, 0.55);
        box-shadow:
            0 16px 40px rgba(10, 16, 38, 0.7),
            inset 0 0 0 1px rgba(151, 168, 255, 0.15);
    }
    .bb-eyebrow {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.9;
    }
    .bb-title {
        font-size: 2rem;
        font-weight: 800;
        margin: 4px 0 2px 0;
        line-height: 1.1;
    }
    .bb-subtitle {
        font-size: 1rem;
        opacity: 0.92;
        margin: 0;
    }
    .bb-card {
        background: var(--bb-panel);
        border: 1px solid var(--bb-border);
        border-radius: 14px;
        padding: 14px;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
    }
    .bb-output {
        background: var(--bb-panel-alt);
        border: 1px solid var(--bb-border);
        border-radius: 14px;
        padding: 14px;
        color: var(--bb-text);
        line-height: 1.65;
        font-size: 1.08rem;
        white-space: pre-wrap;
        box-shadow:
            inset 0 0 0 1px rgba(79, 124, 255, 0.14),
            0 10px 24px rgba(0, 0, 0, 0.25);
    }
    .bb-meta {
        color: var(--bb-muted);
        font-size: 0.88rem;
        margin-top: 6px;
    }
    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(98, 125, 255, 0.45);
        background: linear-gradient(135deg, rgba(27, 39, 79, 0.9), rgba(37, 31, 78, 0.9));
        color: #e8eeff;
        transition: all 0.18s ease-in-out;
    }
    .stButton > button:hover {
        border-color: rgba(45, 212, 191, 0.75);
        box-shadow: 0 0 0 2px rgba(45, 212, 191, 0.15), 0 0 22px rgba(34, 197, 94, 0.28);
        transform: translateY(-1px);
    }
    .stCheckbox label, .stSelectbox label, .stTextArea label {
        color: var(--bb-muted) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="bb-hero">
        <div class="bb-eyebrow">BabelBeam Translator</div>
        <div class="bb-title">BabelBeam</div>
        <p class="bb-subtitle">Beam your words across languages.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

target_options = [name for name in LANGUAGES.keys() if name != "Auto Detect"]
if st.session_state.target_name not in target_options:
    st.session_state.target_name = "English"

with st.container():
    st.markdown('<div class="bb-card">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([5, 1.2, 5])
    with c1:
        source_name = st.selectbox("From", list(LANGUAGES.keys()), key="source_name")
    with c2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        swap_clicked = st.button("Swap", use_container_width=True)
    with c3:
        target_name = st.selectbox("To", target_options, key="target_name")

    if swap_clicked:
        if st.session_state.source_name == "Auto Detect":
            st.info("Set a specific source language before swapping.")
        else:
            old_source = st.session_state.source_name
            st.session_state.source_name = st.session_state.target_name
            st.session_state.target_name = old_source
            st.rerun()

    text = st.text_area(
        "Enter text",
        key="input_text",
        placeholder="Type or paste text you want to translate...",
        height=180,
    )

    words = len(text.split()) if text.strip() else 0
    chars = len(text)
    m1, m2 = st.columns(2)
    m1.markdown(f'<div class="bb-meta">Words: <strong>{words}</strong></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="bb-meta">Characters: <strong>{chars}</strong></div>', unsafe_allow_html=True)

    b1, b2 = st.columns([3, 2])
    translate_clicked = b1.button("Translate", type="primary", use_container_width=True)
    clear_clicked = b2.button("Clear Text", use_container_width=True)

    allow_fallback = st.checkbox(
        "Use backup translator if needed",
        value=False,
        help="Leave this off for best quality. Turn on only when Google translation fails.",
    )
    enable_audio = st.checkbox("Play translated audio", value=True)
    st.markdown("</div>", unsafe_allow_html=True)

if clear_clicked:
    st.session_state.input_text = ""
    st.session_state.translated_text = ""
    st.rerun()

if translate_clicked:
    if not st.session_state.input_text.strip():
        st.warning("Please enter some text first.")
    else:
        source_code = LANGUAGES[st.session_state.source_name]
        target_code = LANGUAGES[st.session_state.target_name]
        clean_text = normalize_text(st.session_state.input_text)

        if source_code == target_code:
            st.info("Source and target languages are the same. Showing original text.")
            translated = clean_text
        else:
            translated = None

        if translated is None:
            try:
                chunks = split_for_translation(clean_text)
                translated_chunks = [
                    translate_google(chunk, source=source_code, target=target_code) for chunk in chunks
                ]
                translated = "\n\n".join(translated_chunks)
            except Exception:
                translated = None

        if translated is None and allow_fallback:
            try:
                mm_source = "auto" if source_code == "auto" else source_code
                chunks = split_for_translation(clean_text, max_len=800)
                translated_chunks = [
                    MyMemoryTranslator(source=mm_source, target=target_code).translate(chunk)
                    for chunk in chunks
                ]
                translated = "\n\n".join(translated_chunks)
                st.info("Used backup translation engine for this result.")
            except Exception as exc:
                st.error(f"Translation failed: {exc}")
                st.stop()
        elif translated is None:
            st.error("Google translation failed. Enable backup translator and try again.")
            st.stop()

        st.session_state.translated_text = translated
        st.session_state.translated_lang = target_code

if st.session_state.translated_text:
    translated = st.session_state.translated_text
    target_code = st.session_state.translated_lang

    st.subheader("Translated Text")
    direction = "rtl" if target_code in RTL_LANGS else "ltr"
    align = "right" if direction == "rtl" else "left"
    safe_translated = escape(translated)
    st.markdown(
        f"""
        <div class="bb-output" style="direction: {direction}; text-align: {align};">
            {safe_translated}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if enable_audio:
        try:
            audio_buffer = io.BytesIO()
            tts_cfg = TTS_OVERRIDES.get(target_code, {"lang": target_code, "tld": "com"})
            tts_lang = tts_cfg["lang"]
            tts_tld = tts_cfg["tld"]

            if tts_lang not in tts_langs():
                st.info("Audio is not available for this language in gTTS.")
            else:
                gTTS(text=translated, lang=tts_lang, tld=tts_tld).write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                st.audio(audio_buffer.read(), format="audio/mp3")
        except Exception as tts_exc:
            st.warning(f"Translation worked, but audio failed: {tts_exc}")


