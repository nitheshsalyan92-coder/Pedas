# Member 4 - Conflict Detection and Risk Analysis

## Your responsibility
Use tracked movement data to identify possible pedestrian-vehicle conflicts and assign a cautious risk level.

## Step-by-step tasks
1. Study the tracking data format from Member 3 before writing the analysis code.
2. Separate pedestrians and vehicles using object_type.
3. Analyse changes in position over time to estimate movement direction and approximate speed when enough frames are available.
4. Identify possible conflicts using proximity together with movement direction and whether paths appear to converge. Do not rely on distance alone.
5. Where data quality allows, estimate time-to-conflict cautiously and document assumptions.
6. Create an explainable rule-based risk classification: LOW, MEDIUM, or HIGH.
7. Return counts, conflict records, risk level, and human-readable alerts.
8. Handle missing tracks, short clips, and insufficient data without crashing.
9. Test the rules on sample tracking data and explain false-positive/false-negative limitations.

## Expected deliverables
- Working risk-analysis module.
- One callable function such as analyse_tracks(tracks).
- Documented risk rules and assumptions.
- Structured result JSON matching the shared data contract.

## Suggested files
```text
ai/prediction.py
```

## Integration handoff
Agree with Member 3 on coordinates, timestamps, object IDs, and track format. Send Member 2 the exact function signature and result JSON. Explain the basis for every risk label.

## Before you finish
- Run your module and test it.
- Tell the team what files you created or changed.
- Share exact run commands and dependencies.
- Commit and push your work to your assigned Git branch.
