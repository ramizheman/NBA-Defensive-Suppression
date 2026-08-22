"""
Cluster-robust inference for the matched-pair DiD.

CR1 standard errors clustered on game; cluster-level sign-flip permutation.
Primary paper interval is the game-clustered CI at caliper 0.10.

Usage:
    python _rtm_cluster_robust.py
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from _rtm_h1_matched import _load_all_stats, _load_triggers
from _rtm_null_test import _build_matched

REPO = Path(__file__).resolve().parent
OUT_DIR = REPO / "playsheet_validation" / "rtm_full_graph"
REPORT_MD = OUT_DIR / "rtm_cluster_robust_results.md"
N_PERM = 5000
DATASETS = [("none", None), ("caliper 0.10", 0.10), ("caliper 0.20", 0.20)]


def _cluster_robust_se(x: np.ndarray, cluster_ids: np.ndarray) -> tuple[float, int]:
    x = np.asarray(x, dtype=float)
    n = len(x)
    r = x - x.mean()
    s_g = pd.Series(r).groupby(cluster_ids).sum().to_numpy()
    g = len(s_g)
    meat = float(np.sum(s_g ** 2))
    var = (meat / (n ** 2)) * (g / (g - 1))
    return float(np.sqrt(var)), g


def _cluster_signflip_p(
    x: np.ndarray, cluster_ids: np.ndarray, n_perm: int = N_PERM, seed: int = 42
) -> float:
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    codes, _ = pd.factorize(cluster_ids)
    g = int(codes.max()) + 1
    obs = x.mean()
    null = np.empty(n_perm)
    for i in range(n_perm):
        signs = rng.choice([-1.0, 1.0], size=g)
        null[i] = float((x * signs[codes]).mean())
    return float((null >= obs).mean())


def _row_signflip_p(x: np.ndarray, n_perm: int = N_PERM, seed: int = 42) -> float:
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    obs = x.mean()
    null = np.empty(n_perm)
    for i in range(n_perm):
        signs = rng.choice([-1.0, 1.0], size=len(x))
        null[i] = float((x * signs).mean())
    return float((null >= obs).mean())


def _analyze(label: str, m: pd.DataFrame) -> dict:
    x = m["excess"].to_numpy(dtype=float)
    n = len(x)
    mean = float(x.mean())
    se_iid = float(stats.sem(x))
    lo_iid, hi_iid = stats.t.interval(0.95, df=n - 1, loc=mean, scale=se_iid)
    p_row = _row_signflip_p(x)

    g_ids = m["gid_str"].to_numpy()
    se_g, n_g = _cluster_robust_se(x, g_ids)
    lo_g, hi_g = stats.t.interval(0.95, df=n_g - 1, loc=mean, scale=se_g)
    p_g = _cluster_signflip_p(x, g_ids)

    gt_ids = (m["gid_str"].astype(str) + "|" + m["off_team"].astype(str)).to_numpy()
    se_gt, n_gt = _cluster_robust_se(x, gt_ids)
    lo_gt, hi_gt = stats.t.interval(0.95, df=n_gt - 1, loc=mean, scale=se_gt)
    p_gt = _cluster_signflip_p(x, gt_ids)

    deff_g = (se_g / se_iid) ** 2
    return {
        "label": label, "n": n, "mean": mean,
        "se_iid": se_iid, "ci_iid": (lo_iid, hi_iid),
        "w_iid": hi_iid - lo_iid, "p_row": p_row,
        "n_g": n_g, "se_g": se_g, "ci_g": (lo_g, hi_g),
        "w_g": hi_g - lo_g, "p_g": p_g, "neff_g": n / deff_g, "deff_g": deff_g,
        "n_gt": n_gt, "se_gt": se_gt, "ci_gt": (lo_gt, hi_gt),
        "w_gt": hi_gt - lo_gt, "p_gt": p_gt, "neff_gt": n / ((se_gt / se_iid) ** 2),
        "mean_per_g": n / n_g,
    }


def main() -> None:
    t0 = time.time()
    print("Cluster-robust inference")
    triggers = _load_triggers()
    all_stats = _load_all_stats()
    base = _build_matched(triggers, all_stats)
    base = base.dropna(subset=["excess", "h1_ppp", "c_h1_ppp"]).copy()
    base["h1_diff"] = (base["h1_ppp"] - base["c_h1_ppp"]).abs()

    results = []
    for label, cal in DATASETS:
        m = base if cal is None else base[base["h1_diff"] <= cal].copy()
        print(f"[{label}] n={len(m):,}")
        r = _analyze(label, m)
        results.append(r)
        print(
            f"  game clusters={r['n_g']:,}  excess={r['mean']:.3f}  "
            f"CI [{r['ci_g'][0]:.3f}, {r['ci_g'][1]:.3f}]  p={r['p_g']:.4g}"
        )

    _write_report(results)
    print(f"Saved {REPORT_MD}")
    print(f"Time: {time.time() - t0:.1f}s")


def _write_report(results: list[dict]) -> None:
    lines = [
        "# Cluster-robust inference (matched DiD)\n",
        "Pairs can share a game. This file reports CR1 cluster-robust standard "
        "errors and a cluster-level sign-flip permutation. The paper cites the "
        "game-clustered interval at caliper 0.10.\n",
        "## Effective sample size\n",
        "| Dataset | Row pairs | Game clusters | Mean pairs/game | "
        "game+team clusters | Eff. n (game) | Eff. n (game+team) |",
        "|---------|-----------|---------------|-----------------|"
        "--------------------|---------------|--------------------|",
    ]
    for r in results:
        lines.append(
            f"| {r['label']} | {r['n']:,} | {r['n_g']:,} | {r['mean_per_g']:.2f} | "
            f"{r['n_gt']:,} | {r['neff_g']:.0f} | {r['neff_gt']:.0f} |"
        )
    lines += [
        "",
        "## SE / CI / p — row vs cluster\n",
        "| Dataset | Mean excess | SE row | SE game | SE game+team | "
        "CI row | CI game | CI game+team | p row | p game | p game+team |",
        "|---------|-------------|--------|---------|--------------|"
        "--------|---------|--------------|-------|--------|-------------|",
    ]
    for r in results:
        lines.append(
            f"| {r['label']} | {r['mean']:.3f} | {r['se_iid']:.4f} | "
            f"{r['se_g']:.4f} | {r['se_gt']:.4f} | "
            f"[{r['ci_iid'][0]:.3f}, {r['ci_iid'][1]:.3f}] | "
            f"[{r['ci_g'][0]:.3f}, {r['ci_g'][1]:.3f}] | "
            f"[{r['ci_gt'][0]:.3f}, {r['ci_gt'][1]:.3f}] | "
            f"{r['p_row']:.4g} | {r['p_g']:.4g} | {r['p_gt']:.4g} |"
        )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
