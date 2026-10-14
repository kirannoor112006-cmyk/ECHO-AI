
import streamlit as st
from google import genai

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ECHO // AI",
    page_icon="🔎",
    layout="wide"
)

# ---------------- DESIGN ----------------
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

# ---------------- HEADER ----------------
st.title("🔎 ECHO // AI")
st.subheader("An Interactive Mystery Investigation")
st.caption("CASE 001: THE MISSING HOUR")

st.write(
    "A scientist has disappeared from a locked laboratory. "
    "One hour of security footage is missing. "
    "Question the suspects, examine the clues, and solve the case."
)

# ---------------- CASE DATA ----------------
SUSPECTS = {
    "Dr. Sara": "The laboratory scientist",
    "Alex": "The security guard",
    "Maya": "The research assistant"
}

CLUES = [
    "The laboratory door was opened at 9:15 PM.",
    "The security camera stopped recording at 9:00 PM.",
    "A research access card was found near the control room.",
    "The security log shows Alex entered the control room at 9:10 PM."
]

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "clues_found" not in st.session_state:
    st.session_state.clues_found = []

if "verdict" not in st.session_state:
    st.session_state.verdict = None

# ---------------- LAYOUT ----------------
left, right = st.columns([1, 2])

# ---------------- SUSPECTS AND CLUES ----------------
with left:
    st.header("👥 Suspects")

    suspect = st.selectbox(
        "Choose a suspect",
        list(SUSPECTS.keys())
    )

    st.write(SUSPECTS[suspect])

    st.divider()
    st.header("🧩 Evidence Board")
    st.caption("Select the clues you want to investigate.")

    for i, clue in enumerate(CLUES):
        found = st.checkbox(clue, key=f"clue_{i}")

        if found and clue not in st.session_state.clues_found:
            st.session_state.clues_found.append(clue)

        if not found and clue in st.session_state.clues_found:
            st.session_state.clues_found.remove(clue)

    st.write(
        f"Clues selected: "
        f"{len(st.session_state.clues_found)}/{len(CLUES)}"
    )

# ---------------- AI INTERROGATION ----------------
with right:
    st.header("💬 Interrogate a Suspect")

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

        # Check whether the API key exists
        api_key = st.secrets.get("GEMINI_API_KEY", "")

        if not api_key:
            answer = (
                "Gemini API key is missing. "
                "Open Streamlit Settings > Secrets and add "
                "GEMINI_API_KEY."
            )
            st.error(answer)

        else:
            prompt = f"""
You are a character in a fictional detective mystery game.

CASE:
A scientist disappeared from a locked laboratory.
The security camera stopped recording at 9:00 PM.
The laboratory door opened at 9:15 PM.
Alex entered the control room at 9:10 PM.
A research access card was found near the control room.

SELECTED SUSPECT:
{suspect}

SUSPECT ROLE:
{SUSPECTS[suspect]}

PLAYER'S QUESTION:
{question}

CLUES THE PLAYER HAS SELECTED:
{st.session_state.clues_found}

RULES:
- Reply in character as the selected suspect.
- Keep your answer short and realistic.
- Be cooperative, nervous, or defensive when appropriate.
- Do not reveal the entire mystery immediately.
- Do not claim evidence that is not in the case.
- This is a fictional game.
"""

            try:
                client = genai.Client(api_key=api_key)

                with st.spinner("The suspect is thinking..."):
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt
                    )

                answer = (
                    response.text
                    or "The suspect has no response right now."
                )

            except Exception as e:
                st.error(
                    f"Gemini API error: {type(e).__name__}: {e}"
                )
                answer = (
                    "The AI could not respond. "
                    "Read the error above to find the cause."
                )

        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    st.divider()

    # ---------------- FINAL VERDICT ----------------
    st.header("⚖️ Your Final Verdict")

    selected_verdict = st.radio(
        "Who do you suspect?",
        list(SUSPECTS.keys()),
        horizontal=True
    )

    if st.button("Submit Final Verdict"):
        st.session_state.verdict = selected_verdict

    if st.session_state.verdict is not None:
        if st.session_state.verdict == "Alex":
            st.success(
                "You identified the leading suspect! "
                "The security log places Alex in the control room "
                "during the missing-footage period."
            )
        else:
            st.warning(
                "That verdict is not the expected answer. "
                "Review the clues and investigate further."
            )

    if st.button("🔄 Start New Investigation"):
        st.session_state.messages = []
        st.session_state.clues_found = []
        st.session_state.verdict = None
        st.rerun()

