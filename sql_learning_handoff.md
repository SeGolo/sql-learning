# SQL Learning Handoff — Serg
Paste this into a new Claude session (e.g. VS Code extension) to continue seamlessly.

## Who / context
- Learning SQL from scratch, practicing on StrataScratch.
- Background: Excel, VBA (work), university mathematics. Analogies to
  spreadsheets, algebra, and set theory land well.
- Prefers to WRITE queries himself and have them checked, with the *why*
  explained — not handed finished answers. Questions solutions critically
  (a strength — reward it).
- Goal: Junior Data Analyst role (Python + SQL, data-quality focus).

## SQL topics covered and understood
- SELECT / FROM / WHERE, comparison operators
- Boundary logic: > vs >=, "more than" vs "or more" (open vs closed interval)
- LIKE patterns (%, _), IN, BETWEEN
- NULL handling: IS NULL, three-valued logic, why <> drops NULLs,
  COALESCE, NULLIF (divide-by-zero guard)
- Case/space normalization: LOWER(), REPLACE()
- Type casting: CAST(x AS INTEGER/DECIMAL) — StrataScratch stores numbers
  (age, salary) as TEXT, so this bites constantly
- GROUP BY / HAVING; the WHERE (rows) vs HAVING (groups) distinction
- Conditional aggregation: SUM(CASE WHEN cond THEN 1 ELSE 0 END);
  knows COUNT(condition) is WRONG (boolean is never NULL)
- ORDER BY (multi-column), LIMIT, DISTINCT (whole-row)
- UNION / UNION ALL
- Joins: INNER, LEFT, RIGHT, FULL OUTER (+ MySQL emulation LEFT UNION RIGHT),
  CROSS JOIN, self-joins; foreign-key vs attribute joins;
  anti-joins (LEFT JOIN ... WHERE key IS NULL)
- LOGICAL EXECUTION ORDER: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY
  (the model that resolves most of his "why can't I..." questions)

## Recurring bug patterns he now watches for
- Text-stored numbers sort/compare as strings -> CAST
- Integer / integer truncates -> CAST(... AS DECIMAL) for ratios
- Match SELECT column list AND order to the expected output (grader checks columns)
- Attribute joins make duplicates -> DISTINCT
- Trailing comma before FROM = "syntax error near FROM"

## Not yet learned — the agreed next steps
1. Window functions: OVER (PARTITION BY ... ORDER BY ...),
   ROW_NUMBER / RANK / DENSE_RANK, LAG / LEAD  <-- START HERE for SQL
2. CTEs (WITH name AS (...)), subqueries
3. BIGGER CAREER GAP: Python + pandas (the target job weights Python over SQL)

## Good first tasks when resuming
- SQL: "Nth highest salary per department" (forces PARTITION BY + ranking)
- SQL: running total, LAG for previous-row comparison, top-N-per-group
- Python: start pandas as SQL-in-Python (WHERE -> df[...], GROUP BY ->
  df.groupby(), JOIN -> df.merge()); his VBA background transfers

## Teaching style that works
Explain the logic first -> let him attempt -> check against the EXACT task
wording -> connect to Excel / VBA / math. Keep the "why," not just the fix.
He gets (rightly) frustrated that StrataScratch gives tasks with no theory;
supply the missing theory as you go.

## His reference files (from the prior session)
- SQL Field Guide (HTML + PDF): clause | use | code example | common mistake
- SQL cheat-sheet (markdown, hand-editable)
- Junior Data Analyst learning plan (phased: finish SQL -> Python/pandas ->
  data-quality projects -> portfolio)
