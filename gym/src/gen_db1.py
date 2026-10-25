"""Generate DB1: 'velo' - a Czech bike & outdoor e-shop (PostgreSQL). Deterministic."""
import random, datetime as dt
from decimal import Decimal, ROUND_HALF_UP

random.seed(20261024)
D = lambda x: Decimal(str(x)).quantize(Decimal('0.01'), ROUND_HALF_UP)

SCHEMA = """
DROP TABLE IF EXISTS reviews, payments, order_items, orders, products, categories, customers CASCADE;

CREATE TABLE customers (
  customer_id  INT PRIMARY KEY,
  first_name   VARCHAR(50) NOT NULL,
  last_name    VARCHAR(50) NOT NULL,
  email        VARCHAR(100),
  city         VARCHAR(50) NOT NULL,
  country      CHAR(2) NOT NULL,
  signup_date  DATE NOT NULL,
  referred_by  INT REFERENCES customers(customer_id),
  is_vip       BOOLEAN NOT NULL
);

CREATE TABLE categories (
  category_id  INT PRIMARY KEY,
  name         VARCHAR(50) NOT NULL,
  parent_id    INT REFERENCES categories(category_id)
);

CREATE TABLE products (
  product_id   INT PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,
  category_id  INT NOT NULL REFERENCES categories(category_id),
  brand        VARCHAR(50) NOT NULL,
  unit_price   NUMERIC(10,2) NOT NULL,
  cost_price   NUMERIC(10,2) NOT NULL,
  launched_date DATE NOT NULL,
  is_active    BOOLEAN NOT NULL
);

CREATE TABLE orders (
  order_id       INT PRIMARY KEY,
  customer_id    INT NOT NULL REFERENCES customers(customer_id),
  order_date     TIMESTAMP NOT NULL,
  status         VARCHAR(20) NOT NULL,
  channel        VARCHAR(20) NOT NULL,
  discount_code  VARCHAR(20),
  shipped_date   DATE,
  delivered_date DATE
);

CREATE TABLE order_items (
  order_id     INT NOT NULL REFERENCES orders(order_id),
  product_id   INT NOT NULL REFERENCES products(product_id),
  quantity     INT NOT NULL,
  unit_price   NUMERIC(10,2) NOT NULL,
  discount_pct INT NOT NULL,
  PRIMARY KEY (order_id, product_id)
);

CREATE TABLE payments (
  payment_id   INT PRIMARY KEY,
  order_id     INT NOT NULL REFERENCES orders(order_id),
  payment_date DATE NOT NULL,
  amount       NUMERIC(10,2) NOT NULL,
  method       VARCHAR(20) NOT NULL,
  status       VARCHAR(20) NOT NULL
);

CREATE TABLE reviews (
  review_id    INT PRIMARY KEY,
  product_id   INT NOT NULL REFERENCES products(product_id),
  customer_id  INT NOT NULL REFERENCES customers(customer_id),
  rating       INT NOT NULL,
  review_date  DATE NOT NULL,
  comment      VARCHAR(200)
);
"""

# ---------- categories ----------
categories = [
    (1, 'Bikes', None), (2, 'Components', None), (3, 'Accessories', None), (4, 'Apparel', None),
    (5, 'Road Bikes', 1), (6, 'Mountain Bikes', 1), (7, 'E-bikes', 1), (8, 'Kids Bikes', 1),
    (9, 'Tires', 2), (10, 'Brakes', 2), (11, 'Chains', 2),
    (12, 'Helmets', 3), (13, 'Lights', 3), (14, 'Locks', 3), (15, 'Bottles', 3),
    (16, 'Jerseys', 4), (17, 'Gloves', 4),
]

