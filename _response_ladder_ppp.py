"""Response ladder: continue vs ranked counters (playoffs and regular season)."""
from __future__ import annotations

import csv
from pathlib import Path

N_GATE = 5
H2_GATE = 5
REPO = Path(__file__).resolve().parent


def load(path):
    rows = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        r["counter_h2_ppp"] = float(r["counter_h2_ppp"])
        r["counter_h2_n"] = int(r["counter_h2_n"])
        r["h1_ppp"] = float(r["h1_ppp"])
        r["h2_ppp"] = float(r["h2_ppp"])
        r["h1_n"] = int(r["h1_n"])
        r["h2_n"] = int(r["h2_n"])
        rows.append(r)
    return rows


def row_mean(rows):
    if not rows:
        return None, 0
    return sum(r["counter_h2_ppp"] for r in rows) / len(rows), len(rows)


def mean(vals):
    return sum(vals) / len(vals) if vals else None


def analyze(path, label):
    rows = load(path)
    gated = [r for r in rows if r["counter_h2_n"] >= N_GATE]
    trig = {}
    for r in rows:
        k = (r["gid"], r["off_team"], r["suppressed_pt"])
        if k not in trig:
            trig[k] = r
    cont = [t for t in trig.values() if t["h2_n"] >= H2_GATE]
    cont_ppp = mean([t["h2_ppp"] for t in cont])
    h1_ppp = mean([t["h1_ppp"] for t in cont])
    drop = h1_ppp - cont_ppp
    vol = sum(t["h2_n"] for t in cont) / sum(t["h1_n"] for t in cont) * 100
    cost = sum((t["h1_ppp"] - t["h2_ppp"]) * t["h2_n"] for t in cont) / len(cont)
    best_ppp, _ = row_mean([r for r in gated if r["tier"] == "BEST"])
    avoid_ppp, _ = row_mean([r for r in gated if r["tier"] == "AVOID"])
    insuff_ppp, _ = row_mean(
        [r for r in gated if r["tier"] in ("SYSTEM_MISSED_GOOD", "SYSTEM_MISSED_BAD")]
    )
    any_ppp, _ = row_mean(gated)
    return {
        "label": label,
        "h1": h1_ppp,
        "h2": cont_ppp,
        "drop": drop,
        "vol": vol,
        "cost": cost,
        "avoid": avoid_ppp,
        "best": best_ppp,
        "insuff": insuff_ppp,
        "any": any_ppp,
    }


def main() -> None:
    po = analyze(
        REPO / "playsheet_validation/h1h2_aggregate_all_graph_series/trigger_table_clean.csv",
        "PO",
    )
    rs = analyze(
        REPO / "playsheet_validation/rs_holdout_25_26/rs_trigger_table_clean.csv",
        "RS",
    )
    print("Row-mean tables (n>=5 on trigger H2 or counter H2)")
    print()
    print(f"{'Metric':<40} {'PO':>8} {'RS':>8}")
    print("-" * 58)
    print(f"{'H1 PPP':<40} {po['h1']:>8.2f} {rs['h1']:>8.2f}")
    print(f"{'H2 PPP (continue suppressed play)':<40} {po['h2']:>8.2f} {rs['h2']:>8.2f}")
    print(f"{'H1->H2 drop':<40} {po['drop']:>8.2f} {rs['drop']:>8.2f}")
    print(f"{'H2 volume vs H1':<40} {po['vol']:>7.0f}% {rs['vol']:>7.0f}%")
    print(f"{'Cost per trigger':<40} {po['cost']:>7.1f} {rs['cost']:>7.1f}")
    print()
    print(f"{'Response':<40} {'PO PPP':>8} {'RS PPP':>8}")
    print("-" * 58)
    print(f"{'Continue suppressed play':<40} {po['h2']:>8.3f} {rs['h2']:>8.3f}")
    print(f"{'AVOID counter (worst)':<40} {po['avoid']:>8.3f} {rs['avoid']:>8.3f}")
    print(f"{'BEST counter':<40} {po['best']:>8.3f} {rs['best']:>8.3f}")
    print(f"{'INSUFF (aggregated)':<40} {po['insuff']:>8.3f} {rs['insuff']:>8.3f}")
    print(f"{'Any pivot':<40} {po['any']:>8.3f} {rs['any']:>8.3f}")
    print(f"{'BEST vs continue':<40} {po['best']-po['h2']:>+8.3f} {rs['best']-rs['h2']:>+8.3f}")
    print(f"{'BEST vs AVOID':<40} {po['best']-po['avoid']:>+8.3f} {rs['best']-rs['avoid']:>+8.3f}")
    print(f"{'AVOID vs continue':<40} {po['avoid']-po['h2']:>+8.3f} {rs['avoid']-rs['h2']:>+8.3f}")
    print(f"{'Any pivot vs continue':<40} {po['any']-po['h2']:>+8.3f} {rs['any']-rs['h2']:>+8.3f}")


if __name__ == "__main__":
    main()
