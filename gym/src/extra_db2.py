# Extra practice + trap questions on the 'ace' tables (after the 38 book questions).
from questions_db2 import q, E, M, H

SF, AG, GH, JN, SQ, WF, NC, EX = ('Select & filter', 'Aggregation', 'Group & having', 'Joins',
                                  'Subqueries & CTEs', 'Window functions', 'NULL & CASE', 'Expressions & sorting')

# ---------------- events ----------------
q('Events by type 2019', E, AG,
  'How many impressions and how many clicks were logged in 2019? Return <code>event_id</code> and <code>events</code>.',
  'Despite its name, event_id holds the event type.',
  "SELECT event_id, COUNT(*) AS events FROM events WHERE timestamp >= '2019-01-01' AND timestamp < '2020-01-01' GROUP BY event_id;")
q('App 2 clicks in December', E, SF,
  'How many clicks did app 2 get in December 2019? Return one number.',
  'Look at the last minutes of 31 December and the first second of 2020.',
  "-- Trap: '<= 2019-12-31' stops at midnight and misses 23:58; '<= 2020-01-01' would add the 00:00:00 click.\nSELECT COUNT(*) AS clicks FROM events WHERE app_id = 2 AND event_id = 'click' AND timestamp >= '2019-12-01' AND timestamp < '2020-01-01';",
  n="SELECT COUNT(*) FROM events WHERE app_id = 2 AND event_id = 'click' AND timestamp BETWEEN '2019-12-01' AND '2019-12-31';")
q('Above-average CTR apps', M, SQ,
  'Which apps had a 2019 CTR above the overall 2019 CTR of all apps together? Return <code>app_id</code>.',
  'Overall CTR = all clicks / all impressions, not the average of the app CTRs.',
  """WITH a AS (
  SELECT app_id, COUNT(*) FILTER (WHERE event_id = 'click') AS c, COUNT(*) FILTER (WHERE event_id = 'impression') AS i
  FROM events WHERE timestamp >= '2019-01-01' AND timestamp < '2020-01-01' GROUP BY app_id
)
SELECT app_id FROM a WHERE 1.0 * c / i > (SELECT 1.0 * SUM(c) / SUM(i) FROM a);""")
q('Apps active in 2020 only', M, SQ,
  'Return <code>app_id</code> of apps that have events in 2020 but none in 2019.',
  'EXCEPT, or NOT EXISTS.',
  """SELECT app_id FROM events WHERE timestamp >= '2020-01-01' AND timestamp < '2021-01-01'
EXCEPT
SELECT app_id FROM events WHERE timestamp >= '2019-01-01' AND timestamp < '2020-01-01';""")
q('Monthly CTR of app 1', M, AG,
  'For app 1 in 2019 return <code>month</code> (1–12) and <code>ctr</code> (percent, rounded to 1). Sort by month.',
  'Group by EXTRACT(MONTH ...). Integer division again.',
  """SELECT EXTRACT(MONTH FROM timestamp) AS month,
       ROUND(100.0 * COUNT(*) FILTER (WHERE event_id = 'click') / COUNT(*) FILTER (WHERE event_id = 'impression'), 1) AS ctr
FROM events
WHERE app_id = 1 AND timestamp >= '2019-01-01' AND timestamp < '2020-01-01'
GROUP BY EXTRACT(MONTH FROM timestamp)
ORDER BY month;""", True)

# ---------------- trades / users ----------------
q('Trade value per city', M, NC,
  "Return <code>city</code> and <code>trade_value</code> = SUM(price × quantity) of completed trades. Show users without a city as 'Unknown'. Sort by trade_value from highest.",
  'Users with NULL city still trade. COALESCE the city.',
  """SELECT COALESCE(u.city, 'Unknown') AS city, SUM(t.price * t.quantity) AS trade_value
FROM trades t JOIN users u ON t.user_id = u.user_id
WHERE t.status = 'complete'
GROUP BY COALESCE(u.city, 'Unknown')
ORDER BY trade_value DESC;""", True)
q('Cancellation rate per user', M, AG,
  'For each user return <code>user_id</code> and <code>cancel_pct</code> = cancelled orders / all orders × 100, rounded to 1. Sort by user_id.',
  'Integer division.',
  "SELECT user_id, ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'cancelled') / COUNT(*), 1) AS cancel_pct FROM trades GROUP BY user_id ORDER BY user_id;", True,
  n="SELECT user_id, ROUND(100 * COUNT(*) FILTER (WHERE status = 'cancelled') / COUNT(*), 1) FROM trades GROUP BY user_id ORDER BY user_id;")
