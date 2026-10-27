# MIND TRAPS for DB3 (appended after the regular questions).
# n = the naive query that falls into the trap; verify.py checks it gives a different result.
from questions_db3 import q, E, M, H, rate, MONEY, FIRST_TOUCH

q('Campaigns live today', E, 'Warm-up',
  'Which campaigns are still running today? Return campaign <code>name</code>.',
  'What does an empty end_date mean?',
  """-- Trap: end_date IS NULL means "no end planned", so the campaign is still running.
SELECT name FROM campaigns
WHERE start_date <= DATE '2025-06-30' AND (end_date IS NULL OR end_date >= DATE '2025-06-30');""",
  n="SELECT name FROM campaigns WHERE start_date <= DATE '2025-06-30' AND end_date >= DATE '2025-06-30';")
q('Subscribers right now', E, 'Subscriptions',
  'How many active subscriptions do real users have right now?',
  'What is "now" in this data? And what does an ended_at in the future mean?',
  """-- Trap 1: "today" is the snapshot date 30 June 2025, not CURRENT_DATE.
-- Trap 2: ended_at after today = already cancelled but still has access, so still active.
SELECT COUNT(*) AS active
FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.started_at <= DATE '2025-06-30' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-30');""",
  n="""SELECT COUNT(*) FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.ended_at IS NULL;""")
q('How many customers', E, 'Subscriptions',
  'How many paying customers have we had since launch?',
  'Who is a customer? Read the notes, all of them.',
  """-- Trap: staff test accounts also have paid invoices. And a customer is a user, not a subscription.
SELECT COUNT(DISTINCT s.user_id) AS customers
FROM invoices i
JOIN subscriptions s ON s.subscription_id = i.subscription_id
JOIN users u ON u.user_id = s.user_id
WHERE i.status = 'paid' AND NOT u.is_test;""",
  n="""SELECT COUNT(DISTINCT s.user_id) FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id
WHERE i.status = 'paid';""")
q('New customers in March', M, 'Subscriptions',
  'How many new paying customers did we win in March 2025?',
  'Starting a subscription is not the same as paying. And some March customers were customers before.',
  """-- Trap: a subscription that starts in March can be a trial that never pays, and a returning
-- customer is not new. New paying customer = first ever paid invoice falls in March.
WITH fp AS (
  SELECT s.user_id, MIN(i.invoice_date) AS first_paid
  FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id
  WHERE i.status = 'paid' GROUP BY s.user_id
)
SELECT COUNT(*) AS new_customers
FROM fp JOIN users u ON u.user_id = fp.user_id
WHERE NOT u.is_test AND fp.first_paid >= '2025-03-01' AND fp.first_paid < '2025-04-01';""",
  n="""SELECT COUNT(*) FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.started_at >= '2025-03-01' AND s.started_at < '2025-04-01';""")
q('MRR today', M, 'Subscriptions',
  'What is our MRR today? One number in EUR, 2 decimals.',
  'M stands for monthly. What does an annual plan contribute per month? Who is paying (vs. trying)?',
  """-- Trap 1: annual plans count price / 12. Trap 2: users in trial pay nothing yet.
SELECT ROUND(SUM(CASE WHEN p.billing_period = 'year' THEN p.price_eur / 12 ELSE p.price_eur END), 2) AS mrr_eur
FROM subscriptions s
JOIN plans p ON p.plan_id = s.plan_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.started_at <= DATE '2025-06-30' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-30')
  AND COALESCE(s.trial_end, s.started_at) <= DATE '2025-06-30';""",
  n="""SELECT ROUND(SUM(p.price_eur), 2) FROM subscriptions s JOIN plans p ON p.plan_id = s.plan_id JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.started_at <= DATE '2025-06-30' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-30');""")
