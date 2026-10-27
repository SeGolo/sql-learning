"""Generate DB3: 'pulse' - a fitness subscription app with paid marketing (PostgreSQL). Deterministic."""
import random, datetime as dt
from decimal import Decimal, ROUND_HALF_UP

random.seed(20261027)
D = lambda x: Decimal(str(x)).quantize(Decimal('0.01'), ROUND_HALF_UP)
START, END = dt.date(2024, 1, 1), dt.date(2025, 6, 30)

SCHEMA = """
DROP TABLE IF EXISTS workouts, refunds, invoices, subscriptions, plans, users, visits, ad_spend, campaigns, channels, fx_rates CASCADE;

CREATE TABLE channels (
  channel_id  INT PRIMARY KEY,
  name        VARCHAR(30) NOT NULL,
  kind        VARCHAR(10) NOT NULL
);

CREATE TABLE campaigns (
  campaign_id       INT PRIMARY KEY,
  channel_id        INT NOT NULL REFERENCES channels(channel_id),
  name              VARCHAR(40) NOT NULL,
  start_date        DATE NOT NULL,
  end_date          DATE,
  daily_budget_eur  NUMERIC(10,2) NOT NULL
);

CREATE TABLE ad_spend (
  campaign_id  INT NOT NULL REFERENCES campaigns(campaign_id),
  spend_date   DATE NOT NULL,
  impressions  INT NOT NULL,
  clicks       INT NOT NULL,
  spend_eur    NUMERIC(10,2) NOT NULL,
  PRIMARY KEY (campaign_id, spend_date)
);

CREATE TABLE visits (
  visit_id     INT PRIMARY KEY,
  visitor_id   INT NOT NULL,
  visit_ts     TIMESTAMP NOT NULL,
  channel_id   INT NOT NULL REFERENCES channels(channel_id),
  campaign_id  INT REFERENCES campaigns(campaign_id),
  device       VARCHAR(10) NOT NULL
);

CREATE TABLE users (
  user_id     INT PRIMARY KEY,
  visitor_id  INT,
  signup_ts   TIMESTAMP NOT NULL,
  country     VARCHAR(2) NOT NULL,
  platform    VARCHAR(10) NOT NULL,
  is_test     BOOLEAN NOT NULL
);

CREATE TABLE plans (
  plan_id         INT PRIMARY KEY,
  name            VARCHAR(30) NOT NULL,
  billing_period  VARCHAR(5) NOT NULL,
  price_eur       NUMERIC(10,2) NOT NULL,
  is_active       BOOLEAN NOT NULL
);

CREATE TABLE subscriptions (
  subscription_id  INT PRIMARY KEY,
  user_id          INT NOT NULL REFERENCES users(user_id),
  plan_id          INT NOT NULL REFERENCES plans(plan_id),
  started_at       DATE NOT NULL,
  trial_end        DATE,
  ended_at         DATE,
  cancel_reason    VARCHAR(20)
);

CREATE TABLE invoices (
  invoice_id       INT PRIMARY KEY,
  subscription_id  INT NOT NULL REFERENCES subscriptions(subscription_id),
  invoice_date     DATE NOT NULL,
  period_start     DATE NOT NULL,
  period_end       DATE NOT NULL,
  currency         CHAR(3) NOT NULL,
  amount           NUMERIC(10,2) NOT NULL,
  status           VARCHAR(10) NOT NULL
);

CREATE TABLE refunds (
  refund_id    INT PRIMARY KEY,
  invoice_id   INT NOT NULL REFERENCES invoices(invoice_id),
  refund_date  DATE NOT NULL,
  amount       NUMERIC(10,2) NOT NULL,
  reason       VARCHAR(20) NOT NULL
);

CREATE TABLE fx_rates (
  rate_date      DATE NOT NULL,
  currency       CHAR(3) NOT NULL,
  units_per_eur  NUMERIC(10,4) NOT NULL,
  PRIMARY KEY (rate_date, currency)
);

CREATE TABLE workouts (
  workout_id    INT PRIMARY KEY,
  user_id       INT NOT NULL REFERENCES users(user_id),
  started_at    TIMESTAMP NOT NULL,
  kind          VARCHAR(10) NOT NULL,
  duration_min  INT
);
"""

def days(a, b):
    d = a
    while d <= b:
        yield d
        d += dt.timedelta(1)

