import streamlit as st

from config import OLLAMA_MODEL, TOP_K
from src.generate import generate_stream
from src.pipeline import REFUSAL_MESSAGE, finalize, prepare
from src.prompt import REFUSAL_TOKEN

st.set_page_config(page_title="Converse with Aristotle")
st.title("Converse with Aristotle")
st.caption(
    "Answers are drawn only from W. D. Ross's translation of the Nicomachean Ethics. "
    f"Running locally on {OLLAMA_MODEL}."
)

with st.sidebar:
    k = st.slider("Passages to retrieve (k)", min_value=2, max_value=6, value=TOP_K)
    st.write("Answers cite passages as [1], [2]. Open 'Sources' under an answer to read them.")

if "history" not in st.session_state:
    st.session_state.history = []


def render_sources(result: dict, gated: bool) -> None:
    with st.expander(f"Sources (top similarity {result['top_score']:.2f})"):
        for i, c in enumerate(result["chunks"], start=1):
            if gated:
                tag = "not sent to the model"
            else:
                tag = "cited" if i in result["cited"] else "retrieved"
            st.markdown(f"**[{i}] {c['citation']}** | similarity {c['score']:.2f} | {tag}")
            st.write(c["text"])


for turn in st.session_state.history:
    with st.chat_message("user"):
        st.write(turn["query"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])
        if turn["refused"]:
            st.caption(f"Refused ({turn['reason']})")
        render_sources(turn, render_sources(turn, gated=turn["reason"] in ("low_retrieval_score", "low_rerank_score")))

query = st.chat_input("Ask about happiness, virtue, justice, friendship...")
if query:
    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant"):
        prep = prepare(query, k)
        placeholder = st.empty()
        raw = None
        if not prep["gated"]:
            raw = ""
            for token in generate_stream(prep["messages"]):
                raw += token
                # do not flash the raw refusal token at the user
                if not REFUSAL_TOKEN.startswith(raw.strip()):
                    placeholder.markdown(raw + "▌")
        result = finalize(prep, raw)
        placeholder.markdown(result["answer"])
        if result["refused"]:
            st.caption(f"Refused ({result['reason']})")
        render_sources(result, gated=prep["gated"])
    st.session_state.history.append(result)