q('Billings in May', M, 'Revenue & FX',
  'How much did we bill in May 2025, in EUR? Real users, paid invoices, before refunds. 2 decimals.',
  'units_per_eur = how many CZK (or PLN, GBP) you get for 1 EUR. Multiply or divide?',
  f"""-- Trap: 199 CZK at 25 CZK/EUR is 199 / 25 = 7.96 EUR, not 199 * 25.
SELECT ROUND(SUM(i.amount / {rate('i.currency', 'i.invoice_date')}), 2) AS billed_eur
FROM invoices i
JOIN subscriptions s ON s.subscription_id = i.subscription_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status = 'paid' AND i.invoice_date >= '2025-05-01' AND i.invoice_date < '2025-06-01';""",
  n=f"""SELECT ROUND(SUM(i.amount * {rate('i.currency', 'i.invoice_date')}), 2)
FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status = 'paid' AND i.invoice_date >= '2025-05-01' AND i.invoice_date < '2025-06-01';""")
q('Billings 2024', H, 'Revenue & FX',
  'How much did we bill in 2024 in EUR (real users, paid invoices, before refunds)? 2 decimals.',
  'Try joining fx_rates on the exact invoice date and count the invoices you keep. Which days have no rate? Which currency has no rate at all?',
  f"""-- Trap 1: rates exist on business days only; a Saturday invoice has no exact-date rate.
-- Trap 2: EUR has no rows in fx_rates; an inner join silently drops every EUR invoice.
SELECT ROUND(SUM(i.amount / {rate('i.currency', 'i.invoice_date')}), 2) AS billed_eur
FROM invoices i
JOIN subscriptions s ON s.subscription_id = i.subscription_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status = 'paid' AND i.invoice_date >= '2024-01-01' AND i.invoice_date < '2025-01-01';""",
  n="""SELECT ROUND(SUM(i.amount / f.units_per_eur), 2)
FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
JOIN fx_rates f ON f.currency = i.currency AND f.rate_date = i.invoice_date
WHERE NOT u.is_test AND i.status = 'paid' AND i.invoice_date >= '2024-01-01' AND i.invoice_date < '2025-01-01';""")
q('Euro billings Q1 2025', M, 'Revenue & FX',
  'What did we bill in Q1 2025 in EUR across all currencies (real users, paid, before refunds)? 2 decimals. Use a LATERAL join for the rate if you like.',
  'An inner LATERAL join returns nothing for a currency with no rate rows.',
  f"""-- Trap: JOIN LATERAL (... fx_rates ...) drops EUR invoices because EUR has no rate rows.
-- Use LEFT JOIN LATERAL ... ON TRUE and COALESCE the rate to 1.
SELECT ROUND(SUM(i.amount / COALESCE(fx.units_per_eur, 1)), 2) AS billed_eur
FROM invoices i
JOIN subscriptions s ON s.subscription_id = i.subscription_id
JOIN users u ON u.user_id = s.user_id
LEFT JOIN LATERAL (SELECT f.units_per_eur FROM fx_rates f WHERE f.currency = i.currency AND f.rate_date <= i.invoice_date
                   ORDER BY f.rate_date DESC LIMIT 1) fx ON TRUE
WHERE NOT u.is_test AND i.status = 'paid' AND i.invoice_date >= '2025-01-01' AND i.invoice_date < '2025-04-01';""",
  n="""SELECT ROUND(SUM(i.amount / fx.units_per_eur), 2)
FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
JOIN LATERAL (SELECT f.units_per_eur FROM fx_rates f WHERE f.currency = i.currency AND f.rate_date <= i.invoice_date
              ORDER BY f.rate_date DESC LIMIT 1) fx ON TRUE
WHERE NOT u.is_test AND i.status = 'paid' AND i.invoice_date >= '2025-01-01' AND i.invoice_date < '2025-04-01';""")
q('Revenue Q1 2025', H, 'Revenue & FX',
  'What was our revenue in Q1 2025? EUR, 2 decimals.',
  'Read the company definition of revenue in the notes word by word.',
  f"""-- Trap: revenue is paid invoices MINUS refunds (notes), not what we billed.
WITH {MONEY}
SELECT ROUND(SUM(eur), 2) AS revenue FROM money WHERE day >= '2025-01-01' AND day < '2025-04-01';""",
  n=f"""SELECT ROUND(SUM(i.amount / {rate('i.currency', 'i.invoice_date')}), 2)
FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status = 'paid' AND i.invoice_date >= '2025-01-01' AND i.invoice_date < '2025-04-01';""")
q('Net CZK 2024', M, 'Revenue & FX',
  'How many CZK did we keep from CZK invoices dated 2024: paid amounts minus everything refunded on them? Real users. One number in CZK.',
  'Some invoices have two partial refunds. Join, then look at how many rows one such invoice becomes.',
  """-- Trap: invoices JOIN refunds repeats an invoice once per refund, so its amount is summed twice.
-- Sum invoices and refunds separately.
WITH inv AS (
  SELECT i.invoice_id, i.amount
  FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test AND i.status = 'paid' AND i.currency = 'CZK' AND i.invoice_date >= '2024-01-01' AND i.invoice_date < '2025-01-01'
)
SELECT (SELECT SUM(amount) FROM inv)
     - (SELECT COALESCE(SUM(r.amount), 0) FROM refunds r WHERE r.invoice_id IN (SELECT invoice_id FROM inv)) AS net_czk;""",
  n="""SELECT SUM(i.amount) - COALESCE(SUM(r.amount), 0)
FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
LEFT JOIN refunds r ON r.invoice_id = i.invoice_id
WHERE NOT u.is_test AND i.status = 'paid' AND i.currency = 'CZK' AND i.invoice_date >= '2024-01-01' AND i.invoice_date < '2025-01-01';""")
q('Billed in pounds', E, 'Revenue & FX',
  'How much did we bill in GBP in 2025 (real users)? One number in GBP.',
  'Look at the status values before you sum.',
  """-- Trap: failed charges and void duplicates are not money.
SELECT SUM(i.amount) AS gbp
FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status = 'paid' AND i.currency = 'GBP' AND i.invoice_date >= '2025-01-01';""",
  n="""SELECT SUM(i.amount) FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.currency = 'GBP' AND i.invoice_date >= '2025-01-01';""")
