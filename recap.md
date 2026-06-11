# MiniDatabase — Session Handoff (2026-06-10)

Paste this at the start of a new session to keep context. Updated as work progresses.

---

## 1. Project at a glance

Lohit is building **MiniDatabase** (a.k.a. `tinydb` — package name), a mini relational database from scratch in Python. Educational project to level up as a general software engineer (not MuleSoft-related).

- **Stack:** Python 3.11+, R1-distill-70b-fp8 for cost model later
- **v1 scope (weeks 1–6):** in-memory SQL engine — parser, Volcano executor, joins, rule-based optimizer, LLM cardinality estimator, Selinger join ordering
- **v2 scope (weeks 7–12):** B+ trees on disk, buffer pool, WAL, MVCC, secondary indexes
- **Project root:** `/Users/lohitbotta/Desktop/MiniDatabase/`

## 2. The coaching contract

He explicitly asked for **brutal coaching, not cheerleading**. Key terms:

- Name patterns when they recur (slip pattern, jumping the gun, vague commitments, CP time-box violations)
- Don't hand over implementation code — explain concepts, review code, run tests, but he writes the code
- Default to "no" on project switches without shipped failure
- Trust him on health non-negotiables (gym, sleep) — don't keep policing
- Specific time commitments only; reject vague ones (`"sure"` is not a commitment)
- Daily log is non-negotiable for continuity

Memory entries that govern coaching style:
- `user-growth-plan` — daily 3hr at 5:30-8:00 AM (migrated from 7:30 PM block on 2026-06-02), goal is *"unrecognizably better year over year for 10 years"*
- `feedback-commit-dont-shop` — his main growth edge is committing and starting vs option-shopping
- `feedback-dont-hand-over-code` — explain/diagnose/review on MiniDatabase, don't write implementation
- `feedback-silent-on-health-accountability` — don't re-ask same accountability question; trust by default
- `feedback-ask-dont-search-filesystem` — when path isn't given, ask once; don't grep across home dir
- `project-tinydb` — the MiniDatabase plan + scope
- `project-cp-difficulty-calibration` — 1200-1300 calibration trial for CP

## 3. Schedule and structure

