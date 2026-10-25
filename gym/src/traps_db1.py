# MIND TRAPS for DB1 (appended as questions 101+).
# n = the naive query that falls into the trap; verify.py checks it gives a different result.
from questions_db1 import q, E, M, H

q('Expensive to stock', E, 'Select & filter',
  'Which products cost the shop more than 15,000 CZK to buy in? Return <code>name</code>.',
  'Who is paying here: the customer or the shop?',
  """-- Trap: "cost the shop to buy in" is cost_price, not the selling price.
SELECT name FROM products WHERE cost_price > 15000;""",
  n="SELECT name FROM products WHERE unit_price > 15000;")
q('April orders', E, 'Select & filter',
  'Return <code>order_id</code> of all orders placed from 1 April 2024 to 30 April 2024, both days included.',
  "order_date is a TIMESTAMP. What time of day is '2024-04-30'?",
  """-- Trap: BETWEEN '2024-04-01' AND '2024-04-30' stops at 30 April 00:00 and loses orders later that day.
SELECT order_id FROM orders WHERE order_date >= '2024-04-01' AND order_date < '2024-05-01';""",
  n="SELECT order_id FROM orders WHERE order_date BETWEEN '2024-04-01' AND '2024-04-30';")
q('Never recommended anyone', M, 'Subqueries & CTEs',
  'Return <code>customer_id</code> of customers who have not referred any other customer.',
  'Try NOT IN first and look at the row count. What does the subquery return besides numbers?',
  """-- Trap: referred_by contains NULLs. x NOT IN (..., NULL) is never TRUE, so NOT IN returns nothing.
SELECT c.customer_id FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM customers r WHERE r.referred_by = c.customer_id);""",
  n="SELECT customer_id FROM customers WHERE customer_id NOT IN (SELECT referred_by FROM customers);")
q('Card orders', E, 'Aggregation',
  'How many orders were paid by card? Return one number.',
  'One order can have several payment rows. And not every payment row is a successful payment.',
  """-- Trap 1: payments also holds failed and refunded rows. Trap 2: one order can have several rows.
SELECT COUNT(DISTINCT order_id) AS card_orders FROM payments WHERE method = 'card' AND status = 'paid';""",
  n="SELECT COUNT(*) FROM payments WHERE method = 'card';")
q('Orders and reviews', H, 'Joins',
  'For customers who wrote at least one review, return <code>customer_id</code>, <code>orders</code> (number of orders) and <code>reviews</code> (number of reviews).',
  'Join orders and reviews to customers in one query and check one customer by hand. Do the numbers look right?',
  """-- Trap: joining orders AND reviews to the same customer multiplies rows (orders x reviews).
-- Count each table separately, then join the counts.
SELECT r.customer_id, COALESCE(o.orders, 0) AS orders, r.reviews
FROM (SELECT customer_id, COUNT(*) AS reviews FROM reviews GROUP BY customer_id) r
LEFT JOIN (SELECT customer_id, COUNT(*) AS orders FROM orders GROUP BY customer_id) o ON o.customer_id = r.customer_id;""",
  n="""SELECT c.customer_id, COUNT(o.order_id) AS orders, COUNT(r.review_id) AS reviews
FROM customers c JOIN reviews r ON r.customer_id = c.customer_id LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id;""")
q('Bikes sold', M, 'Joins',
  'How many units from the Bikes category were sold in delivered orders? Return one number.',
  'Look at which category_id the bike products actually point to.',
  """-- Trap: no product sits directly in 'Bikes'. Products point to sub-categories (Road Bikes, E-bikes, ...),
-- whose parent is Bikes.
SELECT SUM(oi.quantity) AS units
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories sub ON p.category_id = sub.category_id
JOIN categories top ON sub.parent_id = top.category_id
WHERE o.status = 'delivered' AND top.name = 'Bikes';""",
  n="""SELECT SUM(oi.quantity) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id JOIN categories c ON p.category_id = c.category_id
WHERE o.status = 'delivered' AND c.name = 'Bikes';""")
q('Shimano revenue 2023', M, 'Joins',
  'What was the revenue from Shimano products in delivered orders placed in 2023? Rounded to 2.',
  "Is today's list price the price customers paid in 2023?",
  """-- Trap: products.unit_price is TODAY's price (Shimano went up 5% in 2024).
-- Revenue uses the price actually charged, order_items.unit_price, and the discount.
SELECT ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0), 2) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE p.brand = 'Shimano' AND o.status = 'delivered' AND o.order_date < '2024-01-01';""",
  n="""SELECT ROUND(SUM(oi.quantity * p.unit_price * (100 - oi.discount_pct) / 100.0), 2) FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id
WHERE p.brand = 'Shimano' AND o.status = 'delivered' AND o.order_date < '2024-01-01';""")
q('Spring campaign revenue', M, 'Aggregation',
  'What revenue did delivered orders with the code SPRING15 bring? Rounded to 2.',
  'Re-read the definition of line revenue in the schema notes.',
  """-- Trap: these orders were discounted. quantity * unit_price ignores the 15 % off.
SELECT ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0), 2) AS revenue
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.discount_code = 'SPRING15' AND o.status = 'delivered';""",
  n="""SELECT ROUND(SUM(oi.quantity * oi.unit_price), 2) FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.discount_code = 'SPRING15' AND o.status = 'delivered';""")
