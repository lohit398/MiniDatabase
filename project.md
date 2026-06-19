# MiniDatabase

A mini relational database from scratch, in Python, with an LLM-assisted query planner.

Educational project to learn database internals through implementation. Inspired architecturally by SQLite and DuckDB; tiny in scope.

> **START HERE — every session.** This file is the contract and the single source of truth. Read it in full before doing any work or giving any assessment. Do NOT substitute `recap.md`, daily notes, or memory for it — those are convenience summaries that drift; this is the spec. If anything below conflicts with a summary, this wins. The goal driving every decision: **become the best software engineer I can be** — optimize feedback and process for that, not for comfort or for looking on-track.

## Stack

- Python 3.11+
- R1-distill-70b-fp8 for the LLM-augmented cost model
- Everything else hand-rolled — no SQL-parser libraries, no ORMs

## Scope

### v1 (weeks 1–6) — in-memory SQL engine

- Hand-rolled SQL parser: lexer + recursive descent + Pratt parsing for operator precedence
- Volcano-model executor: `Scan`, `Filter`, `Project` iterators
- Joins: nested-loop and hash join, with measured benchmarks
- Logical vs physical plan split
- Rule-based optimizer: predicate pushdown, projection pushdown
- **LLM cardinality estimator** (the showcase) — A/B against a histogram baseline
- Selinger 1979 DP join ordering

### v2 (weeks 7–12) — persistence + transactions

- B+ trees on disk; slotted pages; splits and merges
- Buffer pool with Clock/LRU eviction; pin/unpin protocol
- Write-ahead log + ARIES-lite crash recovery
- MVCC transactions with snapshot isolation
- Secondary indexes

## Weekly milestones

### Week 1 — SQL Parser

Done when: `tinydb parse "SELECT name, age FROM users WHERE age > 30 AND country = 'US'"` prints a clean AST. Tests pass. Daily commits.

| Day | Task |
|---|---|
| 1 | Repo scaffolding (`pyproject.toml`, `src/minidb/`, `tests/`, `notes/`). AST node types sketched on paper. CMU 15-445 Lecture 1. |
| 2 | Tokenizer: keywords, identifiers, string/int literals, operators, comma, parens. |
| 3 | Parser skeleton: `SELECT col, col FROM table`. |
| 4 | `WHERE` clause + Pratt parsing for operator precedence. |
| 5 | `*` all-columns, table aliases, error messages with source position. |
| 6 | 30+ parse tests; 90%+ coverage. |
| 7 | Saturday: `notes/weekly/week-01.md` write-up. |

### Week 2 — In-memory Volcano executor

Done when: `minidb run "SELECT name FROM users WHERE age > 30"` on a CSV returns matching rows.

Define `Operator` interface (`open` / `next` / `close`). Implement `SeqScan`, `Filter`, `Project`. Expression evaluator over WHERE-clause AST. CSV loader. End-to-end pipeline.

### Week 3 — Joins

Done when: `SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id WHERE o.total > 100` works. Hash join measurably faster than nested-loop on a 10K × 100K dataset.

`NestedLoopJoin` (baseline), `HashJoin` (build + probe), multi-table joins (left-deep, fixed order for now), benchmarks.

### Week 4 — Rule-based optimizer

Done when: A query with filters after joins gets rewritten to push them down. `EXPLAIN` visualizes the plan. Measurable speedup.

Separate logical plan (relational algebra) from physical plan (operator tree). Plan printer. Predicate pushdown rule. Projection pushdown rule. Benchmarks.

### Week 5 — LLM cardinality estimator (showcase)

Done when: Histogram cost model + LLM cost model both implemented and compared on 50+ queries. Estimation error plotted. LLM estimates drive join ordering for 3-table joins.

`CostModel` interface. `HistogramCostModel` baseline (per-column histograms, assumes independence). Ground-truth dataset (query → true cardinality). `LLMCostModel` — structured JSON output, retry-with-repair, response caching. A/B benchmark.

### Week 6 — Selinger DP + v1 polish

Done when: Selinger DP works for joins up to 10 tables. Benchmarks against exhaustive and naive. v1 publicly shipped with README, demo, blog write-up.

Read Selinger et al. 1979 three times. Implement bottom-up DP over subsets of relations. Wire into optimizer. Polish: CLI, error messages, README, demo, blog post.

## Daily structure — 7:30 PM to 10:30 PM (transitioning to 4:30 AM + 8:00 PM in ~2 weeks)

