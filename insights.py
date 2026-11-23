import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (cumulative, driver_colors, driver_stats, heading, load, points_matrix, short, show, style, team_color,
                   text)

res, qual, cal = load()
ds, colors = driver_stats(), driver_colors()
gp = cal.set_index("round").gp
heading("Insights")
t1, t2, t3, t4 = st.tabs(["Title race", "Points heatmap", "Qualifying vs race", "Reliability"])

with t1:
    mode = st.radio("Points", ["Official (race + sprint)", "Race only"], horizontal=True)
    cum = cumulative("All" if mode.startswith("Official") else "Race")
    order = cum.iloc[:, -1].sort_values(ascending=False)
    leaders = cum.idxmax()
    changes = int((leaders != leaders.shift()).sum() - 1)
    text(f"<b>{short(order.index[0])}</b> finishes on <b>{int(order.iloc[0])}</b>, <b>{int(order.iloc[0] - order.iloc[2])}</b> clear of "
         f"{short(order.index[2])} in third. The lead changed hands <b>{changes} times</b> across {len(cum.columns)} rounds.")
    picked = st.multiselect("Drivers", list(order.index[:10]), default=list(order.index[:6]))
    fig = go.Figure()
    for d in picked:
        fig.add_trace(go.Scatter(x=list(cum.columns), y=cum.loc[d], name=short(d), mode="lines",
                                 line=dict(width=4 if d == order.index[0] else 2.5, color=colors.get(d, "#888"))))
    race = res[(res.session == "Race") & res.driver.isin(picked) & res.status.isin(["Retired", "Disqualified"])]
    if st.toggle("Mark retirements and disqualifications", value=True) and len(race):
        xs, ys, tx, cs = [], [], [], []
        for r in race.itertuples():
            xs.append(r.round); ys.append(cum.loc[r.driver, r.round]); cs.append(colors.get(r.driver, "#888"))
            tx.append(f"{r.driver}<br>R{r.round} {gp[r.round]}<br>{r.status}")
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", name="Retired / disqualified", text=tx, hovertemplate="%{text}<extra></extra>",
                                 marker=dict(symbol="x", size=11, color=cs, line=dict(width=1, color="#000"))))
    fig.update_layout(xaxis_title="Round", yaxis_title="Cumulative points", hovermode="closest")
    show(style(fig, 500))

with t2:
    sess = st.radio("Session", ["Race", "Sprint", "Race + sprint"], horizontal=True)
    pm = points_matrix({"Race": "Race", "Sprint": "Sprint", "Race + sprint": "All"}[sess]).loc[ds.driver.head(12)]
    top = pm.values.max() or 1
    fig = px.imshow(pm.values, x=[f"R{c}" for c in pm.columns], y=[short(d) for d in pm.index], aspect="auto", text_auto=True,
                    color_continuous_scale=["#15151e", "#e10600"], zmin=0, zmax=top)
    fig.update_layout(coloraxis_showscale=False)
    text("Each square is the points a driver scored in one round. Brighter means a bigger haul.")
    show(style(fig, 520))

with t3:
    race = res[res.session == "Race"]
    avg = race.groupby("driver").agg(grid=("grid", lambda s: s[s > 0].mean()), finish=("position", "mean"), points=("points", "sum"))
    avg = avg.join(ds.set_index("driver").team).dropna().reset_index()
    fig = px.scatter(avg, x="grid", y="finish", size="points", color="team", text=avg.driver.map(short),
                     color_discrete_map={t: team_color(t) for t in avg.team.unique()}, size_max=34)
    fig.add_shape(type="line", x0=1, y0=1, x1=20, y1=20, line=dict(color="#949498", dash="dot"))
    fig.update_traces(textposition="top center")
    fig.update_yaxes(autorange="reversed", title="Average finishing position")
    fig.update_xaxes(title="Average starting position")
    fig.update_layout(showlegend=False)
    text("Drivers below the dotted line finish ahead of where they start on average. Bubble size is total race points.")
    show(style(fig, 520))

with t4:
    race = res[res.session == "Race"]
    bad = race[race.status.isin(["Retired", "Disqualified", "Did not start"])].groupby(["driver", "status"]).size().unstack(fill_value=0)
    bad["total"] = bad.sum(axis=1)
    bad = bad.sort_values("total").tail(12)
    fig = go.Figure()
    for status, col in [("Retired", "#e10600"), ("Disqualified", "#FFD08A"), ("Did not start", "#949498")]:
        if status in bad:
            fig.add_trace(go.Bar(y=[short(d) for d in bad.index], x=bad[status], name=status, orientation="h", marker_color=col))
    fig.update_layout(barmode="stack", xaxis_title="Races")
    text("Races a driver did not finish, was disqualified from, or did not start. Top 12 drivers.")
    show(style(fig, 460))
