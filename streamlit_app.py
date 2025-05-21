import streamlit as st
import openai # For error types like openai.AuthenticationError
from openai import OpenAI # For the OpenAI client
import os

# --- Page Configuration ---
st.set_page_config(page_title="Gen Z Lingo AI", page_icon="🤙", layout="wide")

# --- OpenAI API Key Setup & Client Initialization ---
# Moved to a function for cleaner setup
def initialize_openai_client():
    if 'openai_api_key' not in st.session_state:
        try:
            st.session_state.openai_api_key = os.environ["OPENAI_API_KEY"]
        except KeyError:
            try:
                st.session_state.openai_api_key = st.secrets["OPENAI_API_KEY"]
            except (FileNotFoundError, KeyError):
                st.session_state.openai_api_key = None

    if not st.session_state.openai_api_key:
        st.error("🚨 OpenAI API Key not found. Please set it as a Codespaces secret (OPENAI_API_KEY) or in .streamlit/secrets.toml to use the app.")
        st.stop()

    if 'openai_client' not in st.session_state:
        st.session_state.openai_client = OpenAI(api_key=st.session_state.openai_api_key)

initialize_openai_client()

# --- Constants & Initial State ---
GEN_Z_LINGO_SAMPLES = sorted([
    "Rizz", "Cap / No Cap", "Simp", "Sus", "Bet", "Glow Up", "Mid", "NPC",
    "Finna", "Boujee", "Slay", "Periodt", "IYKYK", "FOMO", "JOMO",
    "Stan", "Tea", "Vibe Check", "Ghosting", "Woke", "Delulu", "Big Yikes",
    "Main Character Energy", "Side Eye", "It's giving", "No Kizzy", "Sheesh",
    "Bussin'", "Cheugy", "Drip", "Based"
])
DEFAULT_SELECTBOX_OPTION = "✨ Pick a term... ✨"
INITIAL_ASSISTANT_MESSAGE = "Yo! What's good? 🤘 Ask me about any Gen Z lingo, or pick a term from the sidebar to get the lowdown! Let's get it! 🚀"
SYSTEM_PROMPT_CONTENT = """You are a fun, engaging, and super knowledgeable assistant, an expert on Gen Z lingo.
Your main goal is to explain Gen Z internet slang clearly to someone who might not be familiar with it.
Always be friendly and approachable.
When explaining a term:
1. Provide a clear, concise definition.
2. Give one or two relevant and easy-to-understand example sentences.
3. Use appropriate emojis to enhance the explanation and keep the vibe light.
Keep your explanations relatively short and to the point unless the user asks for more detail.
If a term is very obscure or has multiple meanings, acknowledge that if relevant.
"""

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT_CONTENT},
        {"role": "assistant", "content": INITIAL_ASSISTANT_MESSAGE}
    ]

# --- Helper Functions ---
def clear_chat_history():
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT_CONTENT},
        {"role": "assistant", "content": INITIAL_ASSISTANT_MESSAGE}
    ]
    # Reset the selectbox to the default option if it exists
    if 'lingo_selector' in st.session_state:
        st.session_state.lingo_selector = DEFAULT_SELECTBOX_OPTION
    st.rerun()


def get_and_display_llm_response(user_prompt_content):
    # Add user's prompt to chat history if it's not already the last message from user
    # (to avoid double-adding if called rapidly or from different triggers)
    if not st.session_state.messages or \
       st.session_state.messages[-1].get("role") != "user" or \
       st.session_state.messages[-1].get("content") != user_prompt_content:
        st.session_state.messages.append({"role": "user", "content": user_prompt_content})
        with st.chat_message("user"):
            st.markdown(user_prompt_content)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response_content = ""
        try:
            with st.spinner("AI is thinking... 🤔"): # ADDED SPINNER
                api_messages_to_send = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                response_stream = st.session_state.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=api_messages_to_send,
                    stream=True,
                )
                for chunk in response_stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response_content += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response_content + "▌")
                message_placeholder.markdown(full_response_content)

        except openai.AuthenticationError:
            full_response_content = "Error: Authentication failed. Please check your OpenAI API key."
            message_placeholder.error(full_response_content)
        except openai.APIError as e:
            full_response_content = f"OpenAI API Error: {e}"
            message_placeholder.error(full_response_content)
        except Exception as e:
            full_response_content = f"Oops! An unexpected error occurred: {e}"
            message_placeholder.error(full_response_content)

    if full_response_content and (not st.session_state.messages or st.session_state.messages[-1].get("content") != full_response_content):
        st.session_state.messages.append({"role": "assistant", "content": full_response_content})

def handle_lingo_selection_change():
    selected_term = st.session_state.get("lingo_selector", DEFAULT_SELECTBOX_OPTION)
    # Only process if a valid term is selected and it's different from the default
    if selected_term != DEFAULT_SELECTBOX_OPTION:
        # Avoid re-processing if the selected term is already the subject of the last user message
        # This can happen if other interactions cause a rerun while a term is selected.
        last_user_message_content = ""
        for i in range(len(st.session_state.messages) -1, -1, -1):
            if st.session_state.messages[i]["role"] == "user":
                last_user_message_content = st.session_state.messages[i]["content"]
                break
        
        prompt_for_llm = f"Tell me about the Gen Z lingo: '{selected_term}'. Explain its meaning and give an example."
        if prompt_for_llm != last_user_message_content:
             get_and_display_llm_response(prompt_for_llm)
        # Note: We don't reset the selectbox here immediately because `on_change` callbacks
        # can be tricky with widget state. Clearing chat will reset it.

# --- Main App UI ---
st.title("🤙 Gen Z Lingo AI 🗣️")
st.caption("Your hip guide to understanding modern slang. Ask away or explore terms!")

# --- Sidebar ---
with st.sidebar:
    st.header("Explore Lingo 🧭")
    st.selectbox(
        "Quick Explanations:",
        options=[DEFAULT_SELECTBOX_OPTION] + GEN_Z_LINGO_SAMPLES,
        key="lingo_selector",
        on_change=handle_lingo_selection_change,
        help="Select a term to get an instant explanation in the chat!"
    )
    st.markdown("---")
    if st.button("🧹 Clear Chat History", use_container_width=True):
        clear_chat_history()
    st.markdown("---")
    st.subheader("About")
    st.markdown(
        "This app uses OpenAI's GPT to explain Gen Z lingo. "
        "Built with ❤️ using [Streamlit](https://streamlit.io)."
    )
    st.markdown("Inspired by the need to stay ✨current✨.")

# --- Chat Interface ---
# Display chat messages from history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Accept user input
if user_typed_prompt := st.chat_input("What lingo is on your mind? Or ask anything!"):
    get_and_display_llm_response(user_typed_prompt)