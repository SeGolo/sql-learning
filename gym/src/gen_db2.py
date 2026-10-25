"""DB2 'ace': tables from Ace the Data Science Interview, ch. 8, with trap-friendly data. Deterministic."""
import random, datetime as dt
from decimal import Decimal, ROUND_HALF_UP

random.seed(8008)
D = lambda x: Decimal(str(x)).quantize(Decimal('0.01'), ROUND_HALF_UP)
T = lambda s: dt.datetime.fromisoformat(s)
def rts(day, h0=7, h1=23):
    return dt.datetime.combine(day, dt.time(random.randint(h0, h1), random.randint(0, 59), random.randint(0, 59)))
def days(a, b):
    a, b = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    return [a + dt.timedelta(k) for k in range((b - a).days + 1)]

S = []   # SQL statements
def lit(v):
    if v is None: return 'NULL'
    if isinstance(v, bool): return 'TRUE' if v else 'FALSE'
    if isinstance(v, (int, Decimal)): return str(v)
    if isinstance(v, dt.datetime): return "'" + v.isoformat(sep=' ') + "'"
    if isinstance(v, dt.date): return "'" + v.isoformat() + "'"
    return "'" + str(v).replace("'", "''") + "'"
def table(ddl, name, cols, rows):
    S.append(ddl.strip())
    for k in range(0, len(rows), 300):
        S.append(f"INSERT INTO {name} ({', '.join(cols)}) VALUES\n" + ",\n".join('(' + ', '.join(lit(v) for v in r) + ')' for r in rows[k:k + 300]) + ';')

# ---------- 8.1 events ----------
ev = []
eid = 0
ctr_target = {1: (400, 0.06), 2: (250, 0.11), 3: (320, 0.035), 4: (90, 0.20), 5: (60, 0.0)}
for app, (imp, p) in ctr_target.items():
    for _ in range(imp):
        d = random.choice(days('2019-01-01', '2019-12-31'))
        ev.append((app, 'impression', rts(d, 0, 23)))
        if random.random() < p:
            ev.append((app, 'click', rts(d, 0, 23)))
for app in (1, 2, 3, 6):   # other years, incl. the edges of 2019
    for _ in range(40):
        d = random.choice(days('2018-06-01', '2018-12-31') + days('2020-01-01', '2020-06-30'))
        ev.append((app, random.choice(['impression'] * 5 + ['click']), rts(d, 0, 23)))
ev += [(2, 'click', T('2019-12-31 23:58:00')), (2, 'click', T('2020-01-01 00:00:00')), (1, 'impression', T('2018-12-31 23:59:30'))]
ev.sort(key=lambda r: r[2])
table("""CREATE TABLE events (app_id INT NOT NULL, event_id VARCHAR(20) NOT NULL, "timestamp" TIMESTAMP NOT NULL);""",
      'events', ['app_id', 'event_id', '"timestamp"'], ev)

# ---------- 8.2 trades + users ----------
cities = ['San Francisco', 'New York', 'Boston', 'Denver', 'Austin', 'Seattle', 'Chicago']
users = []
for uid in range(101, 141):
    city = cities[(uid * 3) % 7] if uid not in (139, 140) else None
    users.append((uid, city, f'user{uid}@mail.com' if uid % 9 else None, T(f'2020-{1 + uid % 12:02}-{1 + uid % 27:02} 10:00:00')))
table("""CREATE TABLE users (user_id INT PRIMARY KEY, city VARCHAR(50), email VARCHAR(100), signup_date TIMESTAMP NOT NULL);""",
      'users', ['user_id', 'city', 'email', 'signup_date'], users)
city_w = {'San Francisco': 6, 'New York': 5, 'Boston': 4, 'Denver': 2, 'Austin': 2, 'Seattle': 3, 'Chicago': 1}
trades, oid = [], 9000
for u in users:
    n = (city_w.get(u[1], 1)) * random.randint(1, 3)
    for _ in range(n):
        oid += 1
        st = 'complete' if random.random() < 0.8 else 'cancelled'
        trades.append((oid, u[0], D(random.uniform(10, 500)), random.randint(1, 50), st, rts(random.choice(days('2021-01-01', '2021-12-31')))))