q('TikTok click-through', M, 'Ad performance',
  'What is the overall click-through rate of TikTok Ads, in %, 2 decimals?',
  'Is the average of daily rates the same as the overall rate? Small days weigh as much as big days.',
  """-- Trap: AVG of daily CTRs gives every day the same weight. Overall CTR = total clicks / total impressions.
SELECT ROUND(100.0 * SUM(a.clicks) / SUM(a.impressions), 2) AS ctr_pct
FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
WHERE c.channel_id = 3;""",
  n="""SELECT ROUND(AVG(100.0 * a.clicks / a.impressions), 2) FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
WHERE c.channel_id = 3;""")
q('Conversion of clicks', M, 'Ad performance',
  'For Google Search campaigns in 2025: what fraction of impressions turned into clicks? Return <code>ctr</code> as a fraction with 4 decimals.',
  'Both columns are INT.',
  """-- Trap: INT / INT is integer division in PostgreSQL and returns 0.
SELECT ROUND(1.0 * SUM(a.clicks) / SUM(a.impressions), 4) AS ctr
FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
WHERE c.channel_id = 1 AND a.spend_date >= '2025-01-01';""",
  n="""SELECT ROUND(SUM(a.clicks) / SUM(a.impressions), 4) FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
WHERE c.channel_id = 1 AND a.spend_date >= '2025-01-01';""")
q('Brand CPC by day', M, 'Ad performance',
  'For GS Brand in June 2025, list every day with its cost per click. Return <code>spend_date</code> and <code>cpc_eur</code> (2 decimals; empty when there were no clicks), in date order.',
  'Look at the weekend rows.',
  """-- Trap: weekend rows have 0 clicks. spend / 0 raises "division by zero"; NULLIF(clicks, 0) turns it into NULL.
SELECT a.spend_date, ROUND(a.spend_eur / NULLIF(a.clicks, 0), 2) AS cpc_eur
FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
WHERE c.name = 'GS Brand' AND a.spend_date >= '2025-06-01'
ORDER BY a.spend_date;""",
  o=True,
  n="""SELECT a.spend_date, ROUND(a.spend_eur / a.clicks, 2) FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
WHERE c.name = 'GS Brand' AND a.spend_date >= '2025-06-01' ORDER BY a.spend_date;""")
q('Brand days live', E, 'Ad performance',
  'On how many days of 2025 did GS Brand actually spend money?',
  'Is every row in ad_spend a day with spend?',
  """-- Trap: the brand campaign writes a row with 0 spend on weekends. A row is not a live day.
SELECT COUNT(*) AS live_days
FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
WHERE c.name = 'GS Brand' AND a.spend_date >= '2025-01-01' AND a.spend_eur > 0;""",
  n="""SELECT COUNT(*) FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
WHERE c.name = 'GS Brand' AND a.spend_date >= '2025-01-01';""")
q('June traffic by channel', M, 'Funnel',
  'How many visits did each channel bring in June 2025? Return channel <code>name</code> and <code>visits</code>.',
  'Do all visits come from a campaign?',
  """-- Trap: organic visits have campaign_id NULL. Going visits → campaigns → channels drops them; visits has its own channel_id.
SELECT ch.name, COUNT(*) AS visits
FROM visits v JOIN channels ch ON ch.channel_id = v.channel_id
WHERE v.visit_ts >= '2025-06-01' AND v.visit_ts < '2025-07-01'
GROUP BY ch.name;""",
  n="""SELECT ch.name, COUNT(*) FROM visits v JOIN campaigns c ON c.campaign_id = v.campaign_id JOIN channels ch ON ch.channel_id = c.channel_id
WHERE v.visit_ts >= '2025-06-01' AND v.visit_ts < '2025-07-01' GROUP BY ch.name;""")
q('People from TikTok', E, 'Funnel',
  'How many people visited us from TikTok Ads in 2024?',
  'People or visits?',
  """-- Trap: one person can come several times. Count visitor_id once.
SELECT COUNT(DISTINCT visitor_id) AS people
FROM visits WHERE channel_id = 3 AND visit_ts >= '2024-01-01' AND visit_ts < '2025-01-01';""",
  n="SELECT COUNT(*) FROM visits WHERE channel_id = 3 AND visit_ts >= '2024-01-01' AND visit_ts < '2025-01-01';")
