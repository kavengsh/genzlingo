import os
import json
import random
import streamlit as st

"""
Gen Z Lingo Trainer — Streamlit Edition (Codespaces‑ready)
-------------------------------------------------------
* Learn popular slang
* Quiz yourself
* Lean on OpenAI’s LLM for fresh terms or deeper explanations

HOW THIS FILE IS ORGANISED
1. Config & API setup
2. Utility helpers (load/save JSON, OpenAI wrappers)
3. Sidebar (mode + add‑term form)
4. Main views: Learn · Quiz · AI Helper
"""

# ────────────────────────────────────────────────────────────────
# 1 ∙ Config & API
# ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Gen Z Lingo Trainer", page_icon="👾", layout="centered")

# Get your API key from environment / Streamlit secrets
OPENAI_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
if OPENAI_KEY:
    import openai  # imported lazily only if key found
    openai.api_key = OPENAI_KEY

# Where we persist the custom dictionary (JSON keeps it human‑editable)
DATA_FILE = "slang.json"

# Default starter dataset
DEFAULT_SLANG = {
    "rizz": "Charisma or charm, especially when flirting.",
    "delulu": "Delusional; having an unrealistic belief.",
    "cap": "Lie or falsehood. Saying 'no cap' means you're truthful.",
    "bet": "Agreement / confirmation, similar to 'OK'.",
    "yeet": "To throw something with force; also an exclamation.",
    "slaps": "Extremely good or enjoyable (music, food).",
    "lowkey": "Somewhat; quietly; not wanting attention.",
    "sigma": "Independent and non‑conforming person.",
    "mid": "Mediocre; neither good nor bad.",
    "sus": "Suspicious or questionable."
}

# ────────────────────────────────────────────────────────────────
# 2 ∙ Helpers
# ────────────────────────────────────────────────────────────────

def load_slang() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf‑8") as f:
            return json.load(f)
    return DEFAULT_SLANG.copy()


def save_slang(data: dict):
    with open(DATA_FILE, "w", encoding="utf‑8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ai_define(term: str) -> str:
    """Get a short definition + example from OpenAI."""
    if not OPENAI_KEY:
        return "⚠️ OpenAI key not configured."
    prompt = (
        "Explain the Gen Z slang term '" + term + "' in a single concise sentence, "
        "then give one short usage example in quotes."
    )
    rsp = openai.chat.completions.create(
        model="gpt‑4o-mini",  # light, fast, cheap
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return rsp.choices[0].message.content.strip()


def ai_chat(q: str) -> str:
    """Free‑form Q&A about slang."""
    if not OPENAI_KEY:
        return "⚠️ OpenAI key not configured."
    rsp = openai.chat.completions.create(
        model="gpt‑4o-mini",
        messages=[{"role": "system", "content": "You are an expert on modern internet slang."},
                  {"role": "user", "content": q}],
        temperature=0.6,
    )
    return rsp.choices[0].message.content.strip()


slang_data = load_slang()

# ────────────────────────────────────────────────────────────────
# 3 ∙ Sidebar UI
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")
    mode = st.radio("Choose a mode:", ["Learn", "Quiz", "AI Helper"])

    # (Optional) show key status
    if OPENAI_KEY:
        st.success("OpenAI API key detected")
    else:
        st.warning("Add an OPENAI_API_KEY secret in Codespaces to unlock LLM features")

    # Add‑term expander
    with st.expander("➕ Add your own slang"):
        new_term = st.text_input("Term")
        new_def = st.text_area("Definition (leave blank to have GPT define it)")
        if st.button("Add to dictionary") and new_term:
            term = new_term.lower().strip()
            definition = new_def.strip() or ai_define(term)
            slang_data[term] = definition
            save_slang(slang_data)
            st.success(f"Added **{term}**!")

# ────────────────────────────────────────────────────────────────
# 4 ∙ Main Views
# ────────────────────────────────────────────────────────────────

st.title("👾 Learn Gen Z Lingo")

# — Learn —
if mode == "Learn":
    st.subheader("📚 Learn a term")
    term = st.selectbox("Pick a term:", sorted(slang_data.keys()))
    st.markdown(f"### {term.capitalize()}")
    st.write(slang_data[term])

    if st.button("Ask GPT for more detail") and OPENAI_KEY:
        with st.spinner("Calling OpenAI…"):
            extra = ai_define(term)
        st.info(extra)

# — Quiz —
elif mode == "Quiz":
    st.subheader("📝 Quiz time!")
    score = st.session_state.get("score", 0)
    q_num = st.session_state.get("q_num", 0)

    if "current_question" not in st.session_state:
        st.session_state.current_question = random.choice(list(slang_data.keys()))

    correct = st.session_state.current_question
    wrong = random.sample([t for t in slang_data.keys() if t != correct], k=min(3, len(slang_data)-1))
    options = wrong + [correct]
    random.shuffle(options)

    st.write(f"**Definition:** {slang_data[correct]}")
    user_choice = st.radio("Which term matches?", options)

    if st.button("Submit"):
        if user_choice == correct:
            st.success("Correct! 🎉")
            score += 1
        else:
            st.error(f"Nope. It was **{correct}**.")
        q_num += 1
        st.session_state.update({"score": score, "q_num": q_num, "current_question": random.choice(list(slang_data.keys()))})
        st.experimental_rerun()

    st.info(f"Score: {score} / {q_num}")

# — AI Helper —
else:
    st.subheader("🤖 AI Helper: Ask anything about slang")
    q = st.text_area("Enter your question (e.g. *What does ‘NPC’ mean?* or *Suggest three new Gen Z phrases about food*):")
    if st.button("Ask") and q.strip():
        with st.spinner("Thinking…"):
            answer = ai_chat(q.strip())
        st.write(answer)

st.caption("Built with Streamlit · Powered by OpenAI © 2025")
