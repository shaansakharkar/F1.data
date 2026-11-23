import plotly.graph_objects as go
import streamlit as st

from utils import (cumulative, driver_colors, driver_img, driver_stats, heading, load, short, show, style, text)

res, qual, cal = load()
ds, colors, cum = driver_stats(), driver_colors(), cumulative()
names = list(ds.driver)
heading("Compare two drivers")
c1, c2 = st.columns(2)
a = c1.selectbox("Driver A", names, index=0)
b = c2.selectbox("Driver B", names, index=1)
if a == b:
    st.warning("Pick two different drivers.")
    st.stop()
sa, sb = ds[ds.driver == a].iloc[0], ds[ds.driver == b].iloc[0]

for col, name in ((c1, a), (c2, b)):
    img = driver_img(name)
    if img:
        col.image(img, width="stretch")

rows = [("Points", "points"), ("Wins", "wins"), ("Podiums", "podiums"), ("Poles", "poles"), ("Fastest laps", "fastest_laps"),
        ("DNFs / DSQ", "dnfs"), ("Average finish", "avg_finish"), ("Average grid", "avg_grid")]
for label, key in rows:
    m1, m2 = st.columns(2)
    better_low = key in ("dnfs", "avg_finish", "avg_grid")
    d = sa[key] - sb[key]
    m1.metric(label, sa[key], None if d == 0 else f"{d:+.1f}".rstrip("0").rstrip(".") if isinstance(d, float) else f"{d:+d}",
              delta_color="inverse" if better_low else "normal")
    m2.metric(label, sb[key])

heading("Points through the season")
fig = go.Figure()
for n in (a, b):
    fig.add_trace(go.Scatter(x=list(cum.columns), y=cum.loc[n], name=n, mode="lines", line=dict(width=3.5, color=colors[n])))
fig.update_layout(xaxis_title="Round", yaxis_title="Cumulative points", hovermode="x unified")
show(style(fig))

heading("Head to head")
race = res[res.session == "Race"]
fa = race[race.driver == a].set_index("round").position
fb = race[race.driver == b].set_index("round").position
both = fa.index.intersection(fb.index)
ahead_a = int(((fa[both] < fb[both]) & fa[both].notna() & fb[both].notna()).sum())
ahead_b = int(((fb[both] < fa[both]) & fa[both].notna() & fb[both].notna()).sum())
qa = qual[qual.driver == a].set_index("round").position
qb = qual[qual.driver == b].set_index("round").position
qboth = qa.index.intersection(qb.index)
qa_ahead = int((qa[qboth] < qb[qboth]).sum()); qb_ahead = int((qb[qboth] < qa[qboth]).sum())
text(f"Both classified in {int(fa[both].notna().mul(fb[both].notna()).sum())} of {len(both)} shared races. "
     f"<b>{short(a)}</b> finished ahead {ahead_a} times, <b>{short(b)}</b> {ahead_b}. In qualifying: "
     f"<b>{short(a)}</b> {qa_ahead}, <b>{short(b)}</b> {qb_ahead}.")
fig = go.Figure()
for n, ser in ((a, fa), (b, fb)):
    fig.add_trace(go.Scatter(x=ser.index, y=ser.values, name=n, mode="lines+markers", line=dict(color=colors[n])))
fig.update_yaxes(autorange="reversed", title="Finishing position")
fig.update_xaxes(title="Round", dtick=1)
show(style(fig, 400))