# Chicago: lots of cancelled orders (trap for counting all orders)
for _ in range(60):
    oid += 1; trades.append((oid, 129 if users[28][1] == 'Chicago' else [u[0] for u in users if u[1] == 'Chicago'][0], D(random.uniform(10, 500)), random.randint(1, 10), 'cancelled', rts(random.choice(days('2021-01-01', '2021-12-31')))))
table("""CREATE TABLE trades (order_id INT PRIMARY KEY, user_id INT NOT NULL, price NUMERIC(10,2) NOT NULL, quantity INT NOT NULL, status VARCHAR(20) NOT NULL, "timestamp" TIMESTAMP NOT NULL);""",
      'trades', ['order_id', 'user_id', 'price', 'quantity', 'status', '"timestamp"'], trades)

# ---------- 8.3 viewership ----------
vw = []
for _ in range(500):
    vw.append((random.randint(1, 80), random.choices(['laptop', 'tablet', 'phone'], [45, 20, 35])[0], rts(random.choice(days('2022-01-01', '2022-03-31')), 0, 23)))
table("""CREATE TABLE viewership (user_id INT NOT NULL, device_type VARCHAR(20) NOT NULL, view_time TIMESTAMP NOT NULL);""",
      'viewership', ['user_id', 'device_type', 'view_time'], vw)

# ---------- 8.4 total_trans ----------
tt, toid = [], 500
for d in days('2022-03-01', '2022-03-31'):
    for pid in ('A1', 'B2', 'C3'):
        for _ in range(random.choice([0, 0, 1, 1, 2])):
            toid += 1; tt.append((toid, random.randint(1, 30), pid, D(random.uniform(5, 120)), d))
table("""CREATE TABLE total_trans (order_id INT PRIMARY KEY, user_id INT NOT NULL, product_id VARCHAR(10) NOT NULL, spend NUMERIC(10,2) NOT NULL, trans_date DATE NOT NULL);""",
      'total_trans', ['order_id', 'user_id', 'product_id', 'spend', 'trans_date'], tt)

# ---------- user_transactions (8.5, 8.9, 8.13, 8.32, 8.33) ----------
ut, utid = [], 7000
prod_base = {p: random.uniform(8, 40) for p in range(1, 9)}
for d in days('2021-01-04', '2022-12-31'):
    for _ in range(random.choice([0, 1, 1, 2, 2, 3])):
        p = random.randint(1, 8)
        if p == 8 and (d.month in (2, 7) and d.year == 2022):   # product 8: missing weeks in 2022 (LAG 52 trap)
            continue
        if p == 8 and d.year == 2021 and d.month == 9:
            continue
        utid += 1
        u = random.choices(range(1, 41), [1 + (k % 7) for k in range(40)])[0]
        ut.append([utid, p, u, D(prod_base[p] * random.uniform(.6, 1.6) * (0.6 + (u % 5) * 0.35)), rts(d)])
# first transaction of some users: make the >=50 check interesting
first = {}
for r in ut:
    if r[2] not in first: first[r[2]] = r
for k, u in enumerate(sorted(first)):
    if k % 3 == 0: first[u][3] = D(random.uniform(50, 90))
first[sorted(first)[1]][3] = D(50)  # exactly 50.00 (>= trap)
# one user with total spend exactly 1000.00 is made below after checking totals
table("""CREATE TABLE user_transactions (transaction_id INT PRIMARY KEY, product_id INT NOT NULL, user_id INT NOT NULL, spend NUMERIC(10,2) NOT NULL, transaction_date TIMESTAMP NOT NULL);""",
      'user_transactions', ['transaction_id', 'product_id', 'user_id', 'spend', 'transaction_date'], [])
UT = ut  # inserted at the end (after adjustments)

