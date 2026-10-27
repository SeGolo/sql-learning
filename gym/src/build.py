"""Build site/: data module per database + copy of PGlite runtime.
Usage: python build.py            (everything)
       python build.py pulse      (only the listed databases)"""
import json, shutil, os, sys, importlib

ONLY = sys.argv[1:]
os.makedirs('site/pglite', exist_ok=True)
src = 'pgl/package/dist/'
for f in (os.listdir(src) if os.path.isdir(src) else []):
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
    if ONLY and dbid not in ONLY: return
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

# ---------- DB3: Pulse fitness app (marketing + subscriptions + money) ----------
SCHEMA_PULSE = [
    ('channels', 'Where traffic comes from.', [
        ('channel_id', 'INT', 'primary key'), ('name', 'VARCHAR', ''),
        ('kind', 'VARCHAR', 'paid or organic')]),
    ('campaigns', 'Paid campaigns.', [
        ('campaign_id', 'INT', 'primary key'), ('channel_id', 'INT', '→ channels.channel_id'),
        ('name', 'VARCHAR', ''), ('start_date', 'DATE', 'planned first day'),
        ('end_date', 'DATE', 'planned last day; NULL = no end planned'),
        ('daily_budget_eur', 'NUMERIC(10,2)', '')]),
    ('ad_spend', 'One row per campaign per day, from the ad platforms. Missing day = paused.', [
        ('campaign_id', 'INT', '→ campaigns.campaign_id'), ('spend_date', 'DATE', ''),
        ('impressions', 'INT', ''), ('clicks', 'INT', ''), ('spend_eur', 'NUMERIC(10,2)', '')]),
    ('visits', 'Website sessions of visitors who accepted cookies (far fewer than ad clicks).', [
        ('visit_id', 'INT', 'primary key'), ('visitor_id', 'INT', 'one browser = one person'),
        ('visit_ts', 'TIMESTAMP', ''), ('channel_id', 'INT', '→ channels.channel_id'),
        ('campaign_id', 'INT', '→ campaigns.campaign_id; NULL for organic visits'),
        ('device', 'VARCHAR', 'mobile, desktop, tablet')]),
    ('users', 'Everyone who created an account.', [
        ('user_id', 'INT', 'primary key'), ('visitor_id', 'INT', '→ visits.visitor_id; NULL = installed from the app store'),
        ('signup_ts', 'TIMESTAMP', ''), ('country', 'VARCHAR', 'ISO code: CZ, SK, PL, DE, AT, GB'),
        ('platform', 'VARCHAR', 'web, ios, android'), ('is_test', 'BOOLEAN', 'staff test account')]),
    ('plans', 'What we sell. Prices are the EUR list price.', [
        ('plan_id', 'INT', 'primary key'), ('name', 'VARCHAR', ''),
        ('billing_period', 'VARCHAR', 'month or year'), ('price_eur', 'NUMERIC(10,2)', 'price per billing period'),
        ('is_active', 'BOOLEAN', 'FALSE = retired, no new sales')]),
    ('subscriptions', 'One row per subscription. A user can have several (plan switch, coming back).', [
        ('subscription_id', 'INT', 'primary key'), ('user_id', 'INT', '→ users.user_id'),
        ('plan_id', 'INT', '→ plans.plan_id'), ('started_at', 'DATE', ''),
        ('trial_end', 'DATE', 'first paid day after a 7-day trial; NULL = no trial'),
        ('ended_at', 'DATE', 'first day without access; NULL = not cancelled'),
        ('cancel_reason', 'VARCHAR', 'NULL when not given')]),
    ('invoices', "Charges, in the customer's currency.", [
        ('invoice_id', 'INT', 'primary key'), ('subscription_id', 'INT', '→ subscriptions.subscription_id'),
        ('invoice_date', 'DATE', ''), ('period_start', 'DATE', ''), ('period_end', 'DATE', 'last day covered'),
        ('currency', 'CHAR(3)', 'EUR, CZK, PLN, GBP'), ('amount', 'NUMERIC(10,2)', 'in currency'),
        ('status', 'VARCHAR', 'paid, failed, void')]),
    ('refunds', 'Money paid back. One invoice can have several refunds.', [
        ('refund_id', 'INT', 'primary key'), ('invoice_id', 'INT', '→ invoices.invoice_id'),
        ('refund_date', 'DATE', ''), ('amount', 'NUMERIC(10,2)', 'in the invoice currency'),
        ('reason', 'VARCHAR', 'full or partial')]),
    ('fx_rates', 'ECB-style rates, business days only.', [
        ('rate_date', 'DATE', ''), ('currency', 'CHAR(3)', 'CZK, PLN, GBP (no EUR rows)'),
        ('units_per_eur', 'NUMERIC(10,4)', 'units of currency for 1 EUR')]),
    ('workouts', 'Training sessions logged in the app. Kept for 1 Apr – 30 Jun 2025 only.', [
        ('workout_id', 'INT', 'primary key'), ('user_id', 'INT', '→ users.user_id'),
        ('started_at', 'TIMESTAMP', ''), ('kind', 'VARCHAR', 'run, strength, yoga, ride, hiit'),
        ('duration_min', 'INT', 'NULL when the tracker failed')]),
]
NOTES_PULSE = [
    '<b>Today</b> is 30 June 2025 (the data snapshot). Data starts 1 Jan 2024.',
    '<b>Test accounts</b> (<code>users.is_test</code>) are staff. They never count in business numbers.',
    '<b>Active</b> subscription on day D: <code>started_at &lt;= D AND (ended_at IS NULL OR ended_at &gt; D)</code>. <b>In trial</b> on D: D &lt; trial_end. <b>Paying</b> on D: active and not in trial.',
    '<b>Paying customer</b> = a user with at least one paid invoice.',
    '<b>Revenue</b> = paid invoices minus refunds, in EUR. Each amount uses the rate valid on its own date (invoice_date or refund_date): the latest rate on or before that date. EUR = amount / units_per_eur; EUR itself has rate 1.',
    '<b>MRR</b> on D = sum of plan <code>price_eur</code> over subscriptions paying on D; annual plans count price / 12.',
    "<b>First touch</b> = channel of the person's earliest visit. <b>Last touch</b> = their latest visit at or before signup. Users without visitor_id came from the App Store (channel 9).",
    '<b>Active user</b> in a period = logged at least one workout in it.',
]
build('pulse', 'Pulse fitness app', 'Subscription app with paid marketing: ads, visits, trials, invoices in 4 currencies, refunds, workouts',
      'db3.sql', ['questions_db3', 'traps_db3'], SCHEMA_PULSE, NOTES_PULSE)

# ---------- DB2: schema read from a real Postgres load ----------
if ONLY and 'ace' not in ONLY: sys.exit()
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
