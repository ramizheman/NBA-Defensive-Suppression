"""
H1-balanced matched-pair difference-in-differences.

Pairs each suppressed play with the opponent's same play type in the same
game, then keeps pairs whose first-half PPP differs by at most a caliper.
Primary caliper is 0.10. Runs from frozen CSVs only.

Usage:
    python _rtm_h1_matched.py
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
from scipy import stats

from _rtm_null_test import N_PERM, _build_matched, _permute_matched

REPO = Path(__file__).resolve().parent
OUT_DIR = REPO / "playsheet_validation" / "rtm_full_graph"
TRIGGER_CSV = OUT_DIR / "suppression_triggers_full_graph.csv"
ALL_STATS_CACHE = OUT_DIR / "all_half_stats_full_graph.csv"
REPORT_MD = OUT_DIR / "rtm_h1_matched_results.md"
CALIPERS = [0.05, 0.10, 0.15, 0.20, 0.30]


def _load_triggers() -> pd.DataFrame:
    df = pd.read_csv(TRIGGER_CSV, dtype={"gid_str": str, "gid": str})
    need = ["gid_str", "off_team", "def_team", "suppressed_pt",
            "h1_ppp", "h2_ppp", "h1_n", "h2_n", "delta"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise SystemExit(f"trigger CSV missing columns: {missing}")
    return df


def _load_all_stats() -> pd.DataFrame:
    if not ALL_STATS_CACHE.exists():
        raise SystemExit(
            f"Missing {ALL_STATS_CACHE}. This release ships the frozen "
            "half-level table; it does not rebuild it from a graph database."
        )
    return pd.read_csv(ALL_STATS_CACHE, dtype={"gid": str})


def _stats_block(matched: pd.DataFrame, *, run_perm: bool) -> dict:
    n = len(matched)
    if n < 2:
        return {"n": n}
    excess = matched["excess"].to_numpy()
    mean_excess = float(excess.mean())
    sem = float(stats.sem(excess))
    lo, hi = stats.t.interval(0.95, df=n - 1, loc=mean_excess, scale=sem)
    t_stat, t_p2 = stats.ttest_rel(matched["delta"], matched["c_delta"])
    out = {
        "n": n,
        "trig_delta": float(matched["delta"].mean()),
        "ctrl_delta": float(matched["c_delta"].mean()),
        "trig_h1": float(matched["h1_ppp"].mean()),
        "ctrl_h1": float(matched["c_h1_ppp"].mean()),
        "h1_gap": float(matched["h1_ppp"].mean() - matched["c_h1_ppp"].mean()),
        "excess": mean_excess,
        "ci_lo": float(lo),
        "ci_hi": float(hi),
        "t": float(t_stat),
        "p_one_sided": float(t_p2 / 2 if t_stat > 0 else 1.0),
    }
    if run_perm:
        perm = _permute_matched(matched, N_PERM)
        out["perm_p"] = float(perm["p_value"])
        out["perm_null_mean"] = float(perm["null_mean"])
    return out


def main() -> None:
    t0 = time.time()
    print("H1-balanced matched control")
    triggers = _load_triggers()
    print(f"  {len(triggers):,} triggers")
    all_stats = _load_all_stats()

    base = _build_matched(triggers, all_stats)
    base = base.dropna(subset=["excess", "h1_ppp", "c_h1_ppp"]).copy()
    base["h1_diff"] = (base["h1_ppp"] - base["c_h1_ppp"]).abs()
    orig = _stats_block(base, run_perm=True)
    print(
        f"  unconstrained n={orig['n']:,}  excess={orig['excess']:.3f}  "
        f"H1 gap={orig['h1_gap']:+.3f}"
    )

    rows = []
    for cal in CALIPERS:
        sub = base[base["h1_diff"] <= cal].copy()
        s = _stats_block(sub, run_perm=True)
        s["caliper"] = cal
        rows.append(s)
        print(
            f"  caliper {cal:.2f}: n={s['n']:,}  excess={s['excess']:.3f}  "
            f"H1 gap={s['h1_gap']:+.3f}"
        )

    _write_report(orig, rows)
    print(f"Saved {REPORT_MD}")
    print(f"Time: {time.time() - t0:.1f}s")


def _write_report(orig: dict, rows: list[dict]) -> None:
    def fmt(s: dict) -> str:
        return (
            f"| {s.get('caliper', '—')} | {s['n']:,} | {s['trig_h1']:.3f} | "
            f"{s['ctrl_h1']:.3f} | {s['h1_gap']:+.3f} | {s['trig_delta']:.3f} | "
            f"{s['ctrl_delta']:.3f} | **{s['excess']:.3f}** | "
            f"[{s['ci_lo']:.3f}, {s['ci_hi']:.3f}] | {s['t']:.1f} | "
            f"{s.get('perm_p', float('nan')):.4g} |"
        )

    lines = [
        "# H1-balanced matched control\n",
        "Opponent control (same game, same play type), with a caliper on "
        "|H1 PPP(trigger) − H1 PPP(control)|. Under a matched first-half "
        "level, regression to the mean predicts equal drops; surviving excess "
        "is the suppression estimate.\n",
        "## Unconstrained vs caliper-matched\n",
        "| Caliper | n pairs | Trig H1 | Ctrl H1 | H1 gap | Trig Δ | Ctrl Δ | "
        "Excess | 95% CI | t | perm p |",
        "|---------|---------|---------|---------|--------|--------|--------|"
        "--------|--------|---|--------|",
        fmt({**orig, "caliper": "none"}),
    ]
    for s in rows:
        lines.append(fmt(s))
    lines += [
        "",
        "Primary specification: caliper 0.10. The paper reports cluster-robust "
        "intervals from `_rtm_cluster_robust.py`, not the row-level intervals "
        "in this file.",
        "",
        f"_Input: `{ALL_STATS_CACHE.name}`, `{TRIGGER_CSV.name}`._",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