q('Users without email', E, NC,
  'How many users have no email? Return one number.',
  "IS NULL, not = NULL.",
  "SELECT COUNT(*) AS no_email FROM users WHERE email IS NULL;",
  n="SELECT COUNT(*) FROM users WHERE email = NULL;")
q('Biggest single trade', E, SF,
  'Return <code>order_id</code>, <code>user_id</code> and <code>value</code> = price × quantity of the most valuable completed trade.',
  'ORDER BY the expression DESC, LIMIT 1 (or compare with MAX).',
  "SELECT order_id, user_id, price * quantity AS value FROM trades WHERE status = 'complete' ORDER BY value DESC LIMIT 1;")
q('Users per city', E, GH,
  'Return <code>city</code> and <code>users</code> for every city, including users with no city as a NULL row. Sort by users from highest, then city.',
  'GROUP BY puts all NULLs in one group.',
  "SELECT city, COUNT(*) AS users FROM users GROUP BY city ORDER BY users DESC, city;", True)
q('Average order value by status', E, AG,
  'For each <code>status</code> return <code>avg_value</code> = average of price × quantity, rounded to 2.',
  'AVG of an expression.',
  "SELECT status, ROUND(AVG(price * quantity), 2) AS avg_value FROM trades GROUP BY status;")

# ---------------- viewership ----------------
q('Views per device and month', E, GH,
  'Return <code>month</code> (1–3), <code>device_type</code> and <code>views</code> for Q1 2022. Sort by month, then device_type.',
  'Group by two things.',
  "SELECT EXTRACT(MONTH FROM view_time) AS month, device_type, COUNT(*) AS views FROM viewership GROUP BY EXTRACT(MONTH FROM view_time), device_type ORDER BY month, device_type;", True)
q('Mobile share', E, AG,
  'What percentage of all views were on mobile (tablet or phone)? Rounded to 2.',
  'COUNT / COUNT is integer division.',
  "SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE device_type IN ('tablet', 'phone')) / COUNT(*), 2) AS mobile_pct FROM viewership;",
  n="SELECT COUNT(*) FILTER (WHERE device_type IN ('tablet', 'phone')) / COUNT(*) * 100 FROM viewership;")
q('All three devices', M, GH,
  'Return <code>user_id</code> of users who watched on all three device types.',
  'HAVING COUNT(DISTINCT device_type) = 3.',
  "SELECT user_id FROM viewership GROUP BY user_id HAVING COUNT(DISTINCT device_type) = 3;",
  n="SELECT user_id FROM viewership GROUP BY user_id HAVING COUNT(device_type) = 3;")
q('Never on a laptop', M, SQ,
  'Return <code>user_id</code> of users who never watched on a laptop.',
  "WHERE device_type <> 'laptop' keeps users who ALSO used a laptop on other rows.",
  "SELECT DISTINCT user_id FROM viewership v WHERE NOT EXISTS (SELECT 1 FROM viewership l WHERE l.user_id = v.user_id AND l.device_type = 'laptop');",
  n="SELECT DISTINCT user_id FROM viewership WHERE device_type <> 'laptop';")
q('Night owls', E, EX,
  'How many views started between 00:00 and 05:59? Return one number.',
  'EXTRACT(HOUR FROM view_time) < 6.',
  "SELECT COUNT(*) AS night_views FROM viewership WHERE EXTRACT(HOUR FROM view_time) < 6;")

# ---------------- total_trans ----------------
q('Daily spend per product', E, GH,
  'Return <code>trans_date</code>, <code>product_id</code> and <code>spend</code> (total) for March 2022. Sort by date, then product.',
  'Several orders can share a date.',
  "SELECT trans_date, product_id, SUM(spend) AS spend FROM total_trans GROUP BY trans_date, product_id ORDER BY trans_date, product_id;", True)
