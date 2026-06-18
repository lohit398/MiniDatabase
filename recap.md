# MiniDatabase — Session Handoff (2026-06-17)

> **`project.md` is the contract and source of truth — read it FIRST and in full.** This recap is a convenience summary that drifts; if it conflicts with `project.md`, the contract wins. Do not let this file stand in for it.

Paste this at the start of a new session to keep context. Project: **MiniDatabase** (package `tinydb`) — an educational mini relational database in Python. Owner: **Lohit**.

---

## 0. How to coach me (READ FIRST — non-negotiable)

He explicitly asked for **brutal coaching, not cheerleading**.

- **Do NOT hand over MiniDatabase implementation code.** Explain, diagnose, review, run tests, write grammar specs, probe — but *he* writes the parser/AST code. (memory: `feedback-dont-hand-over-code`)
- **Do NOT solve CP problems.** CP is his problem-solving rep — discuss methodology only. (memory: `project-cp-difficulty-calibration`)
- **Reject vague commitments** — force specific times. "evening" / "extra hours later" = red flag.
- **Trust him on health non-negotiables** (sleep, gym). Don't re-police. (memory: `feedback-silent-on-health-accountability`)
- **When a path/file isn't given, ask once — don't grep across home dir.** (memory: `feedback-ask-dont-search-filesystem`)
- **His main growth edge: committing and starting vs option-shopping.** Don't talk him out of starting once committed. (memory: `feedback-commit-dont-shop`)
- **Daily log is non-negotiable** for continuity (`notes/daily/YYYY-MM-DD.md`).
- Recurring patterns to name when they recur: deliverable sliding to last in the queue, jumping the gun (pre-designing future days while shipping today), vague time commitments, CP time-box violations.

Governing memories: `user-growth-plan` (daily 3hr at 5:30–8:00 AM; goal "unrecognizably better year over year for 10 years"), `project-tinydb`.

---

## 1. Project at a glance

- **Stack:** Python 3.11+. Educational, general-SWE leveling (not MuleSoft-related).
- **v1 (weeks 1–6):** in-memory SQL engine — parser, Volcano executor, joins, rule-based optimizer, LLM cardinality estimator, Selinger join ordering.
- **v2 (weeks 7–12):** B+ trees on disk, buffer pool, WAL, MVCC, secondary indexes.
- **Project root (this machine, Linux):** `/home/lohit/Desktop/MiniDatabase/`
- **Schedule:** 5:30 AM wake, ~5:30–8:00 AM deep-work block. Thursday = rest day. Non-negotiables: 7+ hrs sleep, exercise 4x/week, one full rest day, daily log.

---

## 2. Where the code stands

**Parser day 5 SHIPPED + committed.** `parse("SELECT * FROM users WHERE x = 5")` →
`BinaryExpr(opr='=', left=Identifier(name='x', line=1, col=27), right=Literal(value=5, ...))`. **11/11 tests green.**
Commits: `8acc5f6` (feat: WHERE clause), `3eabce2` (fix: consume in operands + return real nodes).

### `src/tinydb/ast.py` — current nodes
- `Expr` (empty base, `pass`)
- `Column(token: Token)` — wraps a raw Token (discriminator via `token.type`)
- `Table(name, line, col, alias)`
- `SelectStmt(columns, table, line, col, where: Optional[Expr])` — **`where` has NO `= None` default currently**; works because `parseSelectStmt` always passes it. (Earlier red bug was the missing default — now sidestepped by always passing.)
- `BinaryExpr(Expr)(opr: str, left: Expr, right: Expr)` — operator is a plain `str`, NOT a node (dropped the `Operator` class idea — right call)
- `Identifier(Expr)(name, line, col)`
- `Literal(Expr)(value: str|int|float, line, col)` — carries typed value (`5` the int, not `"5"`)

### `src/tinydb/Parser.py` — current methods
- Helpers `peek / advance / match / consume` (consume raises `ParseError` with line+col).
- `parseColumnList` — `a, b, c` via while-COMMA loop. `matchColumn` — STAR vs IDENTIFIER choice.
- `where_clause` — peeks: EOF → consume + return None; KW_WHERE → consume + `parse_where_clause()`.
- `parseOperand` — IDENTIFIER → `Identifier`; STRING/NUMBER → `Literal`. **Consumes correctly now** (the day-5 bug was that it peeked but never advanced).
- `parse_where_clause` — three steps: `left = parseOperand()`, `consume(EQ)`, `right = parseOperand()`, returns `BinaryExpr("=", left, right)`. **Only handles `=` right now.**
- `parseSelectStmt` wires `where = self.where_clause()` into `SelectStmt`.
- `parse()` — top-level, only handles KW_SELECT (returns None otherwise — backlog PARSER-6).

### Tokenizer (`src/tinydb/Tokenizer.py`) — stable, 5/5 green
`Token(type, lexeme, literal, line, column)`. Case-preserving lexeme. `dotCount` int/float split. Cursor primitives. `KEYWORDS` map in `TokenType.py`.

### Tests (`tests/`)
- `test_tokenizer.py` — 5 tests. `test_parser.py` — 6 tests incl. `test_parser_star_where` and `test_parser_star_where_rev` (reversed operand order `5 = x`). **11/11 total green.**
- Run via `.venv/bin/python -m pytest -v`.

---

## 3. The two lessons locked this week (don't re-teach)

1. **The grammar IS the code.** In hand-written recursive descent there is no grammar object the program reads — *each grammar rule becomes one method, rule order becomes statement order, the cursor carries position.* A comparison is three sequential steps, not a token-scanning loop. (The `while`/`arr` scan he first tried was the stack/postfix mindset leaking back — killed it.) Precedence/nesting = a fixed ladder of one-method-per-precedence-level, each calling the next-tighter level.
2. **A green suite can lie.** Suite passed 9/9 while the WHERE feature was fully broken — no test exercised the new path. Reflex now: **new feature → probe by hand → then trust green → then lock with a test.**

