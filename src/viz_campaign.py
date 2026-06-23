"""
Campaign-level charts (matplotlib) for the Ronaldo UCL project.
Reads the query CSVs produced by analyze_sql.py and writes PNGs to outputs/.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import common as C

# --- simple, clean house style (Real Madrid-ish navy + gold) ---
NAVY, GOLD, GREY, RED = "#0a1f44", "#d4af37", "#9aa3b2", "#c0392b"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GREY,
    "axes.linewidth": 0.8, "axes.grid": True, "grid.color": "#eef0f4",
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 130,
})


def q(name):
    return pd.read_csv(os.path.join(C.PROC, f"q_{name}.csv"))


def _bar_labels(ax, bars, fmt="{:.0f}"):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                fmt.format(b.get_height()), ha="center", va="bottom", fontsize=10, color=NAVY)


def chart_goals_by_stage():
    d = q("goals_by_stage")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [GREY if s == "Group stage" else NAVY for s in d["stage"]]
    colors[d.index[d["stage"] == "Quarter-final"][0]] = GOLD  # highlight his QF dominance
    bars = ax.bar(d["stage"], d["goals"], color=colors)
    _bar_labels(ax, bars)
    ax.set_title("Ronaldo goals by Champions League stage (2015-18)", fontweight="bold", color=NAVY)
    ax.set_ylabel("Goals")
    ax.text(0.99, 0.95, "Quarter-finals: 11 goals in 6 games (1.83/game)",
            transform=ax.transAxes, ha="right", va="top", color=GOLD, fontsize=9, fontweight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(C.OUT, "01_goals_by_stage.png")); plt.close(fig)


def chart_goals_per_season():
    d = q("goals_per_season")
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bars = ax.bar(d["season"], d["goals"], color=NAVY, width=0.55)
    _bar_labels(ax, bars)
    ax2 = ax.twinx()
    ax2.plot(d["season"], d["goals_per_match"], color=GOLD, marker="o", lw=2.5, label="Goals/match")
    ax2.set_ylim(0, 2); ax2.set_ylabel("Goals per match", color=GOLD); ax2.grid(False)
    for x, v in zip(d["season"], d["goals_per_match"]):
        ax2.text(x, v + 0.06, f"{v:.2f}", ha="center", color=GOLD, fontsize=9, fontweight="bold")
    ax.set_title("Top scorer in all three winning campaigns", fontweight="bold", color=NAVY)
    ax.set_ylabel("Goals"); ax.set_ylim(0, 20)
    fig.tight_layout(); fig.savefig(os.path.join(C.OUT, "02_goals_per_season.png")); plt.close(fig)


def chart_goal_timing():
    d = q("goal_timing")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [RED if "late" in w else NAVY for w in d["window"]]
    bars = ax.bar(d["window"], d["goals"], color=colors)
    _bar_labels(ax, bars)
    ax.set_title("When Ronaldo scored: 13 goals came after the 76th minute",
                 fontweight="bold", color=NAVY)
    ax.set_ylabel("Goals"); ax.set_xlabel("Minute of goal")
    fig.tight_layout(); fig.savefig(os.path.join(C.OUT, "03_goal_timing.png")); plt.close(fig)


def chart_cumulative():
    """Cumulative goals across all 39 matches, in chronological order."""
    df = pd.read_csv(os.path.join(C.PROC, "ronaldo_ucl_campaign.csv"))
    df["cum"] = df["ronaldo_goals"].cumsum()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(range(1, len(df) + 1), df["cum"], color=NAVY, lw=2.5)
    ax.fill_between(range(1, len(df) + 1), df["cum"], color=NAVY, alpha=0.07)
    # mark season boundaries
    boundaries = df.reset_index().groupby("season")["index"].min().tolist()
    for b in boundaries[1:]:
        ax.axvline(b + 0.5, color=GREY, ls="--", lw=0.8)
    for season, sub in df.groupby("season"):
        mid = (sub.index.min() + sub.index.max()) / 2 + 1
        ax.text(mid, 3, season, ha="center", color=GREY, fontsize=9)
    ax.text(len(df), df["cum"].iloc[-1], "  43 goals", va="center", color=GOLD, fontweight="bold")
    ax.set_title("Cumulative Champions League goals, 2015-2018", fontweight="bold", color=NAVY)
    ax.set_ylabel("Cumulative goals"); ax.set_xlabel("Match number (chronological)")
    fig.tight_layout(); fig.savefig(os.path.join(C.OUT, "04_cumulative_goals.png")); plt.close(fig)


def run():
    chart_goals_by_stage()
    chart_goals_per_season()
    chart_goal_timing()
    chart_cumulative()
    print("Saved campaign charts -> outputs/01..04")


if __name__ == "__main__":
    run()
