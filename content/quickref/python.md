Everyday tools from the standard library, no `pip install` needed. Full docs: [docs.python.org/3/library](https://docs.python.org/3/library/).

### Files and paths

| Module | Common calls | Use it for |
|---|---|---|
| `pathlib` | `Path("a") / "b"`, `p.exists()`, `p.read_text(encoding="utf-8")`, `p.write_text(s)`, `p.glob("*.py")`, `p.mkdir(parents=True, exist_ok=True)` | Paths as objects. Prefer it over `os.path`. |
| `shutil` | `copy2(src, dst)`, `copytree(src, dst)`, `rmtree(p)`, `move(src, dst)`, `which("git")` | Copying, moving and deleting trees. |
| `tempfile` | `TemporaryDirectory()`, `NamedTemporaryFile()` | Scratch files that clean up after themselves. |
| `os` | `os.environ.get("KEY")`, `os.getcwd()`, `os.listdir(p)` | Environment variables and the working directory. |

### Data formats

| Module | Common calls | Use it for |
|---|---|---|
| `json` | `json.loads(s)`, `json.dumps(obj, indent=2)`, `json.load(f)`, `json.dump(obj, f)` | JSON text or files. |
| `csv` | `csv.reader(f)`, `csv.DictReader(f)`, `csv.writer(f)`, `csv.DictWriter(f, fieldnames)` | CSV files. Open with `newline=""`. |
| `sqlite3` | `connect("x.db")`, `con.execute(sql, params)`, `cur.fetchall()`, `con.commit()` | A small SQL database in one file. Always pass parameters, never format SQL strings. |
| `tomllib` | `tomllib.load(f)` (open with `"rb"`) | Reading TOML (Python 3.11+). |
| `pickle` | `dump`, `load` | Python-only object files. Never load data you don't trust. |

### Text

| Module | Common calls | Use it for |
|---|---|---|
| `re` | `re.search(p, s)`, `re.findall(p, s)`, `re.sub(p, repl, s)`, `re.compile(p)` | Pattern matching. Use raw strings: `r"\d+"`. |
| `string` | `Template`, `ascii_letters`, `digits` | Constants and simple templates. |
| `textwrap` | `wrap(s, 60)`, `dedent(s)`, `shorten(s, 40)` | Reflowing and tidying text. |
| `difflib` | `unified_diff(a, b)`, `get_close_matches(w, words)` | Comparing text, fuzzy matching. |

### Dates and time

| Module | Common calls | Use it for |
|---|---|---|
| `datetime` | `date.today()`, `datetime.now()`, `timedelta(days=7)`, `dt.strftime("%Y-%m-%d")`, `datetime.fromisoformat(s)` | Dates, times and differences. |
| `zoneinfo` | `ZoneInfo("America/New_York")` | Time zones: `datetime.now(ZoneInfo(...))`. |
| `time` | `time.time()`, `time.sleep(1)`, `time.perf_counter()` | Timestamps, pausing, timing code. |

### Data structures and iteration

| Module | Common calls | Use it for |
|---|---|---|
| `collections` | `Counter(xs).most_common(3)`, `defaultdict(list)`, `deque(maxlen=n)`, `namedtuple` | Counting, grouping, queues. |
| `itertools` | `chain`, `groupby`, `islice`, `product`, `permutations`, `combinations`, `batched` (3.12+) | Looping tools. `groupby` needs sorted input. |
| `functools` | `lru_cache`, `partial`, `reduce`, `cache` | Memoizing and pre-filling arguments. |
| `dataclasses` | `@dataclass`, `field(default_factory=list)`, `asdict(obj)` | Classes that mostly hold data. |
| `heapq` / `bisect` | `heappush`, `heappop`, `nlargest` / `bisect_left`, `insort` | Priority queues, sorted lists. |
| `enum` | `Enum`, `auto()` | Named constants. |

### Math and randomness

| Module | Common calls | Use it for |
|---|---|---|
| `math` | `sqrt`, `ceil`, `floor`, `isclose(a, b)`, `pi`, `gcd` | Math functions. Use `isclose` for float comparison. |
| `statistics` | `mean`, `median`, `stdev`, `mode` | Quick stats on a list. |
| `decimal` / `fractions` | `Decimal("0.10")`, `Fraction(1, 3)` | Exact arithmetic, such as money. |
| `random` | `random()`, `randint(a, b)`, `choice(xs)`, `sample(xs, k)`, `shuffle(xs)` | Games and simulations. Not for security. |
| `secrets` | `token_hex(16)`, `choice(xs)` | Passwords and tokens. |

### Programs and the system

| Module | Common calls | Use it for |
|---|---|---|
| `argparse` | `ArgumentParser()`, `add_argument("--n", type=int, default=1)`, `parse_args()` | Command-line options and `--help`. |
| `subprocess` | `run(["git", "status"], capture_output=True, text=True, check=True)` | Running other programs. Pass a list, not a string. |
| `logging` | `basicConfig(level=logging.INFO)`, `logging.info(...)`, `getLogger(__name__)` | Output you can switch on and off. Better than `print`. |
| `sys` | `sys.argv`, `sys.exit(1)`, `sys.stdin` | Arguments and exit codes. |
| `platform` | `system()`, `python_version()` | Which OS and Python you're on. |

### Networking and concurrency

| Module | Common calls | Use it for |
|---|---|---|
| `urllib.request` | `urlopen(url, timeout=30)`, `Request(url, headers={...})` | Simple HTTP fetches. For anything bigger, most people use `requests`. |
| `urllib.parse` | `urlparse(u)`, `urlencode(d)`, `quote(s)` | Building and splitting URLs. |
| `http.server` | `python -m http.server -d site` | Serving a folder locally to test a static site. |
| `concurrent.futures` | `ThreadPoolExecutor`, `ProcessPoolExecutor`, `executor.map(f, xs)` | Running tasks in parallel. Threads for waiting (network), processes for number-crunching. |
| `asyncio` | `asyncio.run(main())`, `await asyncio.gather(...)` | Many tasks that mostly wait. |

### Testing and debugging

| Module | Common calls | Use it for |
|---|---|---|
| `unittest` | `TestCase`, `assertEqual`, `python -m unittest` | Built-in tests. `pytest` is a popular alternative. |
| `doctest` | `python -m doctest file.py` | Running examples written in docstrings. |
| `pdb` | `breakpoint()` | Stop and inspect at that line. |
| `timeit` | `python -m timeit "sum(range(100))"` | Timing small snippets. |
| `traceback` | `print_exc()` | Printing the current error with its stack. |

> Tip: `python -m pydoc json` prints a module's docs in the terminal, and `help(json.dumps)` works in the REPL.
