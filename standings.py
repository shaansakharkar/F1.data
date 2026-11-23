import plotly.graph_objects as go
import streamlit as st

from utils import driver_colors, driver_stats, heading, show, style, team_color, team_stats, text

MODES = {"Official (race + sprint)": "All", "Race only": "Race", "Sprint only": "Sprint"}

heading("Standings")
mode = MODES[st.radio("Points counted", list(MODES), horizontal=True)]
tab_d, tab_t = st.tabs(["Drivers", "Constructors"])

with tab_d:
    ds = driver_stats(mode)
    df = ds[["driver", "team", "wins", "podiums", "poles", "fastest_laps", "dnfs", "points"]].copy()
    df.insert(0, "Pos", range(1, len(df) + 1))
    df.columns = ["Pos", "Driver", "Team", "Wins", "Podiums", "Poles", "Fastest laps", "DNFs / DSQ", "Points"]
    top = int(df["Points"].max()) or 1
    st.dataframe(df, hide_index=True, width="stretch", height=38 * (len(df) + 1),
                 column_config={"Points": st.column_config.ProgressColumn("Points", min_value=0, max_value=top, format="%d")})
    show_n = st.slider("Drivers in the chart", 5, len(ds), 10)
    colors = driver_colors()
    top_ds = ds.head(show_n).iloc[::-1]
    fig = go.Figure(go.Bar(x=top_ds.points, y=top_ds.driver, orientation="h", text=top_ds.points, textposition="outside",
                           marker_color=[colors[d] for d in top_ds.driver], cliponaxis=False))
    fig.update_layout(xaxis_title="Points", yaxis_title=None, showlegend=False)
    show(style(fig, 60 + 36 * show_n))

with tab_t:
    ts = team_stats(mode)
    total = max(int(ts.points.sum()), 1)
    text(f"<b>{ts.iloc[0].team}</b> scored <b>{ts.iloc[0].points}</b> of {total} constructor points "
         f"(<b>{round(ts.iloc[0].points / total * 100)}%</b>).")
    df = ts.copy()
    df.insert(0, "Pos", range(1, len(df) + 1))
    df.columns = ["Pos", "Team", "Points", "Wins"]
    st.dataframe(df, hide_index=True, width="stretch", height=38 * (len(df) + 1),
                 column_config={"Points": st.column_config.ProgressColumn("Points", min_value=0, max_value=int(df.Points.max()) or 1, format="%d")})
    # stacked: each driver's contribution to the team total
    src = driver_stats(mode)
    fig = go.Figure()
    for team in ts.team[::-1]:
        for _, d in src[src.team == team].iterrows():
            fig.add_trace(go.Bar(y=[team], x=[d.points], orientation="h", name=d.driver, marker_color=driver_colors()[d.driver],
                                 text=f"{d.driver.split()[-1]} {d.points}", textposition="inside", hovertemplate="%{text}<extra></extra>"))
    fig.update_layout(barmode="stack", showlegend=False, xaxis_title="Points", yaxis_title=None)
    show(style(fig, 520))