def add_months(d, n):
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    last = [31, 29 if y % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return dt.date(y, m, min(d.day, last))

# ---------- channels ----------
channels = [(1, 'Google Search', 'paid'), (2, 'Meta Ads', 'paid'), (3, 'TikTok Ads', 'paid'), (4, 'YouTube Ads', 'paid'),
            (5, 'Affiliates', 'paid'), (6, 'Organic Search', 'organic'), (7, 'Direct', 'organic'), (8, 'Referral', 'organic'),
            (9, 'App Store', 'organic')]

# ---------- campaigns: (channel, name, start, end, daily budget) ----------
C = [
    (1, 'GS Brand', '2024-01-01', None, 40),
    (1, 'GS Generic Fitness', '2024-01-08', '2024-12-31', 90),
    (1, 'GS Generic Fitness 2025', '2025-01-01', None, 110),
    (2, 'META New Year 2024', '2024-01-02', '2024-02-15', 150),
    (2, 'META Spring Body', '2024-03-15', '2024-05-31', 120),
    (2, 'META Summer Run', '2024-06-01', '2024-08-31', 100),
    (2, 'META Black Friday', '2024-11-20', '2024-12-02', 300),
    (2, 'META New Year 2025', '2025-01-02', '2025-02-28', 170),
    (2, 'META Retargeting', '2024-04-01', None, 35),
    (3, 'TT Launch', '2024-05-01', '2024-07-31', 140),
    (3, 'TT Challenge 30', '2024-09-01', '2024-10-31', 160),
    (3, 'TT New Year 2025', '2025-01-02', '2025-01-31', 200),
    (3, 'TT Summer 2025', '2025-06-01', None, 150),
    (4, 'YT Coach Stories', '2024-02-01', '2024-04-30', 80),
    (4, 'YT Yoga Series', '2024-09-15', '2024-12-15', 70),
    (4, 'YT Spring 2025', '2025-03-01', '2025-05-15', 90),
    (5, 'AFF Bloggers CZ', '2024-03-01', None, 25),
    (5, 'AFF Coupon Sites', '2024-06-01', '2025-03-31', 30),
    (5, 'AFF Podcast Q4', '2024-10-01', '2024-12-31', 45),
    (2, 'META Lookalike Test', '2025-05-05', '2025-05-25', 60),
    (3, 'TT Creator Test', '2025-04-14', '2025-04-20', 50),
    (4, 'YT Bumper Test', '2025-06-10', None, 40),     # created, never got spend
    (1, 'GS Competitor Terms', '2025-04-15', '2025-05-31', 55),  # paused before launch: no spend
]
campaigns = []
for i, (ch, name, s, e, b) in enumerate(C, 1):
    campaigns.append(dict(id=i, ch=ch, name=name, start=dt.date.fromisoformat(s), end=dt.date.fromisoformat(e) if e else None, budget=D(b)))
NO_SPEND = {22, 23}
CPC = {1: 0.9, 2: 0.55, 3: 0.35, 4: 0.7, 5: 1.6}
CTR = {1: 0.045, 2: 0.012, 3: 0.009, 4: 0.006, 5: 0.02}

ad_spend, active_by_day = [], {}
for c in campaigns:
    if c['id'] in NO_SPEND: continue
    for d in days(c['start'], min(c['end'] or END, END)):
        if random.random() < 0.05: continue          # paused day, no row
        season = 1.25 if d.month in (1, 2) else (0.8 if d.month in (7, 8) else 1.0)
        spend = float(c['budget']) * random.uniform(0.7, 1.05) * season
        if c['id'] == 1 and d.weekday() >= 5: spend = 0  # brand search off at weekends, row still written
        cpc = CPC[c['ch']] * random.uniform(0.75, 1.3)
        clicks = int(spend / cpc) if spend else 0
        if spend and random.random() < 0.01: clicks = 0   # tracking outage
        fatigue = (100 / float(c['budget'])) ** 0.5   # small campaigns reach a warmer audience
        impressions = int(clicks / (CTR[c['ch']] * fatigue * random.uniform(0.8, 1.2))) if clicks else int(spend * 40)
        ad_spend.append((c['id'], d, impressions, clicks, D(spend)))
        if spend: active_by_day.setdefault(d, []).append((c, spend))

# ---------- visitors & visits ----------
DEV = ['mobile'] * 6 + ['desktop'] * 3 + ['tablet']
SIGNUP_P = {1: .20, 2: .10, 3: .06, 4: .09, 5: .19, 6: .16, 7: .22, 8: .26}
visits, users = [], []
vid = 0
visitor = 0
def ts_on(d, lo=6, hi=23):
    return dt.datetime(d.year, d.month, d.day, random.randint(lo, hi), random.randint(0, 59), random.randint(0, 59))

def pick_source(d):
    paid = active_by_day.get(d, [])
    opts = [((6, None), 3.0), ((7, None), 1.2), ((8, None), 0.8)] + [((c['ch'], c['id']), s / 45) for c, s in paid]
    tot = sum(w for _, w in opts)
    r = random.uniform(0, tot)
    for o, w in opts:
        r -= w
        if r <= 0: return o
    return opts[-1][0]

for d in days(START, END):
    paid = active_by_day.get(d, [])
    n_new = int((5 + sum(s for _, s in paid) / 45) * random.uniform(0.7, 1.2))
    for _ in range(n_new):
        visitor += 1
        dev = random.choice(DEV)
        ch, camp = pick_source(d)
        t = ts_on(d)
        vs = [(t, ch, camp)]
        for _ in range(random.choices([0, 1, 2, 3], [50, 25, 15, 10])[0]):
            t = t + dt.timedelta(minutes=random.randint(15, 60 * 24 * 20))
            if t.date() > END: break
            r = random.random()
            if r < 0.45: nxt = (7, None)
            elif r < 0.70: nxt = (6, None)
            elif r < 0.75: nxt = (8, None)
            else:
                p = active_by_day.get(t.date(), [])
                nxt = (lambda c: (c['ch'], c['id']))(random.choice(p)[0]) if p else (7, None)
            vs.append((t, nxt[0], nxt[1]))
        for t, ch2, camp2 in vs:
            vid += 1
            visits.append([vid, visitor, t, ch2, camp2, dev if random.random() > .1 else random.choice(DEV)])
        if random.random() < SIGNUP_P[ch] * (1 + 0.15 * (len(vs) - 1)):
            k = random.choices(range(len(vs)), [1 + i for i in range(len(vs))])[0]
            st = vs[k][0] + dt.timedelta(minutes=random.randint(2, 25))
            if st.date() <= END:
                users.append(dict(visitor=visitor, ts=st, platform=random.choices(['web', 'ios', 'android'], [50, 27, 23])[0]))

# app-store installs: no web visit at all
for d in days(START, END):
    for _ in range(random.choices([0, 1, 2], [45, 40, 15])[0]):
        users.append(dict(visitor=None, ts=ts_on(d, 0, 23), platform=random.choice(['ios', 'android'])))

users.sort(key=lambda u: u['ts'])
COUNTRY = ['CZ'] * 40 + ['SK'] * 12 + ['PL'] * 18 + ['DE'] * 12 + ['AT'] * 6 + ['GB'] * 12
CUR = {'CZ': 'CZK', 'PL': 'PLN', 'GB': 'GBP'}
for i, u in enumerate(users, 1):
    u['id'] = i
    u['country'] = random.choice(COUNTRY)
    u['shown'] = u['country'].lower() if u['country'] in ('CZ', 'PL') and random.random() < 0.03 else u['country']
    u['test'] = False
# internal test accounts
for u in random.sample([u for u in users if u['country'] == 'CZ' and u['visitor']], 12):
    u['test'] = True; u['shown'] = 'CZ'

# ---------- fx rates (business days only) ----------
fx, rate = {}, {'CZK': 25.10, 'PLN': 4.33, 'GBP': 0.855}
for d in days(dt.date(2023, 12, 27), END):
    for cur in rate:
        rate[cur] *= random.uniform(0.996, 1.004)
    if d.weekday() < 5 and d not in (dt.date(2024, 1, 1), dt.date(2024, 12, 25), dt.date(2024, 12, 26), dt.date(2025, 1, 1)):
        for cur in rate:
            fx[(d, cur)] = Decimal(str(rate[cur])).quantize(Decimal('0.0001'))
def fx_on(d, cur):
    while (d, cur) not in fx: d -= dt.timedelta(1)
    return fx[(d, cur)]

# ---------- plans & local price lists ----------
plans = [(1, 'Basic Monthly', 'month', D(7.99), True), (2, 'Plus Monthly', 'month', D(12.99), True),
         (3, 'Basic Annual', 'year', D(79.00), True), (4, 'Plus Annual', 'year', D(119.00), True),
         (5, 'Plus Monthly 2024', 'month', D(10.99), False), (6, 'Family Annual', 'year', D(159.00), True)]
PERIOD = {p[0]: p[2] for p in plans}
LOCAL = {
    'EUR': {1: 7.99, 2: 12.99, 3: 79.00, 4: 119.00, 5: 10.99, 6: 159.00},
    'CZK': {1: 199, 2: 329, 3: 1990, 4: 2990, 5: 279, 6: 3990},
    'PLN': {1: 34.99, 2: 55.99, 3: 339, 4: 509, 5: 46.99, 6: 679},
    'GBP': {1: 6.99, 2: 10.99, 3: 67.99, 4: 99.99, 5: 9.49, 6: 135.00},
}

def choose_plan(d):
    plus_m = 2 if d >= dt.date(2024, 7, 1) else 5
    opts = [(1, 40), (plus_m, 30), (3, 15), (4, 12)] + ([(6, 6)] if d >= dt.date(2025, 1, 15) else [])
    return random.choices([o for o, _ in opts], [w for _, w in opts])[0]

subs, invoices, refunds = [], [], []
sid = iid = rid = 0
REASONS = ['too expensive', 'not using', 'technical', 'other']

def run_sub(u, plan, start, trial):
    """Create one subscription and its invoices. Returns (end_date or None, voluntary churn?)."""
    global sid, iid
    sid += 1
    s = dict(id=sid, uid=u['id'], plan=plan, start=start, trial_end=start + dt.timedelta(7) if trial else None, end=None, reason=None)
    subs.append(s)
    cur = CUR.get(u['country'], 'EUR')
    if trial:
        conv = 0.58 if not u['test'] else 1
        if random.random() > conv:
            s['end'] = start + dt.timedelta(random.randint(1, 7))
            s['reason'] = random.choice(['not using', 'too expensive', None])
            return s['end'], True
    p = s['trial_end'] or start
    first = True
    while p <= END:
        nxt = add_months(p, 1 if PERIOD[plan] == 'month' else 12)
        price = Decimal(str(LOCAL[cur][plan]))
        if first and dt.date(2024, 11, 25) <= p <= dt.date(2024, 12, 2):
            price = D(price / 2)
        if not first and random.random() < 0.05:   # failed charge, maybe retried
            iid += 1
            invoices.append([iid, sid, p, p, nxt - dt.timedelta(1), cur, price, 'failed'])
            if random.random() < 0.35:
                s['end'], s['reason'] = p, 'payment failed'
                return p, False
            pay_day = p + dt.timedelta(3)
        else:
            pay_day = p
        if pay_day > END: break
        iid += 1
        invoices.append([iid, sid, pay_day, p, nxt - dt.timedelta(1), cur, price, 'paid'])
        if random.random() < 0.004:
            iid += 1
            invoices.append([iid, sid, pay_day, p, nxt - dt.timedelta(1), cur, price, 'void'])
        first = False
        # decide what happens at the end of this period
        churn = 0.075 if PERIOD[plan] == 'month' else 0.40
        if random.random() < churn:
            s['end'], s['reason'] = nxt, random.choice(REASONS)
            if nxt > END and random.random() > 0.35:
                s['end'] = s['reason'] = None     # not cancelled yet
            return s['end'], True
        if random.random() < 0.02 and nxt <= END:
            s['end'], s['reason'] = nxt, 'switched plan'
            new = {1: 2, 2: 4, 5: 2, 3: 4, 4: 6, 6: 4}[plan]
            if new == 2 and nxt < dt.date(2024, 7, 1): new = 5
            return run_switch(u, new, nxt)
        p = nxt
    return None, False

def run_switch(u, plan, day):
    return run_sub(u, plan, day, False)

for u in users:
    d0 = u['ts'].date()
    if random.random() > (0.72 if not u['test'] else 1): continue
    start = d0 + dt.timedelta(random.choice([0, 0, 0, 0, 1, 2, 5, 12]))
    if start > END: continue
    end, vol = run_sub(u, choose_plan(start), start, random.random() < 0.85)
    if end and vol and end < END and random.random() < 0.12:
        back = end + dt.timedelta(random.randint(30, 200))
        if back <= END:
            run_sub(u, choose_plan(back), back, False)

# refunds
for inv in invoices:
    if inv[7] != 'paid': continue
    r = random.random()
    parts = [1.0] if r < 0.03 else ([0.5] if r < 0.05 else ([0.3, 0.2] if r < 0.056 else []))
    day = inv[2]
    for f in parts:
        day = day + dt.timedelta(random.randint(1, 14))
        if day > END: break
        rid += 1
        refunds.append((rid, inv[0], day, D(inv[6] * Decimal(str(f))), 'full' if f == 1.0 else 'partial'))

# ---------- workouts: kept for 1 Apr - 30 Jun 2025 only ----------
W0 = dt.date(2025, 4, 1)
KINDS = ['run', 'run', 'strength', 'strength', 'yoga', 'ride', 'hiit']
by_user = {}
for s in subs:
    by_user.setdefault(s['uid'], []).append(s)
workouts, wid = [], 0
umap = {u['id']: u for u in users}
for u in users:
    eng = random.betavariate(1.6, 4)
    intervals = [(s['start'], s['end'] - dt.timedelta(1) if s['end'] else END) for s in by_user.get(u['id'], [])]
    if not intervals:
        intervals = [(u['ts'].date(), u['ts'].date() + dt.timedelta(30))]
        eng *= 0.25
    for a, b in intervals:
        for d in days(max(a, W0), min(b, END)):
            if random.random() < eng * 0.55:
                wid += 1
                dur = random.choice([15, 20, 25, 30, 30, 40, 45, 60])
                workouts.append((wid, u['id'], ts_on(d, 5, 23), random.choice(KINDS), None if random.random() < 0.01 else dur))
workouts.sort(key=lambda w: (w[2], w[1]))
workouts = [(i + 1,) + w[1:] for i, w in enumerate(workouts)]

# ---------- emit SQL ----------
def lit(v):
    if v is None: return 'NULL'
    if isinstance(v, bool): return 'TRUE' if v else 'FALSE'
    if isinstance(v, (int, Decimal)): return str(v)
    if isinstance(v, dt.datetime): return "'" + v.isoformat(sep=' ') + "'"
    if isinstance(v, dt.date): return "'" + v.isoformat() + "'"
    return "'" + str(v).replace("'", "''") + "'"

def ins(table, cols, rows):
    out = []
    for k in range(0, len(rows), 500):
        chunk = rows[k:k + 500]
        out.append(f"INSERT INTO {table} ({', '.join(cols)}) VALUES\n" + ",\n".join('(' + ','.join(lit(v) for v in r) + ')' for r in chunk) + ';')
    return '\n'.join(out)

sql = [SCHEMA.strip()]
sql.append(ins('channels', ['channel_id', 'name', 'kind'], channels))
sql.append(ins('campaigns', ['campaign_id', 'channel_id', 'name', 'start_date', 'end_date', 'daily_budget_eur'],
               [(c['id'], c['ch'], c['name'], c['start'], c['end'], c['budget']) for c in campaigns]))
sql.append(ins('ad_spend', ['campaign_id', 'spend_date', 'impressions', 'clicks', 'spend_eur'], sorted(ad_spend, key=lambda r: (r[1], r[0]))))
sql.append(ins('visits', ['visit_id', 'visitor_id', 'visit_ts', 'channel_id', 'campaign_id', 'device'], visits))
sql.append(ins('users', ['user_id', 'visitor_id', 'signup_ts', 'country', 'platform', 'is_test'],
               [(u['id'], u['visitor'], u['ts'], u['shown'], u['platform'], u['test']) for u in users]))
sql.append(ins('plans', ['plan_id', 'name', 'billing_period', 'price_eur', 'is_active'], plans))
sql.append(ins('subscriptions', ['subscription_id', 'user_id', 'plan_id', 'started_at', 'trial_end', 'ended_at', 'cancel_reason'],
               [(s['id'], s['uid'], s['plan'], s['start'], s['trial_end'], s['end'], s['reason']) for s in subs]))
sql.append(ins('invoices', ['invoice_id', 'subscription_id', 'invoice_date', 'period_start', 'period_end', 'currency', 'amount', 'status'], invoices))
sql.append(ins('refunds', ['refund_id', 'invoice_id', 'refund_date', 'amount', 'reason'], refunds))
sql.append(ins('fx_rates', ['rate_date', 'currency', 'units_per_eur'], [(d, c, r) for (d, c), r in sorted(fx.items())]))
sql.append(ins('workouts', ['workout_id', 'user_id', 'started_at', 'kind', 'duration_min'], workouts))

open('db3.sql', 'w', encoding='utf-8').write('\n\n'.join(sql) + '\n')
print('campaigns', len(campaigns), 'ad_spend', len(ad_spend), 'visitors', visitor, 'visits', len(visits), 'users', len(users),
      'subs', len(subs), 'invoices', len(invoices), 'refunds', len(refunds), 'fx', len(fx), 'workouts', len(workouts))