q('Running total by order', M, WF,
  'For product B2 return <code>order_id</code>, <code>trans_date</code> and <code>running_total</code> = spend of this order plus all earlier B2 orders, where orders are in order_id order. Every row must have its own total.',
  'With duplicate dates, ORDER BY trans_date gives tied rows the same total. Order by order_id.',
  "SELECT order_id, trans_date, SUM(spend) OVER (ORDER BY order_id) AS running_total FROM total_trans WHERE product_id = 'B2';")
q('Days without B2 sales', H, SQ,
  'List every day of March 2022 on which product B2 had no sales. Return <code>day</code> (DATE), sorted.',
  'A missing day has no row to select. Generate the calendar with generate_series.',
  """SELECT CAST(d AS DATE) AS day
FROM generate_series(DATE '2022-03-01', DATE '2022-03-31', INTERVAL '1 day') d
WHERE NOT EXISTS (SELECT 1 FROM total_trans t WHERE t.product_id = 'B2' AND t.trans_date = CAST(d AS DATE))
ORDER BY day;""", True)
q('Best day per product', M, WF,
  'For each product return the day with the highest total spend: <code>product_id</code>, <code>trans_date</code>, <code>spend</code>. Keep ties.',
  'Total per day first, then RANK() per product.',
  """SELECT product_id, trans_date, spend FROM (
  SELECT product_id, trans_date, SUM(spend) AS spend,
         RANK() OVER (PARTITION BY product_id ORDER BY SUM(spend) DESC) AS rk
  FROM total_trans GROUP BY product_id, trans_date
) t WHERE rk = 1;""")

# ---------------- user_transactions ----------------
q('Monthly revenue 2022', E, AG,
  'Return <code>month</code> (1–12) and <code>revenue</code> for 2022 from <code>user_transactions</code>. Sort by month.',
  'Half-open date range for the year.',
  "SELECT EXTRACT(MONTH FROM transaction_date) AS month, SUM(spend) AS revenue FROM user_transactions WHERE transaction_date >= '2022-01-01' AND transaction_date < '2023-01-01' GROUP BY EXTRACT(MONTH FROM transaction_date) ORDER BY month;", True)
q('Second biggest spender', M, SQ,
  'Return <code>user_id</code> and <code>total</code> of the user(s) with the second-highest total spend.',
  'DENSE_RANK keeps ties; LIMIT 1 OFFSET 1 does not.',
  "SELECT user_id, total FROM (SELECT user_id, SUM(spend) AS total, DENSE_RANK() OVER (ORDER BY SUM(spend) DESC) AS rk FROM user_transactions GROUP BY user_id) t WHERE rk = 2;")
q('Bought 3, never 5', M, SQ,
  'Return <code>user_id</code> of users who bought product 3 but never product 5.',
  "WHERE product_id = 3 AND product_id <> 5 looks at ONE row. You need the user's whole history.",
  "SELECT user_id FROM user_transactions WHERE product_id = 3\nEXCEPT\nSELECT user_id FROM user_transactions WHERE product_id = 5;",
  n="SELECT DISTINCT user_id FROM user_transactions WHERE product_id = 3 AND product_id <> 5;")
q('Days without sales 2022', H, SQ,
  'How many days of 2022 had no transactions at all? Return one number.',
  'generate_series for the calendar, then NOT EXISTS.',
  """SELECT COUNT(*) AS empty_days
FROM generate_series(DATE '2022-01-01', DATE '2022-12-31', INTERVAL '1 day') d
WHERE NOT EXISTS (SELECT 1 FROM user_transactions t WHERE CAST(t.transaction_date AS DATE) = CAST(d AS DATE));""")
q('Quiet customers', M, GH,
  'Return <code>user_id</code> and <code>last_day</code> (DATE) of users whose last transaction was more than 30 days before 2022-12-31.',
  'MAX per user, then HAVING.',
  "SELECT user_id, CAST(MAX(transaction_date) AS DATE) AS last_day FROM user_transactions GROUP BY user_id HAVING MAX(transaction_date) < DATE '2022-12-31' - 30;")
