# MiniDatabase — Grammar Rules (v1)

The formal grammar for MiniDatabase v1. Written in EBNF. The parser implements this spec; this file IS the spec.

If a query doesn't match these rules, the parser must raise `ParseError`. If a query matches but doesn't make semantic sense (e.g., references a column that doesn't exist), that's a semantic error caught later — not a grammar concern.

---

## Notation

Standard EBNF:

| Symbol | Meaning |
|---|---|
| `→` | "can be filled in with" / production rule |
| `\|` | alternation (choose one) |
| `( ... )` | grouping |
| `?` | optional (zero or one) |
| `*` | zero or more |
| `+` | one or more |
| `"text"` | literal terminal (keyword or operator from the source) |
| `IDENTIFIER`, `NUMBER`, `STRING` | terminal token types from the tokenizer |
| `// comment` | meta-comment, not part of the grammar |

SQL keywords are **case-insensitive** in the source; the tokenizer normalizes for lookup. They're shown in UPPERCASE here by convention.

---

## v1 grammar

### Top level

```
Statement      → SelectStmt
```

For v1, only `SELECT` statements are supported. INSERT, UPDATE, DELETE, DDL, etc. are out of scope (see "Not in v1" below).

### SELECT statement

```
SelectStmt     → "SELECT" ColumnList
                 "FROM" FromClause
                 ( "WHERE" Expr )?
```

A SELECT statement always has columns and a FROM clause. WHERE is optional.

### Columns

```
ColumnList     → "*"
               | Column ( "," Column )*

Column         → Expr ( "AS"? IDENTIFIER )?
```

- `SELECT *` — all columns wildcard (single token, no list).
- `SELECT a, b, c FROM ...` — one-or-more comma-separated columns.
- Each column is an **expression** (so `SELECT a + b * 2 AS total FROM ...` works), optionally aliased with `AS name` or just `name` (AS keyword optional).

### FROM clause

```
FromClause     → TableRef ( JoinClause )*

TableRef       → IDENTIFIER ( "AS"? IDENTIFIER )?

JoinClause     → JoinKind "JOIN" TableRef "ON" Expr

JoinKind       → "INNER"
               | "LEFT"
               | "RIGHT"
               | // implicit INNER if omitted
```

- Single table: `FROM users` or with alias `FROM users u` / `FROM users AS u`.
- Joins: `FROM users u INNER JOIN orders o ON u.id = o.user_id`.
- `JOIN` without a kind keyword defaults to `INNER JOIN`.
- Multiple joins chain: `FROM a JOIN b ON ... JOIN c ON ...`.

### Expressions

Operator precedence is encoded in the grammar — rules lower in this list bind tighter. Pratt parsing or precedence-climbing implements this directly.

```
Expr           → LogicalOr

LogicalOr      → LogicalAnd ( "OR" LogicalAnd )*

LogicalAnd     → LogicalNot ( "AND" LogicalNot )*

LogicalNot     → "NOT" LogicalNot
               | Comparison

Comparison     → Term ( ( "=" | "!=" | "<>" | "<" | "<=" | ">" | ">=" ) Term )?

Term           → Factor ( ( "+" | "-" | "||" ) Factor )*

Factor         → Unary ( ( "*" | "/" ) Unary )*

Unary          → "-" Unary
               | Primary

Primary        → NUMBER
               | STRING
               | "NULL"
               | "TRUE"
               | "FALSE"
               | QualifiedRef
               | "(" Expr ")"

QualifiedRef   → IDENTIFIER ( "." IDENTIFIER )?
```

**Precedence (low → high):** `OR < AND < NOT < comparison < +/-/|| < */ < unary minus < primary`.

**Notes:**
- `=` is equality (single `=`, not `==`).
- `!=` and `<>` are both valid not-equal.
- `||` is string concatenation.
- `Comparison` is non-associative — `a < b < c` is invalid (must be written `a < b AND b < c`).
- `QualifiedRef` handles `users.name` (table-qualified column reference).
- `Primary → "(" Expr ")"` is where the parser RECURSES into a fresh expression. This is the recursion that makes nested expressions work.

### Terminals (from tokenizer)

These are produced by the tokenizer; the parser consumes them:

- `IDENTIFIER` — alphanumeric identifier
- `NUMBER` — integer or float literal
- `STRING` — single-quoted string literal
- `EOF` — end of input sentinel
- Punctuation: `(`, `)`, `,`, `;`, `.`
- Operators: `+`, `-`, `*`, `/`, `||`, `=`, `!=`, `<>`, `<`, `<=`, `>`, `>=`
- Keywords: `SELECT`, `FROM`, `WHERE`, `AND`, `OR`, `NOT`, `AS`, `JOIN`, `ON`, `INNER`, `LEFT`, `RIGHT`, `NULL`, `TRUE`, `FALSE`, `IN`, `IS`

The tokenizer's `KEYWORDS` map enumerates these.

---

## Examples (valid in v1)

```sql
SELECT * FROM users
SELECT name FROM users
SELECT name, age FROM users
SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id
SELECT name AS full_name FROM users WHERE age > 30
SELECT a + b * 2 AS computed FROM t WHERE x > 5 AND (y < 10 OR z = 1)
SELECT * FROM t WHERE name = 'Lohit' AND age != 25
SELECT * FROM t1 LEFT JOIN t2 ON t1.id = t2.fk WHERE t2.active = TRUE
```

## Examples (NOT valid in v1 — will raise ParseError)

```sql
SELECT * FROM users GROUP BY name              -- GROUP BY not in v1
SELECT * FROM users ORDER BY name              -- ORDER BY not in v1
SELECT * FROM users LIMIT 10                   -- LIMIT not in v1
SELECT DISTINCT name FROM users                -- DISTINCT not in v1
SELECT COUNT(*) FROM users                     -- function calls not in v1
SELECT * FROM users WHERE id IN (1, 2, 3)      -- IN not in v1
SELECT * FROM (SELECT * FROM users) AS sub     -- subqueries not in v1
INSERT INTO users VALUES (...)                 -- INSERT not in v1
WITH t AS (...) SELECT * FROM t                -- CTEs not in v1
SELECT * FROM users UNION SELECT * FROM old    -- set operators not in v1
```

---

## Not in v1 (deferred to v2 or later)

These are intentionally excluded to keep v1 focused. Add them in v2 by extending the grammar (each becomes one or a few new rules + corresponding AST nodes + parser methods).

- **DML:** INSERT, UPDATE, DELETE
- **DDL:** CREATE TABLE, DROP, ALTER, TRUNCATE
- **Query features:** GROUP BY, HAVING, ORDER BY, LIMIT, OFFSET, DISTINCT
- **Function calls:** COUNT, SUM, AVG, MIN, MAX, COALESCE, CAST, etc.
- **Predicates:** IN, BETWEEN, LIKE, EXISTS, CASE/WHEN
- **Subqueries:** scalar subqueries, derived tables, correlated subqueries
- **Set operations:** UNION, INTERSECT, EXCEPT
- **CTEs:** `WITH ... AS (...)`
- **Window functions:** `OVER (PARTITION BY ...)`
- **Transactions:** BEGIN, COMMIT, ROLLBACK
- **Specific JOIN kinds:** FULL OUTER, CROSS, NATURAL, USING-syntax
- **Multiple statements:** semicolon-separated batches

When promoting items from v2 backlog into v1+: copy the relevant grammar rule into this file, update the "v1 grammar" section above, and **remove from the "Not in v1" list** so the spec stays authoritative.

---

## Mapping to parser implementation timeline

Each grammar rule maps to a parser method (recursive descent). Build order:

| Rule | Parser method | Build day |
|---|---|---|
| `Statement → SelectStmt` (dispatch) | `parse()` | Day 3 (top-level wired) |
| `SelectStmt → SELECT * FROM IDENTIFIER` (star case only) | `parseSelectStmt()` | **Day 3 — DONE** |
| `ColumnList → Column ( "," Column )*` | `parseColumnList()` + `parseColumn()` | **Day 4 (today)** |
| `WHERE Expr` (optional clause) + Expr machinery | `parseWhereClause()` + `parseExpr()` (Pratt) | Day 5 |
| `FromClause → TableRef ( JoinClause )*` | `parseFromClause()` extension | Day 6 |
| Error reporting + position tracking polish | (cross-cutting) | Day 7 / week 2 |

Tests should cover the **valid examples** above (one per pattern) and a handful of the **invalid examples** asserting `ParseError`.

---

## How to modify this spec

- **Within v1:** if a real bug or oversight is found in a rule, fix the rule here FIRST, then update the parser + tests to match. Spec leads code.
- **Promoting to v2:** when starting v2 work, copy this file to `grammar-rules-v2.md` and extend. Keep v1 frozen as a reference for what v1 was capable of.
- **Removing from v1:** if a planned feature gets cut, move the rule from the active grammar to "Not in v1" with a brief note (date + reason). Don't silently delete; the audit trail matters.
