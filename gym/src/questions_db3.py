# Questions for DB3 (Pulse fitness app). Fields: t title, d difficulty, g topic, p prompt, h hint, s solution, o order matters, n naive query (traps)
# Prompts read like requests from a manager. Company definitions live in the schema notes.
Q = []
def q(t, d, g, p, h, s, o=False, n=None):
    Q.append(dict(t=t, d=d, g=g, p=p, h=h, s=s.strip(), o=o, n=n.strip() if n else None))

E, M, H = 'Easy', 'Medium', 'Hard'
TODAY = "DATE '2025-06-30'"

def rate(cur, day):
    """EUR rate valid on a day: latest published rate on or before it; EUR has no rows."""
    return (f"COALESCE((SELECT f.units_per_eur FROM fx_rates f WHERE f.currency = {cur} AND f.rate_date <= {day} "
            f"ORDER BY f.rate_date DESC LIMIT 1), 1)")

# money events of real users in EUR: paid invoices (+) and refunds (-), each at the rate of its own date
MONEY = f"""money AS (
  SELECT s.user_id, i.invoice_id, i.invoice_date AS day, i.amount / {rate('i.currency', 'i.invoice_date')} AS eur
  FROM invoices i
  JOIN subscriptions s ON s.subscription_id = i.subscription_id
  JOIN users u ON u.user_id = s.user_id
  WHERE i.status = 'paid' AND NOT u.is_test
  UNION ALL
  SELECT s.user_id, i.invoice_id, r.refund_date, -r.amount / {rate('i.currency', 'r.refund_date')}
  FROM refunds r
  JOIN invoices i ON i.invoice_id = r.invoice_id
  JOIN subscriptions s ON s.subscription_id = i.subscription_id
  JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test
)"""

FIRST_TOUCH = """first_touch AS (
  SELECT DISTINCT ON (visitor_id) visitor_id, channel_id, campaign_id
  FROM visits
  ORDER BY visitor_id, visit_ts
)"""

# ---------------- Warm-up ----------------
g = 'Warm-up'
q('Paid channels', E, g,
  'Which of our marketing channels do we actually pay for? Return the channel <code>name</code>.',
  'channels has a column that says whether a channel is paid or organic.',
  "SELECT name FROM channels WHERE kind = 'paid';")
q('Launched in 2025', E, g,
  'Which campaigns did we launch in 2025? Return <code>name</code> and <code>start_date</code>, oldest launch first.',
  'Filter on start_date with a half-open range. Break ties by name.',
  "SELECT name, start_date FROM campaigns WHERE start_date >= '2025-01-01' AND start_date < '2026-01-01' ORDER BY start_date, name;", True)
q('Users by platform', E, g,
  'How many real users signed up on each platform? Return <code>platform</code> and <code>users</code>, biggest first.',
  'Notes: test accounts never count. GROUP BY platform.',
  "SELECT platform, COUNT(*) AS users FROM users WHERE NOT is_test GROUP BY platform ORDER BY users DESC;", True)
q('Ad budget 2024', E, g,
  'How much did we spend on ads in 2024? One number in EUR.',
  'ad_spend has one row per campaign per day.',
  "SELECT SUM(spend_eur) AS spend_2024 FROM ad_spend WHERE spend_date >= '2024-01-01' AND spend_date < '2025-01-01';")
q('Most expensive ad day', E, g,
  'Which campaign had the single most expensive day? Return campaign <code>name</code>, <code>spend_date</code> and <code>spend_eur</code>.',
  'Join ad_spend to campaigns, sort by spend, keep one row.',
  """SELECT c.name, a.spend_date, a.spend_eur
FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
ORDER BY a.spend_eur DESC
LIMIT 1;""")
q('Price list', E, g,
  'What can a new customer buy today? Return plan <code>name</code>, <code>billing_period</code> and <code>price_eur</code>, cheapest first.',
  'Some plans are retired.',
  "SELECT name, billing_period, price_eur FROM plans WHERE is_active ORDER BY price_eur, name;", True)
q('Refund types', E, g,
  'How many refunds were full and how many partial? Return <code>reason</code> and <code>refunds</code>.',
  'One GROUP BY.',
  "SELECT reason, COUNT(*) AS refunds FROM refunds GROUP BY reason;")
q('May workouts', E, g,
  'How many workouts did real users log in May 2025?',
  'started_at is a TIMESTAMP. Test accounts never count.',
  """SELECT COUNT(*) AS workouts
FROM workouts w JOIN users u ON u.user_id = w.user_id
WHERE NOT u.is_test AND w.started_at >= '2025-05-01' AND w.started_at < '2025-06-01';""")