# ---------- 8.6 / 8.10 tweets ----------
tw, tid = [], 0
for u in range(1, 31):
    rate = random.choice([0.05, 0.1, 0.2, 0.4, 0.7])
    for d in days('2019-12-15', '2021-01-10'):
        if random.random() < rate:
            for _ in range(random.choice([1, 1, 1, 2, 3])):
                tid += 1; tw.append((tid, f'tweet {tid}', u, rts(d, 0, 23)))
tw += [(tid + 1, 'late night', 7, T('2020-12-31 22:15:00')), (tid + 2, 'nye', 7, T('2020-12-31 23:59:00')), (tid + 3, 'nye2', 12, T('2020-12-31 18:00:00'))]
table("""CREATE TABLE tweets (tweet_id INT PRIMARY KEY, msg VARCHAR(200) NOT NULL, user_id INT NOT NULL, tweet_date TIMESTAMP NOT NULL);""",
      'tweets', ['tweet_id', 'msg', 'user_id', 'tweet_date'], tw)

# ---------- 8.7 purchases ----------
pu, pid_ = [], 0
for u in range(1, 61):
    for _ in range(random.randint(1, 6)):
        pid_ += 1
        prod = random.randint(1, 15)
        d = random.choice(days('2022-01-01', '2022-06-30'))
        pu.append((pid_, u, prod, random.randint(1, 3), D(random.uniform(5, 80)), rts(d)))
# same product twice on the SAME day (not 'multiple days'), and the RANK() 1,1,3 trap
for u, prod, dd in [(61, 3, '2022-02-02'), (62, 5, '2022-03-03'), (63, 7, '2022-04-04')]:
    for h in (9, 15):
        pid_ += 1; pu.append((pid_, u, prod, 1, D(20), T(f'{dd} {h:02}:00:00')))
for h, dd in [(9, '2022-05-05'), (17, '2022-05-05'), (10, '2022-05-20')]:
    pid_ += 1; pu.append((pid_, 64, 9, 1, D(15), T(f'{dd} {h:02}:00:00')))
table("""CREATE TABLE purchases (purchase_id INT PRIMARY KEY, user_id INT NOT NULL, product_id INT NOT NULL, quantity INT NOT NULL, price NUMERIC(10,2) NOT NULL, purchase_time TIMESTAMP NOT NULL);""",
      'purchases', ['purchase_id', 'user_id', 'product_id', 'quantity', 'price', 'purchase_time'], pu)

# ---------- 8.8 job_listings ----------
titles = ['Data Analyst', 'Data Scientist', 'Data Engineer', 'BI Developer', 'ML Engineer', 'Product Analyst']
descs = ['SQL and dashboards', 'Python, statistics, A/B tests', 'ETL pipelines on Spark', 'Power BI and DAX', 'Model training and MLOps', 'Product metrics and experiments']
jl, jid = [], 0
for c in range(1, 31):
    used = set()
    for _ in range(random.randint(1, 4)):
        t = random.randrange(6)
        if t in used: continue
        used.add(t); jid += 1
        jl.append((jid, c, titles[t], descs[t], random.choice(days('2022-01-01', '2022-06-30'))))
dups = [(3, 0, 0), (3, 0, 0), (8, 2, 2), (12, 1, 1), (12, 1, 1), (12, 4, 4), (12, 4, 4), (17, 3, 0), (17, 3, 3), (21, 5, 5), (21, 5, 1)]
for c, t, dsc in dups:  # c17 / c21: same title, different description (NOT duplicates)
    jid += 1; jl.append((jid, c, titles[t], descs[dsc], random.choice(days('2022-01-01', '2022-06-30'))))
table("""CREATE TABLE job_listings (job_id INT PRIMARY KEY, company_id INT NOT NULL, title VARCHAR(100) NOT NULL, description VARCHAR(200) NOT NULL, post_date DATE NOT NULL);""",
      'job_listings', ['job_id', 'company_id', 'title', 'description', 'post_date'], jl)

# ---------- 8.11 / 8.30 transactions + product ----------
pnames = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'USB Hub', 'Webcam', 'Headset', 'Docking Station', 'Charger', 'Laptop Bag']
table("""CREATE TABLE product (product_id INT PRIMARY KEY, product_name VARCHAR(50) NOT NULL);""",
      'product', ['product_id', 'product_name'], [(i + 1, n) for i, n in enumerate(pnames)])
