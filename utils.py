"""Shared data loading, calculations, helpers and styling for the F1 2025 app."""
import base64
import io
import zlib
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent
DATA, ASSETS = ROOT / "data", ROOT / "assets"
RED, MUTED, LINE = "#e10600", "#949498", "#38383f"

TEAM_COLORS = {
    "McLaren": "#FF8000", "Red Bull Racing": "#3671C6", "Mercedes": "#27F4D2", "Ferrari": "#E80020",
    "Williams": "#64C4FF", "Aston Martin": "#229971", "Racing Bulls": "#6692FF",
    "Kick Sauber": "#52E252", "Haas F1 Team": "#B6BABD", "Alpine": "#FF87BC",
}


def team_color(team):
    return TEAM_COLORS.get(team, "#888888")


def short(name):
    return name.split()[-1]


def slug(name):
    return name.replace(" ", "_")


def lighten(hex_color, f):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * f) for c in (r, g, b))


# ---------------------------------------------------------------- data
def _bundle():
    try:
        import bundle
        return bundle
    except ImportError:
        return None


def _csv_text(name):
    p = DATA / name
    if p.exists():
        return p.read_text(encoding="utf-8")
    b = _bundle()
    return zlib.decompress(base64.b64decode(b.CSV[name])).decode("utf-8") if b and name in b.CSV else None


def load():
    """Return (results, qualifying, calendar). Stops with a clear message if data is missing."""
    missing = [n for n in ("results.csv", "qualifying.csv", "calendar.csv") if _csv_text(n) is None]
    if missing:
        st.error(f"Missing data: {', '.join(missing)}. Upload bundle.py (or the `data` folder) next to app.py.")
        st.stop()
    return _load()


@st.cache_data
def _load():
    res = pd.read_csv(io.StringIO(_csv_text("results.csv")))
    qual = pd.read_csv(io.StringIO(_csv_text("qualifying.csv")))
    cal = pd.read_csv(io.StringIO(_csv_text("calendar.csv")), parse_dates=["date"])
    return res, qual, cal


def _source(session):
    res, _, _ = load()
    return res if session == "All" else res[res.session == session]


@st.cache_data
def driver_stats(session="All"):
    """One row per driver: points for the chosen session plus season statistics."""
    res, qual, _ = load()
    race = res[res.session == "Race"]
    out = race.sort_values("round").groupby("driver").agg(team=("team", "last"), no=("no", "last"))
    out["points"] = _source(session).groupby("driver").points.sum()
    out["wins"] = race[race.position == 1].groupby("driver").size()
    out["podiums"] = race[race.position <= 3].groupby("driver").size()
    out["poles"] = qual[qual.position == 1].groupby("driver").size()
    out["fastest_laps"] = race[race.fastest_lap == "Yes"].groupby("driver").size()
    out["dnfs"] = race[race.status.isin(["Retired", "Disqualified"])].groupby("driver").size()
    out["avg_finish"] = race.groupby("driver").position.mean().round(1)
    out["avg_grid"] = race[race.grid > 0].groupby("driver").grid.mean().round(1)
    out = out.fillna(0)
    for c in ["points", "wins", "podiums", "poles", "fastest_laps", "dnfs"]:
        out[c] = out[c].astype(int)
    return out.sort_values(["points", "wins"], ascending=False).reset_index()


@st.cache_data
def team_stats(session="All"):
    race = _source("Race")
    out = pd.DataFrame({"points": _source(session).groupby("team").points.sum()})
    out["wins"] = race[race.position == 1].groupby("team").size()
    return out.fillna(0).astype(int).sort_values("points", ascending=False).reset_index()


@st.cache_data
def cumulative(session="All"):
    """Cumulative points per driver (rows) after each round (columns 1..24)."""
    m = _source(session).groupby(["driver", "round"]).points.sum().unstack(fill_value=0)
    return m.reindex(columns=range(1, 25), fill_value=0).cumsum(axis=1)


@st.cache_data
def points_matrix(session="All"):
    m = _source(session).groupby(["driver", "round"]).points.sum().unstack(fill_value=0)
    return m.reindex(columns=range(1, 25), fill_value=0)


@st.cache_data
def driver_colors():
    """Teammates share the team colour; the second and third driver get a lighter tint."""
    colors, seen = {}, {}
    for _, row in driver_stats().iterrows():
        n = seen.get(row.team, 0)
        colors[row.driver] = lighten(team_color(row.team), .5 * n) if n else team_color(row.team)
        seen[row.team] = n + 1
    return colors


# ---------------------------------------------------------------- images
@st.cache_data
def _img_bytes(rel):
    p = ASSETS / rel
    if p.exists():
        return p.read_bytes()
    b = _bundle()
    return base64.b64decode(b.IMG[rel]) if b and rel in b.IMG else None


def img_uri(rel):
    data = _img_bytes(rel)
    return "data:image/jpeg;base64," + base64.b64encode(data).decode() if data else ""


def driver_img(name):
    return _img_bytes(f"drivers/{slug(name)}.jpg")


def car_img(team):
    return _img_bytes(f"cars/{slug(team)}.jpg")


def track_img(rnd):
    return _img_bytes(f"tracks/{int(rnd):02d}.jpg")


# ---------------------------------------------------------------- charts
def style(fig, height=440):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Titillium Web, sans-serif", color="#ffffff", size=14), height=height,
                      margin=dict(l=8, r=8, t=24, b=8), legend=dict(orientation="h", y=1.12))
    fig.update_xaxes(gridcolor=LINE, zerolinecolor=LINE)
    fig.update_yaxes(gridcolor=LINE, zerolinecolor=LINE)
    return fig


def show(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# ---------------------------------------------------------------- layout helpers
def one(html):
    """Collapse HTML to one line so Streamlit's markdown parser keeps it as a single block."""
    return "".join(line.strip() for line in html.splitlines())


def heading(title, aside=""):
    st.markdown(f'<div class="sh"><h2>{title}</h2><span>{aside}</span></div>', unsafe_allow_html=True)


def text(html):
    st.markdown(f'<p class="tx">{html}</p>', unsafe_allow_html=True)


def inject_css():
    p = ROOT / "style.css"
    if p.exists():
        css = p.read_text(encoding="utf-8")
    else:
        b = _bundle()
        css = zlib.decompress(base64.b64decode(b.CSS)).decode("utf-8") if b else ""
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def page_path(name):
    """Path of a page file for st.page_link (pages live in views/, or next to app.py)."""
    return f"{name}.py" if (ROOT / f"{name}.py").exists() else f"views/{name}.py"