# ---------------- Ad performance ----------------
g = 'Ad performance'
q('Spend by channel', E, g,
  'Where does our marketing money go? Total ad spend per channel over all time. Return channel <code>name</code> and <code>spend_eur</code>, biggest first.',
  'ad_spend → campaigns → channels.',
  """SELECT ch.name, SUM(a.spend_eur) AS spend_eur
FROM ad_spend a
JOIN campaigns c ON c.campaign_id = a.campaign_id
JOIN channels ch ON ch.channel_id = c.channel_id
GROUP BY ch.name
ORDER BY spend_eur DESC;""", True)
q('Click-through rate by channel', M, g,
  'What is the click-through rate of each paid channel over all time, in % rounded to 2 decimals? Return channel <code>name</code> and <code>ctr_pct</code>, best first.',
  'CTR = clicks / impressions. Sum first, divide once. Watch integer division.',
  """SELECT ch.name, ROUND(100.0 * SUM(a.clicks) / SUM(a.impressions), 2) AS ctr_pct
FROM ad_spend a
JOIN campaigns c ON c.campaign_id = a.campaign_id
JOIN channels ch ON ch.channel_id = c.channel_id
GROUP BY ch.name
ORDER BY ctr_pct DESC;""", True)
q('Cost per click 2025', M, g,
  'Which 2025 campaigns buy clicks most expensively? For each campaign with spend in 2025: <code>name</code> and <code>cpc_eur</code> (2025 spend / 2025 clicks, 2 decimals). Most expensive first.',
  'Filter the rows to 2025 before you sum. Ratio of sums.',
  """SELECT c.name, ROUND(SUM(a.spend_eur) / SUM(a.clicks), 2) AS cpc_eur
FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
WHERE a.spend_date >= '2025-01-01'
GROUP BY c.name
ORDER BY cpc_eur DESC, c.name;""", True)
q('Monthly spend 2025', E, g,
  'Show ad spend per month in 2025. Return <code>month</code> (first day of the month, as a date) and <code>spend_eur</code>, in calendar order.',
  "CAST(date_trunc('month', spend_date) AS DATE).",
  """SELECT CAST(date_trunc('month', spend_date) AS DATE) AS month, SUM(spend_eur) AS spend_eur
FROM ad_spend
WHERE spend_date >= '2025-01-01'
GROUP BY 1
ORDER BY 1;""", True)
q('Over budget days', M, g,
  'Which campaigns overspent their daily budget, and on how many days? Return campaign <code>name</code> and <code>days_over</code>, most first. Only campaigns that overspent at least once.',
  'Compare spend_eur with the campaign\'s daily_budget_eur. HAVING.',
  """SELECT c.name, COUNT(*) AS days_over
FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
WHERE a.spend_eur > c.daily_budget_eur
GROUP BY c.name
ORDER BY days_over DESC, c.name;""", True)
q('Weekend share', M, g,
  'What share of our 2024 ad spend went out on Saturdays and Sundays? In %, 2 decimals.',
  'Conditional sum: SUM(CASE WHEN ... THEN spend_eur ELSE 0 END). ISODOW gives 6 and 7 for the weekend.',
  """SELECT ROUND(100.0 * SUM(CASE WHEN EXTRACT(ISODOW FROM spend_date) IN (6, 7) THEN spend_eur ELSE 0 END) / SUM(spend_eur), 2) AS weekend_pct
FROM ad_spend
WHERE spend_date >= '2024-01-01' AND spend_date < '2025-01-01';""")
q('Cumulative spend 2025', M, g,
  'Finance wants the 2025 spend curve: <code>month</code>, <code>spend_eur</code> and <code>cumulative_eur</code> (spend from January up to and including that month).',
  'Aggregate per month first, then SUM(...) OVER (ORDER BY month).',
  """WITH m AS (
  SELECT CAST(date_trunc('month', spend_date) AS DATE) AS month, SUM(spend_eur) AS spend_eur
  FROM ad_spend WHERE spend_date >= '2025-01-01'
  GROUP BY 1
)
SELECT month, spend_eur, SUM(spend_eur) OVER (ORDER BY month) AS cumulative_eur
FROM m ORDER BY month;""", True)
q('Best day of each campaign', M, g,
  'For every campaign, find its day with the most clicks (if two days tie, take the earlier one). Return <code>name</code>, <code>spend_date</code> and <code>clicks</code>.',
  'ROW_NUMBER() OVER (PARTITION BY campaign ORDER BY clicks DESC, spend_date).',
  """WITH r AS (
  SELECT c.name, a.spend_date, a.clicks,
         ROW_NUMBER() OVER (PARTITION BY a.campaign_id ORDER BY a.clicks DESC, a.spend_date) AS rn
  FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
)
SELECT name, spend_date, clicks FROM r WHERE rn = 1;""")
q('Spend month over month', M, g,
  'How did total ad spend move month to month in 2024? Return <code>month</code>, <code>spend_eur</code> and <code>change_eur</code> (vs the previous month; empty for January).',
  'LAG over the monthly totals.',
  """WITH m AS (
  SELECT CAST(date_trunc('month', spend_date) AS DATE) AS month, SUM(spend_eur) AS spend_eur
  FROM ad_spend WHERE spend_date >= '2024-01-01' AND spend_date < '2025-01-01'
  GROUP BY 1
)
SELECT month, spend_eur, spend_eur - LAG(spend_eur) OVER (ORDER BY month) AS change_eur
FROM m ORDER BY month;""", True)
q('Campaign share of channel', M, g,
  'Inside each channel, how big is each campaign? Return channel <code>name</code>, campaign <code>name</code> and <code>share_pct</code> (campaign spend / channel spend, all time, %, 2 decimals). Only campaigns that spent something.',
  'SUM(spend) OVER (PARTITION BY channel) on top of the per-campaign totals.',
  """WITH c AS (
  SELECT ch.name AS channel, cp.name AS campaign, SUM(a.spend_eur) AS spend
  FROM ad_spend a
  JOIN campaigns cp ON cp.campaign_id = a.campaign_id
  JOIN channels ch ON ch.channel_id = cp.channel_id
  GROUP BY ch.name, cp.name
)
SELECT channel, campaign, ROUND(100 * spend / SUM(spend) OVER (PARTITION BY channel), 2) AS share_pct
FROM c;""")
q('Budget burn', H, g,
  'For campaigns that are finished (they have an end date in the past), how much of the planned budget did they actually spend? Planned = daily budget × number of calendar days from start to end, both included. Return <code>name</code>, <code>planned_eur</code>, <code>spent_eur</code>, <code>burn_pct</code> (2 decimals). Campaigns that never spent show 0.',
  'end_date - start_date + 1 days. LEFT JOIN the spend so a campaign with no rows stays.',
  """SELECT c.name,
       c.daily_budget_eur * (c.end_date - c.start_date + 1) AS planned_eur,
       COALESCE(SUM(a.spend_eur), 0) AS spent_eur,
       ROUND(100 * COALESCE(SUM(a.spend_eur), 0) / (c.daily_budget_eur * (c.end_date - c.start_date + 1)), 2) AS burn_pct
FROM campaigns c LEFT JOIN ad_spend a ON a.campaign_id = c.campaign_id
WHERE c.end_date < DATE '2025-06-30'
GROUP BY c.campaign_id, c.name, c.daily_budget_eur, c.start_date, c.end_date;""")