q('Top 5 share of revenue', M, SQ,
  'What percentage of all revenue comes from the 5 biggest spenders? Rounded to 2.',
  'Top 5 totals in a subquery, divided by the grand total.',
  """SELECT ROUND(100 * (SELECT SUM(total) FROM (SELECT SUM(spend) AS total FROM user_transactions GROUP BY user_id ORDER BY total DESC LIMIT 5) t)
       / (SELECT SUM(spend) FROM user_transactions), 2) AS top5_pct;""")
q('Average transaction per product', E, AG,
  'Return <code>product_id</code> and <code>avg_spend</code> rounded to 2. Sort by product_id.',
  'ROUND(AVG(spend), 2).',
  "SELECT product_id, ROUND(AVG(spend), 2) AS avg_spend FROM user_transactions GROUP BY product_id ORDER BY product_id;", True)
q('Growth vs previous month', H, WF,
  'For 2022 return <code>month</code> (1–12), <code>revenue</code> and <code>growth_pct</code> vs the previous month (December 2021 counts for January), rounded to 1.',
  'Compute monthly revenue over BOTH years, apply LAG, then keep 2022. Filtering 2022 first leaves January without a previous month.',
  """WITH m AS (
  SELECT DATE_TRUNC('month', transaction_date) AS m, SUM(spend) AS revenue FROM user_transactions GROUP BY 1
), g AS (
  SELECT m, revenue, LAG(revenue) OVER (ORDER BY m) AS prev FROM m
)
SELECT EXTRACT(MONTH FROM m) AS month, revenue, ROUND(100 * (revenue - prev) / prev, 1) AS growth_pct
FROM g WHERE m >= '2022-01-01' ORDER BY month;""", True,
  n="""WITH m AS (SELECT DATE_TRUNC('month', transaction_date) AS m, SUM(spend) AS revenue FROM user_transactions WHERE transaction_date >= '2022-01-01' GROUP BY 1)
SELECT EXTRACT(MONTH FROM m), revenue, ROUND(100 * (revenue - LAG(revenue) OVER (ORDER BY m)) / LAG(revenue) OVER (ORDER BY m), 1) FROM m ORDER BY 1;""")

# ---------------- tweets ----------------
q('Tweets per hour', E, EX,
  'Return <code>hour</code> (0–23) and <code>tweets</code> over the whole table. Sort by hour.',
  'EXTRACT(HOUR FROM tweet_date).',
  "SELECT EXTRACT(HOUR FROM tweet_date) AS hour, COUNT(*) AS tweets FROM tweets GROUP BY EXTRACT(HOUR FROM tweet_date) ORDER BY hour;", True)
q('Busiest day per user', H, WF,
  'For each user return the date(s) on which they tweeted most: <code>user_id</code>, <code>tweet_day</code>, <code>tweets</code>. Keep ties.',
  'Count per user and DATE, then RANK per user.',
  """SELECT user_id, tweet_day, tweets FROM (
  SELECT user_id, CAST(tweet_date AS DATE) AS tweet_day, COUNT(*) AS tweets,
         RANK() OVER (PARTITION BY user_id ORDER BY COUNT(*) DESC) AS rk
  FROM tweets GROUP BY user_id, CAST(tweet_date AS DATE)
) t WHERE rk = 1;""")
q('Longest tweeting streak', H, WF,
  'For each user return <code>user_id</code> and <code>longest_streak</code> = the most consecutive calendar days on which they tweeted.',
  'Gaps and islands: day − ROW_NUMBER() is constant inside a streak.',
  """WITH d AS (SELECT DISTINCT user_id, CAST(tweet_date AS DATE) AS day FROM tweets),
g AS (SELECT user_id, day, day - CAST(ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day) AS INT) AS grp FROM d)
SELECT user_id, MAX(len) AS longest_streak
FROM (SELECT user_id, grp, COUNT(*) AS len FROM g GROUP BY user_id, grp) s
GROUP BY user_id;""")
q('Quiet in 2021', M, SQ,
  'Return <code>user_id</code> of users who tweeted in 2020 but not in January 2021.',
  'EXCEPT with two date ranges.',
  """SELECT user_id FROM tweets WHERE tweet_date >= '2020-01-01' AND tweet_date < '2021-01-01'
EXCEPT
SELECT user_id FROM tweets WHERE tweet_date >= '2021-01-01' AND tweet_date < '2021-02-01';""")
q('Users with exactly one tweet day', E, GH,
  'How many users tweeted on exactly one day of December 2019? Return one number.',
  'COUNT(DISTINCT CAST(tweet_date AS DATE)), not COUNT(*).',
  """SELECT COUNT(*) AS users FROM (
  SELECT user_id FROM tweets WHERE tweet_date >= '2019-12-01' AND tweet_date < '2020-01-01'
  GROUP BY user_id HAVING COUNT(DISTINCT CAST(tweet_date AS DATE)) = 1
) t;""")

