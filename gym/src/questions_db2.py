# Questions for DB2 'ace' (Ace the Data Science Interview, ch. 8 + extra traps).
# Fields: t title, d difficulty, g topic, p prompt, h hint, s solution, o order matters,
#         n naive query (trap check), k kind ('sql' | 'theory'), a model answer for theory.
Q = []
def q(t, d, g, p, h, s, o=False, n=None):
    Q.append(dict(t=t, d=d, g=g, p=p, h=h, s=s.strip(), o=o, n=n, k='sql'))
def th(t, d, p, a):
    Q.append(dict(t=t, d=d, g='Theory', p=p, h='', s='', o=False, n=None, k='theory', a=a.strip()))

E, M, H = 'Easy', 'Medium', 'Hard'
B = 'Book ch. 8'

# ======================= BOOK: EASY 8.1 - 8.13 =======================
q('8.1 Facebook: click-through rate', E, B,
  'Using <code>events</code>, get the click-through rate per app in 2019: CTR = clicks / impressions × 100. Return <code>app_id</code> and <code>ctr</code> rounded to 2. Every app with impressions in 2019 must appear, even if it had no clicks.',
  'event_id holds the event TYPE. COUNT(*) FILTER (...) counts each type. Two COUNTs divided = integer division.',
  """SELECT app_id,
       ROUND(100.0 * COUNT(*) FILTER (WHERE event_id = 'click')
                   / COUNT(*) FILTER (WHERE event_id = 'impression'), 2) AS ctr
FROM events
WHERE timestamp >= '2019-01-01' AND timestamp < '2020-01-01'
GROUP BY app_id;""",
  n="""SELECT app_id, ROUND(100 * COUNT(*) FILTER (WHERE event_id = 'click') / COUNT(*) FILTER (WHERE event_id = 'impression'), 2)
FROM events WHERE timestamp >= '2019-01-01' AND timestamp < '2020-01-01' GROUP BY app_id;""")
q('8.2 Robinhood: top cities', E, B,
  'List the top three cities by number of completed orders. Return <code>city</code> and <code>num_orders</code>, highest first.',
  'Only status = \'complete\' counts. Cancelled orders are orders too, but not completed ones.',
  """SELECT u.city, COUNT(DISTINCT t.order_id) AS num_orders
FROM trades t
JOIN users u ON t.user_id = u.user_id
WHERE t.status = 'complete'
GROUP BY u.city
ORDER BY num_orders DESC
LIMIT 3;""", True,
  n="""SELECT u.city, COUNT(*) FROM trades t JOIN users u ON t.user_id = u.user_id GROUP BY u.city ORDER BY 2 DESC LIMIT 3;""")
q('8.3 NYT: laptop vs mobile', E, B,
  'Define "mobile" as tablet + phone. Compare viewership: return one row with <code>laptop_views</code> and <code>mobile_views</code>.',
  'Conditional aggregation: one SUM or COUNT per group, using CASE or FILTER.',
  """SELECT COUNT(*) FILTER (WHERE device_type = 'laptop') AS laptop_views,
       COUNT(*) FILTER (WHERE device_type IN ('tablet', 'phone')) AS mobile_views
FROM viewership;""")
q('8.4 Amazon: cumulative spend', E, B,
  'Using <code>total_trans</code>, calculate the cumulative spend so far by date for each product. Return <code>trans_date</code>, <code>product_id</code>, <code>cum_spend</code> for every row of the table. Orders on the same date all show the total up to and including that date.',
  'SUM(spend) OVER (PARTITION BY product_id ORDER BY trans_date). The default frame treats rows with the same date as one step.',
  """SELECT trans_date, product_id,
       SUM(spend) OVER (PARTITION BY product_id ORDER BY trans_date) AS cum_spend
FROM total_trans;""",
  n="""SELECT trans_date, product_id, SUM(spend) OVER (PARTITION BY product_id ORDER BY trans_date, order_id ROWS UNBOUNDED PRECEDING) FROM total_trans;""")
q('8.5 eBay: top buyers', E, B,
  'Among customers who spent <b>at least</b> $1000 in total (<code>user_transactions</code>), return the 10 who ordered the highest number of products (each row is one product ordered). Return <code>user_id</code> and <code>num_products</code>, highest first.',
  '"At least 1000" — check your comparison operator. The book\'s own solution gets this wrong.',
  """-- Trap: the book uses HAVING SUM(spend) > 1000 and drops user 14, who spent exactly 1000.00.
SELECT user_id, COUNT(product_id) AS num_products
FROM user_transactions
GROUP BY user_id
HAVING SUM(spend) >= 1000
ORDER BY num_products DESC
LIMIT 10;""", True,
  n="""SELECT user_id, COUNT(product_id) FROM user_transactions GROUP BY user_id HAVING SUM(spend) > 1000 ORDER BY 2 DESC LIMIT 10;""")
