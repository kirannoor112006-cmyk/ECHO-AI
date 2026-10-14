
import streamlit as st
from google import genai

st.set_page_config(
    page_title="ECHO // AI",
    page_icon="🔎",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0b1020;
    color: #e6edf7;
}
h1, h2, h3 {
    color: #69e8ff !important;
}
.stButton > button {
    background-color: #15283c;
    color: #69e8ff;
    border: 1px solid #69e8ff;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("🔎 ECHO // AI")
st.subheader("Interactive Mystery Investigation")
st.caption("CASE 001: THE MISSING HOUR")

st.write(
    "A scientist has disappeared from a locked laboratory. "
    "Question suspects, investigate clues, and solve the mystery."
)

SUSPECTS = {
    "Dr. Sara": "Laboratory scientist",
    "Alex": "Security guard",
    "Maya": "Research assistant"
}

CLUES = [
    "The laboratory door opened at 9:15 PM.",
    "The security camera stopped recording at 9:00 PM.",
    "A research access card was found near the control room.",
    "Alex entered the control room at 9:10 PM."
]

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "clues_found" not in st.session_state:
    st.session_state.clues_found = []

if "available_models" not in st.session_state:
    st.session_state.available_models = []

if "model_error" not in st.session_state:
    st.session_state.model_error = ""

if "verdict" not in st.session_state:
    st.session_state.verdict = None

# API key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

client = None

if api_key:
    client = genai.Client(api_key=api_key)

# Check available models
st.sidebar.header("⚙️ AI Settings")

if not api_key:
    st.sidebar.error(
        "API key missing. Add GEMINI_API_KEY in Streamlit Secrets."
    )
else:
    if st.sidebar.button("🔍 Check Available Models"):
        try:
            with st.spinner("Checking models for your API key..."):
                models = list(client.models.list())

                available = []

                for model in models:
                    name = getattr(model, "name", "") or ""
                    actions = getattr(model, "supported_actions", None) or []

                    if (
                        name
                        and "generateContent" in actions
                        and "gemini" in name.lower()
                    ):
                        available.append(
                            name.removeprefix("models/")
                        )

                st.session_state.available_models = sorted(set(available))
                st.session_state.model_error = ""

                if not available:
                    st.session_state.model_error = (
                        "No models supporting generateContent were returned."
                    )

        except Exception as e:
            st.session_state.model_error = (
                f"{type(e).__name__}: {e}"
            )
            st.session_state.available_models = []

    if st.session_state.model_error:
        st.sidebar.error(st.session_state.model_error)

    if st.session_state.available_models:
        st.sidebar.success(
            f"{len(st.session_state.available_models)} models found"
        )

        selected_model = st.sidebar.selectbox(
            "Choose an available model",
            st.session_state.available_models
        )
    else:
        selected_model = None
        st.sidebar.info(
            "Click 'Check Available Models' to load your model list."
        )

# Main layout
left, right = st.columns([1, 2])

with left:
    st.header("👥 Suspects")

    suspect = st.selectbox(
        "Choose someone to question",
        list(SUSPECTS.keys())
    )

    st.write(SUSPECTS[suspect])

    st.divider()
    st.header("🧩 Evidence Board")

    for i, clue in enumerate(CLUES):
        checked = st.checkbox(clue, key=f"clue_{i}")

        if checked and clue not in st.session_state.clues_found:
            st.session_state.clues_found.append(clue)

        elif not checked and clue in st.session_state.clues_found:
            st.session_state.clues_found.remove(clue)

    st.write(
        f"Clues selected: "
        f"{len(st.session_state.clues_found)}/{len(CLUES)}"
    )

with right:
    st.header("💬 Interrogate a Suspect")

    if not st.session_state.available_models:
        st.info(
            "First, open AI Settings in the sidebar and click "
            "'Check Available Models'."
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input("Ask the suspect a question...")

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.write(question)

        answer = ""

        if not api_key:
            answer = "Gemini API key is missing."
            st.error(answer)

        elif not selected_model:
            answer = "Check available models in the sidebar first."
            st.warning(answer)

        else:
            prompt = f"""
You are a character in a fictional detective mystery.

CASE:
A scientist disappeared from a locked laboratory.
The camera stopped recording at 9:00 PM.
The laboratory door opened at 9:15 PM.
Alex entered the control room at 9:10 PM.
A research access card was found near the control room.

SELECTED SUSPECT: {suspect}
ROLE: {SUSPECTS[suspect]}
PLAYER QUESTION: {question}
CLUES SELECTED BY PLAYER: {st.session_state.clues_found}

Respond briefly in character as the selected suspect.
Be realistic and do not reveal the whole mystery immediately.
This is a fictional game.
"""

            try:
                with st.spinner("The suspect is thinking..."):
                    response = client.models.generate_content(
                        model=selected_model,
                        contents=prompt
                    )

                answer = (
                    response.text
                    or "The suspect did not provide a text response."
                )

            except Exception as e:
                st.error(
                    f"Gemini API error: {type(e).__name__}: {e}"
                )
                answer = (
                    "The AI could not respond. "
                    "Check the error displayed above."
                )

        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    st.divider()
    st.header("⚖️ Final Verdict")

    verdict = st.radio(
        "Who do you suspect?",
        list(SUSPECTS.keys()),
        horizontal=True
    )

    if st.button("Submit Final Verdict"):
        st.session_state.verdict = verdict

    if st.session_state.verdict is not None:
        if st.session_state.verdict == "Alex":
            st.success(
                "You identified the expected suspect! "
                "Review the security log for supporting evidence."
            )
        else:
            st.warning(
                "That is not the expected answer. "
                "Review the clues and investigate further."
            )

    if st.button("🔄 Start New Investigation"):
        st.session_state.messages = []
        st.session_state.clues_found = []
        st.session_state.verdict = None
        st.rerun()