# ---------------- Funnel ----------------
g = 'Funnel'
q('Traffic Q1 2025', M, g,
  'How much traffic did each channel bring in Q1 2025? Return channel <code>name</code>, <code>visits</code> and <code>visitors</code> (distinct people).',
  'visitor_id identifies a person, visit_id a single visit.',
  """SELECT ch.name, COUNT(*) AS visits, COUNT(DISTINCT v.visitor_id) AS visitors
FROM visits v JOIN channels ch ON ch.channel_id = v.channel_id
WHERE v.visit_ts >= '2025-01-01' AND v.visit_ts < '2025-04-01'
GROUP BY ch.name;""")
q('Mobile share', M, g,
  'Is traffic going mobile? For each month of 2025 return <code>month</code> and <code>mobile_pct</code> (share of visits on mobile, %, 2 decimals).',
  'AVG(CASE WHEN device = ... THEN 1.0 ELSE 0 END) is a quick share.',
  """SELECT CAST(date_trunc('month', visit_ts) AS DATE) AS month,
       ROUND(100.0 * AVG(CASE WHEN device = 'mobile' THEN 1 ELSE 0 END), 2) AS mobile_pct
FROM visits
WHERE visit_ts >= '2025-01-01'
GROUP BY 1 ORDER BY 1;""", True)
q('Signups per month', E, g,
  'How many real users signed up each month in 2025? Return <code>month</code> and <code>signups</code>.',
  'Test accounts never count.',
  """SELECT CAST(date_trunc('month', signup_ts) AS DATE) AS month, COUNT(*) AS signups
FROM users
WHERE NOT is_test AND signup_ts >= '2025-01-01'
GROUP BY 1 ORDER BY 1;""", True)
q('Visitor conversion 2024', M, g,
  'Of all people whose first visit was in 2024, what share ever signed up (as a real user)? In %, 2 decimals.',
  'One row per visitor first (MIN(visit_ts)). LEFT JOIN users on visitor_id.',
  """WITH v AS (
  SELECT visitor_id FROM visits GROUP BY visitor_id
  HAVING MIN(visit_ts) >= '2024-01-01' AND MIN(visit_ts) < '2025-01-01'
)
SELECT ROUND(100.0 * COUNT(u.user_id) / COUNT(*), 2) AS signup_pct
FROM v LEFT JOIN users u ON u.visitor_id = v.visitor_id AND NOT u.is_test;""")
q('Hours to sign up', M, g,
  'How long do people think before signing up? Average hours from a person\'s first visit to their signup, for real users who came through the website. 2 decimals.',
  'EXTRACT(EPOCH FROM interval) / 3600 turns an interval into hours.',
  """WITH fv AS (SELECT visitor_id, MIN(visit_ts) AS first_ts FROM visits GROUP BY visitor_id)
SELECT ROUND(CAST(AVG(EXTRACT(EPOCH FROM u.signup_ts - fv.first_ts) / 3600) AS NUMERIC), 2) AS avg_hours
FROM users u JOIN fv ON fv.visitor_id = u.visitor_id
WHERE NOT u.is_test;""")
q('Visits before signup', M, g,
  'How many visits does it take to win a user? For real website users, count their visits up to the moment of signup and bucket them: <code>1</code>, <code>2</code>, <code>3</code>, <code>4+</code>. Return <code>visits_bucket</code> and <code>users</code>.',
  'Only visits with visit_ts <= signup_ts. CASE for the bucket, GROUP BY it.',
  """WITH c AS (
  SELECT u.user_id, COUNT(*) AS n
  FROM users u JOIN visits v ON v.visitor_id = u.visitor_id AND v.visit_ts <= u.signup_ts
  WHERE NOT u.is_test
  GROUP BY u.user_id
)
SELECT CASE WHEN n >= 4 THEN '4+' ELSE CAST(n AS VARCHAR) END AS visits_bucket, COUNT(*) AS users
FROM c GROUP BY 1;""")
q('H1 2025 funnel', H, g,
  'Funnel for real users who signed up in the first half of 2025: how many signed up, how many started a trial, how many became paying customers? Return <code>signed_up</code>, <code>trialed</code>, <code>paying</code> in one row.',
  'COUNT(DISTINCT ...) with conditions, or EXISTS per user inside CASE.',
  """SELECT COUNT(*) AS signed_up,
       COUNT(*) FILTER (WHERE EXISTS (SELECT 1 FROM subscriptions s WHERE s.user_id = u.user_id AND s.trial_end IS NOT NULL)) AS trialed,
       COUNT(*) FILTER (WHERE EXISTS (SELECT 1 FROM subscriptions s JOIN invoices i ON i.subscription_id = s.subscription_id
                                      WHERE s.user_id = u.user_id AND i.status = 'paid')) AS paying
FROM users u
WHERE NOT u.is_test AND u.signup_ts >= '2025-01-01' AND u.signup_ts < '2025-07-01';""")
q('Trial conversion by plan', H, g,
  'Which plan converts trials best? For trials that are already over, return plan <code>name</code>, <code>trials</code>, <code>converted</code> (trial followed by a paid invoice) and <code>conv_pct</code> (2 decimals). Real users only.',
  'A trial is over when trial_end <= today. Converted = EXISTS a paid invoice on that subscription.',
  """SELECT p.name, COUNT(*) AS trials,
       COUNT(*) FILTER (WHERE EXISTS (SELECT 1 FROM invoices i WHERE i.subscription_id = s.subscription_id AND i.status = 'paid')) AS converted,
       ROUND(100.0 * COUNT(*) FILTER (WHERE EXISTS (SELECT 1 FROM invoices i WHERE i.subscription_id = s.subscription_id AND i.status = 'paid')) / COUNT(*), 2) AS conv_pct
FROM subscriptions s
JOIN plans p ON p.plan_id = s.plan_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.trial_end <= DATE '2025-06-30'
GROUP BY p.name;""")
q('Days to first payment', H, g,
  'How many days does it usually take from signup to the first payment? Return the median in days for real paying customers (one number).',
  "PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ...). Signup is a timestamp, invoice_date a date: cast the signup to DATE.",
  """WITH fp AS (
  SELECT s.user_id, MIN(i.invoice_date) AS first_paid
  FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id
  WHERE i.status = 'paid' GROUP BY s.user_id
)
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fp.first_paid - CAST(u.signup_ts AS DATE)) AS median_days
FROM fp JOIN users u ON u.user_id = fp.user_id
WHERE NOT u.is_test;""")