# ---------------- purchases ----------------
q('Revenue per product', E, AG,
  'Return <code>product_id</code> and <code>revenue</code> from <code>purchases</code>. Sort by revenue from highest, then product_id.',
  'price is per unit.',
  "SELECT product_id, SUM(quantity * price) AS revenue FROM purchases GROUP BY product_id ORDER BY revenue DESC, product_id;", True,
  n="SELECT product_id, SUM(price) FROM purchases GROUP BY product_id ORDER BY 2 DESC, 1;")
q('One-day shoppers', M, GH,
  'Return <code>user_id</code> of users whose purchases all happened on a single day (at least 2 purchases).',
  'COUNT(*) >= 2 AND COUNT(DISTINCT date) = 1.',
  "SELECT user_id FROM purchases GROUP BY user_id HAVING COUNT(*) >= 2 AND COUNT(DISTINCT CAST(purchase_time AS DATE)) = 1;")
q('Repeat purchase rate', M, SQ,
  'What percentage of users bought at least one product more than once (any days)? Rounded to 2.',
  'Flag per user first, then the percentage.',
  """WITH u AS (
  SELECT user_id, MAX(n) AS max_n FROM (SELECT user_id, product_id, COUNT(*) AS n FROM purchases GROUP BY user_id, product_id) x GROUP BY user_id
)
SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE max_n > 1) / COUNT(*), 2) AS repeat_pct FROM u;""")
q('Average items per purchase', E, AG,
  'What is the average quantity per purchase? Rounded to 2.',
  'AVG of an INT column returns NUMERIC in PostgreSQL. Fine here.',
  "SELECT ROUND(AVG(quantity), 2) AS avg_qty FROM purchases;")

# ---------------- job_listings ----------------
q('Jobs per title', E, GH,
  'Return <code>title</code> and <code>jobs</code>. Sort by jobs from highest, then title.',
  'GROUP BY title.',
  "SELECT title, COUNT(*) AS jobs FROM job_listings GROUP BY title ORDER BY jobs DESC, title;", True)
q('Duplicates to delete', M, WF,
  'For every duplicate listing (same company, title and description), keep the earliest post and list the others: return their <code>job_id</code>.',
  'ROW_NUMBER() OVER (PARTITION BY company_id, title, description ORDER BY post_date, job_id) > 1.',
  """SELECT job_id FROM (
  SELECT job_id, ROW_NUMBER() OVER (PARTITION BY company_id, title, description ORDER BY post_date, job_id) AS rn
  FROM job_listings
) t WHERE rn > 1;""")
q('Busy recruiters', E, GH,
  'Return <code>company_id</code> of companies with more than 3 listings.',
  'HAVING COUNT(*) > 3.',
  "SELECT company_id FROM job_listings GROUP BY company_id HAVING COUNT(*) > 3;")

# ---------------- transactions / product ----------------
q('Transactions per user', E, AG,
  'Return <code>user_id</code> and <code>transactions</code> (number of baskets). Sort by user_id.',
  'One basket = one transaction_id, with several rows.',
  "SELECT user_id, COUNT(DISTINCT transaction_id) AS transactions FROM transactions GROUP BY user_id ORDER BY user_id;", True,
  n="SELECT user_id, COUNT(*) FROM transactions GROUP BY user_id ORDER BY user_id;")
q('Average basket value', M, SQ,
  'What is the average value of a transaction (basket)? Rounded to 2.',
  'AVG(spend) averages ITEM rows. Sum per basket first.',
  "SELECT ROUND(AVG(total), 2) AS avg_basket FROM (SELECT transaction_id, SUM(spend) AS total FROM transactions GROUP BY transaction_id) t;",
  n="SELECT ROUND(AVG(spend), 2) FROM transactions;")
