import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import (driver_colors, driver_img, heading, img_uri, load, one, short, show, slug, style, team_color,
                   track_img)

res, qual, cal = load()
heading("Races")
labels = {int(r.round): f"R{int(r.round):02d} · {r.gp}" for r in cal.itertuples()}
rnd = st.select_slider("Round", options=list(labels), value=max(labels), format_func=lambda r: f"R{r:02d}")
c = cal[cal["round"] == rnd].iloc[0]
st.markdown(f"### {c.gp}")
st.caption(f"{c.circuit}, {c.city} · {c.date:%d %B %Y}" + (" · Sprint weekend" if c.has_sprint else ""))

left, right = st.columns([1.5, 1], gap="large")
with left:
    img = track_img(rnd)
    if img:
        st.image(img, width="stretch")
with right:
    st.markdown(one(f"""<div class="facts">
    <div>Laps<b>{c.laps}</b></div><div>Length<b>{c.length_km} km</b></div><div>Race distance<b>{c.race_km} km</b></div>
    <div>Turns<b>{c.turns}</b></div><div>DRS zones<b>{c.drs_zones}</b></div><div>First GP<b>{c.first_gp}</b></div>
    <div style="grid-column:1/-1">Lap record<b>{c.lap_record} · {c.record_owner} ({c.record_year})</b></div></div>"""),
        unsafe_allow_html=True)

race = res[(res.round == rnd) & (res.session == "Race")].sort_values("position", na_position="last")
sprint = res[(res.round == rnd) & (res.session == "Sprint")].sort_values("position", na_position="last")
quali = qual[qual["round"] == rnd].sort_values("position")

heading("Podium")
cols = st.columns(3)
for col, r in zip(cols, race.head(3).itertuples()):
    col.markdown(one(f"""<div class="pod" style="--c:{team_color(r.team)}"><img alt="" src="{img_uri(f'drivers/{slug(r.driver)}.jpg')}">
    <div><b><em>P{int(r.position)}</em>{r.driver}</b>{r.team} · {r.time}</div></div>"""), unsafe_allow_html=True)

tabs = st.tabs(["Race result", "Qualifying", "Sprint"] if c.has_sprint else ["Race result", "Qualifying"])
with tabs[0]:
    t = race[["position", "driver", "team", "grid", "time", "status", "points", "fastest_lap"]].copy()
    t["gained"] = (t.grid.where(t.grid > 0) - t.position).astype("Int64")
    t["position"] = t.position.astype("Int64")
    t.columns = ["Pos", "Driver", "Team", "Grid", "Time / gap", "Status", "Points", "Fastest lap", "Places gained"]
    st.dataframe(t, hide_index=True, width="stretch", height=38 * (len(t) + 1))
    colors = driver_colors()
    fin = race[race.position.notna()]
    fig = go.Figure(go.Scatter(x=fin.grid.where(fin.grid > 0), y=fin.position, mode="markers+text", text=[short(d) for d in fin.driver],
                               textposition="top center", marker=dict(size=11, color=[colors.get(d, "#888") for d in fin.driver])))
    fig.add_shape(type="line", x0=1, y0=1, x1=20, y1=20, line=dict(color="#949498", dash="dot"))
    fig.update_layout(xaxis_title="Starting grid", yaxis_title="Finishing position", showlegend=False)
    fig.update_yaxes(autorange="reversed")
    st.caption("Drivers below the dotted line gained places; above it lost places.")
    show(style(fig, 460))
with tabs[1]:
    q = quali[["position", "driver", "team", "q1", "q2", "q3"]].copy()
    q["position"] = q.position.astype("Int64")
    q.columns = ["Pos", "Driver", "Team", "Q1", "Q2", "Q3"]
    st.dataframe(q, hide_index=True, width="stretch", height=38 * (len(q) + 1))
if c.has_sprint:
    with tabs[2]:
        s = sprint[["position", "driver", "team", "grid", "time", "points"]].copy()
        s["position"] = s.position.astype("Int64")
        s.columns = ["Pos", "Driver", "Team", "Grid", "Time / gap", "Points"]
        st.dataframe(s, hide_index=True, width="stretch", height=38 * (len(s) + 1))
