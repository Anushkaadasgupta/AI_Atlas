import streamlit as st

from agent import DEFAULT_MODEL, app


WELCOME_MESSAGE = (
    "Hi, I’m AI Atlas — a ChatGPT-style assistant for study help, project guidance, "
    "career advice, mental health support, food/health topics, and image prompts. "
    "Ask naturally and I’ll keep the conversation going."
)

SUGGESTIONS = [
    "Help me plan a project from scratch",
    "Write a better resume summary for me",
    "Give me a detailed image prompt for a study room photo",
    "Explain anxiety support in a kind and simple way",
    "Create a 7-day study plan for exams",
    "Suggest career paths after computer science",
]


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]
    if "provider" not in st.session_state:
        st.session_state.provider = "auto"
    if "model" not in st.session_state:
        st.session_state.model = DEFAULT_MODEL
    if "style" not in st.session_state:
        st.session_state.style = "balanced"
    if "top_k" not in st.session_state:
        st.session_state.top_k = 4


def reset_chat() -> None:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]


def add_custom_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.5rem;
            max-width: 1120px;
        }
        .hero {
            padding: 1.4rem 1.5rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 52%, #7c3aed 100%);
            color: white;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.22);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2.2rem;
            line-height: 1.1;
        }
        .hero p {
            margin: 0.55rem 0 0 0;
            opacity: 0.94;
            font-size: 1rem;
        }
        .feature-card {
            padding: 1rem 1rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.04);
            border: 1px solid rgba(148, 163, 184, 0.22);
            min-height: 104px;
        }
        .feature-card strong {
            display: block;
            color: #0f172a;
            margin-bottom: 0.35rem;
            font-size: 0.98rem;
        }
        .feature-card span {
            color: #475569;
            font-size: 0.92rem;
        }
        div[data-testid="stChatMessage"] {
            border-radius: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>AI Atlas</h1>
            <p>A cleaner, ChatGPT-style assistant for learning, projects, careers, health guidance, and image prompts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    first, second, third, fourth = st.columns(4)
    with first:
        st.markdown(
            """
            <div class="feature-card">
                <strong>Conversational</strong>
                <span>Supports follow-ups, context, and natural back-and-forth dialogue.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with second:
        st.markdown(
            """
            <div class="feature-card">
                <strong>Knowledge aware</strong>
                <span>Uses your dataset as grounding context when it helps the answer.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with third:
        st.markdown(
            """
            <div class="feature-card">
                <strong>Project ready</strong>
                <span>Helpful for planning, docs, debugging, resumes, and career guidance.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with fourth:
        st.markdown(
            """
            <div class="feature-card">
                <strong>Prompt friendly</strong>
                <span>Great for generating detailed photo and image prompts on demand.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar() -> None:
    with st.sidebar:
        st.title("Settings")
        st.caption("Use Groq for the full chat experience, or let the app fall back gracefully.")

        st.session_state.provider = st.selectbox(
            "Provider",
            ["auto", "groq", "fallback"],
            index=["auto", "groq", "fallback"].index(
                "groq" if st.session_state.provider == "openai" else st.session_state.provider
            ),
        )
        st.session_state.model = st.text_input(
            "Model",
            value=st.session_state.model,
            help="Example: llama3-8b-8192",
        )
        st.session_state.style = st.selectbox(
            "Answer style",
            ["balanced", "concise", "detailed"],
            index=["balanced", "concise", "detailed"].index(st.session_state.style),
        )
        st.session_state.top_k = st.slider("Knowledge snippets", 1, 6, st.session_state.top_k)

        st.button("Clear chat", use_container_width=True, on_click=reset_chat)

        st.info(
            "Set `GROQ_API_KEY` in your `.env` file to unlock live LLM replies. Without it, the app uses fallback answers."
        )


def render_suggestions() -> None:
    st.subheader("Try asking")
    prompt_columns = st.columns(2)
    for index, suggestion in enumerate(SUGGESTIONS):
        target_column = prompt_columns[index % 2]
        with target_column:
            if st.button(suggestion, use_container_width=True, key=f"suggestion_{index}"):
                st.session_state.pending_prompt = suggestion
                st.rerun()


def render_messages() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main() -> None:
    st.set_page_config(
        page_title="AI Atlas",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_state()
    add_custom_styles()
    render_sidebar()
    render_header()
    render_suggestions()
    render_messages()

    pending_prompt = st.session_state.pop("pending_prompt", None)
    user_input = pending_prompt or st.chat_input("Ask anything — from projects to health to image prompts...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = app.invoke(
                    {
                        "question": user_input,
                        "messages": st.session_state.messages[:-1],
                        "settings": {
                            "provider": st.session_state.provider,
                            "model": st.session_state.model,
                            "style": st.session_state.style,
                            "top_k": st.session_state.top_k,
                        },
                    }
                )

            answer = result["answer"]
            st.markdown(answer)

            if result.get("context"):
                with st.expander("Knowledge used"):
                    st.markdown(result["context"])

        st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
