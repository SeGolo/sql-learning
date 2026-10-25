"""Build site/: data module per database + copy of PGlite runtime."""
import json, shutil, os, importlib

os.makedirs('site/pglite', exist_ok=True)
src = 'pgl/package/dist/'
for f in os.listdir(src):
    if f in ('index.js', 'postgres.wasm', 'postgres.data') or (f.startswith('chunk-') and f.endswith('.js')):
        shutil.copy(src + f, 'site/pglite/' + f)

SCHEMA_VELO = [
    ('customers', 'One row per registered customer.', [
        ('customer_id', 'INT', 'primary key'),
        ('first_name', 'VARCHAR', ''), ('last_name', 'VARCHAR', ''),
        ('email', 'VARCHAR', 'NULL when the customer gave no email'),
        ('city', 'VARCHAR', ''), ('country', 'CHAR(2)', 'CZ, SK, AT, DE, PL'),
        ('signup_date', 'DATE', ''),
        ('referred_by', 'INT', '→ customers.customer_id of the person who recommended them; NULL if nobody'),
        ('is_vip', 'BOOLEAN', '')]),
    ('categories', 'Two-level category tree.', [
        ('category_id', 'INT', 'primary key'), ('name', 'VARCHAR', ''),
        ('parent_id', 'INT', '→ categories.category_id; NULL = top level (Bikes, Components, Accessories, Apparel)')]),
    ('products', 'One row per product. Prices in CZK.', [
        ('product_id', 'INT', 'primary key'), ('name', 'VARCHAR', ''),
        ('category_id', 'INT', '→ categories (always a sub-category)'), ('brand', 'VARCHAR', ''),
        ('unit_price', 'NUMERIC(10,2)', 'current list price the customer pays'),
        ('cost_price', 'NUMERIC(10,2)', 'what the shop pays the supplier'),
        ('launched_date', 'DATE', ''), ('is_active', 'BOOLEAN', 'FALSE = discontinued')]),
    ('orders', 'One row per order, Jan 2023 – Dec 2024.', [
        ('order_id', 'INT', 'primary key'), ('customer_id', 'INT', '→ customers'),
        ('order_date', 'TIMESTAMP', 'date and time the order was placed'),
        ('status', 'VARCHAR', 'pending, shipped, delivered, cancelled, returned'),
        ('channel', 'VARCHAR', 'web, app, marketplace'),
        ('discount_code', 'VARCHAR', 'WELCOME10, SPRING15, BLACKFRIDAY20 or NULL'),
        ('shipped_date', 'DATE', 'NULL until shipped'), ('delivered_date', 'DATE', 'NULL until delivered')]),
    ('order_items', 'One row per product in an order. Primary key (order_id, product_id).', [
        ('order_id', 'INT', '→ orders'), ('product_id', 'INT', '→ products'),
        ('quantity', 'INT', 'units bought'),
        ('unit_price', 'NUMERIC(10,2)', 'price charged at the time; can differ from today\'s list price'),
        ('discount_pct', 'INT', '0, 10, 15 or 20 (from the discount code)')]),
    ('payments', 'Payment attempts. One order can have several rows.', [
        ('payment_id', 'INT', 'primary key'), ('order_id', 'INT', '→ orders'),
        ('payment_date', 'DATE', ''), ('amount', 'NUMERIC(10,2)', ''),
        ('method', 'VARCHAR', 'card, bank_transfer, paypal, cash_on_delivery'),
        ('status', 'VARCHAR', 'paid, failed, refunded')]),
    ('reviews', 'Product reviews.', [
        ('review_id', 'INT', 'primary key'), ('product_id', 'INT', '→ products'),
        ('customer_id', 'INT', '→ customers'), ('rating', 'INT', '1–5'),
        ('review_date', 'DATE', ''), ('comment', 'VARCHAR', 'NULL when no text was written')]),
]
NOTES_VELO = [
    'Line revenue = <code>quantity * unit_price * (100 - discount_pct) / 100.0</code> (from order_items).',
    'Order value = the sum of line revenue of that order.',
    '“Revenue” in a question counts delivered orders only, unless the question says otherwise.',
    'Data covers 1 Jan 2023 – 31 Dec 2024.',
]

def build(dbid, name, tagline, sql_file, qmod, schema, notes):
    mods = qmod if isinstance(qmod, (list, tuple)) else [qmod]
    for m in mods: importlib.import_module(m)
    Q = importlib.import_module(mods[0]).Q
    data = dict(id=dbid, name=name, tagline=tagline, sql=open(sql_file, encoding='utf-8').read(),
                schema=[dict(table=t, about=a, cols=[dict(c=c, t=ty, n=n) for c, ty, n in cols]) for t, a, cols in schema],
                notes=notes,
                questions=[dict(t=q['t'], d=q['d'], g=q['g'], p=q['p'], h=q['h'], s=q['s'], o=q['o'], k=q.get('k', 'sql'), a=q.get('a', '')) for q in Q])
    with open(f'site/{dbid}.js', 'w', encoding='utf-8') as f:
        f.write('export default ' + json.dumps(data, ensure_ascii=False) + ';\n')
    print(dbid, len(Q), 'questions', os.path.getsize(f'site/{dbid}.js'), 'bytes')

build('velo', 'Velo e-shop', 'Czech bike & outdoor e-shop: customers, orders, payments, reviews',
      'db1.sql', ['questions_db1', 'traps_db1'], SCHEMA_VELO, NOTES_VELO)

# ---------- DB2: schema read from a real Postgres load ----------
import pgserver, psycopg
srv = pgserver.get_server('pgdata', cleanup_mode='stop')
conn = psycopg.connect(srv.get_uri(), autocommit=True)
conn.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
conn.execute(open('db2.sql', encoding='utf-8').read())
TYPES = {'integer': 'INT', 'character varying': 'VARCHAR', 'numeric': 'NUMERIC', 'timestamp without time zone': 'TIMESTAMP', 'date': 'DATE'}
order = ['events', 'trades', 'users', 'viewership', 'total_trans', 'user_transactions', 'tweets', 'purchases', 'job_listings',
         'transactions', 'product', 'product_spend', 'user_topics', 'topic_rankings', 'user_actions', 'sessions', 'activities',
         'age_breakdown', 'reviews', 'measurements', 'signups', 'user_purchases', 'user_logins']
SCHEMA_ACE = []
for t in order:
    cols = conn.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position", (t,)).fetchall()
    SCHEMA_ACE.append((t, '', [(c, TYPES.get(ty, ty), '') for c, ty in cols]))
NOTES_ACE = [
    'Tables follow <i>Ace the Data Science Interview</i>, chapter 8. One table per interview scenario; user_ids are not shared between scenarios.',
    'Money columns are NUMERIC (the book says float).',
    "Questions 8.x come from the book. Several of the book's own solutions are wrong; those questions are traps.",
]
build('ace', 'Ace the DS Interview', 'Book chapter 8 tables: events, trades, tweets, sessions, transactions and more',
      'db2.sql', ['questions_db2', 'extra_db2'], SCHEMA_ACE, NOTES_ACE)
