# 🔎 Multi-Agent Research System

A multi-agent pipeline that researches a topic and produces a reviewed report: **Search Agent → Reader Agent → Writer → Critic**. Runs in the terminal or through a Streamlit UI.

##Live Demo

[https://multi-agent-research-system-ybbul9qehrkljheicujmzi.streamlit.app/]

## Project Structure

```
├── agents.py          # Search, reader, writer and critic definitions
├── tools.py           # Tools used by the agents
├── pipeline.py        # Terminal runner
├── app.py             # Streamlit UI
├── requirements.txt
└── .env               # API keys (not committed)
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install streamlit
```

Create a `.env` file with the API keys your agents and tools need.

## Usage

**Web UI**

```bash
streamlit run app.py
```

**Terminal**

```bash
python pipeline.py
```

## Output

The pipeline returns a dict with `search_results`, `scraped_content`, `report` and `feedback`. The UI shows each in its own tab and lets you download the report as Markdown.