q('8.6 Twitter: tweet histogram 2020', E, B,
  'Build a histogram of tweets posted per user in 2020: return <code>tweet_bucket</code> (number of tweets a user posted in 2020) and <code>num_users</code> (how many users posted that many). Sort by tweet_bucket.',
  'tweet_date is a TIMESTAMP. The book filters with BETWEEN \'2020-01-01\' AND \'2020-12-31\'. What happens to a tweet at 2020-12-31 22:15?',
  """-- Trap: BETWEEN ... '2020-12-31' stops at 31 Dec 00:00 and loses New Year's Eve tweets.
SELECT num_tweets AS tweet_bucket, COUNT(*) AS num_users
FROM (
  SELECT user_id, COUNT(*) AS num_tweets
  FROM tweets
  WHERE tweet_date >= '2020-01-01' AND tweet_date < '2021-01-01'
  GROUP BY user_id
) t
GROUP BY num_tweets
ORDER BY tweet_bucket;""", True,
  n="""SELECT num_tweets, COUNT(*) FROM (SELECT user_id, COUNT(*) AS num_tweets FROM tweets WHERE tweet_date BETWEEN '2020-01-01' AND '2020-12-31' GROUP BY user_id) t GROUP BY num_tweets ORDER BY 1;""")
q('8.7 Stitch Fix: repeat on different days', E, B,
  'How many people purchased the same product on more than one day? Return one number.',
  'Two purchases on the same day are not "multiple days". Count distinct dates per user and product.',
  """-- Trap: the book ranks with RANK() and keeps purchase_no = 2. Two purchases on day 1 rank 1,1 and the
-- next day ranks 3, so that user is missed. Count distinct days instead.
SELECT COUNT(DISTINCT user_id) AS users
FROM (
  SELECT user_id, product_id
  FROM purchases
  GROUP BY user_id, product_id
  HAVING COUNT(DISTINCT CAST(purchase_time AS DATE)) > 1
) t;""",
  n="""SELECT COUNT(DISTINCT user_id) FROM (SELECT user_id, RANK() OVER (PARTITION BY user_id, product_id ORDER BY CAST(purchase_time AS DATE)) AS purchase_no FROM purchases) t WHERE purchase_no = 2;""")
q('8.8 LinkedIn: duplicate job listings', E, B,
  'How many companies have posted duplicate job listings (two jobs at the same company with the same title <b>and</b> description)? Return one number.',
  'GROUP BY company_id, title, description HAVING COUNT(*) > 1. (The book\'s version puts MAX() inside WHERE, which PostgreSQL rejects.)',
  """SELECT COUNT(DISTINCT company_id) AS companies
FROM (
  SELECT company_id, title, description
  FROM job_listings
  GROUP BY company_id, title, description
  HAVING COUNT(*) > 1
) d;""",
  n="""SELECT COUNT(DISTINCT company_id) FROM (SELECT company_id, title FROM job_listings GROUP BY company_id, title HAVING COUNT(*) > 1) d;""")
q('8.9 Etsy: first purchase $50+', E, B,
  'Return <code>user_id</code> of customers whose first transaction (<code>user_transactions</code>) was valued at $50 or more.',
  'ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY transaction_date) = 1. "Or more" includes 50.00.',
  """SELECT user_id
FROM (
  SELECT user_id, spend,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY transaction_date) AS rn
  FROM user_transactions
) t
WHERE rn = 1 AND spend >= 50;""",
  n="""SELECT user_id FROM (SELECT user_id, spend, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY transaction_date) AS rn FROM user_transactions) t WHERE rn = 1 AND spend > 50;""")
