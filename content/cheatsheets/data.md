# Data analytics cheat sheet

## pandas essentials

```python
import pandas as pd
df = pd.read_csv("file.csv", parse_dates=["date"])

df.shape, df.dtypes, df.describe(), df.isna().sum()      # first look
df.query("age > 30 and city == 'Columbus'")              # filter
df.loc[df["score"] > 90, ["name", "score"]]              # rows + columns by label
df.assign(rate=lambda d: d["hits"] / d["tries"])         # new column without mutating
df.groupby("team", as_index=False).agg(avg=("score", "mean"), n=("score", "size"))
df.merge(other, on="id", how="left")                     # join
df.sort_values("score", ascending=False).head(10)
df["date"].dt.month                                      # date parts
```

- `loc` selects by label, `iloc` by position.
- Chained indexing like `df[df.a > 1]["b"] = 0` can silently fail to modify `df` (SettingWithCopy). Use `df.loc[df.a > 1, "b"] = 0`.
- Don't loop over rows with `iterrows` when a vectorized column operation exists.

## SQL: write order vs. run order

You write: `SELECT … FROM … JOIN … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT`.
The database runs: `FROM/JOIN` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`.

That's why you can't use a `SELECT` alias in `WHERE`, and why `WHERE` filters rows while `HAVING` filters groups.

| Join | Keeps |
|---|---|
| `INNER` | Only rows matching in both tables |
| `LEFT` | All rows from the left table, matches from the right (NULL if none) |
| `FULL OUTER` | All rows from both |

`COUNT(*)` counts rows; `COUNT(col)` skips NULLs. `NULL = NULL` is not true; use `IS NULL`.

## Stats quick reference

| Question | Reach for |
|---|---|
| Typical value, skewed data | median (the mean is pulled by outliers) |
| Spread | standard deviation, IQR |
| Two numeric variables move together? | correlation (Pearson for linear, Spearman for ranked) |
| Two groups differ? | t-test (roughly normal) or Mann-Whitney (not) |
| Two categories associated? | chi-squared test |

- A p-value is the probability of seeing a result at least this extreme if there were no real effect. It is not the probability that your hypothesis is true.
- Correlation doesn't show causation.
- Always plot before you summarize; very different datasets can share the same mean and correlation.