# ---------- products: (name, cat, brand, price, cost%, launched, active) ----------
P = [
    ('Trek Domane AL 2', 5, 'Trek', 24990, .72, '2022-03-01', True),
    ('Specialized Allez Sport', 5, 'Specialized', 32990, .70, '2022-05-15', True),
    ('Cube Attain GTC', 5, 'Cube', 41990, .68, '2023-02-01', True),
    ('Author Aura 28', 5, 'Author', 17990, .75, '2021-09-01', False),
    ('Trek Marlin 5', 6, 'Trek', 19990, .72, '2022-01-10', True),
    ('Specialized Rockhopper', 6, 'Specialized', 22990, .70, '2022-04-01', True),
    ('Cube Aim Race', 6, 'Cube', 16990, .74, '2022-02-20', True),
    ('Author Solution 29', 6, 'Author', 14990, .76, '2021-06-01', True),
    ('Cube Stereo Hybrid 140', 7, 'Cube', 89990, .66, '2023-03-01', True),
    ('Trek Rail 5', 7, 'Trek', 99990, .65, '2023-04-15', True),
    ('Specialized Turbo Vado', 7, 'Specialized', 84990, .67, '2022-09-01', True),
    ('Author Simplex E', 7, 'Author', 54990, .70, '2024-10-01', True),
    ('Cube Kid 160', 8, 'Cube', 7990, .70, '2022-03-01', True),
    ('Author Smart 20', 8, 'Author', 6490, .72, '2021-05-01', False),
    ('Trek Precaliber 24', 8, 'Trek', 9490, .70, '2022-06-01', True),
    ('Schwalbe Marathon Plus', 9, 'Schwalbe', 1290, .55, '2020-01-01', True),
    ('Continental Grand Prix 5000', 9, 'Continental', 1690, .55, '2021-01-01', True),
    ('Schwalbe Nobby Nic', 9, 'Schwalbe', 1190, .55, '2020-01-01', True),
    ('Continental Race King', 9, 'Continental', 990, .58, '2020-06-01', True),
    ('Shimano Deore Brake Set', 10, 'Shimano', 2490, .60, '2021-01-01', True),
    ('Shimano XT Brake Set', 10, 'Shimano', 4990, .58, '2021-01-01', True),
    ('SRAM Level TL', 10, 'SRAM', 3290, .60, '2022-01-01', True),
    ('Shimano CN-HG601 Chain', 11, 'Shimano', 690, .50, '2020-01-01', True),
    ('KMC X11 Chain', 11, 'KMC', 590, .52, '2020-01-01', True),
    ('SRAM PC-1110 Chain', 11, 'SRAM', 740, .50, '2023-01-01', True),
    ('Giro Register MIPS Helmet', 12, 'Giro', 1890, .55, '2021-03-01', True),
    ('Abus Viantor Helmet', 12, 'Abus', 2290, .55, '2022-03-01', True),
    ('Giro Aether Spherical Helmet', 12, 'Giro', 7490, .50, '2023-03-01', True),
    ('Lezyne Macro Drive Light', 13, 'Lezyne', 1490, .50, '2021-01-01', True),
    ('Lezyne Strip Rear Light', 13, 'Lezyne', 690, .50, '2021-01-01', True),
    ('Sigma Buster 1100 Light', 13, 'Sigma', 2190, .52, '2023-09-01', True),
    ('Abus Granit X-Plus Lock', 14, 'Abus', 2790, .55, '2020-01-01', True),
    ('Abus Bordo 6000 Lock', 14, 'Abus', 2190, .55, '2020-01-01', True),
    ('Kryptonite Evolution Lock', 14, 'Kryptonite', 1990, .55, '2022-01-01', False),
    ('Elite Fly Bottle 750', 15, 'Elite', 190, .40, '2020-01-01', True),
    ('CamelBak Podium Bottle', 15, 'CamelBak', 390, .42, '2021-01-01', True),
    ('Elite Jet Bottle 950', 15, 'Elite', 240, .40, '2024-11-15', True),
    ('Castelli Competizione Jersey', 16, 'Castelli', 2490, .45, '2022-03-01', True),
    ('Specialized RBX Jersey', 16, 'Specialized', 1990, .45, '2022-03-01', True),
    ('Castelli Aero Race Jersey', 16, 'Castelli', 3990, .45, '2024-12-01', True),
    ('Giro Jag Gloves', 17, 'Giro', 590, .45, '2021-01-01', True),
    ('Castelli Arenberg Gel Gloves', 17, 'Castelli', 990, .45, '2022-01-01', True),
    ('Specialized Body Geometry Gloves', 17, 'Specialized', 790, .45, '2021-01-01', False),
]
products = []
for i, (n, c, b, pr, cp, ld, act) in enumerate(P, 1):
    products.append(dict(id=i, name=n, cat=c, brand=b, price=D(pr), cost=D(pr * cp), launched=dt.date.fromisoformat(ld), active=act))
NEVER_ORDERED = {12, 37, 40}  # launched very late 2024 -> never ordered
INACTIVE_ONLY_2023 = {p['id'] for p in products if not p['active']}
PRICE_RISE_2024 = {'Shimano', 'Schwalbe', 'Abus'}  # +5% from 2024

# ---------- customers ----------
FIRST = ['Jan', 'Petr', 'Tomas', 'Martin', 'Jakub', 'Lukas', 'Ondrej', 'David', 'Michal', 'Pavel',
         'Eva', 'Jana', 'Lucie', 'Tereza', 'Katerina', 'Veronika', 'Anna', 'Petra', 'Marketa', 'Klara',
         'Filip', 'Adam', 'Vojtech', 'Barbora', 'Monika', 'Zuzana', 'Marek', 'Tereza', 'Simona', 'Roman']