q('Discount as fraction', E, 'Expressions & sorting',
  'For order lines with a discount, return <code>order_id</code>, <code>product_id</code> and <code>discount</code> as a fraction (15 % → 0.15).',
  'discount_pct is an INT. What is 15 / 100 in integer maths?',
  """-- Trap: INT / INT is integer division in PostgreSQL: 15 / 100 = 0.
SELECT order_id, product_id, ROUND(discount_pct / 100.0, 2) AS discount FROM order_items WHERE discount_pct > 0;""",
  n="SELECT order_id, product_id, discount_pct / 100 FROM order_items WHERE discount_pct > 0;")
q('Products in 2024 orders', M, 'Joins',
  'For every product return <code>product_id</code> and <code>orders_2024</code> = number of 2024 orders it appears in, showing 0 for products not ordered in 2024. Sort by product_id.',
  'You used a LEFT JOIN, but are all products in the result? Where did you put the date filter?',
  """-- Trap: a WHERE condition on the right-hand table removes the NULL rows, turning LEFT JOIN into INNER JOIN.
-- Put the filter in the ON clause.
SELECT p.product_id, COUNT(DISTINCT o.order_id) AS orders_2024
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.product_id
LEFT JOIN orders o ON o.order_id = oi.order_id AND o.order_date >= '2024-01-01' AND o.order_date < '2025-01-01'
GROUP BY p.product_id
ORDER BY p.product_id;""", True,
  n="""SELECT p.product_id, COUNT(DISTINCT o.order_id) FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.product_id LEFT JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_date >= '2024-01-01' AND o.order_date < '2025-01-01' GROUP BY p.product_id ORDER BY p.product_id;""")
q('No Gmail', E, 'NULL & CASE',
  'Return <code>customer_id</code> of customers who do not have a gmail.com address.',
  'A customer without any email certainly has no gmail.com address. Does your query return them?',
  """-- Trap: NULL NOT LIKE '...' is NULL (not TRUE), so customers without email silently disappear.
SELECT customer_id FROM customers WHERE email IS NULL OR email NOT LIKE '%@gmail.com';""",
  n="SELECT customer_id FROM customers WHERE email NOT LIKE '%@gmail.com';")
q('Runner-up in 5 stars', M, 'Window functions',
  'Which product(s) have the second-highest number of 5-star reviews? Return <code>product_id</code> and <code>five_stars</code>.',
  'What if two products share second place?',
  """-- Trap: LIMIT 1 OFFSET 1 returns exactly one row even when two products tie for 2nd place.
SELECT product_id, five_stars
FROM (
  SELECT product_id, COUNT(*) AS five_stars, DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS rk
  FROM reviews WHERE rating = 5 GROUP BY product_id
) t
WHERE rk = 2;""",
  n="SELECT product_id, COUNT(*) FROM reviews WHERE rating = 5 GROUP BY product_id ORDER BY COUNT(*) DESC LIMIT 1 OFFSET 1;")
q('Money kept from cards 2024', M, 'Aggregation',
  'How much money did the shop actually keep from card payments dated in 2024? Return one number.',
  'Which payment statuses move money, and in which direction?',
  """-- Trap: failed rows moved no money and refunded rows moved money back. Kept = paid - refunded.
SELECT SUM(amount) FILTER (WHERE status = 'paid') - COALESCE(SUM(amount) FILTER (WHERE status = 'refunded'), 0) AS kept
FROM payments
WHERE method = 'card' AND payment_date >= '2024-01-01' AND payment_date < '2025-01-01';""",
  n="SELECT SUM(amount) FROM payments WHERE method = 'card' AND payment_date >= '2024-01-01' AND payment_date < '2025-01-01';")
q('Brand rating', M, 'Aggregation',
  'For each brand with reviews return <code>brand</code> and <code>avg_rating</code> (rounded to 2), where every review counts equally.',
  'Averaging product averages gives a product with 1 review the same weight as one with 20.',
  """-- Trap: AVG of per-product averages weights products, not reviews.
SELECT p.brand, ROUND(AVG(r.rating), 2) AS avg_rating
FROM reviews r JOIN products p ON r.product_id = p.product_id
GROUP BY p.brand;""",
  n="""SELECT brand, ROUND(AVG(a), 2) FROM (SELECT p.brand, AVG(r.rating) AS a FROM reviews r JOIN products p ON r.product_id = p.product_id
GROUP BY p.brand, p.product_id) t GROUP BY brand;""")
q('Sunday shoppers', M, 'Expressions & sorting',
  'How many orders were placed on a Sunday? Return one number.',
  "In EXTRACT(DOW ...) which number is Sunday? Check, don't assume.",
  """-- Trap: DOW counts Sunday = 0 ... Saturday = 6. (ISODOW: Monday = 1 ... Sunday = 7.)
SELECT COUNT(*) AS sunday_orders FROM orders WHERE EXTRACT(DOW FROM order_date) = 0;""",
  n="SELECT COUNT(*) FROM orders WHERE EXTRACT(DOW FROM order_date) = 7;")