q('Laptop without a bag', M, SQ,
  'Return <code>transaction_id</code> of baskets that contain a Laptop but no Laptop Bag.',
  'Two conditions on different rows of the same basket.',
  """SELECT t.transaction_id FROM transactions t JOIN product p ON p.product_id = t.product_id WHERE p.product_name = 'Laptop'
EXCEPT
SELECT t.transaction_id FROM transactions t JOIN product p ON p.product_id = t.product_id WHERE p.product_name = 'Laptop Bag';""")
q('Items per basket', E, GH,
  'Return <code>items</code> (number of products in a basket) and <code>baskets</code> (how many baskets have that many). Sort by items.',
  'Count per transaction_id, then count those counts.',
  "SELECT items, COUNT(*) AS baskets FROM (SELECT transaction_id, COUNT(*) AS items FROM transactions GROUP BY transaction_id) t GROUP BY items ORDER BY items;", True)
q('Not yet bought by user 7', M, JN,
  'Return <code>product_name</code> of every product that user 7 has never bought.',
  'If you LEFT JOIN transactions and then put user_id = 7 in WHERE, the NULL rows disappear. Put the user filter in ON.',
  "SELECT p.product_name FROM product p LEFT JOIN transactions t ON t.product_id = p.product_id AND t.user_id = 7 WHERE t.product_id IS NULL;",
  n="SELECT p.product_name FROM product p LEFT JOIN transactions t ON t.product_id = p.product_id WHERE t.user_id = 7 AND t.product_id IS NULL;")

# ---------------- product_spend ----------------
q('Category spend 2020', E, AG,
  'Return <code>category_id</code> and <code>spend</code> for 2020. Sort by category_id.',
  'transaction_date is a TIMESTAMP.',
  "SELECT category_id, SUM(spend) AS spend FROM product_spend WHERE transaction_date >= '2020-01-01' AND transaction_date < '2021-01-01' GROUP BY category_id ORDER BY category_id;", True,
  n="SELECT category_id, SUM(spend) FROM product_spend WHERE transaction_date BETWEEN '2020-01-01' AND '2020-12-31' GROUP BY category_id ORDER BY category_id;")
q('Best month per category', H, WF,
  'For each category, which month of 2020 had the highest spend? Return <code>category_id</code>, <code>month</code> (1–12), <code>spend</code>.',
  'Spend per category and month, then RANK per category.',
  """SELECT category_id, month, spend FROM (
  SELECT category_id, EXTRACT(MONTH FROM transaction_date) AS month, SUM(spend) AS spend,
         RANK() OVER (PARTITION BY category_id ORDER BY SUM(spend) DESC) AS rk
  FROM product_spend
  WHERE transaction_date >= '2020-01-01' AND transaction_date < '2021-01-01'
  GROUP BY category_id, EXTRACT(MONTH FROM transaction_date)
) t WHERE rk = 1;""")
q('Products quiet in January 2021', M, SQ,
  'Return <code>product_id</code> of products sold in 2020 but not in January 2021.',
  'EXCEPT.',
  """SELECT product_id FROM product_spend WHERE transaction_date >= '2020-01-01' AND transaction_date < '2021-01-01'
EXCEPT
SELECT product_id FROM product_spend WHERE transaction_date >= '2021-01-01' AND transaction_date < '2021-02-01';""")

# ---------------- topics ----------------
q('Followers per topic', E, GH,
  'Return the 5 topics with the most followers: <code>topic_id</code>, <code>followers</code> (distinct users). Highest first, ties by topic_id.',
  'A user can follow the same topic twice?',
  "SELECT topic_id, COUNT(DISTINCT user_id) AS followers FROM user_topics GROUP BY topic_id ORDER BY followers DESC, topic_id LIMIT 5;", True)
q('Biggest rank jump', M, JN,
  'Which topic improved its ranking the most from 2020-12-31 to 2021-01-01? Return <code>topic_id</code> and <code>improvement</code> (old ranking − new ranking).',
  'Join topic_rankings to itself: one copy per date.',
  """SELECT a.topic_id, a.ranking - b.ranking AS improvement
FROM topic_rankings a JOIN topic_rankings b ON a.topic_id = b.topic_id
WHERE a.ranking_date = '2020-12-31' AND b.ranking_date = '2021-01-01'
ORDER BY improvement DESC LIMIT 1;""")