affinity = {1: [2, 10, 9, 8], 4: [8, 3], 2: [3], 6: [7]}
tr, trid = [], 3000
for u in range(1, 51):
    for _ in range(random.choice([1, 2, 2, 3, 4, 5, 6])):
        trid += 1
        ts = rts(random.choice(days('2022-01-01', '2022-12-31')))
        base = random.randint(1, 10)
        items = {base}
        for a in affinity.get(base, []):
            if random.random() < 0.55: items.add(a)
        if random.random() < 0.3: items.add(random.randint(1, 10))
        for p in sorted(items):
            tr.append((trid, u, p, D(random.uniform(10, 900) if p in (1, 4, 8) else random.uniform(5, 120)), ts))
table("""CREATE TABLE transactions (transaction_id INT NOT NULL, user_id INT NOT NULL, product_id INT NOT NULL, spend NUMERIC(10,2) NOT NULL, transaction_date TIMESTAMP NOT NULL);""",
      'transactions', ['transaction_id', 'user_id', 'product_id', 'spend', 'transaction_date'], tr)

# ---------- 8.12 product_spend ----------
ps, psid = [], 0
for cat in (1, 2, 3):
    for prod in range(cat * 100 + 1, cat * 100 + 8):
        w = random.uniform(.3, 2)
        for d in days('2019-11-01', '2021-02-28'):
            if random.random() < 0.025 * w:
                psid += 1; ps.append((psid, cat, prod, random.randint(1, 60), D(random.uniform(10, 200) * w), rts(d)))
# tie for 3rd place in category 2, and a big late-evening 2020-12-31 sale in category 3
ps_tot = {}
for r in ps:
    if r[5].year == 2020: ps_tot[(r[1], r[2])] = ps_tot.get((r[1], r[2]), 0) + r[4]
psid += 1; ps.append((psid, 3, 307, 5, D(4000), T('2020-12-31 20:30:00')))
table("""CREATE TABLE product_spend (transaction_id INT PRIMARY KEY, category_id INT NOT NULL, product_id INT NOT NULL, user_id INT NOT NULL, spend NUMERIC(10,2) NOT NULL, transaction_date TIMESTAMP NOT NULL);""",
      'product_spend', ['transaction_id', 'category_id', 'product_id', 'user_id', 'spend', 'transaction_date'], ps)
PS_TOT = ps_tot

# ---------- 8.22 user_topics + topic_rankings ----------
utp = []
for u in range(1, 41):
    for _ in range(random.randint(1, 4)):
        utp.append((u, random.randint(1, 140), rts(random.choice(days('2020-06-01', '2020-12-31')))))
for u in range(41, 47):       # existing users who follow only unpopular topics (ranked > 100)
    utp.append((u, random.randint(101, 140), rts(random.choice(days('2020-06-01', '2020-12-31')))))
for u in range(47, 51):       # joined after 2021-01-01 -> not existing users on that day
    utp.append((u, random.randint(101, 140), rts(random.choice(days('2021-01-02', '2021-02-28')))))
utp.append((5, 3, T('2021-01-05 10:00:00')))
table("""CREATE TABLE user_topics (user_id INT NOT NULL, topic_id INT NOT NULL, follow_date TIMESTAMP NOT NULL);""",
      'user_topics', ['user_id', 'topic_id', 'follow_date'], utp)
trk = []
for dd in ('2020-12-31', '2021-01-01', '2021-01-02'):
    order = list(range(1, 141)); random.shuffle(order)
    if dd == '2021-01-01':  # keep the 'unpopular' topics 101-140 outside the top 100 on that day
        top = [t for t in order if t <= 100]; rest = [t for t in order if t > 100]; order = top + rest
    for rk, t in enumerate(order, 1):
        trk.append((t, rk, T(dd + ' 00:00:00')))
table("""CREATE TABLE topic_rankings (topic_id INT NOT NULL, ranking INT NOT NULL, ranking_date TIMESTAMP NOT NULL);""",
      'topic_rankings', ['topic_id', 'ranking', 'ranking_date'], trk)