# ---------------- Attribution ----------------
g = 'Attribution'
q('Where users first came from', M, g,
  'For real users who came through the website, which channel first brought them to us? Return channel <code>name</code> and <code>users</code>, biggest first.',
  'Notes: first touch = channel of the earliest visit of that visitor. DISTINCT ON or ROW_NUMBER.',
  f"""WITH {FIRST_TOUCH}
SELECT ch.name, COUNT(*) AS users
FROM users u
JOIN first_touch ft ON ft.visitor_id = u.visitor_id
JOIN channels ch ON ch.channel_id = ft.channel_id
WHERE NOT u.is_test
GROUP BY ch.name
ORDER BY users DESC;""", True)
q('Changed their mind', H, g,
  'For how many real website users is the last-touch channel different from the first-touch channel?',
  'Notes: last touch = latest visit at or before signup. Build both per user and compare.',
  f"""WITH {FIRST_TOUCH},
last_touch AS (
  SELECT DISTINCT ON (u.user_id) u.user_id, u.visitor_id, v.channel_id
  FROM users u JOIN visits v ON v.visitor_id = u.visitor_id AND v.visit_ts <= u.signup_ts
  WHERE NOT u.is_test
  ORDER BY u.user_id, v.visit_ts DESC
)
SELECT COUNT(*) AS switched
FROM last_touch lt JOIN first_touch ft ON ft.visitor_id = lt.visitor_id
WHERE lt.channel_id <> ft.channel_id;""")
q('Paid share of signups', M, g,
  'How dependent are we on paid ads? Of real users who signed up in 2025, what share had a paid channel as first touch? App Store installs count as organic. %, 2 decimals.',
  'LEFT JOIN the first touch so App Store users (no visitor) stay in the denominator.',
  f"""WITH {FIRST_TOUCH}
SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE ch.kind = 'paid') / COUNT(*), 2) AS paid_pct
FROM users u
LEFT JOIN first_touch ft ON ft.visitor_id = u.visitor_id
LEFT JOIN channels ch ON ch.channel_id = ft.channel_id
WHERE NOT u.is_test AND u.signup_ts >= '2025-01-01';""")
q('Top campaigns by signups', M, g,
  'Which five campaigns brought the most real 2025 signups by first touch? Return campaign <code>name</code> and <code>signups</code>, most first (ties by name).',
  'first_touch.campaign_id is NULL for organic first visits.',
  f"""WITH {FIRST_TOUCH}
SELECT c.name, COUNT(*) AS signups
FROM users u
JOIN first_touch ft ON ft.visitor_id = u.visitor_id
JOIN campaigns c ON c.campaign_id = ft.campaign_id
WHERE NOT u.is_test AND u.signup_ts >= '2025-01-01'
GROUP BY c.name
ORDER BY signups DESC, c.name
LIMIT 5;""", True)
q('CAC by channel 2024', H, g,
  'What did a new paying customer cost us per paid channel in 2024? CAC = 2024 spend of the channel / real customers whose first paid invoice was in 2024 and whose first touch was that channel. Return channel <code>name</code>, <code>spend_eur</code>, <code>customers</code>, <code>cac_eur</code> (2 decimals). Cheapest first.',
  'Build two small aggregates (spend per channel, customers per channel) and join them.',
  f"""WITH {FIRST_TOUCH},
fp AS (
  SELECT s.user_id, MIN(i.invoice_date) AS first_paid
  FROM invoices i JOIN subscriptions s ON s.subscription_id = i.subscription_id
  WHERE i.status = 'paid' GROUP BY s.user_id
),
cust AS (
  SELECT ft.channel_id, COUNT(*) AS customers
  FROM fp JOIN users u ON u.user_id = fp.user_id
  JOIN first_touch ft ON ft.visitor_id = u.visitor_id
  WHERE NOT u.is_test AND fp.first_paid >= '2024-01-01' AND fp.first_paid < '2025-01-01'
  GROUP BY ft.channel_id
),
sp AS (
  SELECT c.channel_id, SUM(a.spend_eur) AS spend_eur
  FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
  WHERE a.spend_date >= '2024-01-01' AND a.spend_date < '2025-01-01'
  GROUP BY c.channel_id
)
SELECT ch.name, sp.spend_eur, cust.customers, ROUND(sp.spend_eur / cust.customers, 2) AS cac_eur
FROM sp JOIN cust ON cust.channel_id = sp.channel_id
JOIN channels ch ON ch.channel_id = sp.channel_id
ORDER BY cac_eur;""", True)
q('Cost per signup Q1 2025', H, g,
  'For Q1 2025, what did one signup cost per campaign, by last touch? Spend = campaign spend in Q1; signups = real users who signed up in Q1 whose last touch was that campaign. Return <code>name</code>, <code>signups</code>, <code>cost_per_signup</code> (2 decimals) for campaigns with at least one such signup. Cheapest first.',
  'Last touch = latest visit at or before signup_ts. Its campaign_id can be NULL (organic).',
  """WITH last_touch AS (
  SELECT DISTINCT ON (u.user_id) u.user_id, v.campaign_id
  FROM users u JOIN visits v ON v.visitor_id = u.visitor_id AND v.visit_ts <= u.signup_ts
  WHERE NOT u.is_test AND u.signup_ts >= '2025-01-01' AND u.signup_ts < '2025-04-01'
  ORDER BY u.user_id, v.visit_ts DESC
),
su AS (SELECT campaign_id, COUNT(*) AS signups FROM last_touch WHERE campaign_id IS NOT NULL GROUP BY campaign_id),
sp AS (
  SELECT campaign_id, SUM(spend_eur) AS spend FROM ad_spend
  WHERE spend_date >= '2025-01-01' AND spend_date < '2025-04-01' GROUP BY campaign_id
)
SELECT c.name, su.signups, ROUND(sp.spend / su.signups, 2) AS cost_per_signup
FROM su JOIN sp ON sp.campaign_id = su.campaign_id
JOIN campaigns c ON c.campaign_id = su.campaign_id
ORDER BY cost_per_signup, c.name;""", True)
q('Channel ROAS 2024', H, g,
  'Which paid channel paid back in 2024? ROAS = net revenue of 2024 from customers first-touched by the channel (money dated in 2024) / channel spend in 2024. Return channel <code>name</code> and <code>roas</code> (2 decimals), best first.',
  'Reuse the money definition from the notes: paid invoices minus refunds, EUR at each date\'s rate, real users only.',
  f"""WITH {MONEY}, {FIRST_TOUCH},
rev AS (
  SELECT ft.channel_id, SUM(m.eur) AS revenue
  FROM money m JOIN users u ON u.user_id = m.user_id
  JOIN first_touch ft ON ft.visitor_id = u.visitor_id
  WHERE m.day >= '2024-01-01' AND m.day < '2025-01-01'
  GROUP BY ft.channel_id
),
sp AS (
  SELECT c.channel_id, SUM(a.spend_eur) AS spend
  FROM ad_spend a JOIN campaigns c ON c.campaign_id = a.campaign_id
  WHERE a.spend_date >= '2024-01-01' AND a.spend_date < '2025-01-01'
  GROUP BY c.channel_id
)
SELECT ch.name, ROUND(rev.revenue / sp.spend, 2) AS roas
FROM sp JOIN rev ON rev.channel_id = sp.channel_id
JOIN channels ch ON ch.channel_id = sp.channel_id
ORDER BY roas DESC;""", True)