---

## 4. Day 6 plan (today — full detail in `notes/daily/2026-06-17.md`)

**Parser day 6 — boolean combinators (AND/OR) + the six comparison operators.** Grammar to transcribe (one method per rule):
```
expression  → comparison ( ("AND" | "OR") comparison )*
comparison  → operand ( ("=" | "!=" | "<" | ">" | "<=" | ">=") operand )?
operand     → IDENTIFIER | NUMBER | STRING
```
Target: `WHERE x = 5 AND y > 3` → `BinaryExpr('AND', BinaryExpr('=', x, 5), BinaryExpr('>', y, 3))` — AND at root (binds looser, sits higher in the tree).
- `parseExpression` = `parseComparison` + `while match(AND|OR)` loop (the `( ... )*` → while, same as column list).
- `parseComparison` = today's `parse_where_clause` generalized to accept any of the 6 ops, not just `=`.
- `parseWhere` returns `parseExpression()`.
- **First confirm the tokenizer emits `< > != <= >=`** — quick probe. If not, that's a TOKENIZER sub-task; log it.
- **Done-bar:** old `WHERE x = 5` still green (no regression); `AND`/`OR` cases green; **probe by hand before trusting green.**
- **NOT today (scope discipline):** arithmetic (`+ - * /`), parens `(x*y)`, `NOT` unary, JOIN parsing. Time box 90 min — if not green in 90, stop and log where it stalled, don't grind into arithmetic.

---

## 5. CP status

- Running a **1200–1300 calibration trial**. **Thursday June 18 = the 5-day reassessment** call:
  - solve-rate <50% → drop to 1100–1200; 50–70% → stay; >70% → climb to 1300–1400.
- **`notes/cp/` directory STILL does not exist** — must be created to hold the dataset (date, rating, solved Y/N, time taken). Thursday's call should be mechanical from this data, not vibes.
- Last problem in progress: Codeforces 2223/A (1300).
- **Methodology agreed** (after he pushed back that tag-based practice spoils recognition — a correct insight):
  - Two skills: (1) *technique acquisition* — tags OK when learning a technique you don't own; (2) *technique selection/recognition* — practice blind, tags hidden, virtual contests.
  - Key drill: **classify the problem cold and commit to a guess BEFORE revealing the tag** — tag is feedback, not a hint.
  - **The growth is in the problems that beat you, not the ones you solve.** Easy solves = fine warm-up/volume but plateau. For every loss: editorial it, name the technique, re-implement clean, log it. Don't churn pure volume. Solving in <~5 min = below training zone.
  - His accepted stance: go find 1300s, keep solving, move on from easy ones — with the guardrail that failures are the main event.

---

## 6. Open items / backlog hygiene (~5 min)

In `notes/backlog.md`:
- [ ] Mark **PARSER-2** done (where clause shipped).
- [ ] Add **PARSER-8**: two AST styles coexist — `Column` wraps a raw `Token`; `Identifier`/`Literal` unwrap into typed fields. Pick ONE before the week-2 semantic analyzer walks the tree.
- [ ] Create **`notes/cp/`** and log CP attempts.
- [ ] If tokenizer is missing any comparison operators (from day 6 probe) → log a TOKENIZER item.

Pre-existing deferred backlog (none block current work): PARSER-1 (rename `table`→`from_clause`, bites JOINs), PARSER-3 (no module-level `parse(query)`), PARSER-4 (`Token.column` vs `SelectStmt.col` naming), PARSER-5 (match/consume can return None past end → AttributeError), PARSER-6 (`parse()` silent None for non-SELECT), PARSER-7 (dead lines). TOKENIZER-1..6 (column-position inconsistency, keyword literal, repr, EOF lexeme, reset duplication, vestigial for-i) — revisit before parser error reporting (day 7).

---

## 7. Parked decisions (revisit when rested — NOT killed)

Two convictions floated at 11:30 PM sleepy ~June 10:
1. Restructure schedule to **alternating 3-hour blocks** (one day data structures/project, next day the other).
2. **"CP is the most important thing for being a great SWE."**
Parked for a rested-brain weekend decision. If still believed when rested, argue them out with evidence.

---

## 8. Environment

- Linux machine; `python3-venv` installed, `.venv` rebuilt, `pip install -e . pytest` done.
- **pytest ONLY works from the venv** (that's where `tinydb` is installed editable). Use `.venv/bin/python -m pytest` OR `source .venv/bin/activate` then `pytest`. Bare `pytest` / system `python3 -m pytest` fail with `ModuleNotFoundError: tinydb`.
- Untracked daily notes: `notes/daily/2026-06-16.md` (day-5 retrospective), `notes/daily/2026-06-17.md` (day-6 forward plan).

---

## 9. Files to load for a fresh session (in order)

1. `MiniDatabase/project.md` — **the contract / source of truth (read first, in full)**
2. `MEMORY.md` (Claude memory dir) — auto-loaded
3. `MiniDatabase/recap.md` — this file
3. `MiniDatabase/notes/daily/2026-06-17.md` — today's plan
4. `MiniDatabase/notes/daily/2026-06-16.md` — yesterday's retrospective
5. `MiniDatabase/notes/backlog.md` — outstanding items
6. `MiniDatabase/src/tinydb/Parser.py` and `src/tinydb/ast.py` — current state
7. `MiniDatabase/tests/test_parser.py` — what's tested
8. Run `.venv/bin/python -m pytest -v` to verify the 11/11 green baseline

Kick-off line: **"Status: ready to start parser day 6"** (or wherever you actually are).