LAST = ['Novak', 'Svoboda', 'Novotny', 'Dvorak', 'Cerny', 'Prochazka', 'Kucera', 'Vesely', 'Horak', 'Nemec',
        'Pokorny', 'Marek', 'Pospisil', 'Hajek', 'Kral', 'Jelinek', 'Ruzicka', 'Benes', 'Fiala', 'Sedlacek',
        'Dolezal', 'Zeman', 'Kolar', 'Navratil', 'Cermak', 'Urban', 'Vanek', 'Blazek', 'Kriz', 'Kovac']
CITIES = [('Praha', 'CZ', 16), ('Brno', 'CZ', 9), ('Ostrava', 'CZ', 5), ('Plzen', 'CZ', 4), ('Olomouc', 'CZ', 3),
          ('Liberec', 'CZ', 3), ('Hradec Kralove', 'CZ', 2), ('Bratislava', 'SK', 5), ('Kosice', 'SK', 2),
          ('Vienna', 'AT', 3), ('Dresden', 'DE', 2), ('Wroclaw', 'PL', 2)]
DOMAINS = ['gmail.com', 'seznam.cz', 'email.cz', 'centrum.cz', 'outlook.com']
female = {'Eva', 'Jana', 'Lucie', 'Tereza', 'Katerina', 'Veronika', 'Anna', 'Petra', 'Marketa', 'Klara', 'Barbora', 'Monika', 'Zuzana', 'Simona'}

def fem(last):
    if last.endswith('y'): return last[:-1] + 'a'
    if last == 'Kovac': return 'Kovacova'
    if last.endswith('a'): return last[:-1] + 'ova'
    return last + 'ova'

city_pool = [c for c in CITIES for _ in range(c[2])]
customers = []
used_names = set()
for i in range(1, 61):
    while True:
        f = random.choice(FIRST); l = random.choice(LAST)
        if (f, l) not in used_names: break
    used_names.add((f, l))
    if f in female: l = fem(l)
    city, country, _ = random.choice(city_pool)
    signup = dt.date(2023, 1, 1) + dt.timedelta(days=int((i - 1) * 11.5 + random.randint(0, 9)))
    customers.append(dict(id=i, first=f, last=l, city=city, country=country, signup=signup, ref=None, vip=False,
                          email=f"{f.lower()}.{l.lower()}{random.choice(['', '', str(random.randint(1, 99))])}@{random.choice(DOMAINS)}"))
# two different people named Jan Novak
customers[9].update(first='Jan', last='Novak', city='Praha', country='CZ')
customers[33].update(first='Jan', last='Novak', city='Brno', country='CZ')
customers[9]['email'] = 'jan.novak@seznam.cz'; customers[33]['email'] = 'jnovak77@gmail.com'
for i in (6, 18, 27, 41, 52):
    customers[i]['email'] = None
for i in (3, 8, 12, 20, 25, 30, 38, 45, 47, 55):
    customers[i]['vip'] = True
# referrals: referrer must have signed up earlier
refs = {5: 1, 7: 1, 11: 1, 14: 3, 16: 3, 19: 5, 22: 5, 24: 1, 29: 11, 31: 11, 35: 14, 40: 3, 44: 19, 50: 29, 57: 11}
for c, r in refs.items():
    customers[c - 1]['ref'] = r

NO_ORDERS = {13, 26, 37, 48, 54, 58, 59, 60}
END = dt.date(2024, 12, 31)

# ---------- orders ----------
weights = {}
for c in customers:
    if c['id'] in NO_ORDERS: continue
    weights[c['id']] = random.choice([1, 1, 2, 2, 3, 4, 6, 8]) * (2 if c['vip'] else 1)
weights[4] = 9  # heavy buyer

def pick_customer(day):
    cand = [(cid, w) for cid, w in weights.items() if customers[cid - 1]['signup'] <= day]
    tot = sum(w for _, w in cand); r = random.uniform(0, tot)
    for cid, w in cand:
        r -= w
        if r <= 0: return cid
    return cand[-1][0]

