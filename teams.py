import plotly.graph_objects as go
import streamlit as st

from utils import car_img, driver_colors, driver_stats, heading, load, points_matrix, show, style, team_color, team_stats

res, qual, cal = load()
ts, ds, colors = team_stats(), driver_stats(), driver_colors()
heading("Teams")
team = st.selectbox("Choose a team", list(ts.team))
row = ts[ts.team == team].iloc[0]
mates = ds[ds.team == team]

left, right = st.columns([1, 1.3], gap="large")
with left:
    img = car_img(team)
    if img:
        st.image(img, width="stretch")
with right:
    a, b, c = st.columns(3)
    a.metric("Points", int(row.points)); b.metric("Wins", int(row.wins)); c.metric("Rank", f"{list(ts.team).index(team) + 1} of {len(ts)}")
    st.markdown("**Drivers this season (by points):** " + ", ".join(f"{r.driver} ({r.points})" for r in mates.itertuples()))

heading("Points by round")
pm = points_matrix()
fig = go.Figure()
for drv in mates.driver:
    fig.add_trace(go.Bar(x=list(pm.columns), y=pm.loc[drv], name=drv, marker_color=colors[drv]))
fig.update_layout(barmode="stack", xaxis_title="Round", yaxis_title="Points (race + sprint)")
show(style(fig))

heading("Constructors’ championship")
picked = st.multiselect("Teams", list(ts.team), default=list(ts.team[:5]))
tm = res.groupby(["team", "round"]).points.sum().unstack(fill_value=0).reindex(columns=range(1, 25), fill_value=0).cumsum(axis=1)
fig = go.Figure()
for t in picked:
    fig.add_trace(go.Scatter(x=list(tm.columns), y=tm.loc[t], name=t, mode="lines", line=dict(width=4 if t == team else 2.5, color=team_color(t))))
fig.update_layout(xaxis_title="Round", yaxis_title="Cumulative points", hovermode="x unified")
show(style(fig))