q('First touch done right', H, 'Attribution',
  'How many real website users does each channel own by first touch? Return channel <code>name</code> and <code>users</code>.',
  'GROUP BY visitor_id, channel_id with MIN(visit_ts) gives the first visit per visitor AND channel. Is that what you want?',
  f"""-- Trap: MIN(visit_ts) grouped by visitor and channel keeps one row for EVERY channel a person used,
-- so people are counted several times. Pick exactly one earliest visit per visitor.
WITH {FIRST_TOUCH}
SELECT ch.name, COUNT(*) AS users
FROM users u JOIN first_touch ft ON ft.visitor_id = u.visitor_id
JOIN channels ch ON ch.channel_id = ft.channel_id
WHERE NOT u.is_test
GROUP BY ch.name;""",
  n="""SELECT ch.name, COUNT(*) FROM (
  SELECT visitor_id, channel_id, MIN(visit_ts) AS first_ts FROM visits GROUP BY visitor_id, channel_id
) f JOIN users u ON u.visitor_id = f.visitor_id JOIN channels ch ON ch.channel_id = f.channel_id
WHERE NOT u.is_test GROUP BY ch.name;""")
q('Last touch before signup', H, 'Attribution',
  'Last-touch view: which channel gets the credit for real website signups? Return channel <code>name</code> and <code>users</code>.',
  'People keep visiting after they sign up. Which visits can still deserve credit?',
  """-- Trap: the latest visit overall is often a logged-in visit after signup. Only visits at or before signup_ts count.
WITH lt AS (
  SELECT DISTINCT ON (u.user_id) u.user_id, v.channel_id
  FROM users u JOIN visits v ON v.visitor_id = u.visitor_id AND v.visit_ts <= u.signup_ts
  WHERE NOT u.is_test
  ORDER BY u.user_id, v.visit_ts DESC
)
SELECT ch.name, COUNT(*) AS users FROM lt JOIN channels ch ON ch.channel_id = lt.channel_id GROUP BY ch.name;""",
  n="""WITH lt AS (
  SELECT DISTINCT ON (u.user_id) u.user_id, v.channel_id
  FROM users u JOIN visits v ON v.visitor_id = u.visitor_id WHERE NOT u.is_test ORDER BY u.user_id, v.visit_ts DESC
)
SELECT ch.name, COUNT(*) FROM lt JOIN channels ch ON ch.channel_id = lt.channel_id GROUP BY ch.name;""")
q('All signups by channel', M, 'Attribution',
  'Marketing wants every real 2025 signup split by first-touch channel, nobody left out. Return channel <code>name</code> and <code>signups</code>.',
  'Notes: who has no visitor_id, and which channel do they belong to?',
  f"""-- Trap: app-store installs have no visitor_id. An inner join to visits loses them; notes put them in App Store (channel 9).
WITH {FIRST_TOUCH}
SELECT ch.name, COUNT(*) AS signups
FROM users u
LEFT JOIN first_touch ft ON ft.visitor_id = u.visitor_id
JOIN channels ch ON ch.channel_id = COALESCE(ft.channel_id, 9)
WHERE NOT u.is_test AND u.signup_ts >= '2025-01-01'
GROUP BY ch.name;""",
  n=f"""WITH {FIRST_TOUCH}
SELECT ch.name, COUNT(*) FROM users u JOIN first_touch ft ON ft.visitor_id = u.visitor_id JOIN channels ch ON ch.channel_id = ft.channel_id
WHERE NOT u.is_test AND u.signup_ts >= '2025-01-01' GROUP BY ch.name;""")
q('Customers lost in 2025', H, 'Retention & churn',
  'How many paying customers did we lose in 2025 so far? A lost customer paid at some point, is not paying today, and their last subscription ended in 2025.',
  'A subscription ending is not always a customer leaving. What happens on a plan switch? On a trial cancel?',
  """-- Trap: a plan switch ends one subscription and starts another the same day. Trial cancels never paid.
-- Work per user: paid at least once, not paying today, latest end in 2025.
WITH per_user AS (
  SELECT s.user_id, MAX(s.ended_at) AS last_end,
         BOOL_OR(s.started_at <= DATE '2025-06-30' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-30')
                 AND COALESCE(s.trial_end, s.started_at) <= DATE '2025-06-30') AS paying_today,
         BOOL_OR(EXISTS (SELECT 1 FROM invoices i WHERE i.subscription_id = s.subscription_id AND i.status = 'paid')) AS ever_paid
  FROM subscriptions s JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test
  GROUP BY s.user_id
)
SELECT COUNT(*) AS lost FROM per_user
WHERE ever_paid AND NOT paying_today AND last_end >= '2025-01-01' AND last_end <= DATE '2025-06-30';""",
  n="""SELECT COUNT(DISTINCT s.user_id) FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.ended_at >= '2025-01-01' AND s.ended_at <= DATE '2025-06-30';""")