# ---------- 8.23 user_actions ----------
ua = []
for u in range(1, 61):
    active = {m for m in range(1, 7) if random.random() < (0.75 if u % 4 else 0.35)}
    for m in active:
        for _ in range(random.randint(1, 4)):
            d = random.choice(days(f'2022-{m:02}-01', f'2022-{m:02}-28'))
            ua.append((u, random.choice(['sign-in', 'like', 'comment']), rts(d, 0, 23)))
ua += [(99, 'sign-in', T('2022-03-31 23:50:00')), (99, 'like', T('2022-04-01 00:05:00'))]
table("""CREATE TABLE user_actions (user_id INT NOT NULL, event_id VARCHAR(20) NOT NULL, "timestamp" TIMESTAMP NOT NULL);""",
      'user_actions', ['user_id', 'event_id', '"timestamp"'], ua)

# ---------- 8.24 / 8.26 sessions ----------
se, sid = [], 0
for u in range(1, 21):
    for _ in range(random.randint(3, 8)):
        sid += 1
        st = rts(random.choice(days('2020-12-20', '2021-02-10')), 0, 22)
        dur = random.randint(60, 7200)
        se.append([sid, u, random.choice(['streamer', 'viewer']), dur, st, st + dt.timedelta(seconds=dur)])
# exact-boundary sessions (BETWEEN trap) and a long session that started BEFORE many others overlap it
for u, typ, dur, st in [(3, 'viewer', 5000, '2021-02-01 00:00:00'), (8, 'streamer', 9000, '2021-01-01 00:00:00'),
                        (11, 'viewer', 30000, '2021-01-15 01:00:00')]:
    sid += 1; s0 = T(st); se.append([sid, u, typ, dur, s0, s0 + dt.timedelta(seconds=dur)])
LONG = sid
for k in range(7):  # sessions starting inside the long one
    sid += 1; s0 = T('2021-01-15 03:00:00') + dt.timedelta(minutes=37 * k)
    se.append([sid, 12 + k % 5, 'viewer', 1800, s0, s0 + dt.timedelta(seconds=1800)])
for k in range(3):  # and a session that STARTED BEFORE and overlaps many of them
    pass
sid += 1; s0 = T('2021-01-15 00:30:00'); se.append([sid, 19, 'streamer', 21000, s0, s0 + dt.timedelta(seconds=21000)])
table("""CREATE TABLE sessions (session_id INT PRIMARY KEY, user_id INT NOT NULL, session_type VARCHAR(20) NOT NULL, duration INT NOT NULL, start_time TIMESTAMP NOT NULL, end_time TIMESTAMP NOT NULL);""",
      'sessions', ['session_id', 'user_id', 'session_type', 'duration', 'start_time', 'end_time'], se)

# ---------- 8.25 activities + age_breakdown ----------
buckets = ['18-25', '26-35', '36-45', '46+']
ab = [(u, buckets[u % 4]) for u in range(1, 41)]
table("""CREATE TABLE age_breakdown (user_id INT PRIMARY KEY, age_bucket VARCHAR(10) NOT NULL);""", 'age_breakdown', ['user_id', 'age_bucket'], ab)
ac, aid = [], 0
for u in range(1, 44):  # users 41-43 have no age bucket
    for _ in range(random.randint(3, 12)):
        aid += 1
        typ = random.choices(['send', 'open', 'chat'], [40, 45, 15])[0]
        ac.append((aid, u, typ, D(random.uniform(0.5, 9.5)), random.choice(days('2022-05-01', '2022-05-31'))))
table("""CREATE TABLE activities (activity_id INT PRIMARY KEY, user_id INT NOT NULL, type VARCHAR(10) NOT NULL, time_spent NUMERIC(6,2) NOT NULL, activity_date DATE NOT NULL);""",
      'activities', ['activity_id', 'user_id', 'type', 'time_spent', 'activity_date'], ac)

