# H1-balanced matched control

Opponent control (same game, same play type), with a caliper on |H1 PPP(trigger) − H1 PPP(control)|. Under a matched first-half level, regression to the mean predicts equal drops; surviving excess is the suppression estimate.

## Unconstrained vs caliper-matched

| Caliper | n pairs | Trig H1 | Ctrl H1 | H1 gap | Trig Δ | Ctrl Δ | Excess | 95% CI | t | perm p |
|---------|---------|---------|---------|--------|--------|--------|--------|--------|---|--------|
| none | 9,111 | 1.448 | 1.140 | +0.308 | 0.610 | -0.014 | **0.625** | [0.611, 0.638] | 91.4 | 0 |
| 0.05 | 593 | 1.299 | 1.298 | +0.001 | 0.558 | 0.155 | **0.403** | [0.362, 0.445] | 19.2 | 0 |
| 0.1 | 1,136 | 1.305 | 1.298 | +0.007 | 0.554 | 0.145 | **0.408** | [0.378, 0.438] | 27.1 | 0 |
| 0.15 | 1,715 | 1.311 | 1.301 | +0.011 | 0.553 | 0.156 | **0.397** | [0.373, 0.421] | 32.7 | 0 |
| 0.2 | 2,395 | 1.314 | 1.295 | +0.019 | 0.550 | 0.153 | **0.398** | [0.377, 0.418] | 38.6 | 0 |
| 0.3 | 3,417 | 1.323 | 1.290 | +0.033 | 0.549 | 0.136 | **0.412** | [0.395, 0.429] | 47.2 | 0 |

Primary specification: caliper 0.10. The paper reports cluster-robust intervals from `_rtm_cluster_robust.py`, not the row-level intervals in this file.

_Input: `all_half_stats_full_graph.csv`, `suppression_triggers_full_graph.csv`._
