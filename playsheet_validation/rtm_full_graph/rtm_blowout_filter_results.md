# Garbage-time / blowout filter

Excludes second-half possessions where |score_margin| exceeds the threshold. First-half baselines are left intact. Thresholds 15 / 20 / 25; 20 is the primary robustness cut.

Continue rate is a volume metric, so removing H2 possessions lowers it mechanically. PPP-based excess and cost are the clean comparisons.

## Trigger counts

| Filter | Triggers | RS | PO |
|--------|----------|----|----|
| no filter | 11,064 | 10,418 | 646 |
| \|margin\|<= 15 | 8,060 | 7,619 | 441 |
| \|margin\|<= 20 | 9,396 | 8,861 | 535 |
| \|margin\|<= 25 | 10,198 | 9,620 | 578 |

## Matched-control DiD excess

| Filter | Unconstrained excess | 95% CI | n pairs | H1-caliper 0.10 excess | 95% CI | n pairs |
|--------|---------------------|--------|---------|----------------------|--------|---------|
| no filter | 0.625 | [0.611, 0.638] | 9,111 | 0.408 | [0.378, 0.438] | 1,136 |
| \|margin\|<= 15 | 0.623 | [0.607, 0.639] | 6,245 | 0.403 | [0.370, 0.437] | 836 |
| \|margin\|<= 20 | 0.627 | [0.612, 0.642] | 7,490 | 0.412 | [0.380, 0.443] | 997 |
| \|margin\|<= 25 | 0.622 | [0.608, 0.636] | 8,232 | 0.416 | [0.385, 0.448] | 1,037 |