# ---------------- Subscriptions ----------------
g = 'Subscriptions'
q('Active base by plan', M, g,
  'What does our subscriber base look like today? Number of active subscriptions of real users per plan (trials included). Return plan <code>name</code> and <code>subscriptions</code>, biggest first.',
  'Notes: active on D means started_at <= D and (ended_at IS NULL OR ended_at > D). D = today from the notes.',
  """SELECT p.name, COUNT(*) AS subscriptions
FROM subscriptions s
JOIN plans p ON p.plan_id = s.plan_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.started_at <= DATE '2025-06-30' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-30')
GROUP BY p.name
ORDER BY subscriptions DESC, p.name;""", True)
q('In trial today', E, g,
  'How many real users are in a free trial today?',
  'Notes: in trial on D when D < trial_end. They must also still be active.',
  """SELECT COUNT(DISTINCT s.user_id) AS in_trial
FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.trial_end > DATE '2025-06-30'
  AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-30');""")
q('Why people leave', M, g,
  'Why did subscriptions end in 2025 (up to today)? Return <code>reason</code> (show <code>unknown</code> when none was given) and <code>subscriptions</code>, most first. Real users only.',
  'COALESCE(cancel_reason, ...). ended_at in the future has not happened yet.',
  """SELECT COALESCE(s.cancel_reason, 'unknown') AS reason, COUNT(*) AS subscriptions
FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.ended_at >= '2025-01-01' AND s.ended_at <= DATE '2025-06-30'
GROUP BY 1
ORDER BY subscriptions DESC, reason;""", True)
q('Paid lifetime', H, g,
  'How long do people pay before they leave? For subscriptions of real users that ended (up to today) after at least one paid invoice, not counting plan switches, return <code>billing_period</code> and <code>avg_paid_days</code> (from the first paid day to ended_at, 1 decimal).',
  'Paid days start at COALESCE(trial_end, started_at). Use EXISTS for "at least one paid invoice".',
  """SELECT p.billing_period, ROUND(AVG(s.ended_at - COALESCE(s.trial_end, s.started_at)), 1) AS avg_paid_days
FROM subscriptions s
JOIN plans p ON p.plan_id = s.plan_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.ended_at <= DATE '2025-06-30' AND s.cancel_reason IS DISTINCT FROM 'switched plan'
  AND EXISTS (SELECT 1 FROM invoices i WHERE i.subscription_id = s.subscription_id AND i.status = 'paid')
GROUP BY p.billing_period;""")
q('More than one subscription', E, g,
  'How many real users have had more than one subscription?',
  'GROUP BY user_id HAVING COUNT(*) > 1, then count the groups.',
  """SELECT COUNT(*) AS users FROM (
  SELECT s.user_id FROM subscriptions s JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test GROUP BY s.user_id HAVING COUNT(*) > 1
) x;""")
q('Plan switches', H, g,
  'Which plan moves do real users make? A switch is a subscription that ended with <code>switched plan</code> followed by a new subscription of the same user starting on that same day. Return <code>from_plan</code>, <code>to_plan</code> and <code>switches</code>, most first.',
  'Self-join subscriptions: old.user_id = new.user_id AND new.started_at = old.ended_at.',
  """SELECT po.name AS from_plan, pn.name AS to_plan, COUNT(*) AS switches
FROM subscriptions o
JOIN subscriptions nw ON nw.user_id = o.user_id AND nw.started_at = o.ended_at AND nw.subscription_id <> o.subscription_id
JOIN plans po ON po.plan_id = o.plan_id
JOIN plans pn ON pn.plan_id = nw.plan_id
JOIN users u ON u.user_id = o.user_id
WHERE NOT u.is_test AND o.cancel_reason = 'switched plan'
GROUP BY po.name, pn.name
ORDER BY switches DESC, from_plan, to_plan;""", True)
q('MRR curve 2025', H, g,
  'Show MRR on the first day of every month of 2025 (Jan–Jun). Return <code>month</code> and <code>mrr_eur</code> (2 decimals).',
  'generate_series for the six dates, then join subscriptions that are paying on that date (notes). Annual plans count price / 12.',
  """SELECT CAST(d AS DATE) AS month,
       ROUND(SUM(CASE WHEN p.billing_period = 'year' THEN p.price_eur / 12 ELSE p.price_eur END), 2) AS mrr_eur
FROM generate_series(DATE '2025-01-01', DATE '2025-06-01', INTERVAL '1 month') d
JOIN subscriptions s ON s.started_at <= d AND (s.ended_at IS NULL OR s.ended_at > d) AND COALESCE(s.trial_end, s.started_at) <= d
JOIN plans p ON p.plan_id = s.plan_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test
GROUP BY d ORDER BY d;""", True)
q('Paid starts and endings', H, g,
  'Per month of 2025: how many subscriptions started paying (first paid invoice that month) and how many paying subscriptions ended (ended_at in that month, after at least one payment)? Real users only. Return <code>month</code>, <code>started</code>, <code>ended</code>. Show 0 instead of empty.',
  'Two monthly counts, joined on month. Build the months with generate_series so nothing is missing.',
  """WITH fp AS (
  SELECT i.subscription_id, MIN(i.invoice_date) AS first_paid
  FROM invoices i WHERE i.status = 'paid' GROUP BY i.subscription_id
),
real_fp AS (
  SELECT fp.* FROM fp JOIN subscriptions s ON s.subscription_id = fp.subscription_id JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test
),
months AS (SELECT CAST(m AS DATE) AS month FROM generate_series(DATE '2025-01-01', DATE '2025-06-01', INTERVAL '1 month') m)
SELECT m.month,
       (SELECT COUNT(*) FROM real_fp f WHERE CAST(date_trunc('month', f.first_paid) AS DATE) = m.month) AS started,
       (SELECT COUNT(*) FROM real_fp f JOIN subscriptions s ON s.subscription_id = f.subscription_id
        WHERE s.ended_at <= DATE '2025-06-30' AND CAST(date_trunc('month', s.ended_at) AS DATE) = m.month) AS ended
FROM months m ORDER BY m.month;""", True)
q('Annual vs monthly mix', M, g,
  'Of all subscriptions that started paying in 2025 (first paid invoice in 2025), what share is annual? Real users, %, 2 decimals.',
  'First paid invoice per subscription, then a conditional share by billing_period.',
  """WITH fp AS (
  SELECT i.subscription_id, MIN(i.invoice_date) AS first_paid
  FROM invoices i WHERE i.status = 'paid' GROUP BY i.subscription_id
)
SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE p.billing_period = 'year') / COUNT(*), 2) AS annual_pct
FROM fp
JOIN subscriptions s ON s.subscription_id = fp.subscription_id
JOIN plans p ON p.plan_id = s.plan_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND fp.first_paid >= '2025-01-01';""")