q('8.10 Twitter: 7-day rolling average', M, B,
  'For each user and each date on which they tweeted, return <code>user_id</code>, <code>tweet_day</code> (DATE) and <code>rolling_avg_7d</code> = average tweets per calendar day over that day and the 6 calendar days before it, rounded to 2.',
  'The book uses ROWS BETWEEN 6 PRECEDING over days WITH tweets. If a user skips days, those 7 rows cover more than 7 calendar days.',
  """-- Trap: ROWS BETWEEN 6 PRECEDING counts the last 7 tweeting days, not the last 7 calendar days.
WITH daily AS (
  SELECT user_id, CAST(tweet_date AS DATE) AS tweet_day, COUNT(*) AS n
  FROM tweets
  GROUP BY user_id, CAST(tweet_date AS DATE)
)
SELECT a.user_id, a.tweet_day, ROUND(SUM(b.n) / 7.0, 2) AS rolling_avg_7d
FROM daily a
JOIN daily b ON b.user_id = a.user_id AND b.tweet_day BETWEEN a.tweet_day - 6 AND a.tweet_day
GROUP BY a.user_id, a.tweet_day;""",
  n="""WITH d AS (SELECT user_id, CAST(tweet_date AS DATE) AS day, COUNT(*) AS n FROM tweets GROUP BY 1, 2)
SELECT user_id, day, ROUND(AVG(n) OVER (PARTITION BY user_id ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) FROM d;""")
q('8.11 Uber: third transaction', E, B,
  'Using <code>transactions</code>, return each user\'s third transaction: <code>user_id</code>, <code>transaction_id</code>, <code>total_spend</code> (all items of that transaction) and <code>transaction_date</code>. Users with fewer than 3 transactions are not listed.',
  'Look at the table: one transaction_id can have several rows (one per product). Is a row a transaction?',
  """-- Trap: transactions has one row per PRODUCT. The book numbers rows, so a basket of 3 items
-- looks like 3 transactions. Collapse to one row per transaction first.
WITH t AS (
  SELECT user_id, transaction_id, SUM(spend) AS total_spend, MIN(transaction_date) AS transaction_date
  FROM transactions
  GROUP BY user_id, transaction_id
), n AS (
  SELECT t.*, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY transaction_date) AS rn FROM t
)
SELECT user_id, transaction_id, total_spend, transaction_date FROM n WHERE rn = 3;""",
  n="""SELECT user_id, transaction_id, spend, transaction_date FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY transaction_date, product_id) AS rn FROM transactions) x WHERE rn = 3;""")
q('8.12 Amazon: top 3 per category 2020', M, B,
  'Identify the top three highest-grossing products within each category in 2020. Return <code>category_id</code>, <code>product_id</code>, <code>total_spend</code> and <code>rnk</code> (RANK, so ties are kept).',
  'transaction_date is a TIMESTAMP. The book uses BETWEEN \'2020-01-01\' AND \'2020-12-31\'.',
  """-- Trap: BETWEEN ... '2020-12-31' misses a big sale on 2020-12-31 20:30 and changes category 3's top 3.
WITH s AS (
  SELECT category_id, product_id, SUM(spend) AS total_spend
  FROM product_spend
  WHERE transaction_date >= '2020-01-01' AND transaction_date < '2021-01-01'
  GROUP BY category_id, product_id
)
SELECT * FROM (
  SELECT s.*, RANK() OVER (PARTITION BY category_id ORDER BY total_spend DESC) AS rnk FROM s
) r
WHERE rnk <= 3;""",
  n="""SELECT * FROM (SELECT category_id, product_id, SUM(spend) AS ts, RANK() OVER (PARTITION BY category_id ORDER BY SUM(spend) DESC) AS rnk FROM product_spend
WHERE transaction_date BETWEEN '2020-01-01' AND '2020-12-31' GROUP BY category_id, product_id) r WHERE rnk <= 3;""")
q('8.13 Walmart: last purchase day', M, B,
  'Bucket users by the DAY of their latest transaction (<code>user_transactions</code>). For each such day return <code>transaction_day</code> (DATE), <code>num_users</code> and <code>total_products</code> (transactions on that day by those users). Latest day first.',
  'transaction_date includes a time. Group by the DATE, not the timestamp.',
  """-- Trap: the book groups by transaction_date (a timestamp), so one day splits into many rows.
WITH ranked AS (
  SELECT user_id, product_id, CAST(transaction_date AS DATE) AS transaction_day,
         RANK() OVER (PARTITION BY user_id ORDER BY CAST(transaction_date AS DATE) DESC) AS days_rank
  FROM user_transactions
)
SELECT transaction_day, COUNT(DISTINCT user_id) AS num_users, COUNT(product_id) AS total_products
FROM ranked
WHERE days_rank = 1
GROUP BY transaction_day
ORDER BY transaction_day DESC;""", True,
  n="""SELECT transaction_date, COUNT(DISTINCT user_id), COUNT(product_id) FROM (SELECT *, RANK() OVER (PARTITION BY user_id ORDER BY CAST(transaction_date AS DATE) DESC) AS r FROM user_transactions) x
WHERE r = 1 GROUP BY transaction_date ORDER BY 1 DESC;""")

