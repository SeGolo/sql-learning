"""Run every solution against real PostgreSQL. Report errors, empty results, row counts;
for trap questions (field n) check the naive query gives a DIFFERENT result."""
import sys, importlib
from decimal import Decimal
import pgserver, psycopg

db_sql, mods = sys.argv[1], [m for m in sys.argv[2:] if not m.startswith('-')]
for m in mods:
    importlib.import_module(m)
Q = importlib.import_module(mods[0]).Q
srv = pgserver.get_server('pgdata', cleanup_mode='stop')
conn = psycopg.connect(srv.get_uri(), autocommit=True)
conn.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
conn.execute(open(db_sql, encoding='utf-8').read())

def norm(rows):
    out = []
    for r in rows:
        out.append(tuple('NULL' if v is None else (f'{float(v):.2f}' if isinstance(v, (int, float, Decimal)) and not isinstance(v, bool) else str(v)) for v in r))
    return sorted(out)

print('questions:', len(Q))
bad = 0
for i, q in enumerate(Q, 1):
    if q.get('k') == 'theory':
        print(f'#{i:3} theory  {q["t"]}'); continue
    try:
        cur = conn.execute(q['s'])
        rows = cur.fetchall()
    except Exception as e:
        print(f'#{i} ERROR {q["t"]}: {e}'); bad += 1; continue
    flag = ''
    if not rows or all(all(v is None for v in r) for r in rows):
        flag = ' EMPTY'; bad += 1
    if q.get('n'):
        try:
            nrows = conn.execute(q['n']).fetchall()
            if norm(nrows) == norm(rows):
                flag += ' TRAP-NOT-TRIGGERED'; bad += 1
            else:
                flag += f' | trap ok: naive {nrows[:2]}{"..." if len(nrows) > 2 else ""} vs right {rows[:2]}{"..." if len(rows) > 2 else ""}'
        except Exception as e:
            flag += f' | trap ok: naive errors ({str(e).splitlines()[0][:60]})'
    if '-v' in sys.argv or q.get('n') or flag:
        print(f'#{i:3} [{q["d"][0]}] {"ORD" if q["o"] else "   "} rows={len(rows):4} {q["t"]}{flag}')
print('problems:', bad)