# ---------------- Revenue & FX ----------------
g = 'Revenue & FX'
q('Billed per currency', E, g,
  'How many invoices did we actually collect per currency, and how much (in that currency)? Return <code>currency</code>, <code>invoices</code>, <code>amount</code>. Real users only.',
  'Only status paid is money.',
  """SELECT i.currency, COUNT(*) AS invoices, SUM(i.amount) AS amount
FROM invoices i
JOIN subscriptions s ON s.subscription_id = i.subscription_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status = 'paid'
GROUP BY i.currency;""")
q('CZK rate by month', E, g,
  'Finance asks for the average CZK rate (CZK per 1 EUR) per month of 2025. Return <code>month</code> and <code>avg_rate</code> (4 decimals).',
  'fx_rates only, filter on currency.',
  """SELECT CAST(date_trunc('month', rate_date) AS DATE) AS month, ROUND(AVG(units_per_eur), 4) AS avg_rate
FROM fx_rates
WHERE currency = 'CZK' AND rate_date >= '2025-01-01'
GROUP BY 1 ORDER BY 1;""", True)
q('Billings 2025 in EUR', H, g,
  'What did we bill per month of 2025 in EUR, before refunds? Real users, paid invoices, converted with the rate valid on the invoice date (notes). Return <code>month</code> and <code>billed_eur</code> (2 decimals).',
  'Latest rate on or before the invoice date: correlated subquery with ORDER BY rate_date DESC LIMIT 1. EUR has no rate rows.',
  f"""SELECT CAST(date_trunc('month', i.invoice_date) AS DATE) AS month,
       ROUND(SUM(i.amount / {rate('i.currency', 'i.invoice_date')}), 2) AS billed_eur
FROM invoices i
JOIN subscriptions s ON s.subscription_id = i.subscription_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status = 'paid' AND i.invoice_date >= '2025-01-01'
GROUP BY 1 ORDER BY 1;""", True)
q('Net revenue 2024', H, g,
  'What was our net revenue in 2024 in EUR? Use the company definition from the notes. 2 decimals.',
  'Paid invoices dated 2024 plus refunds dated 2024 (as negatives), each at its own date\'s rate.',
  f"""WITH {MONEY}
SELECT ROUND(SUM(eur), 2) AS net_revenue_2024 FROM money
WHERE day >= '2024-01-01' AND day < '2025-01-01';""")
q('Top customers', M, g,
  'Who are our five most valuable customers so far? Return <code>user_id</code> and <code>net_eur</code> (lifetime net revenue, 2 decimals), highest first.',
  'Same money definition, grouped by user.',
  f"""WITH {MONEY}
SELECT user_id, ROUND(SUM(eur), 2) AS net_eur FROM money
GROUP BY user_id ORDER BY net_eur DESC LIMIT 5;""", True)
q('ARPPU 2024', H, g,
  'Average net revenue per paying customer in 2024: net revenue of 2024 divided by the number of real users with at least one paid invoice in 2024. EUR, 2 decimals.',
  'Numerator and denominator come from different filters; compute both in one query with two CTEs or FILTER.',
  f"""WITH {MONEY}
SELECT ROUND(SUM(eur) / COUNT(DISTINCT user_id) FILTER (WHERE eur > 0), 2) AS arppu
FROM money WHERE day >= '2024-01-01' AND day < '2025-01-01';""")
q('Revenue by plan', M, g,
  'Which plans make the money? Net revenue over all time per plan in EUR. Return plan <code>name</code> and <code>net_eur</code> (2 decimals), biggest first.',
  'Join money (by invoice) back to subscription and plan.',
  f"""WITH {MONEY}
SELECT p.name, ROUND(SUM(m.eur), 2) AS net_eur
FROM money m
JOIN invoices i ON i.invoice_id = m.invoice_id
JOIN subscriptions s ON s.subscription_id = i.subscription_id
JOIN plans p ON p.plan_id = s.plan_id
GROUP BY p.name ORDER BY net_eur DESC;""", True)
q('Revenue running total', H, g,
  'Show net revenue per month of 2025 with a running total. Return <code>month</code>, <code>net_eur</code>, <code>ytd_eur</code> (both 2 decimals).',
  'Aggregate the money events by month, then SUM() OVER (ORDER BY month).',
  f"""WITH {MONEY},
m AS (SELECT CAST(date_trunc('month', day) AS DATE) AS month, SUM(eur) AS net FROM money WHERE day >= '2025-01-01' GROUP BY 1)
SELECT month, ROUND(net, 2) AS net_eur, ROUND(SUM(net) OVER (ORDER BY month), 2) AS ytd_eur
FROM m ORDER BY month;""", True)
q('Weekend invoices', M, g,
  'Data check before a currency report: how many paid non-EUR invoices (all accounts, test ones included) are dated on a day with no published exchange rate?',
  'NOT EXISTS a rate row with the same currency and date.',
  """SELECT COUNT(*) AS invoices
FROM invoices i
WHERE i.status = 'paid' AND i.currency <> 'EUR'
  AND NOT EXISTS (SELECT 1 FROM fx_rates f WHERE f.currency = i.currency AND f.rate_date = i.invoice_date);""")
q('Refunded money by month', M, g,
  'How much did we pay back per month of 2025, in EUR at each refund date\'s rate? Real users. Return <code>month</code> and <code>refunded_eur</code> (2 decimals).',
  'refunds → invoices for the currency. Use the refund_date for both the month and the rate.',
  f"""SELECT CAST(date_trunc('month', r.refund_date) AS DATE) AS month,
       ROUND(SUM(r.amount / {rate('i.currency', 'r.refund_date')}), 2) AS refunded_eur
FROM refunds r
JOIN invoices i ON i.invoice_id = r.invoice_id
JOIN subscriptions s ON s.subscription_id = i.subscription_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND r.refund_date >= '2025-01-01'
GROUP BY 1 ORDER BY 1;""", True)
q('Failed payment rate', M, g,
  'How often do charges fail? Share of charge attempts on real users in 2025 that failed (failed / (paid + failed)), %, 2 decimals. Void invoices are not attempts.',
  'Conditional count over invoices with status in (paid, failed).',
  """SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE i.status = 'failed') / COUNT(*), 2) AS failed_pct
FROM invoices i
JOIN subscriptions s ON s.subscription_id = i.subscription_id
JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND i.status IN ('paid', 'failed') AND i.invoice_date >= '2025-01-01';""")