# ======================= BOOK: THEORY 8.14 - 8.21 =======================
th('8.14 Facebook: views', E, 'What is a database view? What advantages do views have over tables?',
"""A view is a saved SELECT query that you can query like a table. It stores no data itself (except a materialized view); every time you read it, the database runs the underlying query.

Advantages:
- Simplicity: hide complex joins and logic behind one name (e.g. a view "active_customers").
- Security: grant access to a view that shows only some columns or rows, not the whole table.
- Consistency: the business definition (e.g. revenue) lives in one place instead of being copied into many reports.
- Abstraction: the underlying tables can change while the view keeps the same shape for its users.
- No extra storage, and always up to date.

Trade-off: a normal view is recomputed on every read, so a heavy view can be slow; a materialized view stores the result but must be refreshed.""")
th('8.15 Expedia: indexes and workload', M, 'Most queries are UPDATEs / INSERTs / DELETEs. How does that affect your decision to create indexes? What if the queries were mostly SELECTs and JOINs?',
"""An index speeds up reading (finding rows by a column) but every write must also update every index on the table.

Write-heavy workload (INSERT/UPDATE/DELETE): keep indexes to a minimum — usually the primary key and a few that support critical lookups. Each extra index slows every write and uses storage.

Read-heavy workload (SELECT/JOIN): add indexes on columns used in WHERE filters, JOIN keys (foreign keys), and ORDER BY / GROUP BY. They let the database avoid full table scans. Check with EXPLAIN that the indexes are actually used.""")
th('8.16 Microsoft: primary key', E, 'What is a primary key? What characteristics does a good primary key have?',
"""A primary key is the column (or set of columns) that uniquely identifies each row of a table. It cannot be NULL and cannot repeat, and other tables reference it with foreign keys.

A good primary key is:
- Unique and never NULL.
- Stable: it never changes (changing it breaks every reference).
- Minimal: as few columns as possible.
- Compact: e.g. an integer is faster to index and join than a long text.
- Meaningless (often): a surrogate id is safer than a business value like an email or a name, which can change or repeat.""")
th('8.17 Amazon: relational vs NoSQL', M, 'Describe some advantages and disadvantages of relational databases vs. NoSQL databases.',
"""Relational (PostgreSQL, SQL Server, Oracle):
+ Fixed schema, data integrity (constraints, foreign keys), ACID transactions.
+ SQL: powerful joins and ad-hoc analysis.
− Scaling writes horizontally is harder; schema changes need migrations; awkward for very nested or rapidly changing data.

NoSQL (document, key-value, wide-column, graph):
+ Flexible schema, easy horizontal scaling, very fast for simple access patterns at huge volume.
+ Natural fit for nested documents, caches, graphs.
− Usually weaker consistency (BASE / eventual consistency), limited or no joins, integrity must be enforced by the application, harder ad-hoc analytics.

Rule of thumb: relational when correctness and relationships matter (orders, payments, ERP); NoSQL when scale and flexibility of a known access pattern matter (sessions, logs, product catalogue documents).""")
th('8.18 Capital One: MapReduce shuffle', H, 'You want a MapReduce job that shuffles a dataset: the output is the same dataset in random order. At a high level, describe the algorithm.',
"""Map: for every record, emit (random_key, record), where random_key is a random number (e.g. a random integer from a large range).

Shuffle/sort: the framework groups and sorts all pairs by key and sends them to reducers. Because the keys are random, records land in random order and on random reducers.

Reduce: for each key, output its record(s), dropping the key. If several records got the same key, they can be output in random order within that key.

Concatenating the reducer outputs gives a uniformly shuffled dataset. To make it reproducible, seed the random generator (e.g. with the record id).""")
th('8.19 Amazon: WHERE vs HAVING', E, 'Name one major similarity and one difference between a WHERE clause and a HAVING clause in SQL.',
"""Similarity: both filter — they keep only the rows (or groups) for which a condition is TRUE.

Difference: WHERE filters individual rows BEFORE grouping, so it cannot use aggregates. HAVING filters groups AFTER GROUP BY, so it can use aggregates like COUNT(*) > 2 or SUM(spend) >= 1000.

Order of execution: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY.""")
th('8.20 KPMG: foreign key', E, 'Describe what a foreign key is and how it relates to a primary key.',
"""A foreign key is a column in one (child) table whose values must match the primary key of another (parent) table — e.g. orders.customer_id references customers.customer_id.

It enforces referential integrity: you cannot insert an order for a customer that does not exist, and (depending on the rule) you cannot delete a customer who still has orders — or the delete cascades.

It defines the relationship between tables: one-to-many (one customer, many orders), or many-to-many through a link table (order_items links orders and products).""")
th('8.21 Microsoft: clustered vs non-clustered index', M, 'Describe what a clustered index and a non-clustered index are. Compare and contrast the two.',
"""Clustered index: the table rows themselves are stored on disk in the order of the index key. There can be only ONE per table (the data can be sorted only one way). Very fast for range scans and ordered reads on that key. In SQL Server the primary key is clustered by default.

Non-clustered index: a separate structure that stores the key values plus a pointer to the row. A table can have many. Lookups need an extra step (find key, then jump to the row), unless the index covers all needed columns.

Compared: clustered = fastest range reads on one key, but inserts in the middle and key updates are costly; non-clustered = flexible and many per table, but uses extra storage and adds a lookup step. (PostgreSQL has no permanently clustered tables; CLUSTER sorts once, and all indexes are non-clustered.)""")

