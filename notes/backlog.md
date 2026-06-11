# MiniDatabase — Backlog

Cross-day deferred work. Items added with reason and "when this bites" so priority is clear. Resolve as the trigger condition arrives; archive (or strike) once shipped.

---

## Open

### TOKENIZER-1 — Column position is END for keywords/identifiers, START for numbers/strings (inconsistent)

- **What:** `KW_SELECT`, `KW_FROM`, `IDENTIFIER` tokens report `col` as the position of the *last char* of the lexeme. `NUMBER`, `STRING`, and single-char operators correctly report `col` as the *start* of the lexeme.
- **Why it matters:** Inconsistent token positions across types. When the parser emits *"unexpected identifier `name` at line 1, col 11"*, the caret points past `name`, not at it.
- **Fix concept:** In `scan()`'s alphanumeric branch (~line 123), when `curr` is empty (first char of a new lexeme), snapshot `self.line, self.column` into `self.start_line, self.start_col`. `checkKeywordsAndIdentifiers` passes those snapshots into `Token(...)`. Same pattern `number()`/`string()` already use.
- **When this bites:** First parser error message that points at an identifier/keyword position. **Resolve before writing parser error reporting.**

### TOKENIZER-2 — KEYWORD/IDENTIFIER `literal` is lowercased form, not `None` (deviates from spec)

- **What:** `KW_SELECT.literal = 'select'`, `IDENTIFIER.literal = 'name'`. Per the lexeme/literal spec, `literal` should be `None` for these — the lowercased form is a *normalized* form, not a parsed value.
- **Why it matters:** Muddles the lexeme/literal mental model. `literal` was meant for "parsed value" (int for NUMBER, unquoted contents for STRING). Stuffing the normalized form there creates a third concept living in the literal slot, depending on token type.
- **Fix options:** (a) add a separate `normalized` field on Token, (b) compute `tok.lexeme.lower()` on demand and set `literal=None`, (c) keep as-is and document the deviation.
- **When this bites:** Parser starts doing case-insensitive comparisons against keywords/identifiers and reads `tok.literal` thinking it's a parsed value.

### TOKENIZER-3 — `__repr__` doesn't show `literal`

- **What:** `Token.__repr__` shows `type + lexeme + position`, but not `literal`. The field is set but invisible when printing.
- **Why it matters:** Print-debugging is harder; have to remember to access `tok.literal` explicitly.
- **Fix concept:** Append `literal={self.literal!r}` to the f-string in `__repr__`.
- **When this bites:** First time you `print(token_list)` to debug parser work and can't see literal values.

### TOKENIZER-4 — `EOF` lexeme is the string `"EOF"` (cosmetic)

- **What:** `EOF` token has `lexeme="EOF"`. Conventionally an EOF sentinel has `lexeme=""` (empty) or `lexeme=None` — it represents end-of-input and has no source text.
- **Why it matters:** Cosmetic. Slight confusion for anyone reading output.
- **When this bites:** Probably never. Nice-to-have.

### TOKENIZER-5 — `cc` / `curr` reset duplication

- **What:** `cc = ""; curr = ""` appears in 4 places in `scan()` (lines 116–117, 125–126, 131–132, 138–139).
- **Why it matters:** DRY. If a third accumulator or different reset logic is added, 4 places to update.
- **Fix concept:** Tiny `_reset_accumulators()` helper.
- **When this bites:** Only if you add another accumulator or change reset behavior. Low.

### TOKENIZER-6 — For-i counter in `number()` and `string()` is vestigial

- **What:** Both handlers have `for i in range(self.index+1, len(self.input)+1)` alongside `self.advance()`/`self.peek()`. The `i` counter walks separately from `self.index` — happens to stay in sync, but the dual counter is brittle. `i` is mostly used as a "have we hit end of input?" check, which `self.peek() == "\0"` already answers.
- **Why it matters:** Two cursor sources in one function = drift risk if logic changes.
- **Fix concept:** Replace `for i in range(...)` with `while self.peek() != "\0"` loops in both handlers. Single cursor source through advance/peek.
- **When this bites:** Won't currently — but the next change to either handler that breaks the for-i / self.index sync gives a confusing bug.

### PARSER-1 — Rename `SelectStmt.table` → `from_clause`

- **What:** `SelectStmt` currently has a field named `table: Table`. Naming choice — works for single-table queries (`SELECT * FROM users`), but doesn't generalize when JOINs let multiple tables live in the FROM clause.
- **Why it matters:** Day 6 adds JOIN parsing, and the FROM clause will eventually hold either a `Table` or a `JoinClause`. Calling the field `from_clause` matches what it semantically *is*; calling it `table` lies the moment a join enters.
- **Fix concept:** Rename the field on `SelectStmt`. Update every reference (parser construction sites, tests, future AST consumers).
- **When this bites:** Day 6 (JOIN parsing). Cheap rename now; cheaper than later when more code depends on it.

