import uuid

import requests
import streamlit as st


API_BASE_URL = "http://localhost:8000"


def get_session_id() -> str:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id


def reset_session() -> None:
    session_id = st.session_state.get("session_id")
    if not session_id:
        return
    try:
        requests.post(f"{API_BASE_URL}/reset_session", json={"session_id": session_id}, timeout=5)
    except Exception:
        # Best-effort reset; UI should still continue.
        pass
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []


def send_message_to_api(message: str) -> dict:
    session_id = get_session_id()
    payload = {"session_id": session_id, "message": message}
    resp = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    st.set_page_config(
        page_title="E-commerce Support Assistant",
        page_icon="🛒",
        layout="wide",
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.markdown("### Store Support Assistant")
        st.write("Smart, contextual help for your customers.")
        st.markdown("---")
        st.write("**Session**")
        st.text(f"Session ID:\n{get_session_id()[:8]}...")
        if st.button("Start new chat"):
            reset_session()
        st.markdown("---")
        st.write("**Appearance**")
        personality = st.radio(
            "Personality",
            options=["Friendly", "Formal"],
            index=0,
            help="This currently hints tone; the backend stays general-purpose.",
        )
        st.session_state.personality = personality
        st.markdown("---")
        st.caption("Tip: Ask about shipping, returns, orders, or payments.")

    st.markdown(
        "<h2 style='text-align: center;'>E-commerce Support Chatbot</h2>",
        unsafe_allow_html=True,
    )

    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="🧑"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])
                    faqs = msg.get("suggested_faqs") or []
                    if faqs:
                        with st.expander("Suggested help articles"):
                            for faq in faqs:
                                st.markdown(f"**{faq['question']}**")
                                st.write(faq["answer"])

    user_input = st.chat_input("Type your question about your order, shipping, or returns...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    response = send_message_to_api(user_input)
                    reply = response.get("reply", "")
                    suggested_faqs = response.get("suggested_faqs", [])
                except Exception as e:
                    reply = "Sorry, I could not reach the support service. Please try again in a moment."
                    suggested_faqs = []
                    st.error(str(e))
                st.markdown(reply)
                if suggested_faqs:
                    with st.expander("Suggested help articles"):
                        for faq in suggested_faqs:
                            st.markdown(f"**{faq['question']}**")
                            st.write(faq["answer"])

        st.session_state.messages.append(
            {"role": "assistant", "content": reply, "suggested_faqs": suggested_faqs}
        )


if __name__ == "__main__":
    main()