orders, items = [], []
oid = 1000
day = dt.date(2023, 1, 3)
first_order_done = set()
while day <= END:
    season = 1.8 if day.month in (4, 5, 6, 7, 8) else (1.4 if day.month in (11, 12) else 0.7)
    n = sum(1 for _ in range(3) if random.random() < 0.18 * season)
    for _ in range(n):
        cid = pick_customer(day)
        oid += 1
        ts = dt.datetime.combine(day, dt.time(random.randint(6, 23), random.choice([0, 7, 15, 22, 30, 41, 45, 58])))
        code = None
        if cid not in first_order_done and random.random() < 0.35: code = 'WELCOME10'
        elif day.month in (3, 4, 5) and random.random() < 0.15: code = 'SPRING15'
        elif day.month == 11 and day.day >= 22 and random.random() < 0.6: code = 'BLACKFRIDAY20'
        first_order_done.add(cid)
        pct = {'WELCOME10': 10, 'SPRING15': 15, 'BLACKFRIDAY20': 20}.get(code, 0)
        if (END - day).days <= 6:
            status = random.choice(['pending', 'shipped', 'shipped'])
        else:
            r = random.random()
            status = 'delivered' if r < 0.80 else ('cancelled' if r < 0.90 else 'returned')
        channel = random.choices(['web', 'app', 'marketplace'], [55, 30, 15])[0]
        shipped = delivered = None
        if status in ('shipped', 'delivered', 'returned'):
            shipped = day + dt.timedelta(days=random.choice([0, 1, 1, 1, 2, 2, 3, 5]))
        if status in ('delivered', 'returned'):
            delivered = shipped + dt.timedelta(days=random.choice([1, 1, 2, 2, 2, 3, 4, 6]))
        orders.append(dict(id=oid, cid=cid, ts=ts, status=status, channel=channel, code=code, shipped=shipped, delivered=delivered))
        # items
        k = random.choices([1, 2, 3, 4], [45, 30, 17, 8])[0]
        avail = [p for p in products if p['id'] not in NEVER_ORDERED and p['launched'] <= day
                 and (p['active'] or day.year == 2023)]
        wts = [1 if p['cat'] in (5, 6, 7, 8) else (0.6 if p['cat'] == 7 else 3) for p in avail]
        chosen = set()
        while len(chosen) < k:
            chosen.add(random.choices(avail, wts)[0]['id'])
        for pid in sorted(chosen):
            p = products[pid - 1]
            qty = 1 if p['cat'] in (5, 6, 7, 8) else random.choices([1, 2, 3, 4], [60, 25, 10, 5])[0]
            price = p['price'] if (day.year == 2024 or p['brand'] not in PRICE_RISE_2024) else D(p['price'] / Decimal('1.05'))
            items.append(dict(oid=oid, pid=pid, qty=qty, price=price, pct=pct))
    day += dt.timedelta(days=1)

# ---------- payments ----------
def order_total(o):
    return sum((it['price'] * it['qty'] * (100 - it['pct']) / 100 for it in items if it['oid'] == o['id']), Decimal(0)).quantize(Decimal('0.01'), ROUND_HALF_UP)

payments = []
pay_id = 5000
for o in orders:
    if o['status'] == 'pending': continue
    tot = order_total(o)
    method = random.choices(['card', 'bank_transfer', 'paypal', 'cash_on_delivery'], [50, 20, 15, 15])[0]
    d0 = o['ts'].date()
    if method == 'cash_on_delivery':
        if o['status'] in ('shipped', 'cancelled'):
            continue  # nothing paid yet / never paid
        pay_id += 1; payments.append((pay_id, o['id'], o['delivered'], tot, method, 'paid'))
        if o['status'] == 'returned':
            pay_id += 1; payments.append((pay_id, o['id'], o['delivered'] + dt.timedelta(days=random.randint(5, 14)), tot, method, 'refunded'))
        continue
    if random.random() < 0.08:
        pay_id += 1; payments.append((pay_id, o['id'], d0, tot, method, 'failed'))
    if o['status'] == 'cancelled' and random.random() < 0.5:
        pay_id += 1; payments.append((pay_id, o['id'], d0, tot, method, 'failed'))
        continue
    pay_id += 1; payments.append((pay_id, o['id'], d0, tot, method, 'paid'))
    if o['status'] == 'cancelled':
        pay_id += 1; payments.append((pay_id, o['id'], d0 + dt.timedelta(days=random.randint(1, 3)), tot, method, 'refunded'))
    if o['status'] == 'returned':
        pay_id += 1; payments.append((pay_id, o['id'], o['delivered'] + dt.timedelta(days=random.randint(5, 14)), tot, method, 'refunded'))
# data-quality issue on purpose: a few returned orders never got their refund
returned_ids = [o['id'] for o in orders if o['status'] == 'returned']
no_refund = {returned_ids[k] for k in (4, 19, 37)}
payments = [p for p in payments if not (p[1] in no_refund and p[5] == 'refunded')]

