from __future__ import annotations

import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="MarketMind AI", page_icon="🧭", layout="wide")

# ---------- Session state ----------
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "key"

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container { max-width: 1100px; padding-top: 2rem; }
.hero { padding: 42px 28px; border-radius: 24px; background: linear-gradient(135deg,#f5f7ff,#eef6ff); margin-bottom: 24px; }
.hero h1 { margin: 0; font-size: 42px; }
.card { padding: 22px; border: 1px solid #e8eaf0; border-radius: 18px; background: white; min-height: 130px; }
.small { color:#6b7280; }
</style>
""", unsafe_allow_html=True)


def key_page():
    st.markdown("<div class='hero'><h1>🧭 MarketMind AI</h1><p class='small'>Connect your OpenAI API key to continue.</p></div>", unsafe_allow_html=True)

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.subheader("🔐 OpenAI API Key")
        key = st.text_input(
            "Enter your API key",
            type="password",
            placeholder="sk-...",
            help="Your key is kept in this Streamlit session and is not displayed.",
        )

        if st.button("Connect & Continue", type="primary", use_container_width=True):
            if not key.strip():
                st.error("Please enter your OpenAI API key.")
                return
            try:
                client = OpenAI(api_key=key.strip())
                # Lightweight validation call.
                client.models.list()
                st.session_state.api_key = key.strip()
                os.environ["OPENAI_API_KEY"] = key.strip()
                st.session_state.page = "app"
                st.rerun()
            except Exception:
                st.error("The API key could not be verified. Please check the key and try again.")

        st.caption("Your key is required before the main MarketMind page opens.")


def app_page():
    api_key = st.session_state.api_key
    client = OpenAI(api_key=api_key)

    with st.sidebar:
        st.markdown("### 🧭 MarketMind AI")
        st.success("API connected")
        model = st.selectbox("Model", ["gpt-5", "gpt-4.1", "gpt-4o-mini"], index=0)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)
        if st.button("New conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        if st.button("Change API key", use_container_width=True):
            st.session_state.api_key = ""
            st.session_state.messages = []
            st.session_state.page = "key"
            st.rerun()

    st.markdown("<div class='hero'><h1>How can MarketMind help?</h1><p class='small'>Ask questions, analyze markets, summarize information, or explore an idea.</p></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='card'><b>📊 Market analysis</b><br><span class='small'>Explore trends, competitors, and opportunities.</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card'><b>🔎 Research</b><br><span class='small'>Turn questions into clear, structured answers.</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='card'><b>📝 Synthesis</b><br><span class='small'>Summarize and compare information quickly.</span></div>", unsafe_allow_html=True)

    st.write("")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask MarketMind anything...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are MarketMind AI, a helpful market research and analysis assistant. Give clear, useful, well-structured answers."},
                            *st.session_state.messages,
                        ],
                        temperature=temperature,
                    )
                    answer = response.choices[0].message.content or "I couldn't generate a response."
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception:
                    st.error("The request failed. Please check your API key, selected model, or OpenAI account limits.")


if st.session_state.page == "key":
    key_page()
else:
    app_page()