# ---------- 8.27 reviews ----------
rv = []
for b in range(1, 41):
    good = b % 3 == 0
    for _ in range(random.randint(1, 8)):
        stars = random.choice([4, 5]) if good else random.choices([1, 2, 3, 4, 5], [5, 8, 15, 35, 37])[0]
        rv.append((b, random.randint(1, 200), 'Review text', stars, random.choice(days('2021-01-01', '2022-12-31'))))
table("""CREATE TABLE reviews (business_id INT NOT NULL, user_id INT NOT NULL, review_text VARCHAR(200), review_stars INT NOT NULL, review_date DATE NOT NULL);""",
      'reviews', ['business_id', 'user_id', 'review_text', 'review_stars', 'review_date'], rv)

# ---------- 8.28 measurements ----------
ms = []
mid_pool = list(range(1001, 1001 + 70)); random.shuffle(mid_pool)  # ids NOT in time order (trap)
k = 0
for d in days('2022-07-10', '2022-07-16'):
    for _ in range(random.randint(3, 7)):
        ms.append((mid_pool[k], D(random.uniform(100, 2000)), rts(d, 0, 23))); k += 1
table("""CREATE TABLE measurements (measurement_id INT PRIMARY KEY, measurement_value NUMERIC(10,2) NOT NULL, measurement_time TIMESTAMP NOT NULL);""",
      'measurements', ['measurement_id', 'measurement_value', 'measurement_time'], ms)

# ---------- 8.29 signups + user_purchases ('today' = 2022-07-01) ----------
sg = [(u, rts(random.choice(days('2022-05-01', '2022-06-30')), 0, 23)) for u in range(1, 81)]
sg += [(81, T('2022-06-23 23:30:00')), (82, T('2022-06-24 00:10:00')), (83, T('2022-06-30 21:00:00'))]
table("""CREATE TABLE signups (user_id INT PRIMARY KEY, signup_date TIMESTAMP NOT NULL);""", 'signups', ['user_id', 'signup_date'], sg)
up = []
for u, sd in sg:
    if random.random() < 0.45:
        for _ in range(random.randint(1, 3)):
            up.append((u, random.randint(1, 20), sd + dt.timedelta(hours=random.randint(1, 200))))
up.append((82, 4, T('2022-06-25 12:00:00')))
table("""CREATE TABLE user_purchases (user_id INT NOT NULL, product_id INT NOT NULL, purchase_date TIMESTAMP NOT NULL);""",
      'user_purchases', ['user_id', 'product_id', 'purchase_date'], up)

# ---------- 8.31 user_logins ----------
ul = []
for u in range(1, 71):
    start = random.randint(1, 9)
    for m in range(start, 13):
        if random.random() < 0.55:
            for _ in range(random.randint(1, 3)):
                ul.append((u, rts(random.choice(days(f'2022-{m:02}-01', f'2022-{m:02}-28')), 0, 23)))
table("""CREATE TABLE user_logins (user_id INT NOT NULL, login_date TIMESTAMP NOT NULL);""", 'user_logins', ['user_id', 'login_date'], ul)

# ---------- user_transactions: total of exactly 1000.00 for one heavy user ----------
tot = {}
for r in UT: tot[r[2]] = tot.get(r[2], 0) + r[3]
cnt = {}
for r in UT: cnt[r[2]] = cnt.get(r[2], 0) + 1
over = sorted([u for u in tot if tot[u] > 1000], key=lambda u: -cnt[u])
target = over[3]
diff = tot[target] - Decimal(1000)
rows = [r for r in UT if r[2] == target]
while diff > 0:          # lower spends of this user until the total is exactly 1000.00
    r = rows.pop()
    cut = min(diff, r[3] - Decimal('1.00'))
    r[3] -= cut; diff -= cut
S.append("INSERT INTO user_transactions (transaction_id, product_id, user_id, spend, transaction_date) VALUES\n" +
         ",\n".join('(' + ', '.join(lit(v) for v in r) + ')' for r in UT) + ';')

open('db2.sql', 'w', encoding='utf-8').write('\n\n'.join(S) + '\n')
print('statements', len(S), 'user_transactions', len(UT), 'exact-1000 user', target)
