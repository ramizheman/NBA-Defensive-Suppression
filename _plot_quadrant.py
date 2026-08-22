"""Team-level quadrant: suppression severity vs unrealized counter gain."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    from adjustText import adjust_text
    HAS_ADJUST = True
except ImportError:
    HAS_ADJUST = False

REPO = Path(__file__).resolve().parent
FIGURES = REPO / "figures"
TRIGGER_CSV = REPO / "playsheet_validation/rs_holdout_25_26/rs_trigger_table_clean.csv"
TOTAL_GAMES = 82
DROP_MED = 0.631
GAIN_MED = 0.571
HIGH_AVOID = {"BKN", "UTA", "POR"}


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    seen = set()
    trig_rows = []
    trig_gids = defaultdict(set)
    for r in csv.DictReader(open(TRIGGER_CSV, encoding="utf-8")):
        key = (r["gid"], r["off_team"], r["suppressed_pt"])
        if key in seen:
            continue
        seen.add(key)
        trig_rows.append(r)
        trig_gids[r["off_team"]].add(r["gid"])

    by_team = defaultdict(lambda: {"h1": [], "h2": [], "best": []})
    for r in trig_rows:
        t = r["off_team"]
        by_team[t]["h1"].append(float(r["h1_ppp"]))
        by_team[t]["h2"].append(float(r["h2_ppp"]))

    for r in csv.DictReader(open(TRIGGER_CSV, encoding="utf-8")):
        if r.get("tier") == "BEST" and int(r.get("counter_h2_n", 0)) >= 5:
            by_team[r["off_team"]]["best"].append(float(r["counter_h2_ppp"]))

    teams = []
    for team in sorted(by_team.keys()):
        d = by_team[team]
        h1 = mean(d["h1"])
        h2 = mean(d["h2"])
        drop = h1 - h2
        best = mean(d["best"]) if d["best"] else None
        gain = (best - h2) if best is not None else None
        trig_pct = len(trig_gids[team]) / TOTAL_GAMES
        if drop and gain:
            teams.append((team, drop, gain, trig_pct))

    pct_min = min(t[3] for t in teams)
    pct_max = max(t[3] for t in teams)
    s_min, s_max = 200, 2200

    def bubble_size(pct):
        if pct_max <= pct_min:
            return (s_min + s_max) / 2
        t = (pct - pct_min) / (pct_max - pct_min)
        return s_min + (t ** 1.5) * (s_max - s_min)

    fig, ax = plt.subplots(figsize=(22, 9))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")
    ax.axvspan(0.555, DROP_MED, ymin=0, ymax=1, color="#EBF3FB", alpha=0.5, zorder=0)
    ax.axvspan(DROP_MED, 0.725, ymin=0, ymax=1, color="#F2E8F5", alpha=0.6, zorder=0)
    ax.axhline(GAIN_MED, color="#AAAAAA", linewidth=1.2, linestyle="--", zorder=1)
    ax.axvline(DROP_MED, color="#AAAAAA", linewidth=1.2, linestyle="--", zorder=1)
    ax.text(0.718, 0.795, "High drop · High gain\n(hurt most, most to gain)",
            fontsize=12, color="#666", va="top", ha="right", style="italic")
    ax.text(0.558, 0.795, "Low drop · High gain\n(lighter hit, still leaving value)",
            fontsize=12, color="#666", va="top", ha="left", style="italic")
    ax.text(0.718, GAIN_MED - 0.005, "High drop · Low gain\n(suppressed hard, weak counter menu)",
            fontsize=12, color="#666", va="top", ha="right", style="italic")
    ax.text(0.558, GAIN_MED - 0.005, "Low drop · Low gain\n(best-adapted or no counter signal)",
            fontsize=12, color="#666", va="top", ha="left", style="italic")

    texts = []
    for team, drop, gain, trig_pct in teams:
        c = "#C0392B" if team in HIGH_AVOID else "#2C3E50"
        ax.scatter(drop, gain, s=bubble_size(trig_pct), color=c, zorder=3,
                   edgecolors="white", linewidths=1.0, alpha=0.82)
        fc = "#C0392B" if team in HIGH_AVOID else "#1A252F"
        texts.append(ax.text(
            drop, gain, team, fontsize=11, fontweight="bold", color=fc,
            ha="center", va="center", zorder=10,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.88),
        ))

    if HAS_ADJUST:
        adjust_text(
            texts,
            x=[d for _, d, _, _ in teams],
            y=[g for _, _, g, _ in teams],
            ax=ax,
            expand=(2.2, 2.0),
            force_text=(1.0, 1.2),
            force_points=(1.0, 1.0),
            arrowprops=dict(arrowstyle="-", color="#BBBBBB", lw=0.6, shrinkA=12, shrinkB=2),
        )

    ax.set_xlabel("Suppression severity: H1 → H2 PPP drop (higher = hurt more)", fontsize=16, labelpad=14)
    ax.set_ylabel("Unrealized gain: Best counter PPP − H2 PPP\n(higher = more pts/poss left on table)", fontsize=16, labelpad=14)
    ax.set_xlim(0.555, 0.725)
    ax.set_ylim(0.22, 0.80)
    ax.tick_params(labelsize=14)
    for pct in (pct_min, (pct_min + pct_max) / 2, pct_max):
        ax.scatter([], [], s=bubble_size(pct), color="#888888", alpha=0.65,
                   edgecolors="white", linewidths=1.2, label=f"{pct:.0%} of games")
    legend1 = ax.legend(
        title="Bubble size = share of games\nwith suppression trigger",
        fontsize=11, title_fontsize=11, loc="lower left",
        framealpha=0.95, edgecolor="#CCCCCC",
    )
    ax.add_artist(legend1)
    ax.legend(handles=[
        mpatches.Patch(color="#C0392B", label="High AVOID rate (>15%)"),
        mpatches.Patch(color="#2C3E50", label="All other teams"),
    ], fontsize=12, loc="lower right", framealpha=0.9, edgecolor="#CCCCCC")
    for spine in ax.spines.values():
        spine.set_edgecolor("#CCCCCC")
    plt.tight_layout()
    out = FIGURES / "suppression-quadrant.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