q('Invoices per customer', M, 'Revenue & FX',
  'On average, how many paid invoices does one paying customer have? Real users, 2 decimals.',
  'Customer = user. Some users have several subscriptions.',
  """-- Trap: averaging per subscription is not per customer.
SELECT ROUND(1.0 * COUNT(*) / COUNT(DISTINCT s.user_id), 2) AS invoices_per_customer
FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status = 'paid';""",
  n="""SELECT ROUND(1.0 * COUNT(*) / COUNT(DISTINCT i.subscription_id), 2)
FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status = 'paid';""")
q('First half of June', E, 'Funnel',
  'How many real users signed up from 1 to 15 June 2025, both days included?',
  "signup_ts is a TIMESTAMP. What time is '2025-06-15'?",
  """-- Trap: BETWEEN ... AND '2025-06-15' stops at midnight and loses signups during 15 June.
SELECT COUNT(*) AS signups FROM users
WHERE NOT is_test AND signup_ts >= '2025-06-01' AND signup_ts < '2025-06-16';""",
  n="SELECT COUNT(*) FROM users WHERE NOT is_test AND signup_ts BETWEEN '2025-06-01' AND '2025-06-15';")
q('May spend per campaign', M, 'Ad performance',
  'Show May 2025 spend for every campaign that was planned to run on at least one day in May (by its start and end dates), with 0 where nothing was spent. Return <code>name</code> and <code>spend_eur</code>.',
  'Where do you put the May filter on ad_spend: WHERE or ON?',
  """-- Trap: a WHERE condition on the right table of a LEFT JOIN removes the zero rows again. Put it in ON.
SELECT c.name, COALESCE(SUM(a.spend_eur), 0) AS spend_eur
FROM campaigns c
LEFT JOIN ad_spend a ON a.campaign_id = c.campaign_id AND a.spend_date >= '2025-05-01' AND a.spend_date < '2025-06-01'
WHERE c.start_date <= DATE '2025-05-31' AND (c.end_date IS NULL OR c.end_date >= DATE '2025-05-01')
GROUP BY c.campaign_id, c.name;""",
  n="""SELECT c.name, COALESCE(SUM(a.spend_eur), 0) FROM campaigns c LEFT JOIN ad_spend a ON a.campaign_id = c.campaign_id
WHERE c.start_date <= DATE '2025-05-31' AND (c.end_date IS NULL OR c.end_date >= DATE '2025-05-01')
  AND a.spend_date >= '2025-05-01' AND a.spend_date < '2025-06-01'
GROUP BY c.campaign_id, c.name;""")
q('Visitors who never joined', M, 'Funnel',
  'How many people visited us but never signed up?',
  'Try NOT IN. Then look at users.visitor_id for app-store installs.',
  """-- Trap: users.visitor_id is NULL for app installs. x NOT IN (..., NULL) is never TRUE, so NOT IN returns 0.
SELECT COUNT(DISTINCT v.visitor_id) AS never_joined
FROM visits v
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.visitor_id = v.visitor_id);""",
  n="SELECT COUNT(DISTINCT visitor_id) FROM visits WHERE visitor_id NOT IN (SELECT visitor_id FROM users);")