# ======================= BOOK: MEDIUM 8.22 - 8.29 =======================
q('8.22 Twitter: no popular topics', M, B,
  'Return <code>user_id</code> of users who existed on 2021-01-01 (followed at least one topic on or before that day) and did not follow any of the 100 most popular topics of that day (<code>topic_rankings.ranking</code> ≤ 100 on 2021-01-01).',
  'EXCEPT (the book uses Oracle\'s MINUS). Only follows that existed on 2021-01-01 count, on both sides.',
  """WITH top_topics AS (
  SELECT topic_id FROM topic_rankings
  WHERE ranking_date = '2021-01-01' AND ranking <= 100
)
SELECT DISTINCT user_id FROM user_topics WHERE follow_date < '2021-01-02'
EXCEPT
SELECT u.user_id FROM user_topics u JOIN top_topics t ON u.topic_id = t.topic_id
WHERE u.follow_date < '2021-01-02';""")
q('8.23 Facebook: monthly retention', M, B,
  'An active user took an action in a month. For each month from February to June 2022, return <code>month</code> (first day, DATE) and <code>retained_users</code> = users active that month who were also active the previous month.',
  'The book\'s EXISTS subquery never compares user_id with the outer row. What does it check then?',
  """-- Trap: the book's EXISTS is not correlated on user_id, so it only checks that ANYONE was active
-- last month - it returns plain monthly active users, not retained ones.
WITH m AS (
  SELECT DISTINCT user_id, CAST(DATE_TRUNC('month', timestamp) AS DATE) AS month FROM user_actions
)
SELECT c.month, COUNT(*) AS retained_users
FROM m c
WHERE EXISTS (SELECT 1 FROM m p WHERE p.user_id = c.user_id AND p.month = c.month - INTERVAL '1 month')
GROUP BY c.month
ORDER BY c.month;""", True,
  n="""SELECT CAST(DATE_TRUNC('month', c.timestamp) AS DATE), COUNT(DISTINCT c.user_id) FROM user_actions c
WHERE EXISTS (SELECT 1 FROM user_actions l WHERE DATE_TRUNC('month', l.timestamp) + INTERVAL '1 month' = DATE_TRUNC('month', c.timestamp))
GROUP BY 1 ORDER BY 1;""")
q('8.24 Twitter: rank by session time', M, B,
  'For sessions that started in January 2021 (from 2021-01-01 up to but not including 2021-02-01), rank users by total session duration within each <code>session_type</code>. Return <code>session_type</code>, <code>user_id</code>, <code>total_duration</code>, <code>rnk</code> (RANK, 1 = longest).',
  'The book uses BETWEEN \'2021-01-01\' AND \'2021-02-01\'. Is a session starting exactly at 2021-02-01 00:00:00 in January?',
  """-- Trap: BETWEEN includes 2021-02-01 00:00:00. The book also partitions by user_id, which ranks nothing.
WITH d AS (
  SELECT session_type, user_id, SUM(duration) AS total_duration
  FROM sessions
  WHERE start_time >= '2021-01-01' AND start_time < '2021-02-01'
  GROUP BY session_type, user_id
)
SELECT session_type, user_id, total_duration,
       RANK() OVER (PARTITION BY session_type ORDER BY total_duration DESC) AS rnk
FROM d;""",
  n="""SELECT session_type, user_id, SUM(duration), RANK() OVER (PARTITION BY session_type ORDER BY SUM(duration) DESC) FROM sessions
WHERE start_time BETWEEN '2021-01-01' AND '2021-02-01' GROUP BY session_type, user_id;""")
q('8.25 Snapchat: send vs open by age', M, B,
  'For each age group, return <code>age_bucket</code>, <code>send_perc</code> and <code>open_perc</code> = time spent sending / opening snaps as a percentage of (send + open) time, rounded to 2.',
  'activities also has type \'chat\'. It is not part of "send vs open".',
  """SELECT a.age_bucket,
       ROUND(100.0 * SUM(t.time_spent) FILTER (WHERE t.type = 'send') / SUM(t.time_spent), 2) AS send_perc,
       ROUND(100.0 * SUM(t.time_spent) FILTER (WHERE t.type = 'open') / SUM(t.time_spent), 2) AS open_perc
FROM activities t
JOIN age_breakdown a ON a.user_id = t.user_id
WHERE t.type IN ('send', 'open')
GROUP BY a.age_bucket;""",
  n="""SELECT a.age_bucket, ROUND(100.0 * SUM(t.time_spent) FILTER (WHERE t.type = 'send') / SUM(t.time_spent), 2), ROUND(100.0 * SUM(t.time_spent) FILTER (WHERE t.type = 'open') / SUM(t.time_spent), 2)
FROM activities t JOIN age_breakdown a ON a.user_id = t.user_id GROUP BY a.age_bucket;""")
q('8.26 Pinterest: most concurrent session', H, B,
  'Two sessions are concurrent if they overlap in time. Return the <code>session_id</code> that is concurrent with the largest number of <b>other users\'</b> sessions, and that number as <code>concurrents</code>. Keep ties.',
  'The book counts only sessions that START during s1. A session that started earlier and is still running also overlaps.',
  """-- Trap: overlap is s1.start <= s2.end AND s2.start <= s1.end. The book's
-- "s2.start BETWEEN s1.start AND s1.end" misses sessions that began before s1.
WITH c AS (
  SELECT s1.session_id, COUNT(*) AS concurrents
  FROM sessions s1
  JOIN sessions s2 ON s1.session_id <> s2.session_id AND s1.user_id <> s2.user_id
   AND s2.start_time <= s1.end_time AND s1.start_time <= s2.end_time
  GROUP BY s1.session_id
)
SELECT session_id, concurrents FROM c WHERE concurrents = (SELECT MAX(concurrents) FROM c);""",
  n="""SELECT s1.session_id, COUNT(s2.session_id) FROM sessions s1 JOIN sessions s2 ON s1.session_id != s2.session_id AND s1.user_id <> s2.user_id
AND s2.start_time BETWEEN s1.start_time AND s1.end_time GROUP BY s1.session_id ORDER BY 2 DESC LIMIT 1;""")
q('8.27 Yelp: top-rated businesses', M, B,
  'A top-rated business has only 4- or 5-star reviews. Return <code>top_rated</code> (number of such businesses) and <code>top_rated_pct</code> (percentage of all businesses, rounded to 2).',
  'Lowest star rating per business ≥ 4. Watch integer division in the percentage.',
  """WITH b AS (SELECT business_id, MIN(review_stars) AS min_stars FROM reviews GROUP BY business_id)
SELECT COUNT(*) FILTER (WHERE min_stars >= 4) AS top_rated,
       ROUND(100.0 * COUNT(*) FILTER (WHERE min_stars >= 4) / COUNT(*), 2) AS top_rated_pct
FROM b;""",
  n="""WITH b AS (SELECT business_id, MIN(review_stars) AS m FROM reviews GROUP BY business_id)
SELECT COUNT(*) FILTER (WHERE m >= 4), COUNT(*) FILTER (WHERE m >= 4) / COUNT(*) * 100 FROM b;""")
q('8.28 Google: odd and even measurements', M, B,
  'Measurements are numbered 1, 2, 3 … within each day <b>in time order</b>. For each day return <code>measurement_day</code>, <code>odd_sum</code> (sum of the 1st, 3rd, 5th … values) and <code>even_sum</code>. Sort by day.',
  'Is measurement_id in time order? Check a few rows before you trust it.',
  """-- Trap: measurement_id is not chronological. Number the rows by measurement_time.
WITH n AS (
  SELECT CAST(measurement_time AS DATE) AS measurement_day, measurement_value,
         ROW_NUMBER() OVER (PARTITION BY CAST(measurement_time AS DATE) ORDER BY measurement_time) AS rn
  FROM measurements
)
SELECT measurement_day,
       SUM(measurement_value) FILTER (WHERE rn % 2 = 1) AS odd_sum,
       SUM(measurement_value) FILTER (WHERE rn % 2 = 0) AS even_sum
FROM n
GROUP BY measurement_day
ORDER BY measurement_day;""", True,
  n="""WITH n AS (SELECT CAST(measurement_time AS DATE) AS d, measurement_value AS v, ROW_NUMBER() OVER (PARTITION BY CAST(measurement_time AS DATE) ORDER BY measurement_id) AS rn FROM measurements)
SELECT d, SUM(v) FILTER (WHERE rn % 2 = 1), SUM(v) FILTER (WHERE rn % 2 = 0) FROM n GROUP BY d ORDER BY d;""")
q('8.29 Etsy: last week\'s buyers', M, B,
  'Assume today is 2022-07-01 00:00. Of the users who signed up within the past 7 days (signup_date ≥ 2022-06-24 00:00), what percentage also purchased at least one item? Return <code>last_week_pct</code> rounded to 2.',
  'The book divides COUNT(...) / COUNT(...) * 100. Both COUNTs are integers.',
  """-- Trap: the book's COUNT(...) / COUNT(...) * 100 is integer division in PostgreSQL and returns 0.
SELECT ROUND(100.0 * COUNT(DISTINCT p.user_id) / COUNT(DISTINCT s.user_id), 2) AS last_week_pct
FROM signups s
LEFT JOIN user_purchases p ON p.user_id = s.user_id
WHERE s.signup_date >= TIMESTAMP '2022-07-01' - INTERVAL '7 days';""",
  n="""SELECT COUNT(DISTINCT p.user_id) / COUNT(DISTINCT s.user_id) * 100 FROM signups s LEFT JOIN user_purchases p ON p.user_id = s.user_id
WHERE s.signup_date > TIMESTAMP '2022-07-01' - INTERVAL '7 days';""")