q('Variety of customer 4', E, 'Aggregation',
  'How many different products has customer 4 ever ordered? Return one number.',
  'The same product can appear in many of their orders.',
  """-- Trap: COUNT(*) counts order lines; the question asks for distinct products.
SELECT COUNT(DISTINCT oi.product_id) AS products
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.customer_id = 4;""",
  n="SELECT COUNT(*) FROM orders o JOIN order_items oi ON o.order_id = oi.order_id WHERE o.customer_id = 4;")
q('Helmets sold', E, 'Joins',
  'How many helmets were sold in delivered orders? Return one number.',
  'A line with quantity 3 is three helmets.',
  """-- Trap: "how many sold" means units, i.e. SUM(quantity), not the number of order lines.
SELECT SUM(oi.quantity) AS helmets
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
WHERE c.name = 'Helmets' AND o.status = 'delivered';""",
  n="""SELECT COUNT(*) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id WHERE c.name = 'Helmets' AND o.status = 'delivered';""")
q('Top referrer', M, 'Joins',
  'Who referred the most new customers? Return <code>first_name</code> and <code>last_name</code> of that person.',
  'referred_by is filled in on the row of the NEW customer. Whose name do you want?',
  """-- Trap: grouping the referred customers' own names returns the wrong people.
-- The referrer is the row whose customer_id equals referred_by.
SELECT r.first_name, r.last_name
FROM customers c JOIN customers r ON c.referred_by = r.customer_id
GROUP BY r.customer_id, r.first_name, r.last_name
ORDER BY COUNT(*) DESC
LIMIT 1;""",
  n="""SELECT c.first_name, c.last_name FROM customers c JOIN customers r ON c.referred_by = r.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name ORDER BY COUNT(*) DESC, c.customer_id LIMIT 1;""")
q('Shipped orders', E, 'Select & filter',
  'How many orders have been shipped? Return one number.',
  'Was a delivered order ever shipped?',
  """-- Trap: status shows the CURRENT stage. Delivered and returned orders were shipped too.
SELECT COUNT(*) AS shipped FROM orders WHERE shipped_date IS NOT NULL;""",
  n="SELECT COUNT(*) FROM orders WHERE status = 'shipped';")
q('Accessories revenue 2024', M, 'Joins',
  'What was the revenue of the Accessories category from delivered orders placed in 2024? Rounded to 2.',
  'Same structure as the bike question: where do accessory products point?',
  """-- Trap: Accessories is a top-level category; products live in its sub-categories.
SELECT ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0), 2) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories sub ON p.category_id = sub.category_id
WHERE sub.parent_id = (SELECT category_id FROM categories WHERE name = 'Accessories')
  AND o.status = 'delivered' AND o.order_date >= '2024-01-01' AND o.order_date < '2025-01-01';""",
  n="""SELECT ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0), 2) FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id JOIN products p ON oi.product_id = p.product_id JOIN categories c ON p.category_id = c.category_id
WHERE c.name = 'Accessories' AND o.status = 'delivered' AND o.order_date >= '2024-01-01' AND o.order_date < '2025-01-01';""")
q('Paid orders total', H, 'Joins',
  'What is the total value (sum of line revenue) of delivered orders that have a successful payment? Rounded to 2.',
  'Some orders have a failed attempt AND a paid row. What happens to their lines when you join payments?',
  """-- Trap: joining payments to order_items repeats every line once per payment row. Use EXISTS instead.
SELECT ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0), 2) AS total
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'delivered'
  AND EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.order_id AND p.status = 'paid');""",
  n="""SELECT ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0), 2) FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id JOIN payments p ON p.order_id = o.order_id
WHERE o.status = 'delivered';""")
q('Average delivery delay', M, 'NULL & CASE',
  'What is the average number of days from order to delivery across ALL orders, counting orders that were never delivered as 0 days? Rounded to 2.',
  'AVG skips NULLs. Is that what the question asks?',
  """-- Trap: AVG ignores NULL, so undelivered orders would not count. The question wants them as 0.
SELECT ROUND(AVG(COALESCE(delivered_date - CAST(order_date AS DATE), 0)), 2) AS avg_days FROM orders;""",
  n="SELECT ROUND(AVG(delivered_date - CAST(order_date AS DATE)), 2) FROM orders;")
