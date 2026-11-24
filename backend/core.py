"""Shared logic: explain a form field and turn it into speech.

Used by both lambda_handler.py (AWS) and local_server.py (offline demo).
Order of preference for explanations:
  1. Amazon Bedrock (if BEDROCK_MODEL_ID is set and boto3 is available)
  2. Built-in glossary for common SSP fields (works offline)
  3. Generic fallback sentence
"""
import base64
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "glossary_ssp.json"), encoding="utf-8") as f:
    GLOSSARY = json.load(f)

LANG_NAMES = {"en": "English", "hi": "Hindi", "kn": "Kannada"}
GENERIC = {
    "en": "Fill this field carefully. Keep the matching document ready.",
    "hi": "इस खाने को ध्यान से भरें। संबंधित दस्तावेज़ पास रखें।",
    "kn": "ಈ ಕ್ಷೇತ್ರವನ್ನು ಎಚ್ಚರಿಕೆಯಿಂದ ಭರ್ತಿ ಮಾಡಿ. ಸಂಬಂಧಿತ ದಾಖಲೆ ಹತ್ತಿರ ಇಟ್ಟುಕೊಳ್ಳಿ.",
}
_cache = {}


def _glossary_lookup(label, lang):
    text = label.lower()
    for entry in GLOSSARY:
        if any(k in text for k in entry["keywords"]):
            return {"explanation": entry[lang], "documents": entry.get("documents", [])}
    return None


def _bedrock_explain(label, ftype, options, lang):
    model_id = os.environ.get("BEDROCK_MODEL_ID")
    if not model_id:
        return None
    try:
        import boto3  # available in the Lambda runtime
        client = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "ap-south-1"))
        prompt = (
            f"A person is filling the Karnataka State Scholarship Portal form. "
            f"Field label: '{label}'. Field type: {ftype}. Options: {options or 'none'}.\n"
            f"Explain in simple {LANG_NAMES[lang]}, in at most 2 short sentences, what to enter "
            f"and which document they should keep ready. Do not ask for personal data."
        )
        resp = client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 200, "temperature": 0.2},
        )
        return resp["output"]["message"]["content"][0]["text"].strip()
    except Exception:
        return None


def explain(payload):
    label = (payload.get("label") or "").strip()[:200]
    ftype = payload.get("type", "text")
    options = payload.get("options", [])[:15]
    lang = payload.get("lang", "en")
    if lang not in LANG_NAMES:
        lang = "en"
    key = (label.lower(), lang)
    if key in _cache:
        return _cache[key]

    result = _glossary_lookup(label, lang)
    if result is None:
        text = _bedrock_explain(label, ftype, options, lang) or GENERIC[lang]
        result = {"explanation": text, "documents": []}
    _cache[key] = result
    return result


def tts(text, lang="en"):
    """ElevenLabs text-to-speech. Returns base64 mp3, or None if not configured."""
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID")
    if not api_key or not voice_id:
        return None
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps({"text": text, "model_id": "eleven_multilingual_v2"}).encode(),
        headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return base64.b64encode(r.read()).decode()
    except Exception:
        return None