- **Wake:** 5:30 AM (migrated from 7:30 PM evening block on 2026-06-02 — variant of original "4:30 AM" plan, working in practice)
- **Morning block:** ~5:30 AM to 8:00 AM (3 hours) — primary deep-work session
- **Rest day:** Thursday (confirmed June 4); Friday/Saturday/Sunday are "weekend productive days"
- **Weekday evening:** gym + CP (Monday onward, after work)
- **Non-negotiables:** 7+ hours sleep, exercise 4x/week (he's hit it), one full rest day, daily log

## 4. Where the code is

### Tokenizer (`src/tinydb/Tokenizer.py`)
- **5/5 tokenizer tests green** consistently
- Token data model fully refactored: `Token(type, lexeme, literal, line, column)`
- `cc` variable preserves original case in lexeme (case-preservation fix landed)
- `dotCount`-based int/float discrimination for NUMBER literal
- `advance() / peek()` cursor primitives; bounds-guarded
- Structured error collection via `self.errors`
- `__repr__` shows `Type:` label
- `KEYWORDS` map in `TokenType.py` covers v1 keywords

### Parser (`src/tinydb/Parser.py`)
- **9/9 tests green** (4 parser + 5 tokenizer)
- **Day 3 SHIPPED 2026-06-07** — `parse("SELECT * FROM users")` works (broke a 6-day slip pattern)
- **Day 4 SHIPPED 2026-06-09** — column lists, edge case errors
- `ParseError(Exception)` for syntax errors
- Helpers: `peek`, `advance`, `match`, `consume` (consume raises on mismatch with line+col)
- `parseSelectStmt()` — consumes KW_SELECT → calls `matchColumn` → consumes KW_FROM → consumes IDENTIFIER → consumes EOF → builds SelectStmt
- `matchColumn()` — Python `match` statement on token type, dispatches STAR / IDENTIFIER / default-raises
- `parseColumnList()` — comma-separated identifiers (helper for non-star branch)
- `parse()` — top-level dispatch, currently only handles KW_SELECT (returns None silently otherwise — PARSER-6)

### AST (`src/tinydb/ast.py`)
- **`Column`** — single class wrapping a Token (`token: Token`). Discriminator approach (he chose to feel the pain of this later vs split into Star/Identifier now).
- **`Table`** — `name: str, line: int, col: int, alias: str`
- **`SelectStmt`** — `columns: list[Column], table: Table, line: int, col: int`. No `where_clause` field yet (PARSER-2 in backlog — closes today on day 5).

### Tests (`tests/`)
- **`test_tokenizer.py`** — 5 tests covering star, no-space star, filters with strings/numbers, unterminated string error, mid-query string
- **`test_parser.py`** — 4 tests: star, column list (4 cols incl. capital `Username`), empty-column error, mixed-star-with-identifier error
- All run via `pytest` with editable install (`pip install -e .` in `.venv`)

## 5. Project structure

```
MiniDatabase/
├── project.md                     ← v1/v2 plan, weekly milestones
├── grammar-rules.md               ← v1 EBNF grammar spec (written 2026-06-08)
├── recap.md                       ← this file
├── pyproject.toml
├── src/tinydb/
│   ├── __init__.py
│   ├── Tokenizer.py
│   ├── TokenType.py               ← Token class + TokenType enum + KEYWORDS map
│   ├── Parser.py
│   └── ast.py
├── tests/
│   ├── test_tokenizer.py
│   └── test_parser.py
└── notes/
    ├── backlog.md                 ← persistent cross-day backlog (TOKENIZER-1..6 + PARSER-1..7)
    └── daily/
        ├── 2026-05-29.md          ← rest day
        ├── 2026-05-30.md
        ├── 2026-05-31.md
        ├── 2026-06-07.md          ← parser day 3 SHIPPED
        ├── 2026-06-08.md          ← tomorrow's-plan-from-night-before
        └── ...
```

Venv at `.venv/`. Run pytest as `.venv/bin/python -m pytest -v`.

## 6. Backlog (in `notes/backlog.md`)

**Tokenizer (deferred — revisit before parser error reporting on day 7):**
- **TOKENIZER-1** — column position is END for keywords/identifiers, START for numbers/strings (inconsistent — bites error messages)
- **TOKENIZER-2** — KEYWORD/IDENTIFIER literal is lowercased form, not None
- **TOKENIZER-3** — `__repr__` doesn't show `literal`
- **TOKENIZER-4** — EOF lexeme is `"EOF"` (cosmetic)
- **TOKENIZER-5** — cc/curr reset duplicated in 4 places
- **TOKENIZER-6** — vestigial `for-i` in number()/string() (cursor drift risk)

**Parser (deferred — none block current work):**
- **PARSER-1** — rename `SelectStmt.table` → `from_clause` (bites day 6 JOINs)
- **PARSER-2** — no `where_clause` field on SelectStmt (**closes today on day 5**)
- **PARSER-3** — no module-level `parse(query: str)` orchestration function
- **PARSER-4** — naming inconsistency `Token.column` vs `SelectStmt.col`
- **PARSER-5** — match/consume can silently return None past end of tokens → AttributeError in error message
- **PARSER-6** — `parse()` silently returns None for non-SELECT
- **PARSER-7** — commented-out dead lines (now also test file lines 40, 51)

## 7. Concepts internalized this session

These were genuinely learned through conversation — pointers for the next session not to re-explain:

- **EBNF → parser primitive mapping** (`X` → `consume`, `X | Y` → peek+branch, `X?` → `if match`, `X*` → `while match`)
- **Grammar as spec, not just dispatch** — grammars encode ORDER, REQUIRED/OPTIONAL, REPETITION, CHOICE rules; semantics is a separate layer
- **Why trees vs stacks/postfix** — for a database, the entire optimizer in weeks 5-6 is tree rewriting. Trees support analysis, transformation, optimization. Stacks/postfix solve one-shot evaluation only.
- **Lexeme vs literal** — lexeme is raw source text (case preserved); literal is parsed value (int/float/unquoted-string) or None
- **Local-capture pattern** for dataclass construction — capture `consume()` returns into locals, build dataclass at end with all fields passed at once
- **One method per grammar rule** — `parseSelectStmt`, `parseColumnList`, `parseColumn` (each rule = one Parser method)
- **CHOICE point inside the rule that owns it** — not at the caller (e.g., `*` vs identifier-list lives inside `parseColumnList`, not at `parse()`)
- **Code-then-formalize** — code first, read chapter after to formalize. Stronger learning than read-then-code.
- **Predictive parsing / LL(1)** — each rule identified by next 1-or-few tokens; recursive descent literally translates grammar rules to methods
- **Pratt parsing concept** (not yet implemented — day 5/6 work) — top-down operator precedence, one level per precedence

## 8. Active coaching patterns

These get named when they recur:

- **The parser slip pattern** — parser day 3 slipped 6 days (May 31 → June 6) before shipping. Day 4 nearly slipped to today before shipping yesterday. Watch for "parser last in the queue" — slips every time. Parser-first is the structural protection.
- **Vague commitments** — `"sure will stick to that"` without specific times = warning sign. Force specific times.
- **CP time-box violation** — June 2 had a 3-hour CP grind; June 8 had a multi-hour session. He acknowledges "I thought I was close" is sunk-cost rationalization. The 60-min hard box has held twice now (June 8 1300 solve, June 9 solve).
- **Jumping the gun** — pre-anticipating complexity (day 4-7 design questions while shipping day 3) is procrastination dressed as preparation. He self-diagnosed this on June 7.
- **CP confidence calibration** — solving 1/6 at 1500 was demoralizing; calibration trial at 1200-1300 with explicit 5-day Thursday reassessment. Started June 8.

## 9. CP calibration trial

- **Decided:** 2026-06-03 (1200-1300 range; 5-day trial; Thursday June 11 = reassessment)
- **Day 1 (2026-06-07):** solved one 1200 problem ✓
- **Day 2 (2026-06-08):** solved Codeforces 2230/C at 1300 inside the 60-min box ✓ — stronger signal than expected; might be 1400-ready
- **Day 3 (2026-06-09):** solved one problem yesterday (confirmed today) ✓
- **Day 4 (today, 2026-06-10):** queued for today
- **Day 5 (2026-06-11 / Thursday):** REASSESSMENT — solve rate <50% → drop to 1100-1200; 50-70% → stay; >70% → climb to 1300-1400

He should be tracking in `notes/cp/` — check whether this is actually being maintained.

## 10. Today (2026-06-10) — queue

1. **Parser day 5 — WHERE clause + minimum-viable expression** (FIRST)
   - **Goal:** `parse("SELECT * FROM users WHERE x = 5")` → `SelectStmt(..., where_clause=BinaryOp(=, Identifier("x"), Literal(5)))`
   - New AST nodes: `BinaryOp`, `Identifier`, `Literal`
   - `where_clause: Optional[Expr]` field on SelectStmt (closes PARSER-2)
   - `parseWhere()` — wraps `if match(KW_WHERE): expr = parseExpr()`
   - `parseExpr()` — start at the `Comparison` rule (Identifier OP Literal), don't try full Pratt today
   - Full Pratt (OR/AND/NOT/arithmetic layers) extends into **day 6**

2. **CP day 4 of calibration trial** — fresh 1200-1300 problem, 60-min HARD box

3. **Daily log** at end of session in `notes/daily/2026-06-10.md`

Time-box: morning block runs ~5:30–8:00 AM.

## 11. Future days (roughly)

- **Day 6** — full Pratt expression precedence (OR/AND/NOT/comparison/arithmetic) + JOIN parsing in FROM clause
- **Day 7** — parser error reporting + position tracking polish + **resolve TOKENIZER-1 through TOKENIZER-3** (the error-message-related items)
- **Week 2** — semantic analyzer (name resolution, type checking) + start executor (Volcano scan/filter/project)
- **Weeks 3+** — joins (nested-loop, hash), rule-based optimizer, LLM cardinality estimator, Selinger DP

Per project.md: B+ tree danger zone is weeks 7-8.

## 12. Key files to load for new session

If starting fresh, the next session should read in this order:

1. `MEMORY.md` (in user's Claude memory dir) — auto-loaded
2. `MiniDatabase/project.md` — project plan
3. `MiniDatabase/grammar-rules.md` — current grammar spec
4. `MiniDatabase/recap.md` — this file
5. `MiniDatabase/notes/backlog.md` — outstanding items
6. `MiniDatabase/notes/daily/<latest>.md` — yesterday's log
7. `MiniDatabase/src/tinydb/Parser.py` — current parser state
8. `MiniDatabase/src/tinydb/ast.py` — current AST nodes
9. `MiniDatabase/tests/test_parser.py` — what's tested
10. Run `.venv/bin/python -m pytest -v` to verify current green state

---

To kick off a new session after pasting: **"Status: ready to start parser day 5"** (or wherever you actually are).
