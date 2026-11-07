# Python cheat sheet

## Idioms worth knowing

| Instead of | Write | Why |
|---|---|---|
| `for i in range(len(xs)): xs[i]` | `for x in xs:` | Iterate over items, not indexes. |
| `i = 0; for x in xs: ... i += 1` | `for i, x in enumerate(xs):` | `enumerate` hands you the index. |
| `for a, b in zip(xs, ys):` with manual indexing | `zip(xs, ys)` | Walks two sequences in step; stops at the shorter. |
| a loop that builds a list | `[f(x) for x in xs if cond]` | A comprehension is shorter and usually faster. |
| `if x == True` / `if len(xs) == 0` | `if x:` / `if not xs:` | Empty containers and `0`/`None` are falsy. |
| `"a" + str(n) + "b"` | `f"a{n}b"` | f-strings; `f"{x:.2f}"` formats to 2 decimals. |
| opening a file and calling `close()` | `with open(p) as f:` | The file closes even if an error occurs. |
| `dict.has_key` / checking then setting | `d.get(k, default)`, `collections.defaultdict`, `Counter` | Fewer branches. |
| `os.path.join(...)` | `pathlib.Path("a") / "b"` | Paths as objects. |

## The mutable-default trap

```python
def add(item, bucket=[]):      # WRONG: one list is shared by every call
    bucket.append(item); return bucket

def add(item, bucket=None):    # RIGHT
    bucket = [] if bucket is None else bucket
    bucket.append(item); return bucket
```

The default is evaluated once, when the function is defined, so every call without `bucket` mutates the same list.

## Comparing things

- `==` compares values. `is` compares identity; use it for `None` only (`if x is None`).
- Copying a list: `b = a` makes a second name for the same list; use `a.copy()` or `a[:]` (shallow) or `copy.deepcopy(a)` for nested data.

## Handy standard-library modules

`collections` (Counter, defaultdict, deque), `itertools`, `functools`, `pathlib`, `json`, `csv`, `datetime`, `argparse`, `statistics`, `sqlite3`, `dataclasses`.

## Environments

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip freeze > requirements.txt
```

Use one virtual environment per project so package versions don't collide.
