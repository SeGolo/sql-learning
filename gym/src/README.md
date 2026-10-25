# SQL Gym sources

Build and verification scripts for the SQL Gym page (`../index.html`).

- `gen_db1.py` / `gen_db2.py`: generate the Velo and Ace databases (`db1.sql`, `db2.sql`).
- `questions_db1.py`, `traps_db1.py`, `questions_db2.py`, `extra_db2.py`: questions, hints, solutions, and the naive query each trap must catch.
- `verify.py`: runs every solution on real PostgreSQL (`pip install pgserver psycopg[binary]`) and checks every trap.
  Example: `python verify.py db2.sql questions_db2 extra_db2`
- `build.py`: writes `velo.js` and `ace.js` into `site/` (expects PGlite 0.2.17 unpacked in `pgl/`).
- `page.html`: the page body as published to claude.ai; `../index.html` is the same wrapped in `<html>`/`<head>`.

Progress moves between laptops with the Progress button (export code, then import and merge).
