# SQL Gym sources

Build and verification scripts for the SQL Gym page (`../index.html`).

- `gen_db1.py` / `gen_db2.py` / `gen_db3.py`: generate the Velo, Ace and Pulse databases (`db1.sql`, `db2.sql`, `db3.sql`).
- `questions_db1.py`, `traps_db1.py`, `questions_db2.py`, `extra_db2.py`, `questions_db3.py`, `traps_db3.py`: questions, hints, solutions, and the naive query each trap must catch.
- `verify.py`: runs every solution on real PostgreSQL (`pip install pgserver psycopg[binary]`) and checks every trap.
  Example: `python verify.py db2.sql questions_db2 extra_db2`, `python verify.py db3.sql questions_db3 traps_db3`
- `build.py`: writes `velo.js`, `pulse.js` and `ace.js` into `site/` (expects PGlite 0.2.17 unpacked in `pgl/`). `python build.py pulse` builds one database only.
- `page.html`: the page body as published to claude.ai; `../index.html` is the same wrapped in `<html>`/`<head>`.
- `cz_grammar.py`, `cz_vocab.py`: Czech practice (A1 grammar lessons + drills, work vocabulary). `velo_cz.py`: Czech text of the Velo tasks (CZ hover icon).
- `mindset.py`: Mindset reading (Khomiak, sins and virtues, EN / UK / CZ) and the Czech reading card (Czech text, English in the right panel).
  `mindset_scenarios.py`: 50 real-life scenarios as a multiple-choice exam (English in Mindset, Czech in Čeština · čtení).
  `python build_cz.py` writes `../czgram.js`, `../czvocab.js`, `../czread.js`, `../mindset.js` and adds the Czech text to `../velo.js` (a full `build.py` run adds it too).

Progress moves between laptops with the Progress button (export code, then import and merge).