### PARSER-2 — No `where_clause` field on `SelectStmt`

- **What:** `SelectStmt` has `columns`, `table`, and `line/col` — but no `where_clause` field. Fine for day 3 (`SELECT * FROM users` has no WHERE).
- **Why it matters:** Day 5 adds WHERE-clause parsing with expressions. The field will need to be added then.
- **Fix concept:** Add `where_clause: Optional[Expr] = None` to `SelectStmt` either now (future-proof) or when day 5 work begins. If added now, no constructor changes needed elsewhere because of the default.
- **When this bites:** Day 5 (WHERE-clause parsing).

### PARSER-3 — No module-level `parse(query: str)` orchestration function

- **What:** Tests and any future caller must instantiate `Tokenizer` + `Parser` manually and chain them. There's no top-level `parse(query: str) -> SelectStmt` function in `parser.py` that wires the two layers together.
- **Why it matters:** Convention. The user-facing API for a parser is normally a single function that takes source text and returns an AST. Without it, every caller (tests, future REPL, future CLI) duplicates the same Tokenizer-then-Parser setup.
- **Fix concept:** Add a module-level `parse(query: str) -> SelectStmt` in `parser.py` (OUTSIDE the `Parser` class) that creates a `Tokenizer`, sets `input`, calls `scan()`, then constructs `Parser(tokens)` and calls `parseSelectStmt()` (or the future top-level dispatcher).
- **When this bites:** Right now — every test repeats the wiring. Also the moment you build a REPL or CLI.

### PARSER-4 — Naming inconsistency: `Token.column` vs `SelectStmt.col` / `Table.col`

- **What:** `Token` uses the field name `column`. AST nodes (`SelectStmt`, `Table`, `Column`'s line/col when surfaced) use the shorter name `col`. Constructor calls like `SelectStmt(cols, tt, sst.line, sst.column)` work because of positional args, but the naming mismatch is jarring on the eye.
- **Why it matters:** Cognitive friction. When debugging, readers wonder if `col` and `column` refer to the same thing. They do, but the inconsistency invites mistakes (typing `node.column` and getting AttributeError, or `tok.col` and getting the same).
- **Fix concept:** Pick one — `column` everywhere (more readable, matches Python's `csv.DictReader` etc.) OR `col` everywhere (shorter). Rename one set of fields to match.
- **When this bites:** First real debugging session involving line/col fields, or when you introduce code that mixes Token and AST node attribute access.

### PARSER-5 — `match()` and `consume()` can silently return `None` past end of tokens, leading to AttributeError on error messages

- **What:** Both `match()` and `consume()` have early-return guards: `if(self.pos >= len(self.tokens)): return`. In `consume()`, if the cursor is past the end, the function silently returns `None` — but the caller expects either a Token or a raised `ParseError`. Worse, if you DO reach the error-raise line on a None peek, `t.type.name` raises AttributeError instead of giving a clean ParseError message.
- **Why it matters:** Two failure modes: (a) silent None return means caller gets None where Token expected → crash later; (b) malformed error messages when peek is at end-of-input. Either way, error reporting is brittle at the input boundary.
- **Fix concept:** Either (a) make `peek()` return a sentinel "EOF" Token (same pattern your tokenizer uses with `"\0"` for chars) so callers never see None, OR (b) have `consume()` raise a clean ParseError when called past end-of-input ("unexpected end of input, expected X"). Option (a) is more consistent with the tokenizer.
- **When this bites:** Any malformed input that ends mid-statement, e.g., `"SELECT *"` (no FROM).

### PARSER-6 — `parse()` silently returns `None` for non-SELECT first tokens

- **What:** `parse()` checks `if peek().type == KW_SELECT: return parseSelectStmt()`. If the first token is anything else (e.g., `KW_INSERT`, an identifier, garbage), `parse()` returns `None` silently.
- **Why it matters:** No error feedback for caller. Also doesn't extend naturally to dispatching across multiple statement kinds (INSERT, UPDATE, DELETE, etc.).
- **Fix concept:** Restructure `parse()` as a dispatcher with explicit branches per statement kind, and a final `else: raise ParseError(...)` for unrecognized first tokens. As statement parsers (parseInsert, parseUpdate) are added, they slot into the dispatch cleanly.
- **When this bites:** When INSERT/UPDATE/DELETE/DROP parsing enters (week 2). Also: any call to `parse()` with non-SELECT input today silently produces None — a hidden correctness bug.

### PARSER-7 — Commented-out dead line `#sst = SelectStmt()` in `parseSelectStmt`

- **What:** Line 46 (`#sst = SelectStmt()`) is leftover from the previous broken implementation. Already unused.
- **Why it matters:** Cleanup. Dead code is noise.
- **Fix concept:** Delete the line.
- **When this bites:** Never, but the next reader (you or someone else) wastes 5 seconds parsing whether it's significant.

---

## Resolved

*(none yet — track resolutions here as items get fixed)*
