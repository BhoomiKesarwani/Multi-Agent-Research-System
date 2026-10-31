import time
import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Multi-Agent Research System")
st.caption("Search Agent → Reader Agent → Writer → Critic")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "state" not in st.session_state:
    st.session_state.state = None
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "elapsed" not in st.session_state:
    st.session_state.elapsed = None

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
1. **Search Agent** finds recent, reliable information  
2. **Reader Agent** scrapes the most relevant URL  
3. **Writer** drafts the research report  
4. **Critic** reviews the report and gives feedback
        """
    )
    st.divider()
    if st.button("🗑️ Clear results", use_container_width=True):
        st.session_state.state = None
        st.session_state.topic = ""
        st.session_state.elapsed = None
        st.rerun()

# ---------------------------------------------------------------------------
# Pipeline (same logic as pipeline.py, but reports progress to the UI)
# ---------------------------------------------------------------------------
def run_pipeline_with_ui(topic: str) -> dict:
    state = {}

    # Step 1: search agent
    with st.status("Step 1 — Search agent is working...", expanded=False) as status:
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent , reliable and detailed information about:{topic}")]
        })
        state["search_results"] = search_result["messages"][-1].content
        status.update(label="Step 1 — Search complete ✅", state="complete")

    # Step 2: reader agent
    with st.status("Step 2 — Reader agent is scraping...", expanded=False) as status:
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}',"
                f"pick the most relevant URL and Scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:1000]}"
            )]
        })
        state["scraped_content"] = reader_result["messages"][-1].content
        status.update(label="Step 2 — Scraping complete ✅", state="complete")

    # Step 3: writer chain
    with st.status("Step 3 — Writer is drafting the report...", expanded=False) as status:
        research_combined = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n {state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
        })
        status.update(label="Step 3 — Report drafted ✅", state="complete")

    # Step 4: critic chain
    with st.status("Step 4 — Critic is reviewing the report...", expanded=False) as status:
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        status.update(label="Step 4 — Review complete ✅", state="complete")

    return state


# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------
with st.form("research_form"):
    topic_input = st.text_input(
        "Research topic",
        placeholder="e.g. Latest advances in solid-state batteries",
    )
    submitted = st.form_submit_button("🚀 Run research", type="primary")

if submitted:
    if not topic_input.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.state = None
        start = time.time()
        try:
            result = run_pipeline_with_ui(topic_input.strip())
            st.session_state.state = result
            st.session_state.topic = topic_input.strip()
            st.session_state.elapsed = time.time() - start
        except Exception as e:
            st.error(f"Something went wrong while running the pipeline:\n\n`{e}`")

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
state = st.session_state.state
if state:
    st.success(
        f"Research on **{st.session_state.topic}** finished in "
        f"{st.session_state.elapsed:.0f}s"
    )

    tab_report, tab_feedback, tab_search, tab_scrape = st.tabs(
        ["📄 Final Report", "🧐 Critic Feedback", "🔍 Search Results", "🌐 Scraped Content"]
    )

    with tab_report:
        st.markdown(state["report"])
        st.download_button(
            "⬇️ Download report (.md)",
            data=state["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_feedback:
        st.markdown(state["feedback"])

    with tab_search:
        st.markdown(state["search_results"])

    with tab_scrape:
        st.markdown(state["scraped_content"])