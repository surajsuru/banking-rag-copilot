import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Banking RAG Copilot",
    page_icon="🏦",
    layout="wide"
)


with st.sidebar:
    st.title("🏦 Banking Copilot")
    st.markdown("---")

    role = st.selectbox(
        "Select your role",
        options=["public", "agent", "operations", "compliance", "admin"],
        index=0
    )

    top_k = st.slider("Chunks to retrieve (top_k)", min_value=1, max_value=10, value=5)

    st.markdown("---")
    st.caption("Role controls which documents you can access.")



if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("🏦 Banking RAG Copilot")
st.caption(f"Logged in as: **{role}** | Retrieving top **{top_k}** chunks")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("Ask a banking operations question..."):

    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": prompt, "role": role, "top_k": top_k},
                    timeout=60
                )
                data = response.json()

                answer = data.get("answer", "No answer returned.")
                sources = data.get("sources", [])
                grounding_score = data.get("grounding_score", 0.0)
                is_grounded = data.get("is_grounded", False)

                # Display answer
                st.markdown(answer)

                # Display sources
                if sources:
                    st.markdown("**📄 Sources:**")
                    for s in sources:
                        st.markdown(f"- `{s}`")

                # Display grounding badge
                grounded_label = "✅ Grounded" if is_grounded else "⚠️ Low Confidence"
                st.caption(f"{grounded_label} | Score: {grounding_score:.2f}")

                # Save to history
                full_reply = f"{answer}\n\n**Sources:** {', '.join(sources)}"
                st.session_state.messages.append({"role": "assistant", "content": full_reply})

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure `uvicorn app.api:app --port 8000` is running.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

