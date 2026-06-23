"""
Event-level visuals for the THREE finals, using StatsBomb open data + mplsoccer.

StatsBomb's free data only covers the finals (not the group/knockout matches), but it's
true event data: every shot, pass and touch with pitch coordinates and an xG value. We use
it for the most detailed views:
  - Ronaldo's shot map across the three finals (marker size = xG, goals highlighted)
  - Ronaldo's touch heatmaps per final (his positional evolution: wide in 2016 -> central in 2018)

Outputs: outputs/05_finals_shot_map.png, outputs/06_finals_heatmaps.png
"""
import os, warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch
from statsbombpy import sb
import common as C

NAVY, GOLD, RED, GREY = "#0a1f44", "#d4af37", "#c0392b", "#9aa3b2"
FINALS = [  # (match_id, label, opponent)
    (18243, "2016 Final", "vs Atlético Madrid"),
    (18244, "2017 Final", "vs Juventus"),
    (18245, "2018 Final", "vs Liverpool"),
]


def ronaldo_events(match_id):
    ev = sb.events(match_id=match_id)
    return ev[ev["player"].astype(str).str.contains("Cristiano Ronaldo", na=False)].copy()


def shot_map():
    pitch = VerticalPitch(pitch_type="statsbomb", half=True, pitch_color="white",
                          line_color=GREY, linewidth=1)
    fig, axes = pitch.draw(nrows=1, ncols=3, figsize=(13, 6))
    for ax, (mid, label, opp) in zip(axes, FINALS):
        ev = ronaldo_events(mid)
        # exclude penalty-shootout shots (StatsBomb period 5) so this reflects open play / ET
        shots = ev[(ev["type"] == "Shot") & (ev["period"] != 5)]
        for _, s in shots.iterrows():
            x, y = s["location"]
            xg = s.get("shot_statsbomb_xg", 0) or 0
            goal = s.get("shot_outcome") == "Goal"
            pitch.scatter(x, y, s=400 * xg + 60, ax=ax, zorder=3,
                          color=GOLD if goal else NAVY, alpha=0.85 if goal else 0.5,
                          edgecolors=RED if goal else NAVY, linewidth=2 if goal else 0.8)
        goals = int((shots["shot_outcome"] == "Goal").sum())
        ax.set_title(f"{label}\n{opp}\n{len(shots)} shots · {goals} goal{'s' if goals != 1 else ''}",
                     fontsize=11, color=NAVY, fontweight="bold")
    fig.suptitle("Cristiano Ronaldo — shot maps across the three finals  (marker size = xG, gold = goal)",
                 fontsize=13, color=NAVY, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(C.OUT, "05_finals_shot_map.png"), bbox_inches="tight", dpi=130)
    plt.close(fig)


def heatmaps():
    pitch = Pitch(pitch_type="statsbomb", pitch_color="white", line_color=GREY, linewidth=1)
    fig, axes = pitch.draw(nrows=1, ncols=3, figsize=(15, 5))
    for ax, (mid, label, opp) in zip(axes, FINALS):
        ev = ronaldo_events(mid)
        touches = ev[ev["location"].notna()]
        xs = [loc[0] for loc in touches["location"]]
        ys = [loc[1] for loc in touches["location"]]
        pitch.kdeplot(xs, ys, ax=ax, fill=True, levels=60, thresh=0.05,
                      cmap="Blues", alpha=0.9)
        pitch.scatter(xs, ys, ax=ax, s=8, color=NAVY, alpha=0.35, zorder=2)
        ax.set_title(f"{label} {opp}\n{len(touches)} touches",
                     fontsize=11, color=NAVY, fontweight="bold")
    fig.suptitle("Ronaldo's touch maps — positional evolution (attack →) : wide in 2016, central by 2018",
                 fontsize=13, color=NAVY, fontweight="bold", y=1.04)
    fig.tight_layout()
    fig.savefig(os.path.join(C.OUT, "06_finals_heatmaps.png"), bbox_inches="tight", dpi=130)
    plt.close(fig)


def run():
    shot_map()
    heatmaps()
    print("Saved finals visuals -> outputs/05, 06")


if __name__ == "__main__":
    run()
