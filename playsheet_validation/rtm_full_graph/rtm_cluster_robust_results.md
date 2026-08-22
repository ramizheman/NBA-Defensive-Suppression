# Cluster-robust inference (matched DiD)

Pairs can share a game. This file reports CR1 cluster-robust standard errors and a cluster-level sign-flip permutation. The paper cites the game-clustered interval at caliper 0.10.

## Effective sample size

| Dataset | Row pairs | Game clusters | Mean pairs/game | game+team clusters | Eff. n (game) | Eff. n (game+team) |
|---------|-----------|---------------|-----------------|--------------------|---------------|--------------------|
| none | 9,111 | 4,342 | 2.10 | 6,496 | 7979 | 9192 |
| caliper 0.10 | 1,136 | 848 | 1.34 | 1,099 | 1088 | 1121 |
| caliper 0.20 | 2,395 | 1,661 | 1.44 | 2,203 | 2305 | 2376 |

## SE / CI / p — row vs cluster

| Dataset | Mean excess | SE row | SE game | SE game+team | CI row | CI game | CI game+team | p row | p game | p game+team |
|---------|-------------|--------|---------|--------------|--------|---------|--------------|-------|--------|-------------|
| none | 0.625 | 0.0068 | 0.0073 | 0.0068 | [0.611, 0.638] | [0.610, 0.639] | [0.611, 0.638] | 0 | 0 | 0 |
| caliper 0.10 | 0.408 | 0.0151 | 0.0154 | 0.0152 | [0.378, 0.438] | [0.378, 0.438] | [0.378, 0.438] | 0 | 0 | 0 |
| caliper 0.20 | 0.398 | 0.0103 | 0.0105 | 0.0103 | [0.377, 0.418] | [0.377, 0.418] | [0.377, 0.418] | 0 | 0 | 0 |