# ---------------- user_actions ----------------
q('Monthly active users', E, AG,
  'Return <code>month</code> (first day, DATE) and <code>mau</code> = distinct active users. Sort by month.',
  'Distinct users, not actions.',
  "SELECT CAST(DATE_TRUNC('month', timestamp) AS DATE) AS month, COUNT(DISTINCT user_id) AS mau FROM user_actions GROUP BY 1 ORDER BY 1;", True,
  n="SELECT CAST(DATE_TRUNC('month', timestamp) AS DATE), COUNT(user_id) FROM user_actions GROUP BY 1 ORDER BY 1;")
q('Active every month', M, GH,
  'Return <code>user_id</code> of users active in every month from January to June 2022.',
  'COUNT(DISTINCT month) = 6.',
  "SELECT user_id FROM user_actions WHERE timestamp >= '2022-01-01' AND timestamp < '2022-07-01' GROUP BY user_id HAVING COUNT(DISTINCT DATE_TRUNC('month', timestamp)) = 6;")
q('Comment share', E, AG,
  'What share of all actions are comments, in percent rounded to 1?',
  'Integer division.',
  "SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE event_id = 'comment') / COUNT(*), 1) AS comment_pct FROM user_actions;")

# ---------------- sessions ----------------
q('Average session in minutes', E, EX,
  'Return <code>session_type</code> and <code>avg_minutes</code> = average duration in minutes (duration is in seconds), rounded to 1.',
  'duration / 60 is integer division.',
  "SELECT session_type, ROUND(AVG(duration / 60.0), 1) AS avg_minutes FROM sessions GROUP BY session_type;",
  n="SELECT session_type, ROUND(AVG(duration / 60), 1) FROM sessions GROUP BY session_type;")
q('Long sessions', E, SF,
  'How many sessions lasted more than 2 hours? Return one number.',
  'Units! duration is in seconds.',
  "SELECT COUNT(*) AS long_sessions FROM sessions WHERE duration > 2 * 3600;",
  n="SELECT COUNT(*) FROM sessions WHERE duration > 120;")
q('Peak concurrency', H, SQ,
  'What is the largest number of sessions running at the same moment? Return one number.',
  'Concurrency changes only when a session starts. Count, at each start_time, the sessions that are running then.',
  """SELECT MAX(running) AS peak FROM (
  SELECT s.start_time, COUNT(*) AS running
  FROM sessions s JOIN sessions o ON o.start_time <= s.start_time AND o.end_time >= s.start_time
  GROUP BY s.session_id, s.start_time
) t;""")

# ---------------- activities ----------------
q('Time per activity type', E, AG,
  'Return <code>type</code> and <code>time_spent</code> (total). Sort by time from highest.',
  'SUM per type.',
  "SELECT type, SUM(time_spent) AS time_spent FROM activities GROUP BY type ORDER BY time_spent DESC;", True)
q('Users without age group', M, JN,
  'How much total time did users WITHOUT an age group spend? Return one number.',
  'An INNER JOIN to age_breakdown drops exactly these users.',
  "SELECT SUM(a.time_spent) AS time_spent FROM activities a LEFT JOIN age_breakdown b ON a.user_id = b.user_id WHERE b.user_id IS NULL;")

# ---------------- reviews ----------------
q('Single-review businesses', E, GH,
  'How many businesses have exactly one review? Return one number.',
  'GROUP BY business_id HAVING COUNT(*) = 1, then count.',
  "SELECT COUNT(*) AS businesses FROM (SELECT business_id FROM reviews GROUP BY business_id HAVING COUNT(*) = 1) t;")
q('Five-star share per business', M, AG,
  'For each business return <code>business_id</code> and <code>five_star_pct</code>, rounded to 1. Sort by business_id.',
  'Integer division.',
  "SELECT business_id, ROUND(100.0 * COUNT(*) FILTER (WHERE review_stars = 5) / COUNT(*), 1) AS five_star_pct FROM reviews GROUP BY business_id ORDER BY business_id;", True,
  n="SELECT business_id, ROUND(100 * COUNT(*) FILTER (WHERE review_stars = 5) / COUNT(*), 1) FROM reviews GROUP BY business_id ORDER BY business_id;")