q('Users by country', E, 'Warm-up',
  'How many real users do we have per country? Return <code>country</code> and <code>users</code>.',
  'Look at the distinct values of country first.',
  """-- Trap: some rows store the code in lower case (cz, pl). Normalise before grouping.
SELECT UPPER(country) AS country, COUNT(*) AS users FROM users WHERE NOT is_test GROUP BY UPPER(country);""",
  n="SELECT country, COUNT(*) FROM users WHERE NOT is_test GROUP BY country;")
q('Best day for new customers', M, 'Funnel',
  'Which day of 2025 brought the most new paying customers (first ever paid invoice)? Return <code>day</code> and <code>customers</code>. Real users.',
  'What if several days are equally good?',
  """-- Trap: several days tie for first place. LIMIT 1 hides the others; RANK keeps them all.
WITH fp AS (
  SELECT s.user_id, MIN(i.invoice_date) AS first_paid
  FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id
  WHERE i.status = 'paid' GROUP BY s.user_id
),
d AS (
  SELECT fp.first_paid AS day, COUNT(*) AS customers
  FROM fp JOIN users u ON u.user_id = fp.user_id
  WHERE NOT u.is_test AND fp.first_paid >= '2025-01-01'
  GROUP BY fp.first_paid
)
SELECT day, customers FROM (SELECT d.*, RANK() OVER (ORDER BY customers DESC) AS r FROM d) x WHERE r = 1;""",
  n="""WITH fp AS (
  SELECT s.user_id, MIN(i.invoice_date) AS first_paid
  FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id
  WHERE i.status = 'paid' GROUP BY s.user_id
)
SELECT fp.first_paid, COUNT(*) AS n FROM fp JOIN users u ON u.user_id = fp.user_id
WHERE NOT u.is_test AND fp.first_paid >= '2025-01-01'
GROUP BY fp.first_paid ORDER BY n DESC LIMIT 1;""")
q('Workouts per subscriber', H, 'Product usage',
  'How many workouts did an average paying customer log in June 2025? Base = real users paying on 1 June 2025. 2 decimals.',
  'Customers who did not train at all are part of the average.',
  """-- Trap: an inner join to workouts drops customers with zero workouts and inflates the average.
WITH base AS (
  SELECT DISTINCT s.user_id FROM subscriptions s JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test AND s.started_at <= DATE '2025-06-01' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-01')
    AND COALESCE(s.trial_end, s.started_at) <= DATE '2025-06-01'
)
SELECT ROUND(1.0 * COUNT(w.workout_id) / COUNT(DISTINCT b.user_id), 2) AS workouts_per_customer
FROM base b LEFT JOIN workouts w ON w.user_id = b.user_id AND w.started_at >= '2025-06-01' AND w.started_at < '2025-07-01';""",
  n="""WITH base AS (
  SELECT DISTINCT s.user_id FROM subscriptions s JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test AND s.started_at <= DATE '2025-06-01' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-01')
    AND COALESCE(s.trial_end, s.started_at) <= DATE '2025-06-01'
)
SELECT ROUND(1.0 * COUNT(w.workout_id) / COUNT(DISTINCT b.user_id), 2)
FROM base b JOIN workouts w ON w.user_id = b.user_id AND w.started_at >= '2025-06-01' AND w.started_at < '2025-07-01';""")
q('Paying on 1 June', M, 'Subscriptions',
  'How many subscriptions of real users were paying on 1 June 2025?',
  'Active is not the same as paying.',
  """-- Trap: subscriptions still in their free trial are active but not paying.
SELECT COUNT(*) AS paying
FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.started_at <= DATE '2025-06-01' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-01')
  AND COALESCE(s.trial_end, s.started_at) <= DATE '2025-06-01';""",
  n="""SELECT COUNT(*) FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.started_at <= DATE '2025-06-01' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-01');""")
