# Full-graph trigger counts and unconstrained match

Trigger rule: H1 n≥5, H2 n≥5, H1 PPP − H2 PPP ≥ 0.25. Seasons 2022–23 through 2025–26, regular season and playoffs.

The unconstrained excess (+0.625) is the naive same-game match before first-half balancing. The paper's locked estimate is the H1-balanced excess (+0.408) in `rtm_h1_matched_results.md`.

## Dataset

| Metric | Value |
|--------|-------|
| Classified possessions (6 play types) | 863,752 |
| Games | 5,234 |
| Suppression triggers | 11,064 |
| — Regular season (002*) | 10,418 |
| — Playoffs (004*) | 646 |

## Unconstrained matched control (triggered − opponent, same PT, same game)

| Cohort | Triggers | Matched pairs | Trig Δ (H1−H2) | Ctrl Δ | Excess |
|--------|----------|---------------|----------------|--------|--------|
| Full graph | 11,064 | 9,111 | 0.610 | -0.014 | 0.625 |
| Regular season only | 10,418 | 8,614 | 0.610 | -0.012 | 0.621 |
| Playoffs only | 646 | 497 | 0.624 | -0.056 | 0.680 |
