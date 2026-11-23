import plotly.graph_objects as go
import streamlit as st

from utils import (cumulative, driver_colors, driver_img, driver_stats, heading, load, points_matrix, show, short, style,
                   team_color, text)

res, qual, cal = load()
ds = driver_stats().set_index("driver")
heading("Drivers")
name = st.selectbox("Choose a driver", list(ds.index), format_func=lambda n: f"{n} · {ds.loc[n, 'team']}")
d = ds.loc[name]
colors = driver_colors()

left, right = st.columns([1, 1.4], gap="large")
with left:
    img = driver_img(name)
    if img:
        st.image(img, width="stretch")
    st.markdown(f"**{name}** · {d.team} · #{int(d.no)}")
with right:
    a, b, c = st.columns(3)
    a.metric("Points", int(d.points)); b.metric("Wins", int(d.wins)); c.metric("Podiums", int(d.podiums))
    a, b, c = st.columns(3)
    a.metric("Poles", int(d.poles)); b.metric("Fastest laps", int(d.fastest_laps)); c.metric("DNFs / DSQ", int(d.dnfs))
    a, b = st.columns(2)
    a.metric("Average finish", d.avg_finish); b.metric("Average grid", d.avg_grid)

heading("Points through the season")
champ = ds.index[0]
cum = cumulative()
fig = go.Figure()
fig.add_trace(go.Scatter(x=list(cum.columns), y=cum.loc[name], name=name, mode="lines+markers", line=dict(width=4, color=colors[name])))
if name != champ and st.toggle(f"Compare with the champion ({short(champ)})", value=True):
    fig.add_trace(go.Scatter(x=list(cum.columns), y=cum.loc[champ], name=champ, mode="lines", line=dict(width=2, dash="dot", color="#ffffff")))
fig.update_layout(xaxis_title="Round", yaxis_title="Cumulative points", hovermode="x unified")
show(style(fig))

heading("Round by round")
race = res[(res.driver == name) & (res.session == "Race")].merge(cal[["round", "gp"]], on="round").sort_values("round")
sprint = res[(res.driver == name) & (res.session == "Sprint")].set_index("round").points
race["sprint_pts"] = race["round"].map(sprint).fillna(0).astype(int)
fig = go.Figure()
fig.add_trace(go.Scatter(x=race["round"], y=race.grid.where(race.grid > 0), name="Starting grid", mode="lines+markers", line=dict(dash="dot", color="#949498")))
fig.add_trace(go.Scatter(x=race["round"], y=race.position, name="Finish", mode="lines+markers", line=dict(width=3, color=colors[name])))
fig.update_yaxes(autorange="reversed", title="Position")
fig.update_xaxes(title="Round", dtick=1)
text("Dotted line: where the driver started. Solid line: where they finished. A gap in the line means the race was not classified.")
show(style(fig, 380))
table = race[["round", "gp", "grid", "position", "status", "points", "sprint_pts"]].copy()
table.columns = ["Round", "Grand Prix", "Grid", "Finish", "Status", "Race pts", "Sprint pts"]
table["Finish"] = table["Finish"].astype("Int64")
st.dataframe(table, hide_index=True, width="stretch")