| Block | Time | What |
|---|---|---|
| Deep build | 2h 15min | The week's algorithm + integration. Code, tests, commits. No browsing, no Slack, no email. |
| Read | 30 min | CMU 15-445 lecture, a chapter of *Database Internals*, or the relevant paper. Pen + notebook. |
| Daily log | 15 min | `notes/daily/YYYY-MM-DD.md` — what you did, what you got stuck on, tomorrow's first action. Commit it. |

Weekly: Saturday review → `notes/weekly/week-NN.md`. Sunday off.

Monthly: public artifact — blog post or polished README.

## Resources (locked in — no shopping for alternatives)

- **CMU 15-445** — Andy Pavlo's intro database course on YouTube. One lecture per week.
- ***Database Internals*** by Alex Petrov — the modern reference.
- **Selinger et al. (1979)** — "Access Path Selection in a Relational Database Management System." Read three times in Week 6.
- **BusTub** — CMU 15-445's reference project. Structural inspiration only; don't copy code.
- ***Designing Data-Intensive Applications*** by Kleppmann — big-picture context.

## Non-negotiables

1. 7+ hours sleep, every night
2. Exercise 4x/week, 30+ min each
3. One full rest day per week (Sunday)
4. No social media doomscroll — delete or block
5. Daily log every working day, no exceptions
6. Show up at the build slot. Every. Day.

## Calibration & risks

- This is the **hardest** of the three projects considered. Picked over the safer recommendation; eyes open.
- v1 is independently shippable. If v2 stalls, v1 stands alone as a real artifact.
- **Week 7–8 (B+ trees) is the explicit danger zone.** Most learners stall here. v1 first; don't skip ahead.
- Don't add features outside the plan. Backlog → `notes/backlog.md`.
- Cut corners ruthlessly early. Use `dict` where a B+ tree will go later. Add complexity only when forced.
- Each week's deliverable is *barely working* — not polished. Polish week is week 6.

## Contract

- Brutal coaching mode. Criticism welcome over comfort. Harsh = accurate and unflinching, never demeaning.
- No project switches without demonstrated failure of the current project.
- No option-shopping for alternatives — backlog new ideas, don't pivot.
- Daily log is non-negotiable.
- Stalls happen — silence after a stall is the failure mode, not the stall itself.
- "True friend" = tells you the truth when it's uncomfortable. Both ways.
- **I write the implementation code.** The coach explains, diagnoses, reviews, runs tests, and probes — never hands over MiniDatabase code. Same for CP: methodology only, never solutions.

### Definition-of-done discipline (added 2026-06-17, after two repeats of the same failure)

- **"Passes" ≠ "works."** A green suite proves nothing if no test exercises the new path. Every new feature: **probe it by hand first** (build the input, print the AST), confirm it, *then* trust green, *then* lock it with a test.
- **Tests must attack, not confirm.** Write the test that tries to prove the feature is broken — assert the *tree shape*, not a single leaf field — and write it *before* declaring done. A test shaped to pass what you already built is theater.
- **Coach verifies, doesn't take claims on faith.** "I did X" → the coach runs/probes it before agreeing. Reporting "it's done" when it isn't is the exact self-deception this project exists to kill.
- **No silent shipping of the easy half.** Doing the mechanical part (more `case` branches) and stopping before the part that teaches the concept (the recursion/loop/precedence) is not progress on the deliverable. Name it when it happens.

### Week-close discipline

- **Count weeks by their done-bar, not by elapsed "days."** A week is not done until its "Done when" line is literally true — including the CLI command, the test count, and the coverage number. Do not invent "day N+1" to avoid closing a week; renumbering the work to always look on-track is a way of hiding that the bar isn't met.
- **The week's done-bar is a checklist, not a vibe.** Before moving to the next week, the coach restates the "Done when" line and verifies each clause against the actual repo (run the command, count the tests, measure coverage). Below the bar on any clause = week not closed.
- No new-week or out-of-plan features start while the current week is below its bar. Ideas → `notes/backlog.md`.

### Anti-patterns observed (name these out loud when they recur)

- **Green-suite-can-lie** — suite passes while the headline feature is missing/broken because no test exercises it. (Hit twice: parser day-5 `parseOperand` non-consume; the AND combinator.)
- **Shipping the easy half** — mechanical branches done, the conceptual core skipped, then called done.
- **Day-renumbering drift** — redefining the schedule so there's always a "next day," hiding that the week's bar isn't met.
- **Tests that confirm instead of attack** — assertions shaped around what was built, blind to what wasn't.
- **Knowing ≠ doing** — the discipline is written in the daily log and skipped anyway. The skill is running it every time, especially when green tempts you to stop.

## Goal

Be unrecognizably better in one year. Repeat for ten. World-class is built by doing this ~3,650 times — not by declaring it once.
