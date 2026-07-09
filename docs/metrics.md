# Reading the metrics

The measurement layer joins each prediction to the realized price move for its event and reports
whether the predictions carry information — and whether they beat simple baselines. Generate a
report with:

```bash
make report
```

This writes `report.json` (all metrics) and `report_frame.csv` (the per-event joined rows, for
external plotting) for the configured pair.

## The analytical frame

Every metric is computed over the same frame: predictions inner-joined to outcomes on `event_id`
for one pair. Only measurable events survive — an event with a prediction but no realized outcome
(or vice versa) is dropped, and a horizon whose price bar is missing stays `null` rather than being
treated as a zero move.

## Accuracy and its confidence interval

Directional accuracy is the share of predictions whose `direction` matches the realized direction
(events with no realized direction are dropped from the denominator). On its own a hit rate is
misleading on few events, so it comes with a **Wilson score interval**: a 70% hit rate over 10
events spans roughly `[0.40, 0.89]`. Read the interval, not just the point — if it straddles 0.5,
the sample cannot yet distinguish the system from a coin flip.

## Information Coefficient (IC)

The IC is the **Spearman rank correlation** between the signed prediction `score` and the realized
return over a horizon. It asks a stronger question than accuracy: not just "was the direction
right" but "did a more confident, more strongly-signed call line up with a larger move".

- **IC ≈ +1** — perfect monotonic agreement: higher score, higher return. The signal is
  informative.
- **IC ≈ 0** — the score's ranking is unrelated to the move. No information.
- **IC < 0** — the score ranks moves the wrong way round (a contrarian signal).

Because it is rank-based, the IC is robust to outliers and to the score's scale.

## Calibration and the Brier score

Confidence should mean what it says: across all calls made with confidence 0.7, about 70% should be
correct. Calibration buckets predictions by confidence and, for each bucket, compares the mean
confidence to the observed accuracy — that pairing is the reliability curve. A well-calibrated
system sits on the diagonal.

The **Brier score** summarizes this as the mean squared error between confidence and the
correctness indicator (0 or 1). Lower is better: a perfectly confident, always-correct system
scores 0. For a well-calibrated signal at confidence `p`, the Brier score tends toward `p(1-p)`
(e.g. 0.21 at `p = 0.7`), so compare the observed Brier against that expectation rather than
against 0.

## Event-study path

For each prediction bucket (by predicted direction), the event study averages the log-return path
around `t0` at a set of hour offsets, anchored to 0 at the event. It shows the *shape* of the move,
not just its sign — whether the "up" bucket drifts up over the hours after the statement, and how
quickly. A synthetic upward drift produces a rising mean path; a signal with no timing information
produces a flat one.

## Lift over baselines

A metric is only meaningful relative to a baseline. Lift is the system's accuracy minus a
baseline's accuracy on the **same events**:

- **Surprise-sign baseline** — predict direction from the sign of the numeric surprise alone
  (positive → up). Lift over this asks whether reading the *statement* adds anything beyond the
  headline number.
- **Coin-flip baseline** — a fixed 0.5 hit rate.

**Lift ≈ 0** means the system is no better than the baseline; positive lift is the whole point of
the project — evidence that the LLM's reading carries information the baseline does not.