# ---------------- Retention & churn ----------------
g = 'Retention & churn'
q('2024 cohorts today', H, g,
  'How sticky are our 2024 signups? For each signup month of 2024 (real users): <code>cohort</code>, <code>signups</code>, <code>paying_today</code> (users paying today, notes), <code>pct</code> (2 decimals).',
  'One row per user with a flag "paying today" (EXISTS), then group by signup month.',
  """WITH c AS (
  SELECT u.user_id, CAST(date_trunc('month', u.signup_ts) AS DATE) AS cohort,
         EXISTS (SELECT 1 FROM subscriptions s WHERE s.user_id = u.user_id
                 AND s.started_at <= DATE '2025-06-30' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-30')
                 AND COALESCE(s.trial_end, s.started_at) <= DATE '2025-06-30') AS paying
  FROM users u
  WHERE NOT u.is_test AND u.signup_ts < '2025-01-01'
)
SELECT cohort, COUNT(*) AS signups, COUNT(*) FILTER (WHERE paying) AS paying_today,
       ROUND(100.0 * COUNT(*) FILTER (WHERE paying) / COUNT(*), 2) AS pct
FROM c GROUP BY cohort ORDER BY cohort;""", True)
q('Involuntary churn', M, g,
  'How much of our churn is just failed cards? Of paying subscriptions of real users that ended up to today, what share ended with <code>payment failed</code>? %, 2 decimals. Subscriptions that ended inside the trial or by switching plan do not count as churn.',
  'Paying subscriptions = have a paid invoice. Exclude switched plan.',
  """SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE s.cancel_reason = 'payment failed') / COUNT(*), 2) AS involuntary_pct
FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.ended_at <= DATE '2025-06-30'
  AND s.cancel_reason IS DISTINCT FROM 'switched plan'
  AND EXISTS (SELECT 1 FROM invoices i WHERE i.subscription_id = s.subscription_id AND i.status = 'paid');""")
q('90-day retention', H, g,
  'Of monthly-plan subscriptions of real users that started paying in Q1 2024, what share were still active 90 days after their first paid day? %, 2 decimals.',
  'First paid day = COALESCE(trial_end, started_at). Still active on that day + 90 means ended_at IS NULL or later than it.',
  """WITH s AS (
  SELECT s.*, COALESCE(s.trial_end, s.started_at) AS paid_from
  FROM subscriptions s
  JOIN plans p ON p.plan_id = s.plan_id
  JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test AND p.billing_period = 'month'
    AND EXISTS (SELECT 1 FROM invoices i WHERE i.subscription_id = s.subscription_id AND i.status = 'paid')
)
SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE ended_at IS NULL OR ended_at > paid_from + 90) / COUNT(*), 2) AS retained_pct
FROM s WHERE paid_from >= '2024-01-01' AND paid_from < '2024-04-01';""")
q('Came back', H, g,
  'Who came back after leaving? Count real users who had a subscription end (not a plan switch) and later started another one, and the average gap in days between the end and the restart. Return <code>users</code> and <code>avg_gap_days</code> (1 decimal).',
  'Self-join: later.started_at > earlier.ended_at. Take the first restart per end, or the next subscription with LEAD.',
  """WITH x AS (
  SELECT s.user_id, s.ended_at, s.cancel_reason,
         LEAD(s.started_at) OVER (PARTITION BY s.user_id ORDER BY s.started_at) AS next_start
  FROM subscriptions s JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test
)
SELECT COUNT(DISTINCT user_id) AS users, ROUND(AVG(next_start - ended_at), 1) AS avg_gap_days
FROM x WHERE next_start > ended_at AND cancel_reason IS DISTINCT FROM 'switched plan';""")
q('Quick quitters', M, g,
  'Trials that were cancelled: on which day of the trial do people quit? Return <code>trial_day</code> (ended_at - started_at) and <code>trials</code>, in day order. Real users.',
  'A trial cancel ends on or before trial_end and never got a paid invoice.',
  """SELECT s.ended_at - s.started_at AS trial_day, COUNT(*) AS trials
FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test AND s.trial_end IS NOT NULL AND s.ended_at <= s.trial_end
GROUP BY 1 ORDER BY 1;""", True)
q('Monthly logo churn 2025', H, g,
  'Churn rate per month of 2025: users paying on the first day of the month who are not paying on the first day of the next month, divided by users paying on the first day. Real users. Return <code>month</code> and <code>churn_pct</code> (2 decimals), January to May.',
  'Build "paying users on date D" once (a CTE over generate_series), then compare D with D + 1 month.',
  """WITH d AS (SELECT CAST(x AS DATE) AS day FROM generate_series(DATE '2025-01-01', DATE '2025-06-01', INTERVAL '1 month') x),
paying AS (
  SELECT DISTINCT d.day, s.user_id
  FROM d JOIN subscriptions s ON s.started_at <= d.day AND (s.ended_at IS NULL OR s.ended_at > d.day)
                              AND COALESCE(s.trial_end, s.started_at) <= d.day
  JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test
)
SELECT a.day AS month,
       ROUND(100.0 * COUNT(*) FILTER (WHERE b.user_id IS NULL) / COUNT(*), 2) AS churn_pct
FROM paying a
LEFT JOIN paying b ON b.user_id = a.user_id AND b.day = CAST(a.day + INTERVAL '1 month' AS DATE)
WHERE a.day < '2025-06-01'
GROUP BY a.day ORDER BY a.day;""", True)

