
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
    color: #69e8ff;
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
st.subheader("An Interactive AI Mystery")
st.caption("CASE 001: THE MISSING HOUR")

st.write(
    "A scientist disappeared from a locked laboratory. "
    "One hour of security footage is missing. "
    "Question the suspects, examine the clues, and solve the mystery."
)

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

if "messages" not in st.session_state:
    st.session_state.messages = []

if "clues_found" not in st.session_state:
    st.session_state.clues_found = []

if "verdict" not in st.session_state:
    st.session_state.verdict = False

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
        if st.checkbox(f"Clue {i + 1}", key=f"clue_{i}"):
            if clue not in st.session_state.clues_found:
                st.session_state.clues_found.append(clue)

    st.write(
        f"Clues discovered: {len(st.session_state.clues_found)}/{len(CLUES)}"
    )

with right:
    st.header("💬 Interrogate Suspect")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input(
        "Ask the suspect a question..."
    )

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.write(question)

        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)

            prompt = f"""
You are playing a fictional detective mystery game.

CASE:
A scientist disappeared from a locked laboratory.
The security camera stopped recording at 9:00 PM.
The laboratory door opened at 9:15 PM.
Alex entered the control room at 9:10 PM.
A research access card was found near the control room.

SUSPECT: {suspect}
SUSPECT ROLE: {SUSPECTS[suspect]}

The player asks: {question}

Available clues:
{st.session_state.clues_found}

Instructions:
- Respond in character as the selected suspect.
- Keep the answer short and realistic.
- You may be nervous, defensive, or cooperative.
- Do not reveal the entire solution immediately.
- Treat this as a fictional mystery.
"""

            with st.spinner("The suspect is responding..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            answer = response.text or "The suspect remains silent."

        except Exception:
            answer = (
                "AI connection failed. Check your Gemini API key "
                "in Streamlit Secrets and try again."
            )

        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    st.divider()
    st.header("⚖️ Your Final Verdict")

    verdict = st.radio(
        "Who do you think is responsible?",
        ["Dr. Sara", "Alex", "Maya"],
        horizontal=True
    )

    if st.button("Submit Final Verdict"):
        st.session_state.verdict = True
        st.session_state.selected_verdict = verdict

    if st.session_state.verdict:
        if st.session_state.selected_verdict == "Alex":
            st.success(
                "Correct! Alex is the leading suspect based on the "
                "security log and missing footage. Detective work complete!"
            )
        else:
            st.warning(
                "Not quite! Review the security log and the missing "
                "footage before making your decision."
            )

    if st.button("🔄 Start New Investigation"):
        st.session_state.messages = []
        st.session_state.clues_found = []
        st.session_state.verdict = False
        st.rerun()
