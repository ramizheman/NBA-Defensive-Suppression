# NBA Defensive Suppression

Replication materials for:

**Zheman, R. (2026).** *Suppressed but Unmoved: Defensive Suppression and Failed Offensive Adaptation in the NBA.*

Paper: [`suppression_paper.tex`](suppression_paper.tex) · PDF: [`Detecting_Defensive_Suppression.pdf`](Detecting_Defensive_Suppression.pdf)

This repository reproduces the paper's tables and figures from **frozen possession-summary and trigger tables**. It does not include the NBA Stats API ingestion stack or a graph database.

## Setup

```bash
python -m pip install -r requirements.txt
```

Python 3.10+. Optional: `adjustText` for label placement on the quadrant figure.

## Reproduce the locked estimates

From the repository root:

```bash
python _rtm_h1_matched.py          # naive +0.625 vs balanced +0.408; caliper sweep
python _rtm_cluster_robust.py      # CR1 CI [0.378, 0.438]; 848 game clusters
python _response_ladder_ppp.py     # BEST − continue +0.445 / +0.584
python _h1h2_drop_compare.py       # raw H1→H2 drop ≈ 0.63
python _plot_quadrant.py           # figures/suppression-quadrant.png
```

Expected runtime: a few minutes for the matched-pair scripts (5,000 permutations); seconds for the ladder.

## Claim map

| Paper claim | Section | Script | Output |
|---|---|---|---|
| 863,752 possessions · 5,234 games · 11,064 triggers | Data, Table 1 | Frozen full-graph extract | [`playsheet_validation/rtm_full_graph/rtm_null_full_graph_results.md`](playsheet_validation/rtm_full_graph/rtm_null_full_graph_results.md) · [`playsheet_validation/rtm_full_graph/suppression_triggers_full_graph.csv`](playsheet_validation/rtm_full_graph/suppression_triggers_full_graph.csv) |
| Naive excess +0.625 (H1 gap +0.308) | Results, Table 2 | `_rtm_h1_matched.py` | [`playsheet_validation/rtm_full_graph/rtm_h1_matched_results.md`](playsheet_validation/rtm_full_graph/rtm_h1_matched_results.md) |
| Locked excess **+0.408** · triggered 1.305→0.751 · control 1.298→1.153 | Results, Tables 2–4 | `_rtm_h1_matched.py` | [`playsheet_validation/rtm_full_graph/rtm_h1_matched_results.md`](playsheet_validation/rtm_full_graph/rtm_h1_matched_results.md) |
| Cluster-robust 95% CI **[0.378, 0.438]** · *p*<0.0002 · 848 games | Inference | `_rtm_cluster_robust.py` | [`playsheet_validation/rtm_full_graph/rtm_cluster_robust_results.md`](playsheet_validation/rtm_full_graph/rtm_cluster_robust_results.md) |
| Caliper 0.05–0.30: +0.397 to +0.412 | Robustness, Table 3 | `_rtm_h1_matched.py` | [`playsheet_validation/rtm_full_graph/rtm_h1_matched_results.md`](playsheet_validation/rtm_full_graph/rtm_h1_matched_results.md) |
| Blowout \|margin\|≤15/20/25: +0.403 / **+0.412** / +0.416 | Robustness, Table 3 | Frozen | [`playsheet_validation/rtm_full_graph/rtm_blowout_filter_results.md`](playsheet_validation/rtm_full_graph/rtm_blowout_filter_results.md) |
| Continue in 93% of events · ~97–98% of H1 volume · ~5.4 points/trigger | Adaptation | `_response_ladder_ppp.py`, `_h1h2_drop_compare.py` | stdout · [`playsheet_validation/cost_of_ignoring_results.md`](playsheet_validation/cost_of_ignoring_results.md) |
| Collapse already on first 5 H2 attempts (0.852) | Adaptation, Table 5 | Frozen | [`playsheet_validation/cost_of_ignoring_results.md`](playsheet_validation/cost_of_ignoring_results.md) |
| Initiator swap 68% · drops 0.600 vs 0.639 | Initiator, Table 6 | Frozen | [`playsheet_validation/rs_holdout_25_26/suppression_vs_routing.md`](playsheet_validation/rs_holdout_25_26/suppression_vs_routing.md) |
| 1,539 triggers · 1,466 (95.3%) already had a better option · no systematic pivots | Pivots | Frozen | [`playsheet_validation/rs_holdout_25_26/adaptation_vs_generic.csv`](playsheet_validation/rs_holdout_25_26/adaptation_vs_generic.csv) |
| BEST − continue **+0.445** (PO) / **+0.584** (RS) | Ladder, Table 7 | `_response_ladder_ppp.py` | stdout |
| Team quadrant (drop vs unrealized gain) | Figure 1 | `_plot_quadrant.py` | [`figures/suppression-quadrant.png`](figures/suppression-quadrant.png) |
| BEST-tier share vs win % | Figure 2 | Frozen figure | [`figures/talent-vs-process.png`](figures/talent-vs-process.png) |

Three numbers that look similar and are not the same:

- **~0.63** — raw H1→H2 drop on the suppressed play (includes regression to the mean).
- **+0.41** — extra drop versus a same-game matched control (the identification claim).
- **~0.45 / ~0.58** — BEST counter minus continuing the dead play (opportunity cost, different possessions).

## Data files

| File | Role |
|---|---|
| `playsheet_validation/rtm_full_graph/all_half_stats_full_graph.csv` | Half-level (game, team, play type) counts and PPP |
| `playsheet_validation/rtm_full_graph/suppression_triggers_full_graph.csv` | 11,064 triggers for the DiD |
| `playsheet_validation/h1h2_aggregate_all_graph_series/trigger_table_clean.csv` | Playoff holdout (55 series, 633 triggers) |
| `playsheet_validation/rs_holdout_25_26/rs_trigger_table_clean.csv` | 2025–26 regular-season holdout (2,779 triggers) |

Trigger rule (Definition 1): both halves have at least 5 possessions of the play type, and first-half PPP exceeds second-half PPP by at least 0.25.

## What is not in this repository

- NBA Stats API ingestion and play-type classification (including PNR calibration).
- Graph-database query scripts used to build the frozen CSVs.
- Test, diagnostic, and exploratory notebooks.

A researcher with the same cached play-by-play and classifier version will obtain the same possession labels. The primary DiD needs only a flat table with game, team, play type, half, and points — the frozen CSVs are that table already aggregated.

## License

Paper © 2026 Rami Zheman. Code in this repository is provided for replication of the published estimates.