q('Refund rate 2024', M, 'Revenue & FX',
  'What share of paid invoices dated 2024 got refunded, fully or partly? Real users, %, 2 decimals.',
  'One invoice can have two refund rows.',
  """-- Trap: counting refund rows counts an invoice with two partial refunds twice.
SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE EXISTS (SELECT 1 FROM refunds r WHERE r.invoice_id = i.invoice_id)) / COUNT(*), 2) AS refunded_pct
FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status = 'paid' AND i.invoice_date >= '2024-01-01' AND i.invoice_date < '2025-01-01';""",
  n="""SELECT ROUND(100.0 * COUNT(r.refund_id) / COUNT(DISTINCT i.invoice_id), 2)
FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id JOIN users u ON u.user_id = s.user_id
LEFT JOIN refunds r ON r.invoice_id = i.invoice_id
WHERE NOT u.is_test AND i.status = 'paid' AND i.invoice_date >= '2024-01-01' AND i.invoice_date < '2025-01-01';""")
q('Last day of June', E, 'Product usage',
  'How many workouts were logged on 30 June 2025? Real users.',
  "started_at is a TIMESTAMP. What does started_at = '2025-06-30' compare with?",
  """-- Trap: '2025-06-30' means 30 June 00:00:00 exactly. Compare the date part or use a range.
SELECT COUNT(*) AS workouts FROM workouts w JOIN users u ON u.user_id = w.user_id
WHERE NOT u.is_test AND w.started_at >= '2025-06-30' AND w.started_at < '2025-07-01';""",
  n="""SELECT COUNT(*) FROM workouts w JOIN users u ON u.user_id = w.user_id
WHERE NOT u.is_test AND w.started_at = '2025-06-30';""")
q('Average session length', E, 'Product usage',
  'Product asks: what is the average workout length in minutes, counting only workouts where the length was recorded? And how many workouts have no recorded length? Return <code>avg_min</code> (2 decimals) and <code>missing</code>. Real users.',
  'COUNT(column) skips NULLs; COUNT(*) does not.',
  """-- Trap: COUNT(duration_min) never counts NULLs, so "missing" must come from COUNT(*) - COUNT(duration_min).
SELECT ROUND(AVG(w.duration_min), 2) AS avg_min, COUNT(*) - COUNT(w.duration_min) AS missing
FROM workouts w JOIN users u ON u.user_id = w.user_id WHERE NOT u.is_test;""",
  n="""SELECT ROUND(AVG(w.duration_min), 2), COUNT(w.duration_min) FILTER (WHERE w.duration_min IS NULL)
FROM workouts w JOIN users u ON u.user_id = w.user_id WHERE NOT u.is_test;""")
