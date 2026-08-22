"""Raw first-to-second-half drop on holdout trigger tables (row-mean)."""
from __future__ import annotations

import csv
from pathlib import Path

REPO = Path(__file__).resolve().parent


def trig_stats(rows, label, h2_min=5):
    trig = {}
    for r in rows:
        k = (r["gid"], r["off_team"], r["suppressed_pt"])
        if k not in trig:
            trig[k] = {
                "h1_ppp": float(r["h1_ppp"]),
                "h2_ppp": float(r["h2_ppp"]),
                "h1_n": int(r["h1_n"]),
                "h2_n": int(r["h2_n"]),
            }
    cont = [t for t in trig.values() if t["h2_n"] >= h2_min]
    h1_mean = sum(t["h1_ppp"] for t in cont) / len(cont)
    h2_mean = sum(t["h2_ppp"] for t in cont) / len(cont)
    drop_per_trig = sum(t["h1_ppp"] - t["h2_ppp"] for t in cont) / len(cont)
    h1_poss = sum(t["h1_n"] for t in cont)
    h2_poss = sum(t["h2_n"] for t in cont)
    cost_per_trig = sum((t["h1_ppp"] - t["h2_ppp"]) * t["h2_n"] for t in cont) / len(cont)
    print(f"\n=== {label} (h2_n>={h2_min}) ===")
    print(f"  Triggers: {len(cont)}")
    print(f"  mean H1 PPP: {h1_mean:.3f}")
    print(f"  mean H2 PPP: {h2_mean:.3f}")
    print(f"  mean drop per trigger: {drop_per_trig:.3f}")
    print(f"  H2 volume / H1 volume: {h2_poss / h1_poss * 100:.1f}%")
    print(f"  Cost per trigger (pts vs H1 on H2 volume): {cost_per_trig:.1f}")


def load_csv(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def main() -> None:
    po = load_csv(REPO / "playsheet_validation/h1h2_aggregate_all_graph_series/trigger_table_clean.csv")
    rs = load_csv(REPO / "playsheet_validation/rs_holdout_25_26/rs_trigger_table_clean.csv")
    trig_stats(po, "Playoffs (55 series)")
    trig_stats(rs, "Regular season 2025-26")
    fg_path = REPO / "playsheet_validation/rtm_full_graph/suppression_triggers_full_graph.csv"
    if fg_path.exists():
        fg = load_csv(fg_path)
        drops = [float(r["h1_ppp"]) - float(r["h2_ppp"]) for r in fg]
        print(f"\n=== Full-graph triggers ({len(fg)}) ===")
        print(f"  mean drop per trigger: {sum(drops)/len(drops):.3f}")


if __name__ == "__main__":
    main()
