"""Helper: start embedded Postgres, load a .sql file, run queries."""
import sys, pgserver, psycopg

def connect(sql_file):
    srv = pgserver.get_server('pgdata', cleanup_mode='stop')
    uri = srv.get_uri()
    conn = psycopg.connect(uri, autocommit=True)
    conn.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
    conn.execute(open(sql_file, encoding='utf-8').read())
    return srv, conn

if __name__ == '__main__':
    srv, conn = connect(sys.argv[1])
    for q in sys.argv[2:]:
        cur = conn.execute(q)
        print([d.name for d in cur.description])
        for r in cur.fetchall():
            print(r)
        print('---')
