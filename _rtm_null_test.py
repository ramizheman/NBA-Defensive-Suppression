"""
Same-game matched control for defensive suppression.

For each triggered (game, team, play type), the control is the opponent
running the same play type in the same game. Excess is the difference in
first-to-second-half PPP drops (triggered minus control).

This module is CSV-only. It does not query a database.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

N_PERM = 5_000
PLAY_TYPES = ["CUT", "DRIVE", "PNR", "POST_UP", "PULL_UP", "SPOT_UP"]
TRIGGER_MIN_H1 = 5


def _fmt_gid(gid) -> str:
    s = str(int(gid)) if str(gid).isdigit() else str(gid)
    return "00" + s if len(s) < 10 else s


def _build_matched(triggers: pd.DataFrame, all_stats: pd.DataFrame) -> pd.DataFrame:
    """Pair each trigger with the opponent's same-play-type H1/H2 stats."""
    h1 = all_stats[all_stats["half"] == "H1"].copy()
    h2 = all_stats[all_stats["half"] == "H2"].copy()
    h1 = h1.rename(columns={"n": "c_h1_n", "sum_ppp": "c_h1_sum"}).drop(columns=["half"])
    h2 = h2.rename(columns={"n": "c_h2_n", "sum_ppp": "c_h2_sum"}).drop(columns=["half"])
    wide = pd.merge(h1, h2, on=["gid", "team", "pt"], how="inner")
    wide["c_h1_ppp"] = wide["c_h1_sum"] / wide["c_h1_n"]
    wide["c_h2_ppp"] = wide["c_h2_sum"] / wide["c_h2_n"]
    wide["c_delta"] = wide["c_h1_ppp"] - wide["c_h2_ppp"]
    wide = wide[wide["c_h1_n"] >= TRIGGER_MIN_H1]
    wide = wide[wide["c_h2_n"] >= TRIGGER_MIN_H1]

    opponent = pd.merge(
        triggers[["gid_str", "off_team", "def_team", "suppressed_pt",
                  "h1_ppp", "h2_ppp", "h1_n", "h2_n", "delta"]],
        wide.rename(columns={"gid": "gid_str", "team": "def_team", "pt": "suppressed_pt"}),
        on=["gid_str", "def_team", "suppressed_pt"],
        how="inner",
    )
    opponent["excess"] = opponent["delta"] - opponent["c_delta"]
    return opponent


def _permute_matched(matched: pd.DataFrame, n_perm: int = N_PERM) -> dict:
    """Row-level sign-flip permutation of excess under a zero-mean null."""
    rng = np.random.default_rng(42)
    real_excess = matched["excess"].mean()
    null_means = []
    for _ in range(n_perm):
        flips = rng.integers(0, 2, size=len(matched))
        null_excess = np.where(
            flips == 1,
            matched["c_delta"].values - matched["delta"].values,
            matched["excess"].values,
        )
        null_means.append(null_excess.mean())
    null_means = np.array(null_means)
    p_val = (null_means >= real_excess).mean()
    return {
        "real_excess": real_excess,
        "null_mean": null_means.mean(),
        "null_std": null_means.std(),
        "p95": np.percentile(null_means, 95),
        "p_value": p_val,
        "significant": bool(p_val < 0.05),
        "n_perm": n_perm,
    }