# ======================= BOOK: HARD 8.30 - 8.35 (rebuilt from the book's solutions) =======================
q('8.30 Amazon: bought together', H, B,
  'Using <code>transactions</code> and <code>product</code>, find the 10 product pairs bought together in the same transaction most often. Return <code>product1</code>, <code>product2</code> (names; product1 has the lower product_id) and <code>count</code>, highest first; break ties by product1, then product2, A–Z.',
  'Self-join on transaction_id. Use a.product_id < b.product_id so (X, Y) and (Y, X) count once and a product is not paired with itself.',
  """SELECT p1.product_name AS product1, p2.product_name AS product2, COUNT(*) AS count
FROM transactions a
JOIN transactions b ON a.transaction_id = b.transaction_id AND a.product_id < b.product_id
JOIN product p1 ON p1.product_id = a.product_id
JOIN product p2 ON p2.product_id = b.product_id
GROUP BY p1.product_name, p2.product_name
ORDER BY count DESC, product1, product2
LIMIT 10;""", True,
  n="""SELECT p1.product_name, p2.product_name, COUNT(*) FROM transactions a JOIN transactions b ON a.transaction_id = b.transaction_id AND a.product_id <> b.product_id
JOIN product p1 ON p1.product_id = a.product_id JOIN product p2 ON p2.product_id = b.product_id GROUP BY 1, 2 ORDER BY 3 DESC, 1, 2 LIMIT 10;""")
q('8.31 Reactivated users', H, B,
  'A reactivated user logged in this month, did NOT log in the previous month, but had logged in at some point before that. For each month of 2022, return <code>month</code> (first day, DATE) and <code>reactivated_users</code>. Months with none are not listed. Sort by month.',
  'Brand-new users also did not log in last month — but they are not reactivated. And one user can log in many times a month.',
  """-- Trap: the book counts login ROWS (COUNT(*)) and includes brand-new users.
WITH m AS (
  SELECT DISTINCT user_id, CAST(DATE_TRUNC('month', login_date) AS DATE) AS month FROM user_logins
)
SELECT c.month, COUNT(*) AS reactivated_users
FROM m c
WHERE NOT EXISTS (SELECT 1 FROM m p WHERE p.user_id = c.user_id AND p.month = c.month - INTERVAL '1 month')
  AND EXISTS (SELECT 1 FROM m e WHERE e.user_id = c.user_id AND e.month < c.month - INTERVAL '1 month')
GROUP BY c.month
ORDER BY c.month;""", True,
  n="""SELECT CAST(DATE_TRUNC('month', c.login_date) AS DATE), COUNT(*) FROM user_logins c
WHERE NOT EXISTS (SELECT 1 FROM user_logins l WHERE l.user_id = c.user_id AND DATE_TRUNC('month', l.login_date) = DATE_TRUNC('month', c.login_date) - INTERVAL '1 month')
GROUP BY 1 ORDER BY 1;""")
q('8.32 Year-over-year weekly spend', H, B,
  'Using <code>user_transactions</code>, compute weekly spend per product (<code>week</code> = DATE_TRUNC(\'week\') as DATE). For 2022 weeks that have spend in the same week one year earlier (exactly 52 weeks before), return <code>product_id</code>, <code>week</code>, <code>total_spend</code>, <code>prev_year_spend</code> and <code>spend_yoy</code> = total / previous, rounded to 2.',
  'The book uses LAG(total_spend, 52). That is "52 ROWS back", which is 52 weeks back only if no week is missing.',
  """-- Trap: product 8 has weeks with no sales, so LAG(..., 52) jumps to the wrong week. Join on the date instead.
WITH w AS (
  SELECT product_id, CAST(DATE_TRUNC('week', transaction_date) AS DATE) AS week, SUM(spend) AS total_spend
  FROM user_transactions
  GROUP BY product_id, CAST(DATE_TRUNC('week', transaction_date) AS DATE)
)
SELECT c.product_id, c.week, c.total_spend, p.total_spend AS prev_year_spend,
       ROUND(c.total_spend / p.total_spend, 2) AS spend_yoy
FROM w c
JOIN w p ON p.product_id = c.product_id AND p.week = c.week - 364
WHERE c.week >= '2022-01-01';""",
  n="""SELECT * FROM (SELECT product_id, week, ts, LAG(ts, 52) OVER (PARTITION BY product_id ORDER BY week) AS prev, ROUND(ts / LAG(ts, 52) OVER (PARTITION BY product_id ORDER BY week), 2) AS yoy
FROM (SELECT product_id, CAST(DATE_TRUNC('week', transaction_date) AS DATE) AS week, SUM(spend) AS ts FROM user_transactions GROUP BY 1, 2) w) x
WHERE week >= '2022-01-01' AND prev IS NOT NULL;""")
q('8.33 Rolling weekly total', H, B,
  'For each day in December 2022 that has transactions (<code>user_transactions</code>), return <code>transaction_day</code> and <code>weekly_rolling_total</code> = total spend of that day and the 6 days before it. Sort by day.',
  'The first days of December need spend from late November. When do you apply the December filter?',
  """-- Trap: filtering to December BEFORE the window loses the November days that 1-6 Dec need.
WITH daily AS (
  SELECT CAST(transaction_date AS DATE) AS transaction_day, SUM(spend) AS total
  FROM user_transactions
  GROUP BY CAST(transaction_date AS DATE)
)
SELECT d.transaction_day, SUM(x.total) AS weekly_rolling_total
FROM daily d
JOIN daily x ON x.transaction_day BETWEEN d.transaction_day - 6 AND d.transaction_day
WHERE d.transaction_day >= '2022-12-01'
GROUP BY d.transaction_day
ORDER BY d.transaction_day;""", True,
  n="""WITH daily AS (SELECT CAST(transaction_date AS DATE) AS day, SUM(spend) AS total FROM user_transactions WHERE transaction_date >= '2022-12-01' GROUP BY 1)
SELECT d.day, SUM(x.total) FROM daily d JOIN daily x ON x.day BETWEEN d.day - 6 AND d.day GROUP BY d.day ORDER BY d.day;""")
th('8.34 Facebook: mutual friends with MapReduce', H, 'Using MapReduce, find the number of mutual friends for every pair of Facebook users.',
"""Input: for each user X, the list of X's friends.

Map: for user X with friends list F, for every friend Y in F emit key = the pair (X, Y) sorted so that (min, max) — and value = F. So both X and Y send their full friend lists under the same key (X, Y).

Shuffle: all values with the same key go to the same reducer, so the reducer for (X, Y) receives two lists: friends of X and friends of Y.

Reduce: intersect the two lists; the size of the intersection is the number of mutual friends of X and Y. Output ((X, Y), count).

Example: X: [W, Y, Z], Y: [X, Z]. Key (X, Y) receives [W, Y, Z] and [X, Z]; intersection = [Z] → 1 mutual friend.""")
th('8.35 Google: tracking search queries', H, 'Design a system that tracks search query strings and how often each is searched, at very large scale.',
"""Core: a key-value store — key = normalized query string, value = count.

Ingest: search servers write query events to a log / message queue (e.g. Kafka) instead of updating counts directly, so a traffic spike never slows down search.

Aggregate: stream processors consume the queue, pre-aggregate counts in memory over short windows (e.g. 1 minute) and flush increments to storage. Batch jobs (MapReduce/Spark) recompute daily totals from the raw log for correctness.

Scale: shard the key space by a hash of the query string across many machines (horizontal scaling); replicate shards for availability. Vertical scaling (more CPU/RAM) helps only up to a point.

Read path: keep the top-N / most frequent queries in a cache; for "trending" use counts per time window. Use approximate structures (Count-Min Sketch, HyperLogLog) when exact counts are too expensive.""")
