"""
╔══════════════════════════════════════════════════════════════╗
║   NEXORA COMMUNICATE AI  —  System 1                        ║
║   Universal AI Communication Assistant                      ║
║   Run:  streamlit run app.py                                ║
╚══════════════════════════════════════════════════════════════╝
"""

import os, re, time
import streamlit as st
import anthropic
from braille import to_braille, from_braille
from sign_language import get_sign, available_words, VARIANTS

# ─── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexora Communicate AI",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:1rem !important; padding-bottom:0.5rem !important; max-width:100% !important; }

.nxr-header {
  display:flex; align-items:center; justify-content:space-between;
  padding:14px 22px; background:#111118; border-radius:12px;
  border:1px solid rgba(255,255,255,0.08); margin-bottom:14px;
}
.nxr-logo { font-family:'Space Mono',monospace; font-size:15px; font-weight:700;
  color:#f0f0f8; display:flex; align-items:center; gap:10px; }
.logo-pulse { width:10px; height:10px; border-radius:50%; background:#7c6fff;
  display:inline-block; box-shadow:0 0 10px #7c6fff; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.6;transform:scale(1.3)} }
.nxr-status { font-size:12px; color:#3dca8a; display:flex; align-items:center; gap:6px; }
.g-dot { width:7px; height:7px; border-radius:50%; background:#3dca8a;
  display:inline-block; box-shadow:0 0 6px #3dca8a; }
.hist-pill { background:rgba(124,111,255,0.15); color:#a89fff; border-radius:10px;
  padding:2px 10px; font-size:11px; font-family:'Space Mono',monospace; }

/* messages */
.user-msg {
  background:rgba(124,111,255,0.12); border:1px solid rgba(124,111,255,0.25);
  border-radius:16px; border-top-right-radius:3px;
  padding:13px 17px; margin:6px 0 2px auto;
  color:#c4baff; font-size:14px; line-height:1.7; max-width:82%; width:fit-content;
}
.ai-msg {
  background:#16161f; border:1px solid rgba(255,255,255,0.09);
  border-radius:16px; border-top-left-radius:3px;
  padding:13px 17px; margin:6px 0 2px 0;
  color:#eeeef8; font-size:14px; line-height:1.7; max-width:82%;
}
.msg-meta { font-size:10px; color:#4a4a65; margin-top:5px; font-family:'Space Mono',monospace; }

/* braille */
.brl-box {
  background:#0e0e18; border:1px solid rgba(56,212,192,0.25);
  border-radius:10px; padding:12px 16px; margin-top:10px;
}
.brl-label { font-size:10px; color:#38d4c0; font-family:'Space Mono',monospace;
  letter-spacing:1.5px; margin-bottom:6px; }
.brl-chars { font-size:22px; color:#f0f0f8; letter-spacing:4px; line-height:2; word-break:break-all; }
.brl-note  { font-size:10px; color:#38d4c0; margin-top:4px; font-family:'Space Mono',monospace; }

/* tags */
.tag { display:inline-block; font-size:11px; padding:3px 10px; border-radius:12px; margin:5px 4px 0 0; }
.t-sign  { background:rgba(56,212,192,0.1);  color:#38d4c0; }
.t-trans { background:rgba(255,184,77,0.1);  color:#ffb84d; }
.t-brl   { background:rgba(56,212,192,0.1);  color:#38d4c0; }
.t-voice { background:rgba(124,111,255,0.1); color:#a89fff; }

/* sign card */
.sign-card {
  background:#0e1a1a; border:1px solid rgba(56,212,192,0.3);
  border-radius:10px; padding:14px 16px; margin-top:8px;
}
.sign-h { font-size:12px; font-weight:600; color:#38d4c0; font-family:'Space Mono',monospace; margin-bottom:8px; }
.sign-body { font-size:13.5px; color:#eeeef8; line-height:1.7; }

/* sidebar */
section[data-testid="stSidebar"] { background:#0d0d14 !important; border-right:1px solid rgba(255,255,255,0.07) !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span { color:#9898b0 !important; font-size:13px !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color:#f0f0f8 !important; }
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
  background:#1a1a24 !important; border:1px solid rgba(255,255,255,0.12) !important;
  color:#f0f0f8 !important; border-radius:8px !important; font-size:13px !important;
}
section[data-testid="stSidebar"] .stButton > button {
  background:#1a1a24 !important; color:#9898b0 !important;
  border:1px solid rgba(255,255,255,0.12) !important;
  border-radius:8px !important; font-size:12.5px !important; width:100% !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  border-color:#7c6fff !important; color:#a89fff !important;
}

/* main textarea */
.stTextArea textarea {
  background:#16161f !important; border:1px solid rgba(255,255,255,0.14) !important;
  border-radius:12px !important; color:#f0f0f8 !important;
  font-family:'DM Sans',sans-serif !important; font-size:14px !important;
}
.stTextArea textarea:focus { border-color:rgba(124,111,255,0.5) !important; }
.stTextArea textarea::placeholder { color:#4a4a65 !important; }

/* send button */
.stButton > button {
  border-radius:10px !important; font-size:13px !important;
  font-family:'DM Sans',sans-serif !important;
}

/* expander */
.streamlit-expanderHeader { color:#9898b0 !important; font-size:13px !important;
  background:#111118 !important; border-radius:8px !important; }

hr { border-color:rgba(255,255,255,0.06) !important; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.1); border-radius:4px; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ──────────────────────────────────────────────────────
LANGUAGES = {
    "English":"en","Chichewa":"ny","Swahili":"sw","French":"fr",
    "Portuguese":"pt","Arabic":"ar","Chinese":"zh","Spanish":"es",
    "German":"de","Hindi":"hi","Japanese":"ja","Korean":"ko",
    "Zulu":"zu","Yoruba":"yo","Lingala":"ln","Tumbuka":"tum",
    "Hausa":"ha","Igbo":"ig","Amharic":"am","Afrikaans":"af",
}
FLAGS = {
    "English":"🇬🇧","Chichewa":"🇲🇼","Swahili":"🌍","French":"🇫🇷",
    "Portuguese":"🇵🇹","Arabic":"🇸🇦","Chinese":"🇨🇳","Spanish":"🇪🇸",
    "German":"🇩🇪","Hindi":"🇮🇳","Japanese":"🇯🇵","Korean":"🇰🇷",
    "Zulu":"🇿🇦","Yoruba":"🇳🇬","Lingala":"🇨🇩","Tumbuka":"🇲🇼",
    "Hausa":"🇳🇬","Igbo":"🇳🇬","Amharic":"🇪🇹","Afrikaans":"🇿🇦",
}
MODES = ["💬 Chat", "🌐 Translate", "🤟 Sign Language", "⠿ Braille", "🎙 Voice"]

SYSTEM_PROMPT = """You are Aria, the Nexora Communicate AI — a universal communication assistant.

CAPABILITIES:
- Translate between 20+ languages: English, Chichewa, Swahili, French, Portuguese, Arabic,
  Chinese, Spanish, German, Hindi, Japanese, Korean, Zulu, Tumbuka, Lingala, Yoruba,
  Hausa, Igbo, Amharic, Afrikaans
- Describe sign language gestures step-by-step (ASL, BSL, SASL, International Sign)
- Support Braille accessibility (app auto-converts your text)
- Emotional intelligence and adaptive communication

RULES:
1. UNCLEAR REQUEST → ask ONE specific follow-up question before proceeding.
   e.g. "Translate hello" → "Which language should I translate to?"
2. TRANSLATIONS → label both sides: Original [LANG]: ... | Translation [LANG]: ...
3. SIGN LANGUAGE → describe hand shape, position, movement step by step. Name the variant.
4. Keep responses under 180 words unless translation or explanation requires more.
5. End every response with: [CHIPS: option1 | option2 | option3]

PERSONALITY: Warm, clear, patient, inclusive."""

# ─── Session state ───────────────────────────────────────────────────
def _init():
    # Try Streamlit secrets first, then env var
    try:
        default_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        default_key = os.environ.get("ANTHROPIC_API_KEY", "")

    defaults = {
        "messages":     [],
        "braille_mode": False,
        "sign_variant": "ASL",
        "from_lang":    "English",
        "to_lang":      "Auto detect",
        "mode":         "💬 Chat",
        "api_key":      default_key,
        "brl_out":      "",
        "brl_dir":      "braille",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ─── Helpers ────────────────────────────────────────────────────────
def get_client():
    k = st.session_state.api_key
    return anthropic.Anthropic(api_key=k) if k else None

def ts_now():
    return time.strftime("%H:%M")

def extract_chips(text):
    m = re.search(r"\[CHIPS:(.*?)\]", text)
    if not m: return []
    return [c.strip() for c in m.group(1).split("|") if c.strip()]

def clean(text):
    return re.sub(r"\[CHIPS:.*?\]", "", text).strip()

def detect_tags(user_text):
    u = user_text.lower()
    tags = []
    if any(w in u for w in ["sign","asl","bsl","sasl","gesture"]): tags.append("sign")
    if st.session_state.to_lang != "Auto detect" or "translat" in u: tags.append("trans")
    if st.session_state.braille_mode: tags.append("brl")
    if any(w in u for w in ["voice","speak","audio"]): tags.append("voice")
    return tags

# ─── Stream AI ───────────────────────────────────────────────────────
def stream_ai(user_text):
    client = get_client()
    if not client:
        yield "⚠️ No API key. Add your Anthropic key in the sidebar."
        return

    mode   = st.session_state.mode
    from_l = st.session_state.from_lang
    to_l   = st.session_state.to_lang
    ctx    = f"[Mode: {mode}]"
    if to_l != "Auto detect":
        ctx += f" [Translate from {from_l} to {to_l}]"

    st.session_state.messages.append({
        "role":"user","content":user_text,
        "ts":ts_now(),"braille":None,"tags":[],"chips":[]
    })

    api_msgs = [{"role":m["role"],"content":m["content"]} for m in st.session_state.messages]
    api_msgs[-1]["content"] = f"{ctx} {user_text}"

    full = ""
    try:
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=api_msgs,
        ) as s:
            for chunk in s.text_stream:
                full += chunk
                yield chunk
    except anthropic.AuthenticationError:
        yield "\n\n⚠️ Invalid API key."
        return
    except Exception as e:
        yield f"\n\n⚠️ Error: {e}"
        return

    chips = extract_chips(full)
    text  = clean(full)
    tags  = detect_tags(user_text)
    brl   = to_braille(text) if st.session_state.braille_mode else None

    st.session_state.messages.append({
        "role":"assistant","content":text,
        "ts":ts_now(),"braille":brl,"tags":tags,"chips":chips
    })

# ─── Render message ──────────────────────────────────────────────────
def render_msg(msg, idx):
    role    = msg["role"]
    content = msg["content"]
    ts      = msg.get("ts","")

    if role == "user":
        st.markdown(f"""
        <div class="user-msg">
            {content}
            <div class="msg-meta">{ts} &nbsp;·&nbsp; You</div>
        </div>""", unsafe_allow_html=True)
    else:
        tag_map   = {"sign":"🤟 Sign","trans":"🌐 Translation","brl":"⠿ Braille","voice":"🎙 Voice"}
        class_map = {"sign":"t-sign","trans":"t-trans","brl":"t-brl","voice":"t-voice"}
        tag_html  = "".join(
            f'<span class="tag {class_map[t]}">{tag_map[t]}</span>'
            for t in msg.get("tags",[]) if t in tag_map
        )
        mode_lbl = st.session_state.mode.split()[-1]
        st.markdown(f"""
        <div class="ai-msg">
            {content}
            <div class="msg-meta">{ts} &nbsp;·&nbsp; Aria &nbsp;·&nbsp; {mode_lbl}</div>
            {tag_html}
        </div>""", unsafe_allow_html=True)

        if msg.get("braille"):
            st.markdown(f"""
            <div class="brl-box">
                <div class="brl-label">⠿ BRAILLE OUTPUT — Grade 1 Unicode</div>
                <div class="brl-chars">{msg["braille"]}</div>
                <div class="brl-note">Copy into a braille display or printer</div>
            </div>""", unsafe_allow_html=True)

        chips = msg.get("chips",[])
        if chips:
            cols = st.columns(min(len(chips),3))
            for ci,chip in enumerate(chips[:3]):
                with cols[ci]:
                    if st.button(chip, key=f"chip_{idx}_{ci}"):
                        do_send(chip)

# ─── Send ────────────────────────────────────────────────────────────
def do_send(text):
    if not text.strip(): return
    with st.chat_message("assistant", avatar="🤖"):
        ph = st.empty()
        streamed = ""
        for chunk in stream_ai(text):
            streamed += chunk
            ph.markdown(clean(streamed) + "▌")
        ph.markdown(clean(streamed))
    st.rerun()

# ════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌟 Nexora AI")
    st.markdown("**System 1 — Communicate**")
    st.divider()

    # API Key
    with st.expander("🔑 API Key", expanded=not bool(st.session_state.api_key)):
        new_key = st.text_input("Anthropic API Key",
            value=st.session_state.api_key, type="password", placeholder="sk-ant-...")
        if new_key != st.session_state.api_key:
            st.session_state.api_key = new_key
            st.success("✓ Saved")
        st.caption("Get yours → [console.anthropic.com](https://console.anthropic.com)")

    st.divider()

    # Mode
    st.markdown("**Mode**")
    chosen = st.radio("mode_r", MODES,
        index=MODES.index(st.session_state.mode), label_visibility="collapsed")
    st.session_state.mode = chosen

    st.divider()

    # Language — pure Streamlit, NO template tags
    st.markdown("**Language**")
    lang_names = list(LANGUAGES.keys())

    from_lang = st.selectbox("From", lang_names,
        index=lang_names.index(st.session_state.from_lang))
    st.session_state.from_lang = from_lang

    to_options = ["Auto detect"] + lang_names
    to_lang = st.selectbox("To", to_options,
        index=to_options.index(st.session_state.to_lang)
              if st.session_state.to_lang in to_options else 0)
    st.session_state.to_lang = to_lang

    # Quick translate buttons — built in Python, not Jinja
    st.markdown("**Quick translate to:**")
    qlangs = [("🇲🇼","Chichewa"),("🌍","Swahili"),("🇳🇬","Yoruba"),("🇿🇦","Zulu")]
    qc = st.columns(2)
    for i,(flag,lang) in enumerate(qlangs):
        with qc[i % 2]:
            if st.button(f"{flag} {lang}", key=f"ql_{lang}"):
                st.session_state.to_lang = lang
                st.rerun()

    st.divider()

    # Braille
    st.markdown("**⠿ Braille**")
    st.session_state.braille_mode = st.checkbox(
        "Add Braille to every response", value=st.session_state.braille_mode)

    with st.expander("Braille Converter"):
        brl_input = st.text_area("Input text or ⠿ braille",
            height=70, placeholder="Type here...", key="brl_in_widget")
        bc = st.columns(2)
        with bc[0]:
            if st.button("→ Braille", key="tobrl"):
                if brl_input.strip():
                    st.session_state.brl_out = to_braille(brl_input)
                    st.session_state.brl_dir = "braille"
        with bc[1]:
            if st.button("→ Text", key="frombrl"):
                if brl_input.strip():
                    st.session_state.brl_out = from_braille(brl_input)
                    st.session_state.brl_dir = "text"
        if st.session_state.brl_out:
            label = "⠿ Braille" if st.session_state.brl_dir == "braille" else "📝 Text"
            st.code(f"{label}:\n{st.session_state.brl_out}", language=None)
            st.caption(f"{len(st.session_state.brl_out)} characters")

    st.divider()

    # Sign Language — built in Python, no template
    st.markdown("**🤟 Sign Language**")
    st.session_state.sign_variant = st.selectbox("Variant", VARIANTS,
        index=VARIANTS.index(st.session_state.sign_variant))

    with st.expander("Sign Dictionary"):
        sign_words = available_words()
        picked = st.selectbox("Look up a sign", ["— select —"] + sign_words, key="sign_pick")
        if picked != "— select —":
            res = get_sign(picked, st.session_state.sign_variant)
            if res["found"]:
                st.markdown(f"""
                <div class="sign-card">
                  <div class="sign-h">🤟 {picked.upper()} — {st.session_state.sign_variant}</div>
                  <div class="sign-body">{res['description']}</div>
                </div>""", unsafe_allow_html=True)

    st.divider()

    # Session stats
    n_user = sum(1 for m in st.session_state.messages if m["role"] == "user")
    n_ai   = len(st.session_state.messages) - n_user
    st.markdown(f"**Session** · {n_user} sent · {n_ai} replies")
    st.caption("Model: `claude-sonnet-4-6`")

    if st.button("🗑  Clear Chat History"):
        st.session_state.messages = []
        st.session_state.brl_out  = ""
        st.rerun()

# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════

# Header bar — built from Python variables, no template syntax
n_msgs     = len(st.session_state.messages)
from_flag  = FLAGS.get(st.session_state.from_lang, "")
from_name  = st.session_state.from_lang
to_disp    = ""
if st.session_state.to_lang != "Auto detect":
    to_flag = FLAGS.get(st.session_state.to_lang, "")
    to_disp = f"&nbsp;→&nbsp; {to_flag} {st.session_state.to_lang}"
brl_flag   = " &nbsp;·&nbsp; ⠿ Braille ON" if st.session_state.braille_mode else ""
mode_lbl   = st.session_state.mode

st.markdown(f"""
<div class="nxr-header">
  <div class="nxr-logo">
    <span class="logo-pulse"></span>
    NEXORA COMMUNICATE
    <span class="hist-pill">{n_msgs} messages</span>
  </div>
  <div class="nxr-status">
    <span class="g-dot"></span>
    Aria online &nbsp;·&nbsp; {mode_lbl} &nbsp;·&nbsp;
    {from_flag} {from_name}{to_disp}{brl_flag}
  </div>
</div>
""", unsafe_allow_html=True)

# Chat messages
if not st.session_state.messages:
    st.markdown("""
    <div class="ai-msg" style="max-width:100%">
      <strong>Hello! I'm Aria 👋</strong><br><br>
      I'm your Nexora Universal Communication AI. I can:<br><br>
      🌐 <strong>Translate</strong> — 20+ languages including Chichewa, Swahili, Zulu, Yoruba, Lingala<br>
      🤟 <strong>Sign language</strong> — ASL, BSL, SASL, International Sign (step-by-step descriptions)<br>
      ⠿ <strong>Braille</strong> — convert any text to Grade 1 Unicode Braille and back<br>
      💬 <strong>Chat</strong> — I ask follow-up questions when anything is unclear<br>
      🎙 <strong>Voice guidance</strong> — tips for voice-based communication<br><br>
      <em>Select a mode in the sidebar, then type below to begin.</em>
      <div class="msg-meta">Aria · Now · Ready</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for i, msg in enumerate(st.session_state.messages):
        render_msg(msg, i)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# Quick action chips — all built in Python
mode     = st.session_state.mode
variant  = st.session_state.sign_variant

QUICK = {
    "💬 Chat": [
        ("🇲🇼 Chichewa",       "Translate 'Good morning, how are you?' to Chichewa"),
        ("🌍 Swahili",         "Translate 'Good morning, how are you?' to Swahili"),
        ("🤟 Sign: hello",     f"How do I sign 'hello' in {variant}?"),
        ("⠿ To Braille",      "Convert 'I love Nexora' to braille"),
        ("🌐 Languages",       "What languages do you support?"),
    ],
    "🌐 Translate": [
        ("🇲🇼 Chichewa",  "Translate 'Hello, how are you?' to Chichewa"),
        ("🌍 Swahili",    "Translate 'Hello, how are you?' to Swahili"),
        ("🇳🇬 Yoruba",    "Translate 'Hello, how are you?' to Yoruba"),
        ("🇿🇦 Zulu",      "Translate 'Hello, how are you?' to Zulu"),
        ("🇫🇷 French",    "Translate 'Good evening' to French"),
    ],
    "🤟 Sign Language": [
        (f"Hello — {variant}",      f"Show me the {variant} sign for hello"),
        (f"Thank you — {variant}",  f"Show me the {variant} sign for thank you"),
        (f"Help — {variant}",       f"Show me the {variant} sign for help"),
        (f"Stop — {variant}",       f"Show me the {variant} sign for stop"),
        (f"Love — {variant}",       f"Show me the {variant} sign for love"),
    ],
    "⠿ Braille": [
        ("Hello → Braille",       "Convert 'Hello Nexora' to braille"),
        ("I love you → Braille",  "Convert 'I love you' to braille"),
        ("250 Kwacha → Braille",  "Convert '250 Kwacha' to braille"),
        ("What is braille?",      "Explain what braille is and how it helps blind people"),
        ("Decode braille",        "Decode this braille: ⠠⠓⠑⠇⠇⠕"),
    ],
    "🎙 Voice": [
        ("Voice tips",            "Give me tips for clear voice communication"),
        ("Noise cancellation",    "How does noise cancellation help communication?"),
        ("Voice + sign",          "How can voice and sign language be used together?"),
        ("Languages for voice",   "Which languages work best for voice AI?"),
        ("Deaf accessibility",    "What voice accessibility features exist for deaf users?"),
    ],
}

quick_list = QUICK.get(mode, QUICK["💬 Chat"])
q_cols = st.columns(len(quick_list))
for i, (label, prompt) in enumerate(quick_list):
    with q_cols[i]:
        if st.button(label, key=f"q_{i}_{mode}"):
            do_send(prompt)

st.divider()

# Input
placeholders = {
    "💬 Chat":          "Ask me anything — I'll follow up if unclear...",
    "🌐 Translate":     f"Type text to translate from {st.session_state.from_lang} to {st.session_state.to_lang}...",
    "🤟 Sign Language": f"Ask for a sign — e.g. 'How do I sign love in {variant}?'",
    "⠿ Braille":        "Type text to convert to Braille, or paste ⠿ to decode...",
    "🎙 Voice":         "Ask about voice communication or audio accessibility...",
}

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "message",
        height=100,
        placeholder=placeholders.get(mode, "Type a message..."),
        label_visibility="collapsed",
    )
    col_send, col_space = st.columns([1,5])
    with col_send:
        submitted = st.form_submit_button("Send ➤", use_container_width=True)

if submitted and user_input.strip():
    do_send(user_input.strip())

# History viewer
if st.session_state.messages:
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    with st.expander(f"📋 Chat history — {len(st.session_state.messages)} messages"):
        for i, m in enumerate(st.session_state.messages, 1):
            who  = "**You**" if m["role"] == "user" else "**Aria**"
            ts   = m.get("ts","")
            snip = m["content"][:200] + ("..." if len(m["content"]) > 200 else "")
            brl  = f"\n  `⠿ {m['braille'][:50]}...`" if m.get("braille") else ""
            c    = " · ".join(m.get("chips",[])) 
            chips_txt = f"\n  ↳ {c}" if c else ""
            st.markdown(f"{i}. {who} `{ts}` — {snip}{brl}{chips_txt}")
