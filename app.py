"""Season ’25 — Formula 1 results, standings and analysis (Streamlit).

Run locally:  streamlit run app.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Season ’25 — F1 results & analysis", page_icon="🏁", layout="wide")

HERE = Path(__file__).parent
PAGES = [  # (file name without .py, title, icon)
    ("overview", "Overview", "🏁"),
    ("standings", "Standings", "🏆"),
    ("drivers", "Drivers", "🧑‍✈️"),
    ("teams", "Teams", "🏎️"),
    ("races", "Races", "🗓️"),
    ("insights", "Insights", "📈"),
    ("compare", "Compare", "⚔️"),
]


def find(name):
    """Pages sit next to app.py (flat layout); a views/ folder is also accepted."""
    for p in (HERE / f"{name}.py", HERE / "views" / f"{name}.py"):
        if p.exists():
            return p.relative_to(HERE).as_posix()
    return None


missing = [n for n, _, _ in PAGES if find(n) is None]
if missing or not (HERE / "utils.py").exists():
    st.error("Some app files are missing from the GitHub repository.")
    st.write("Missing page files:", [f"views/{n}.py" for n in missing] or "none",
             "· utils.py found:", (HERE / "utils.py").exists())
    st.write("Files next to app.py:", sorted(p.name for p in HERE.iterdir() if not p.name.startswith(".")))
    st.info("Upload all the project files (app.py, utils.py, bundle.py and the seven page files) to the "
            "repository, then reboot the app.")
    st.stop()

from utils import inject_css  # noqa: E402  (must come after set_page_config)

inject_css()

pages = [st.Page(find(n), title=t, icon=i, default=(n == "overview")) for n, t, i in PAGES]
try:
    nav = st.navigation(pages, position="top")
except TypeError:  # older Streamlit versions only support the sidebar
    nav = st.navigation(pages)
nav.run()