# ---------- reviews ----------
quality = {p['id']: random.choice([3.2, 3.8, 4.1, 4.4, 4.7]) for p in products}
COMMENTS = {5: ['Excellent, highly recommend', 'Perfect fit', 'Great value for money', 'Love it'],
            4: ['Very good', 'Good quality', 'Works as expected', 'Solid product'],
            3: ['OK for the price', 'Average', 'Delivery was slow'],
            2: ['Not great', 'Broke after a month', 'Smaller than expected'],
            1: ['Terrible', 'Returned it', 'Does not work']}
reviews, seen = [], set()
rid = 1
omap = {o['id']: o for o in orders}
for it in items:
    o = omap[it['oid']]
    if o['status'] != 'delivered' or (o['cid'], it['pid']) in seen or random.random() > 0.27: continue
    seen.add((o['cid'], it['pid']))
    r = max(1, min(5, round(random.gauss(quality[it['pid']], 0.9))))
    rdate = o['delivered'] + dt.timedelta(days=random.randint(2, 30))
    if rdate > END: continue
    com = random.choice(COMMENTS[r]) if random.random() < 0.7 else None
    reviews.append((rid, it['pid'], o['cid'], r, rdate, com)); rid += 1
# reviews from people who never bought the product
for cid, pid, r in [(2, 9, 5), (13, 26, 4), (21, 10, 1), (26, 1, 3), (44, 33, 2), (8, 28, 5)]:
    if (cid, pid) in seen: continue
    seen.add((cid, pid))
    reviews.append((rid, pid, cid, r, dt.date(2024, random.randint(1, 11), random.randint(1, 28)), random.choice([None, COMMENTS[r][0]]))); rid += 1
reviews.sort(key=lambda x: (x[4], x[0]))
reviews = [(i + 1,) + r[1:] for i, r in enumerate(reviews)]

# ---------- emit SQL ----------
def lit(v):
    if v is None: return 'NULL'
    if isinstance(v, bool): return 'TRUE' if v else 'FALSE'
    if isinstance(v, (int, Decimal)): return str(v)
    if isinstance(v, float): return repr(v)
    if isinstance(v, (dt.date, dt.datetime)): return "'" + v.isoformat(sep=' ') + "'" if isinstance(v, dt.datetime) else "'" + v.isoformat() + "'"
    return "'" + str(v).replace("'", "''") + "'"

def ins(table, cols, rows):
    out = []
    for k in range(0, len(rows), 200):
        chunk = rows[k:k + 200]
        out.append(f"INSERT INTO {table} ({', '.join(cols)}) VALUES\n" + ",\n".join('(' + ', '.join(lit(v) for v in r) + ')' for r in chunk) + ';')
    return '\n'.join(out)

sql = [SCHEMA.strip()]
sql.append(ins('customers', ['customer_id', 'first_name', 'last_name', 'email', 'city', 'country', 'signup_date', 'referred_by', 'is_vip'],
               [(c['id'], c['first'], c['last'], c['email'], c['city'], c['country'], c['signup'], None, c['vip']) for c in customers]))
sql += [f"UPDATE customers SET referred_by = {c['ref']} WHERE customer_id = {c['id']};" for c in customers if c['ref']]
sql.append(ins('categories', ['category_id', 'name', 'parent_id'], [c for c in categories if c[2] is None] + [c for c in categories if c[2] is not None]))
sql.append(ins('products', ['product_id', 'name', 'category_id', 'brand', 'unit_price', 'cost_price', 'launched_date', 'is_active'],
               [(p['id'], p['name'], p['cat'], p['brand'], p['price'], p['cost'], p['launched'], p['active']) for p in products]))
sql.append(ins('orders', ['order_id', 'customer_id', 'order_date', 'status', 'channel', 'discount_code', 'shipped_date', 'delivered_date'],
               [(o['id'], o['cid'], o['ts'], o['status'], o['channel'], o['code'], o['shipped'], o['delivered']) for o in orders]))
sql.append(ins('order_items', ['order_id', 'product_id', 'quantity', 'unit_price', 'discount_pct'],
               [(i['oid'], i['pid'], i['qty'], i['price'], i['pct']) for i in items]))
sql.append(ins('payments', ['payment_id', 'order_id', 'payment_date', 'amount', 'method', 'status'], payments))
sql.append(ins('reviews', ['review_id', 'product_id', 'customer_id', 'rating', 'review_date', 'comment'], reviews))

open('db1.sql', 'w', encoding='utf-8').write('\n\n'.join(sql) + '\n')
print('customers', len(customers), 'products', len(products), 'orders', len(orders), 'items', len(items),
      'payments', len(payments), 'reviews', len(reviews))