q('Rating dropped', M, JN,
  'Return <code>business_id</code> of businesses whose average stars in 2022 were lower than in 2021 (only businesses reviewed in both years).',
  'Average per business per year, then compare the two years.',
  """WITH y AS (SELECT business_id, EXTRACT(YEAR FROM review_date) AS yr, AVG(review_stars) AS a FROM reviews GROUP BY 1, 2)
SELECT a.business_id FROM y a JOIN y b ON a.business_id = b.business_id AND a.yr = 2021 AND b.yr = 2022
WHERE b.a < a.a;""")

# ---------------- measurements ----------------
q('Daily min, max, average', E, AG,
  'Return <code>day</code>, <code>min_value</code>, <code>max_value</code>, <code>avg_value</code> (rounded to 2). Sort by day.',
  'Group by CAST(measurement_time AS DATE).',
  "SELECT CAST(measurement_time AS DATE) AS day, MIN(measurement_value) AS min_value, MAX(measurement_value) AS max_value, ROUND(AVG(measurement_value), 2) AS avg_value FROM measurements GROUP BY 1 ORDER BY 1;", True)
q('Change from previous reading', M, WF,
  'For every measurement return <code>measurement_time</code>, <code>measurement_value</code> and <code>change</code> = value minus the previous reading of the SAME day (NULL for the first one).',
  'LAG(...) OVER (PARTITION BY day ORDER BY measurement_time).',
  "SELECT measurement_time, measurement_value, measurement_value - LAG(measurement_value) OVER (PARTITION BY CAST(measurement_time AS DATE) ORDER BY measurement_time) AS change FROM measurements;",
  n="SELECT measurement_time, measurement_value, measurement_value - LAG(measurement_value) OVER (ORDER BY measurement_time) FROM measurements;")

# ---------------- signups / purchases ----------------
q('Never purchased', E, JN,
  'How many signed-up users never purchased anything? Return one number.',
  'LEFT JOIN + IS NULL, or NOT EXISTS.',
  "SELECT COUNT(*) AS never FROM signups s WHERE NOT EXISTS (SELECT 1 FROM user_purchases p WHERE p.user_id = s.user_id);")
q('Hours to first purchase', M, SQ,
  'For buyers, what is the average time from signup to first purchase in hours? Rounded to 1.',
  'MIN(purchase_date) per user; EXTRACT(EPOCH FROM interval) / 3600.',
  """SELECT ROUND(AVG(EXTRACT(EPOCH FROM f.first_buy - s.signup_date) / 3600), 1) AS avg_hours
FROM signups s JOIN (SELECT user_id, MIN(purchase_date) AS first_buy FROM user_purchases GROUP BY user_id) f ON f.user_id = s.user_id;""")

# ---------------- user_logins ----------------
q('Login MAU', E, AG,
  'Return <code>month</code> (1–12) and <code>active_users</code> for 2022. Sort by month.',
  'Users, not logins.',
  "SELECT EXTRACT(MONTH FROM login_date) AS month, COUNT(DISTINCT user_id) AS active_users FROM user_logins GROUP BY 1 ORDER BY 1;", True,
  n="SELECT EXTRACT(MONTH FROM login_date), COUNT(*) FROM user_logins GROUP BY 1 ORDER BY 1;")
q('New users per month', M, SQ,
  'Return <code>month</code> (1–12) and <code>new_users</code> = users whose FIRST login was in that month. Sort by month.',
  'MIN(login_date) per user first.',
  "SELECT EXTRACT(MONTH FROM first_login) AS month, COUNT(*) AS new_users FROM (SELECT user_id, MIN(login_date) AS first_login FROM user_logins GROUP BY user_id) t GROUP BY 1 ORDER BY 1;", True)
q('Churned in December', M, SQ,
  'Return <code>user_id</code> of users who logged in in November 2022 but not in December 2022.',
  'EXCEPT.',
  """SELECT user_id FROM user_logins WHERE login_date >= '2022-11-01' AND login_date < '2022-12-01'
EXCEPT
SELECT user_id FROM user_logins WHERE login_date >= '2022-12-01' AND login_date < '2023-01-01';""")
