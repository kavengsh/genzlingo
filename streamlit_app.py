import streamlit as st
import openai
import os # To access environment variables like secrets

# --- Page Configuration ---
st.set_page_config(page_title="Gen Z Lingo Explainer", page_icon="🤙")

# --- OpenAI API Key Setup ---
# Try to get the API key from Codespaces secrets (environment variable)
# Fallback to Streamlit secrets if not found (for local dev with secrets.toml)
try:
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    try:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
    except FileNotFoundError: # For when .streamlit/secrets.toml doesn't exist
        st.error("OpenAI API Key not found. Please set it as a Codespaces secret (OPENAI_API_KEY) or in .streamlit/secrets.toml.")
        st.stop()
    except KeyError: # For when OPENAI_API_KEY is not in secrets.toml
        st.error("OPENAI_API_KEY not found in .streamlit/secrets.toml. Please add it.")
        st.stop()


# --- App Title and Description ---
st.title("🤙 Gen Z Lingo Explainer Chatbot 🗣️")
st.caption("Ask me to explain any Gen Z lingo! (e.g., 'What does rizz mean?', 'Explain 'no cap' an example')")

# --- Session State for Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful and cool assistant, an expert on Gen Z lingo. Your goal is to explain Gen Z internet slang to someone who might not know it. Be friendly, clear, and provide examples. Keep it concise unless asked for more detail. You can use relevant emojis."},
        {"role": "assistant", "content": "Yo! What's up? Got any Gen Z lingo you want me to break down for ya? Lay it on me! 🤔"}
    ]

# --- Display Chat History ---
for message in st.session_state.messages:
    if message["role"] != "system": # Don't display system messages
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- Chat Input from User ---
if prompt := st.chat_input("What lingo do you want to understand?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Create the list of messages to send to the API (including system prompt)
            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            # Call OpenAI API (using the chat completions endpoint)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", # You can try other models like gpt-4 if you have access
                messages=api_messages,
                stream=True, # For a streaming effect
            )
            for chunk in response:
                if chunk.choices[0].delta.get("content"):
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌") # Blinking cursor effect
            message_placeholder.markdown(full_response)
        except openai.error.AuthenticationError:
            full_response = "Error: Authentication failed. Please check your OpenAI API key and ensure it's configured correctly."
            message_placeholder.error(full_response)
        except Exception as e:
            full_response = f"Oops! Something went wrong: {e}"
            message_placeholder.error(full_response)

    # Add AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})