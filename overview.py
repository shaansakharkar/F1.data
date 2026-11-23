import streamlit as st

from utils import (driver_stats, heading, img_uri, load, one, page_path, short, slug, team_color, team_stats)

res, qual, cal = load()
ds, ts = driver_stats(), team_stats()
champ, second, third = ds.iloc[0], ds.iloc[1], ds.iloc[2]
most = ds.sort_values(["wins", "points"], ascending=False).iloc[0]
race = res[res.session == "Race"]
winners = race[race.position == 1].merge(cal[["round", "gp", "circuit", "date"]], on="round").sort_values("round")
n_rounds, top_team = len(cal), ts.iloc[0]
share = round(top_team.points / ts.points.sum() * 100)


def photo(path_key, kind):
    """Embed a driver/car image as a data URI so it can sit inside the HTML cards."""
    return img_uri(f"{kind}/{slug(path_key)}.jpg")


if most.driver == champ.driver:
    caption = f"{short(champ.driver)} wins the title and the most races: {champ.wins} wins, {champ.points} points"
else:
    gap = champ.points - int(ds.loc[ds.driver == most.driver, "points"].iloc[0])
    caption = f"{short(most.driver)} wins {most.wins} races but {short(champ.driver)} takes the title by {gap} points"

# ---- info strip
last = winners.iloc[-1]
st.markdown(one(f"""
<div class="sh" style="margin:0 0 18px"><h2 style="font-size:15px;letter-spacing:0">● Season complete › {last.gp} · Round {int(last['round'])} of {n_rounds}</h2>
<span>Championship leader {short(champ.driver)} {champ.points} · Top constructor {top_team.team} {top_team.points}</span></div>"""),
    unsafe_allow_html=True)

# ---- headline grid
cards = [
    (f"{short(champ.driver)} wins the title by {champ.points - second.points} points: {champ.points} to {second.points}", photo(champ.driver, "drivers")),
    (f"{top_team.team} scored {share}% of all constructor points", photo(top_team.team, "cars")),
    (f"{short(most.driver)} won the most races: {most.wins} of {len(winners)}", photo(most.driver, "drivers")),
    (f"{short(third.driver)} finished {champ.points - third.points} points off the title", photo(third.driver, "drivers")),
]
mid = "".join(f'<div class="mc"><div class="th"><img alt="" src="{src}"></div>{t}</div>' for t, src in cards)
latest = "".join(
    f'<div class="ri"><span>{r.gp}: {short(r.driver)} wins</span><span class="bd" style="--c:{team_color(r.team)}">{r.no}</span></div>'
    for r in winners.tail(4).iloc[::-1].itertuples())
st.markdown(one(f"""
<div class="hg"><div class="big"><img alt="Red Bull Racing car" src="{img_uri('hero.jpg')}"><div class="cap"><span class="tag">Title race</span><div>{caption}</div></div></div>
<div class="mg">{mid}</div><div>{latest}</div></div>
<div class="ban"><p>{n_rounds} rounds. {winners.driver.nunique()} winners. <b>{top_team.points}</b> points for {top_team.team}.</p></div>"""),
    unsafe_allow_html=True)

# ---- key numbers
a, b, c, d = st.columns(4)
a.metric("Rounds", n_rounds, f"{int(cal.has_sprint.sum())} with a sprint")
b.metric("Different winners", winners.driver.nunique())
c.metric("Champion", short(champ.driver), f"{champ.points} pts")
d.metric("Pole positions", int(ds.poles.max()), short(ds.sort_values("poles", ascending=False).iloc[0].driver))

# ---- race by race carousel
heading("Race by race", "Scroll sideways →")
cards_html = "".join(
    f'<div class="rc"><div class="rv" style="--c:{team_color(w.team)}"><i>#{w.no}</i><b>R{int(w.round):02d}</b></div>'
    f'<div class="rt">{w.gp}</div><div class="rs">{short(w.driver)} · {w.time}</div></div>' for w in winners.itertuples())
st.markdown(f'<div class="car">{cards_html}</div>', unsafe_allow_html=True)

# ---- jump links
heading("Explore")
cols = st.columns(6)
for col, (page, label) in zip(cols, [("standings", "Standings"), ("drivers", "Drivers"), ("teams", "Teams"),
                                      ("races", "Races"), ("insights", "Insights"), ("compare", "Compare")]):
    col.page_link(page_path(page), label=label)
st.caption("Source: Formula 1 2025 season datasets (race, sprint and qualifying results, calendar, driver and circuit "
           "images). Standings include sprint points. Independent fan project, not affiliated with Formula 1.")
