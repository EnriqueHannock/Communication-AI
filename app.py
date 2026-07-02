"""
Nexora Communicate AI — System 1
Universal AI Communication Assistant
Flask backend — 100% Python
"""

import os
import json
import re
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import anthropic
from braille import text_to_braille, braille_to_text
from translator import detect_language, get_supported_languages
from sign_language import get_sign_description

app = Flask(__name__)

# ─── Anthropic client ───────────────────────────────────────────────
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

SYSTEM_PROMPT = """You are Aria, the Nexora Communicate AI — a universal communication assistant.

CAPABILITIES:
- Communicate via text, voice guidance, and sign language descriptions
- Translate between 20+ languages: English, Chichewa, Swahili, French, Portuguese, Arabic,
  Chinese, Spanish, German, Japanese, Korean, Hindi, Zulu, Tumbuka, Lingala, Yoruba, Afrikaans, 
  Hausa, Igbo, Amharic
- Describe sign language gestures (ASL, BSL, SASL, International Sign)
- Support accessibility for blind users (Braille-compatible text)
- Emotional intelligence and adaptive communication

RULES:
1. If the user's request is UNCLEAR, ask ONE specific follow-up question before proceeding.
   Example: "Translate hello" → ask "Which language should I translate to?"
2. For translations, always label: Original [LANG]: ... | Translation [LANG]: ...
3. For sign language, describe hand positions clearly and name the sign language variant.
4. When browsing/searching the web, say "Searching the web..." and summarise findings.
5. If the user asks for braille, note that the app will convert your response automatically.
6. Keep responses concise (under 200 words) unless translation or detailed explanation requires more.
7. Suggest 2–3 follow-up options at the end as: [CHIPS: option1 | option2 | option3]

PERSONALITY: Warm, clear, patient, inclusive. You celebrate diversity and accessibility."""


# ─── Routes ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    langs = get_supported_languages()
    return render_template("index.html", languages=langs)


@app.route("/api/chat", methods=["POST"])
def chat():
    """Main chat endpoint — streaming AI response."""
    data = request.get_json()
    messages = data.get("messages", [])
    braille_mode = data.get("braille_mode", False)
    from_lang = data.get("from_lang", "en")
    to_lang = data.get("to_lang", "auto")

    # Inject lang context into last user message
    if messages and to_lang != "auto":
        messages[-1]["content"] = (
            f"[Translate from {from_lang} to {to_lang}] " + messages[-1]["content"]
        )

    def generate():
        full_text = ""
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                full_text += text
                yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"

        # Strip chip tags from main text for braille conversion
        clean_text = re.sub(r"\[CHIPS:.*?\]", "", full_text).strip()

        if braille_mode:
            braille_output = text_to_braille(clean_text)
            yield f"data: {json.dumps({'type': 'braille', 'content': braille_output})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/braille", methods=["POST"])
def braille_convert():
    """Convert text ↔ braille."""
    data = request.get_json()
    text = data.get("text", "")
    direction = data.get("direction", "to_braille")  # to_braille | from_braille

    if direction == "to_braille":
        result = text_to_braille(text)
        return jsonify({"result": result, "direction": "to_braille"})
    else:
        result = braille_to_text(text)
        return jsonify({"result": result, "direction": "from_braille"})


@app.route("/api/sign", methods=["POST"])
def sign_language():
    """Get sign language description for a word or phrase."""
    data = request.get_json()
    word = data.get("word", "")
    variant = data.get("variant", "ASL")
    description = get_sign_description(word, variant)
    return jsonify({"word": word, "variant": variant, "description": description})


@app.route("/api/translate", methods=["POST"])
def translate():
    """Quick direct translation via AI."""
    data = request.get_json()
    text = data.get("text", "")
    from_lang = data.get("from_lang", "en")
    to_lang = data.get("to_lang", "ny")
    braille_output = data.get("braille", False)

    prompt = f"Translate this text from {from_lang} to {to_lang}. Return ONLY the translation, nothing else:\n\n{text}"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    translation = message.content[0].text.strip()

    result = {
        "original": text,
        "translation": translation,
        "from_lang": from_lang,
        "to_lang": to_lang,
    }

    if braille_output:
        result["braille"] = text_to_braille(translation)

    return jsonify(result)


@app.route("/api/detect-lang", methods=["POST"])
def detect_lang():
    """Detect language of given text."""
    data = request.get_json()
    text = data.get("text", "")
    detected = detect_language(text, client)
    return jsonify({"detected": detected, "text": text})


@app.route("/api/languages", methods=["GET"])
def languages():
    return jsonify(get_supported_languages())


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "model": "claude-sonnet-4-6", "version": "1.0.0"})


# ─── Run ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"\n🌟 Nexora Communicate AI running on http://0.0.0.0:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