# ---------------- Product usage ----------------
g = 'Product usage'
q('Weekly active users', M, g,
  'How many real users trained each week in Q2 2025? Return <code>week</code> (Monday, as a date) and <code>active_users</code>.',
  "date_trunc('week', ...) starts on Monday. COUNT(DISTINCT user_id).",
  """SELECT CAST(date_trunc('week', w.started_at) AS DATE) AS week, COUNT(DISTINCT w.user_id) AS active_users
FROM workouts w JOIN users u ON u.user_id = w.user_id
WHERE NOT u.is_test
GROUP BY 1 ORDER BY 1;""", True)
q('Minutes by workout kind', M, g,
  'What do people train most, measured in time? Return <code>kind</code>, <code>minutes</code> and <code>share_pct</code> (of all minutes, 2 decimals). Real users, biggest first.',
  'SUM(duration_min) per kind, and the share with SUM(SUM(...)) OVER ().',
  """SELECT w.kind, SUM(w.duration_min) AS minutes,
       ROUND(100.0 * SUM(w.duration_min) / SUM(SUM(w.duration_min)) OVER (), 2) AS share_pct
FROM workouts w JOIN users u ON u.user_id = w.user_id
WHERE NOT u.is_test
GROUP BY w.kind ORDER BY minutes DESC;""", True)
q('Workouts per active user', M, g,
  'How intensive are our active users? Per month (Apr, May, Jun 2025): <code>month</code>, <code>active_users</code>, <code>workouts_per_user</code> (2 decimals). Real users.',
  'COUNT(*) / COUNT(DISTINCT user_id) per month. Mind integer division.',
  """SELECT CAST(date_trunc('month', w.started_at) AS DATE) AS month, COUNT(DISTINCT w.user_id) AS active_users,
       ROUND(1.0 * COUNT(*) / COUNT(DISTINCT w.user_id), 2) AS workouts_per_user
FROM workouts w JOIN users u ON u.user_id = w.user_id
WHERE NOT u.is_test
GROUP BY 1 ORDER BY 1;""", True)
q('Every month', M, g,
  'How many real users trained in each of April, May and June 2025?',
  'Count distinct months per user and keep users with 3.',
  """SELECT COUNT(*) AS users FROM (
  SELECT w.user_id FROM workouts w JOIN users u ON u.user_id = w.user_id
  WHERE NOT u.is_test
  GROUP BY w.user_id HAVING COUNT(DISTINCT date_trunc('month', w.started_at)) = 3
) x;""")
q('Paying but not training', H, g,
  'Who is at risk? How many real users were paying on 1 June 2025 and still paying today, yet logged no workout in June 2025?',
  'Paying on two dates (notes). NOT EXISTS a workout in June.',
  """SELECT COUNT(DISTINCT s.user_id) AS at_risk
FROM subscriptions s JOIN users u ON u.user_id = s.user_id
WHERE NOT u.is_test
  AND COALESCE(s.trial_end, s.started_at) <= DATE '2025-06-01' AND s.started_at <= DATE '2025-06-01'
  AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-30')
  AND NOT EXISTS (SELECT 1 FROM workouts w WHERE w.user_id = s.user_id AND w.started_at >= '2025-06-01' AND w.started_at < '2025-07-01');""")
q('Busiest hour', E, g,
  'At what hour of the day do real users start most workouts? Return <code>hour</code> and <code>workouts</code> for the top hour.',
  'EXTRACT(HOUR FROM started_at).',
  """SELECT EXTRACT(HOUR FROM w.started_at) AS hour, COUNT(*) AS workouts
FROM workouts w JOIN users u ON u.user_id = w.user_id
WHERE NOT u.is_test
GROUP BY 1 ORDER BY workouts DESC LIMIT 1;""")
q('Longest streak', H, g,
  'Who has the longest streak of consecutive training days in Q2 2025? Return the top 5 real users: <code>user_id</code>, <code>streak_days</code>, longest first (ties by user_id).',
  'Gaps and islands: one row per user per day, then day - ROW_NUMBER() days is constant inside a streak.',
  """WITH d AS (
  SELECT DISTINCT w.user_id, CAST(w.started_at AS DATE) AS day
  FROM workouts w JOIN users u ON u.user_id = w.user_id WHERE NOT u.is_test
),
g AS (SELECT user_id, day, day - CAST(ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day) AS INT) AS grp FROM d)
SELECT user_id, MAX(n) AS streak_days FROM (SELECT user_id, grp, COUNT(*) AS n FROM g GROUP BY user_id, grp) x
GROUP BY user_id ORDER BY streak_days DESC, user_id LIMIT 5;""", True)
q('Usage quartiles', H, g,
  'Split real users who trained in Q2 2025 into 4 equal groups by number of workouts (4 = most). Return <code>quartile</code>, <code>users</code>, <code>min_workouts</code>, <code>max_workouts</code>.',
  'NTILE(4) OVER (ORDER BY workouts), then group by the tile.',
  """WITH c AS (
  SELECT w.user_id, COUNT(*) AS workouts
  FROM workouts w JOIN users u ON u.user_id = w.user_id WHERE NOT u.is_test
  GROUP BY w.user_id
),
t AS (SELECT workouts, NTILE(4) OVER (ORDER BY workouts, user_id) AS quartile FROM c)
SELECT quartile, COUNT(*) AS users, MIN(workouts) AS min_workouts, MAX(workouts) AS max_workouts
FROM t GROUP BY quartile ORDER BY quartile;""", True)
q('Do trainers stay?', H, g,
  'Do people who train more stay longer? For real users paying on 1 April 2025, split them into <code>trained</code> (at least 4 workouts in April) and <code>light</code> (the rest, including none). Return <code>segment</code>, <code>users</code>, <code>still_paying_pct</code> (paying today, 2 decimals).',
  'One row per user with two flags. LEFT JOIN or a scalar count for April workouts, so zero-workout users stay.',
  """WITH base AS (
  SELECT DISTINCT s.user_id FROM subscriptions s JOIN users u ON u.user_id = s.user_id
  WHERE NOT u.is_test AND s.started_at <= DATE '2025-04-01' AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-04-01')
    AND COALESCE(s.trial_end, s.started_at) <= DATE '2025-04-01'
),
f AS (
  SELECT b.user_id,
         (SELECT COUNT(*) FROM workouts w WHERE w.user_id = b.user_id AND w.started_at >= '2025-04-01' AND w.started_at < '2025-05-01') AS apr,
         EXISTS (SELECT 1 FROM subscriptions s WHERE s.user_id = b.user_id AND s.started_at <= DATE '2025-06-30'
                 AND (s.ended_at IS NULL OR s.ended_at > DATE '2025-06-30') AND COALESCE(s.trial_end, s.started_at) <= DATE '2025-06-30') AS stays
  FROM base b
)
SELECT CASE WHEN apr >= 4 THEN 'trained' ELSE 'light' END AS segment, COUNT(*) AS users,
       ROUND(100.0 * COUNT(*) FILTER (WHERE stays) / COUNT(*), 2) AS still_paying_pct
FROM f GROUP BY 1;""")
