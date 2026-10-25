# Questions for DB1 (Velo e-shop). Fields: t title, d difficulty, g topic, p prompt, h hint, s solution, o order matters
Q = []
def q(t, d, g, p, h, s, o=False, n=None):
    Q.append(dict(t=t, d=d, g=g, p=p, h=h, s=s.strip(), o=o, n=n))

E, M, H = 'Easy', 'Medium', 'Hard'
REV = "quantity * unit_price * (100 - discount_pct) / 100.0"

# ---------------- 1. SELECT & WHERE ----------------
g = 'Select & filter'
q('Product catalogue', E, g,
  'List every product with its <code>product_id</code>, <code>name</code>, <code>brand</code> and <code>unit_price</code>. Sort by <code>product_id</code>.',
  'No filter needed. Pick four columns and add ORDER BY.',
  "SELECT product_id, name, brand, unit_price FROM products ORDER BY product_id;", True)
q('Customers in Brno', E, g,
  'Return <code>customer_id</code>, <code>first_name</code> and <code>last_name</code> of all customers who live in Brno.',
  "Text values go in single quotes: city = 'Brno'.",
  "SELECT customer_id, first_name, last_name FROM customers WHERE city = 'Brno';")
q('Premium products', E, g,
  'Return <code>name</code> and <code>unit_price</code> of products that cost more than 20,000 CZK. Sort from most to least expensive.',
  'WHERE unit_price > 20000, then ORDER BY ... DESC.',
  "SELECT name, unit_price FROM products WHERE unit_price > 20000 ORDER BY unit_price DESC, name;", True)
q('Missing emails', E, g,
  'Return <code>customer_id</code>, <code>first_name</code> and <code>last_name</code> of customers who have no email address.',
  'A missing value is NULL. You can\'t compare NULL with =.',
  "SELECT customer_id, first_name, last_name FROM customers WHERE email IS NULL;")
q('Discontinued products', E, g,
  'Return <code>product_id</code> and <code>name</code> of products that are no longer active.',
  'is_active is a BOOLEAN. Use WHERE NOT is_active or WHERE is_active = FALSE.',
  "SELECT product_id, name FROM products WHERE NOT is_active;")
q('March 2024 orders', E, g,
  'Return <code>order_id</code> and <code>order_date</code> of all orders placed in March 2024.',
  'order_date is a TIMESTAMP. Use a half-open range: >= first day of March AND < first day of April.',
  "SELECT order_id, order_date FROM orders WHERE order_date >= '2024-03-01' AND order_date < '2024-04-01';")
q('Slovak customers', E, g,
  'Return <code>customer_id</code>, <code>first_name</code>, <code>last_name</code> and <code>city</code> of customers from Slovakia (country code <code>SK</code>).',
  "Filter on the country column, not on city.",
  "SELECT customer_id, first_name, last_name, city FROM customers WHERE country = 'SK';")
q('Helmets by name', E, g,
  'Return <code>product_id</code> and <code>name</code> of products whose name contains the word "helmet" in any letter case.',
  'ILIKE is the case-insensitive LIKE in PostgreSQL. % matches any text.',
  "SELECT product_id, name FROM products WHERE name ILIKE '%helmet%';")
q('Failed orders', E, g,
  'Return <code>order_id</code>, <code>customer_id</code> and <code>status</code> of orders that were cancelled or returned.',
  "status IN ('cancelled', 'returned')",
  "SELECT order_id, customer_id, status FROM orders WHERE status IN ('cancelled', 'returned');")
q('Bulk lines', E, g,
  'Return all columns of order lines where at least 3 units were bought.',
  '"At least 3" includes 3, so use >=.',
  "SELECT * FROM order_items WHERE quantity >= 3;")
q('2024 sign-ups', E, g,
  'Return <code>customer_id</code> and <code>signup_date</code> of customers who signed up in 2024. Sort by <code>signup_date</code>, then <code>customer_id</code>.',
  "signup_date is a DATE. A range >= '2024-01-01' AND < '2025-01-01' works, so does EXTRACT(YEAR FROM ...).",
  "SELECT customer_id, signup_date FROM customers WHERE signup_date >= '2024-01-01' AND signup_date < '2025-01-01' ORDER BY signup_date, customer_id;", True)
q('Mid-range price', E, g,
  'Return <code>name</code> and <code>unit_price</code> of products priced from 500 to 1,500 CZK, both limits included.',
  'BETWEEN includes both ends.',
  "SELECT name, unit_price FROM products WHERE unit_price BETWEEN 500 AND 1500;")
q('Orders with a code', E, g,
  'Return <code>order_id</code> and <code>discount_code</code> of orders where a discount code was used.',
  'Used = the column is not empty (NOT NULL).',
  "SELECT order_id, discount_code FROM orders WHERE discount_code IS NOT NULL;")
q('Top 5 prices', E, g,
  'Return <code>name</code> and <code>unit_price</code> of the 5 most expensive products, most expensive first.',
  'ORDER BY ... DESC, then LIMIT 5.',
  "SELECT name, unit_price FROM products ORDER BY unit_price DESC, name LIMIT 5;", True)

# ---------------- 2. DISTINCT, expressions, sorting ----------------
g = 'Expressions & sorting'
q('Customer cities', E, g,
  'Return the list of cities where at least one customer lives, each city once, alphabetically.',
  'DISTINCT removes duplicate rows.',
  "SELECT DISTINCT city FROM customers ORDER BY city;", True)
q('Product margin', E, g,
  'For each product return <code>name</code> and <code>margin</code> = unit_price minus cost_price. Sort by margin from highest, then by name.',
  'You can calculate in SELECT and give the result an alias with AS.',
  "SELECT name, unit_price - cost_price AS margin FROM products ORDER BY margin DESC, name;", True)
q('Margin percent', M, g,
  'For each product return <code>name</code> and <code>margin_pct</code> = (unit_price − cost_price) / unit_price × 100, rounded to 1 decimal place.',
  'ROUND(value, 1). Both columns are NUMERIC, so no integer-division trap here.',
  "SELECT name, ROUND((unit_price - cost_price) / unit_price * 100, 1) AS margin_pct FROM products;")
q('VIP full names', E, g,
  'Return one column <code>full_name</code> ("first_name last_name", with one space) for VIP customers. Sort by last_name, then first_name.',
  "Concatenate with || or CONCAT(first_name, ' ', last_name).",
  "SELECT first_name || ' ' || last_name AS full_name FROM customers WHERE is_vip ORDER BY last_name, first_name;", True)
q('Email domains', M, g,
  'Return <code>customer_id</code> and <code>domain</code> = the part of the email after "@", for customers who have an email.',
  "SPLIT_PART(email, '@', 2) returns the 2nd piece after splitting on '@'.",
  "SELECT customer_id, SPLIT_PART(email, '@', 2) AS domain FROM customers WHERE email IS NOT NULL;")
q('Weekend orders', M, g,
  'Return <code>order_id</code> and <code>order_date</code> of orders placed on a Saturday or Sunday.',
  'EXTRACT(ISODOW FROM order_date) returns 1 (Monday) to 7 (Sunday).',
  "SELECT order_id, order_date FROM orders WHERE EXTRACT(ISODOW FROM order_date) IN (6, 7);")
q('Second page', M, g,
  'Products are shown 5 per page, sorted by price from highest (ties by name A–Z). Return <code>name</code> and <code>unit_price</code> of the products on page 2.',
  'LIMIT 5 OFFSET 5 skips the first page.',
  "SELECT name, unit_price FROM products ORDER BY unit_price DESC, name LIMIT 5 OFFSET 5;", True)

# ---------------- 3. NULL, CASE, COALESCE ----------------
g = 'NULL & CASE'
q('Email or placeholder', E, g,
  "Return <code>customer_id</code> and <code>contact</code> = the email, or the text 'no email' if it is missing.",
  'COALESCE returns the first value that is not NULL.',
  "SELECT customer_id, COALESCE(email, 'no email') AS contact FROM customers;")
q('Price bands', E, g,
  "Return <code>name</code>, <code>unit_price</code> and <code>band</code>: 'budget' below 1,000; 'mid' from 1,000 up to (not incl.) 10,000; 'premium' from 10,000.",
  'CASE checks conditions top to bottom and stops at the first true one. Make sure bands do not overlap.',
  """SELECT name, unit_price,
       CASE WHEN unit_price < 1000 THEN 'budget'
            WHEN unit_price < 10000 THEN 'mid'
            ELSE 'premium' END AS band
FROM products;""")
q('Email coverage', M, g,
  'Return one row with two columns: <code>with_email</code> and <code>without_email</code> = number of customers in each group.',
  'COUNT(email) skips NULLs; COUNT(*) does not. Or use COUNT(*) FILTER (WHERE ...).',
  "SELECT COUNT(email) AS with_email, COUNT(*) - COUNT(email) AS without_email FROM customers;")
q('Delivery time', M, g,
  'For delivered orders return <code>order_id</code> and <code>delivery_days</code> = days between the order date and the delivery date.',
  'order_date is a TIMESTAMP, delivered_date a DATE. CAST(order_date AS DATE) first; DATE − DATE gives whole days.',
  "SELECT order_id, delivered_date - CAST(order_date AS DATE) AS delivery_days FROM orders WHERE status = 'delivered';")
q('Waiting to ship', E, g,
  'Return <code>order_id</code> and <code>status</code> of orders that have not shipped yet and are not cancelled.',
  "shipped_date IS NULL AND status <> 'cancelled'.",
  "SELECT order_id, status FROM orders WHERE shipped_date IS NULL AND status <> 'cancelled';")
q('Referred customers', E, g,
  'How many customers were referred by another customer? Return one number <code>referred</code>.',
  'COUNT(column) counts only non-NULL values.',
  "SELECT COUNT(referred_by) AS referred FROM customers;")
q('Safe ratio', M, g,
  'For each product return <code>name</code> and <code>markup</code> = unit_price / (unit_price − cost_price), rounded to 2. Write it so that a zero margin would give NULL instead of an error.',
  'NULLIF(x, 0) turns 0 into NULL, and dividing by NULL gives NULL.',
  "SELECT name, ROUND(unit_price / NULLIF(unit_price - cost_price, 0), 2) AS markup FROM products;")

# ---------------- 4. Aggregation ----------------
g = 'Aggregation'
q('Customer count', E, g,
  'How many customers does the shop have? Return one number.',
  'COUNT(*).',
  "SELECT COUNT(*) AS customers FROM customers;")
q('Orders by status', E, g,
  'Return each order <code>status</code> and the number of orders with it.',
  '"For each status" = GROUP BY status.',
  "SELECT status, COUNT(*) AS orders FROM orders GROUP BY status;")
q('Average price', E, g,
  'Return the average product price, rounded to 2 decimals.',
  'ROUND(AVG(...), 2).',
  "SELECT ROUND(AVG(unit_price), 2) AS avg_price FROM products;")
q('Price range per category', E, g,
  'For each <code>category_id</code> that has products, return the cheapest and the most expensive price.',
  'MIN and MAX in the same query, GROUP BY category_id.',
  "SELECT category_id, MIN(unit_price) AS min_price, MAX(unit_price) AS max_price FROM products GROUP BY category_id;")
q('Products per brand', E, g,
  'Return each <code>brand</code> and its number of products. Sort by the count from highest, then by brand A–Z.',
  'GROUP BY brand; ORDER BY can use the alias.',
  "SELECT brand, COUNT(*) AS products FROM products GROUP BY brand ORDER BY products DESC, brand;", True)
q('Units sold per product', E, g,
  'For every product that was ever ordered, return <code>product_id</code> and <code>units</code> = total quantity across all order lines. Sort by product_id.',
  'The amount is in the quantity column, so SUM it, do not COUNT rows.',
  "SELECT product_id, SUM(quantity) AS units FROM order_items GROUP BY product_id ORDER BY product_id;", True)
q('Orders per year', E, g,
  'Return each <code>year</code> and the number of orders placed in it.',
  'EXTRACT(YEAR FROM order_date) in SELECT and in GROUP BY.',
  "SELECT EXTRACT(YEAR FROM order_date) AS year, COUNT(*) AS orders FROM orders GROUP BY EXTRACT(YEAR FROM order_date);")
q('Customers per country', E, g,
  'Return each <code>country</code> and its number of customers. Sort by count from highest, then country A–Z.',
  'GROUP BY country.',
  "SELECT country, COUNT(*) AS customers FROM customers GROUP BY country ORDER BY customers DESC, country;", True)
q('Well-reviewed products', M, g,
  'For products with at least 3 reviews, return <code>product_id</code> and <code>avg_rating</code> rounded to 2 decimals.',
  'Filter on a group (count of reviews) goes in HAVING.',
  "SELECT product_id, ROUND(AVG(rating), 2) AS avg_rating FROM reviews GROUP BY product_id HAVING COUNT(*) >= 3;")
q('Paid by method', E, g,
  "For each payment <code>method</code> return the total <code>amount</code> of successful payments (status 'paid').",
  'Row filter (status) goes in WHERE, before grouping.',
  "SELECT method, SUM(amount) AS paid FROM payments WHERE status = 'paid' GROUP BY method;")
q('Active buyers 2024', E, g,
  'How many different customers placed at least one order in 2024?',
  'One customer can have many orders, so COUNT(DISTINCT customer_id).',
  "SELECT COUNT(DISTINCT customer_id) AS buyers FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';")
q('Cancellation rate', M, g,
  'Return the percentage of all orders that were cancelled, rounded to 2 decimals.',
  'COUNT returns integers. Make one side NUMERIC (CAST or 100.0) or you get 0.',
  "SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'cancelled') / COUNT(*), 2) AS cancel_pct FROM orders;")
q('Busy days', M, g,
  'Return each calendar day (<code>order_day</code>, a DATE) with more than 2 orders, and the number of orders. Sort by day.',
  'Group by CAST(order_date AS DATE), not by the timestamp.',
  "SELECT CAST(order_date AS DATE) AS order_day, COUNT(*) AS orders FROM orders GROUP BY CAST(order_date AS DATE) HAVING COUNT(*) > 2 ORDER BY order_day;", True)

# ---------------- 5. GROUP BY + HAVING ----------------
g = 'Group & having'
q('Loyal customers', E, g,
  'Return <code>customer_id</code> and <code>orders</code> for customers who placed at least 20 orders.',
  'GROUP BY customer_id HAVING COUNT(*) >= 20.',
  "SELECT customer_id, COUNT(*) AS orders FROM orders GROUP BY customer_id HAVING COUNT(*) >= 20;")
q('Popular products', M, g,
  'Return <code>product_id</code> and <code>orders</code> = number of different orders it appears in, for products in more than 30 orders.',
  'One row in order_items = one product in one order.',
  "SELECT product_id, COUNT(DISTINCT order_id) AS orders FROM order_items GROUP BY product_id HAVING COUNT(DISTINCT order_id) > 30;")
q('Strong months 2024', M, g,
  "Return each <code>month</code> of 2024 (1–12) where successful payments (status 'paid', by payment_date) added up to more than 400,000 CZK, with the total. Sort by month.",
  'WHERE for the year and status, GROUP BY month, HAVING for the total.',
  "SELECT EXTRACT(MONTH FROM payment_date) AS month, SUM(amount) AS paid FROM payments WHERE status = 'paid' AND payment_date >= '2024-01-01' AND payment_date < '2025-01-01' GROUP BY EXTRACT(MONTH FROM payment_date) HAVING SUM(amount) > 400000 ORDER BY month;", True)
q('Never unhappy', H, g,
  "Return <code>customer_id</code> of customers who have at least 3 orders and none of their orders was cancelled or returned.",
  "Count all orders and count bad orders in the same group: COUNT(*) FILTER (WHERE status IN (...)) = 0.",
  "SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) >= 3 AND COUNT(*) FILTER (WHERE status IN ('cancelled', 'returned')) = 0;")
q('Channel mix', M, g,
  'For each <code>channel</code> return the number of orders and the share of all orders in percent, rounded to 1 decimal.',
  'Total of all orders = a subquery (SELECT COUNT(*) FROM orders), or SUM(COUNT(*)) OVER ().',
  "SELECT channel, COUNT(*) AS orders, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 1) AS share_pct FROM orders GROUP BY channel;")
q('Rating distribution', E, g,
  'Return each <code>rating</code> (1–5) and how many reviews gave it. Sort by rating.',
  'GROUP BY rating.',
  "SELECT rating, COUNT(*) AS reviews FROM reviews GROUP BY rating ORDER BY rating;", True)
q('Codes by year', M, g,
  'For each year and each discount code, return how many orders used it. Leave out orders without a code. Sort by year, then code.',
  'Group by two columns.',
  "SELECT EXTRACT(YEAR FROM order_date) AS year, discount_code, COUNT(*) AS orders FROM orders WHERE discount_code IS NOT NULL GROUP BY EXTRACT(YEAR FROM order_date), discount_code ORDER BY year, discount_code;", True)

# ---------------- 6. JOINs ----------------
g = 'Joins'
q('Who ordered', E, g,
  'For orders placed in January 2024 return <code>order_id</code>, <code>order_date</code>, <code>first_name</code> and <code>last_name</code> of the customer. Sort by order_id.',
  'JOIN customers ON orders.customer_id = customers.customer_id.',
  "SELECT o.order_id, o.order_date, c.first_name, c.last_name FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_date >= '2024-01-01' AND o.order_date < '2024-02-01' ORDER BY o.order_id;", True)
q('Product with category', E, g,
  'Return product <code>name</code> and its <code>category</code> name for every product.',
  'Both tables have a column called name, so give the outputs aliases.',
  "SELECT p.name, c.name AS category FROM products p JOIN categories c ON p.category_id = c.category_id;")
q('Category tree', M, g,
  'For every sub-category (one that has a parent) return <code>category</code> and <code>parent</code> names.',
  'Join categories to itself: one copy is the child, the other the parent.',
  "SELECT c.name AS category, p.name AS parent FROM categories c JOIN categories p ON c.parent_id = p.category_id;")
q('Never ordered', M, g,
  'Return <code>customer_id</code>, <code>first_name</code> and <code>last_name</code> of customers who never placed an order.',
  'LEFT JOIN orders, then keep rows where the orders side IS NULL.',
  "SELECT c.customer_id, c.first_name, c.last_name FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_id IS NULL;")
q('Unsold products', M, g,
  'Return <code>product_id</code> and <code>name</code> of products that never appeared in any order.',
  'Same pattern: LEFT JOIN + IS NULL, or NOT EXISTS.',
  "SELECT p.product_id, p.name FROM products p LEFT JOIN order_items oi ON p.product_id = oi.product_id WHERE oi.product_id IS NULL;")
q('Order value', M, g,
  f'For every order return <code>order_id</code> and <code>order_value</code> = sum of line revenue, rounded to 2. Line revenue = <code>{REV}</code>. Sort by order_id.',
  'Watch the integer trap: discount_pct is INT, so divide by 100.0, not 100.',
  f"SELECT order_id, ROUND(SUM({REV}), 2) AS order_value FROM order_items GROUP BY order_id ORDER BY order_id;", True)
q('Revenue by category', M, g,
  'Return category <code>name</code> and <code>revenue</code> (rounded to 2) from delivered orders only. Sort by revenue from highest.',
  'Three tables: order_items → orders (status) and order_items → products → categories.',
  """SELECT c.name, ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0), 2) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
WHERE o.status = 'delivered'
GROUP BY c.name
ORDER BY revenue DESC;""", True)
q('Top spenders', M, g,
  'Return <code>customer_id</code>, <code>first_name</code>, <code>last_name</code> and <code>spent</code> (rounded to 2) of the 5 customers with the highest revenue from delivered orders. Highest first.',
  'Join order_items → orders → customers, group by the customer, ORDER BY ... DESC LIMIT 5.',
  f"""SELECT c.customer_id, c.first_name, c.last_name,
       ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0), 2) AS spent
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'delivered'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY spent DESC
LIMIT 5;""", True)
q('Who referred whom', M, g,
  'For every referred customer return <code>customer</code> and <code>referred_by</code> as full names ("first last").',
  'Self-join customers: e.referred_by = r.customer_id.',
  "SELECT c.first_name || ' ' || c.last_name AS customer, r.first_name || ' ' || r.last_name AS referred_by FROM customers c JOIN customers r ON c.referred_by = r.customer_id;")
q('Referral counts', M, g,
  'For every customer return <code>customer_id</code> and <code>referrals</code> = how many people they referred (0 if none). Sort by customer_id.',
  'LEFT self-join and COUNT a column from the right side, so unmatched rows give 0.',
  "SELECT c.customer_id, COUNT(r.customer_id) AS referrals FROM customers c LEFT JOIN customers r ON r.referred_by = c.customer_id GROUP BY c.customer_id ORDER BY c.customer_id;", True)
q('Orders per customer incl. zero', M, g,
  'For every customer return <code>customer_id</code> and <code>orders</code>, including customers with 0 orders. Sort by customer_id.',
  'COUNT(*) would count 1 for a customer without orders. COUNT(o.order_id) counts 0.',
  "SELECT c.customer_id, COUNT(o.order_id) AS orders FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id ORDER BY c.customer_id;", True)
q('E-bike orders', M, g,
  "Return <code>order_id</code> of orders that contain at least one product from the 'E-bikes' category. Each order once.",
  'Join order_items → products → categories, filter on the category name, DISTINCT.',
  "SELECT DISTINCT oi.order_id FROM order_items oi JOIN products p ON oi.product_id = p.product_id JOIN categories c ON p.category_id = c.category_id WHERE c.name = 'E-bikes';")
q('Average basket by channel', M, g,
  'For each <code>channel</code> return the average order value (rounded to 2) of delivered orders. Order value = sum of line revenue of that order.',
  'Two levels: first value per order (CTE or subquery), then AVG per channel. AVG over joined lines would be the average line, not the average order.',
  f"""WITH ov AS (
  SELECT oi.order_id, SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0) AS v
  FROM order_items oi GROUP BY oi.order_id
)
SELECT o.channel, ROUND(AVG(ov.v), 2) AS avg_order_value
FROM orders o JOIN ov ON o.order_id = ov.order_id
WHERE o.status = 'delivered'
GROUP BY o.channel;""")
q('Brand revenue 2024', M, g,
  'Return each <code>brand</code> and its revenue (rounded to 2) from delivered orders placed in 2024. Sort by revenue from highest.',
  'order_items → orders (date, status) and → products (brand).',
  """SELECT p.brand, ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0), 2) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.status = 'delivered' AND o.order_date >= '2024-01-01' AND o.order_date < '2025-01-01'
GROUP BY p.brand
ORDER BY revenue DESC;""", True)
q('Price changes', M, g,
  'Some products were sold at a different price than their current list price. Return <code>product_id</code>, <code>name</code>, the current <code>list_price</code> and the lowest price it was ever sold at (<code>min_sold_price</code>), only for products where these differ.',
  'Compare products.unit_price with MIN(order_items.unit_price) in HAVING.',
  "SELECT p.product_id, p.name, p.unit_price AS list_price, MIN(oi.unit_price) AS min_sold_price FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.product_id, p.name, p.unit_price HAVING MIN(oi.unit_price) <> p.unit_price;")
q('Customers per top category', H, g,
  "For each top-level category (Bikes, Components, Accessories, Apparel) return its <code>name</code> and the number of different customers who bought something from it (any status).",
  'products → sub-category → parent category. Join categories twice.',
  """SELECT top.name, COUNT(DISTINCT o.customer_id) AS customers
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories sub ON p.category_id = sub.category_id
JOIN categories top ON sub.parent_id = top.category_id
GROUP BY top.name;""")

# ---------------- 7. Subqueries & CTEs ----------------
g = 'Subqueries & CTEs'
q('Above average price', E, g,
  'Return <code>name</code> and <code>unit_price</code> of products priced above the average product price.',
  'WHERE unit_price > (SELECT AVG(unit_price) FROM products).',
  "SELECT name, unit_price FROM products WHERE unit_price > (SELECT AVG(unit_price) FROM products);")
q('Latest order', E, g,
  'Return <code>order_id</code>, <code>customer_id</code> and <code>order_date</code> of the most recent order(s).',
  'Find MAX(order_date) in a subquery and compare with =, so ties are kept.',
  "SELECT order_id, customer_id, order_date FROM orders WHERE order_date = (SELECT MAX(order_date) FROM orders);")
q('Above average spenders', M, g,
  'Using delivered orders, return <code>customer_id</code> and <code>spent</code> (rounded to 2) for customers whose total spending is above the average spending per customer (average over customers who spent anything).',
  'CTE 1: spending per customer. Then compare each row with (SELECT AVG(spent) FROM cte).',
  """WITH s AS (
  SELECT o.customer_id, SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0) AS spent
  FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
  WHERE o.status = 'delivered'
  GROUP BY o.customer_id
)
SELECT customer_id, ROUND(spent, 2) AS spent FROM s WHERE spent > (SELECT AVG(spent) FROM s);""")
q('Pricier than category average', M, g,
  'Return <code>name</code>, <code>category_id</code> and <code>unit_price</code> of products that cost more than the average price of their own category.',
  'Correlated subquery: the inner query uses the outer row\'s category_id.',
  "SELECT p.name, p.category_id, p.unit_price FROM products p WHERE p.unit_price > (SELECT AVG(p2.unit_price) FROM products p2 WHERE p2.category_id = p.category_id);")
q('Lost customers', M, g,
  'Return <code>customer_id</code> of customers who ordered in 2023 but not in 2024.',
  'IN (2023 buyers) AND NOT IN (2024 buyers), or EXCEPT.',
  """SELECT customer_id FROM orders WHERE order_date < '2024-01-01'
EXCEPT
SELECT customer_id FROM orders WHERE order_date >= '2024-01-01';""")
q('No reviews yet', E, g,
  'Return <code>product_id</code> and <code>name</code> of products that have never been reviewed.',
  'NOT EXISTS (SELECT 1 FROM reviews r WHERE r.product_id = p.product_id).',
  "SELECT p.product_id, p.name FROM products p WHERE NOT EXISTS (SELECT 1 FROM reviews r WHERE r.product_id = p.product_id);")
q('Best rated per category', H, g,
  'For each category return the product(s) with the highest average rating: <code>category_id</code>, <code>name</code>, <code>avg_rating</code> (rounded to 2). Keep ties.',
  'CTE with avg rating per product, then keep rows where avg = the max avg in the same category.',
  """WITH a AS (
  SELECT p.category_id, p.name, AVG(r.rating) AS avg_rating
  FROM products p JOIN reviews r ON p.product_id = r.product_id
  GROUP BY p.category_id, p.product_id, p.name
)
SELECT category_id, name, ROUND(avg_rating, 2) AS avg_rating
FROM a
WHERE avg_rating = (SELECT MAX(a2.avg_rating) FROM a a2 WHERE a2.category_id = a.category_id);""")
q('Order count distribution', M, g,
  'How many customers have 1 order, 2 orders, 3 orders …? Return <code>orders</code> and <code>customers</code>, sorted by orders. Only customers with at least one order.',
  'Aggregate twice: count orders per customer in a subquery, then count customers per number.',
  """SELECT orders, COUNT(*) AS customers
FROM (SELECT customer_id, COUNT(*) AS orders FROM orders GROUP BY customer_id) t
GROUP BY orders
ORDER BY orders;""", True)
q('Time to first order', M, g,
  'For each customer who ordered, return <code>customer_id</code>, <code>signup_date</code>, <code>first_order</code> (DATE of their first order) and <code>days_to_first</code>.',
  'MIN(order_date) per customer, then join to customers.',
  """SELECT c.customer_id, c.signup_date, f.first_order, f.first_order - c.signup_date AS days_to_first
FROM customers c
JOIN (SELECT customer_id, CAST(MIN(order_date) AS DATE) AS first_order FROM orders GROUP BY customer_id) f
  ON c.customer_id = f.customer_id;""")
q('Bad first impression', H, g,
  'Return <code>customer_id</code> of customers whose very first order was cancelled or returned.',
  'Find each customer\'s first order_date, join back to orders on customer AND date, check status.',
  """SELECT o.customer_id
FROM orders o
JOIN (SELECT customer_id, MIN(order_date) AS first_date FROM orders GROUP BY customer_id) f
  ON o.customer_id = f.customer_id AND o.order_date = f.first_date
WHERE o.status IN ('cancelled', 'returned');""")
q('Big categories', H, g,
  'Return category <code>name</code> and <code>share_pct</code> (rounded to 1) for categories that make more than 10 % of total revenue from delivered orders.',
  'CTE with revenue per category; total = SUM over the CTE.',
  """WITH r AS (
  SELECT c.name, SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0) AS rev
  FROM order_items oi
  JOIN orders o ON oi.order_id = o.order_id
  JOIN products p ON oi.product_id = p.product_id
  JOIN categories c ON p.category_id = c.category_id
  WHERE o.status = 'delivered'
  GROUP BY c.name
)
SELECT name, ROUND(100 * rev / (SELECT SUM(rev) FROM r), 1) AS share_pct
FROM r
WHERE rev > 0.1 * (SELECT SUM(rev) FROM r);""")
q('Shipped but unpaid', H, g,
  "Return <code>order_id</code> and <code>status</code> of orders that are shipped or delivered but have no successful payment (no payment row with status 'paid').",
  "NOT EXISTS with a filter on status inside the subquery.",
  "SELECT o.order_id, o.status FROM orders o WHERE o.status IN ('delivered', 'shipped') AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.order_id AND p.status = 'paid');")
q('Buyers of the best seller', M, g,
  'Find the product with the most units sold (all orders). Return <code>customer_id</code> of every customer who bought it, each once.',
  'Inner subquery: product_id with MAX units (ORDER BY SUM(quantity) DESC LIMIT 1).',
  """SELECT DISTINCT o.customer_id
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
WHERE oi.product_id = (SELECT product_id FROM order_items GROUP BY product_id ORDER BY SUM(quantity) DESC, product_id LIMIT 1);""")
q('Reviews without purchase', H, g,
  'Return <code>review_id</code>, <code>customer_id</code> and <code>product_id</code> of reviews written by customers who never ordered that product.',
  'NOT EXISTS joining orders and order_items on both customer and product.',
  """SELECT r.review_id, r.customer_id, r.product_id
FROM reviews r
WHERE NOT EXISTS (
  SELECT 1 FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
  WHERE o.customer_id = r.customer_id AND oi.product_id = r.product_id
);""")

# ---------------- 8. Window functions ----------------
g = 'Window functions'
q('Price rank in category', M, g,
  'Return <code>category_id</code>, <code>name</code>, <code>unit_price</code> and <code>price_rank</code> = rank of the product by price inside its category (most expensive = 1, ties share the rank, no gaps).',
  'DENSE_RANK() OVER (PARTITION BY category_id ORDER BY unit_price DESC).',
  "SELECT category_id, name, unit_price, DENSE_RANK() OVER (PARTITION BY category_id ORDER BY unit_price DESC) AS price_rank FROM products;")
q('Running total 2024', M, g,
  "Return each <code>month</code> of 2024 (1–12), the paid amount that month (status 'paid', by payment_date) and <code>running_total</code> from January. Sort by month.",
  'Aggregate per month first, then SUM(...) OVER (ORDER BY month).',
  """SELECT month, paid, SUM(paid) OVER (ORDER BY month) AS running_total
FROM (
  SELECT EXTRACT(MONTH FROM payment_date) AS month, SUM(amount) AS paid
  FROM payments
  WHERE status = 'paid' AND payment_date >= '2024-01-01' AND payment_date < '2025-01-01'
  GROUP BY EXTRACT(MONTH FROM payment_date)
) m
ORDER BY month;""", True)
q('First order per customer', M, g,
  'For each customer who ordered, return their first order: <code>customer_id</code>, <code>order_id</code>, <code>order_date</code>.',
  'ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date), keep row number 1.',
  """SELECT customer_id, order_id, order_date
FROM (
  SELECT customer_id, order_id, order_date,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS rn
  FROM orders
) t
WHERE rn = 1;""")
q('Average gap between orders', H, g,
  'For customers with at least 2 orders, return <code>customer_id</code> and <code>avg_gap_days</code> = average number of days between consecutive orders (by order date), rounded to 1.',
  'LAG(order_date) gives the previous order. CAST both to DATE and subtract.',
  """SELECT customer_id, ROUND(AVG(gap), 1) AS avg_gap_days
FROM (
  SELECT customer_id,
         CAST(order_date AS DATE) - CAST(LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS DATE) AS gap
  FROM orders
) t
WHERE gap IS NOT NULL
GROUP BY customer_id;""")
q('Month-over-month growth', H, g,
  "For 2024, return <code>month</code>, <code>orders</code> and <code>growth_pct</code> = change vs the previous month in percent (rounded to 1; NULL for January). Sort by month.",
  'Count per month, then LAG(orders) OVER (ORDER BY month). Watch integer division.',
  """SELECT month, orders,
       ROUND(100.0 * (orders - LAG(orders) OVER (ORDER BY month)) / LAG(orders) OVER (ORDER BY month), 1) AS growth_pct
FROM (
  SELECT EXTRACT(MONTH FROM order_date) AS month, COUNT(*) AS orders
  FROM orders
  WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'
  GROUP BY EXTRACT(MONTH FROM order_date)
) m
ORDER BY month;""", True)
q('Top 2 per category', H, g,
  'For each category return the 2 products with the most units sold (all orders): <code>category_id</code>, <code>name</code>, <code>units</code>. If there is a tie for 2nd place, keep all tied products.',
  'Units per product, then RANK() OVER (PARTITION BY category_id ORDER BY units DESC) <= 2.',
  """SELECT category_id, name, units
FROM (
  SELECT p.category_id, p.name, SUM(oi.quantity) AS units,
         RANK() OVER (PARTITION BY p.category_id ORDER BY SUM(oi.quantity) DESC) AS rk
  FROM products p JOIN order_items oi ON p.product_id = oi.product_id
  GROUP BY p.category_id, p.product_id, p.name
) t
WHERE rk <= 2;""")
q('Share inside category', H, g,
  'For every product sold in delivered orders return <code>category_id</code>, <code>name</code>, <code>revenue</code> and <code>share_pct</code> = its share of its category revenue (both rounded: revenue to 2, share to 1).',
  'Revenue per product with GROUP BY, then divide by SUM(revenue) OVER (PARTITION BY category_id).',
  """SELECT category_id, name, ROUND(rev, 2) AS revenue,
       ROUND(100 * rev / SUM(rev) OVER (PARTITION BY category_id), 1) AS share_pct
FROM (
  SELECT p.category_id, p.name, SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0) AS rev
  FROM order_items oi
  JOIN orders o ON oi.order_id = o.order_id
  JOIN products p ON oi.product_id = p.product_id
  WHERE o.status = 'delivered'
  GROUP BY p.category_id, p.product_id, p.name
) t;""")
q('Quick second order', H, g,
  'Return <code>customer_id</code> of customers whose second order came within 30 days of their first order.',
  'ROW_NUMBER to number orders; LEAD(order_date) from the first order gives the second.',
  """SELECT customer_id
FROM (
  SELECT customer_id, order_date,
         LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS next_date,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS rn
  FROM orders
) t
WHERE rn = 1 AND next_date IS NOT NULL AND CAST(next_date AS DATE) - CAST(order_date AS DATE) <= 30;""")
q('Moving average', H, g,
  'For every month in 2023–2024 return <code>month_start</code> (DATE, first day of month), <code>orders</code>, and <code>ma3</code> = average orders over this and the 2 previous months, rounded to 1. Sort by month_start.',
  "DATE_TRUNC('month', order_date) groups by month. AVG(...) OVER (ORDER BY ... ROWS BETWEEN 2 PRECEDING AND CURRENT ROW).",
  """SELECT month_start, orders,
       ROUND(AVG(orders) OVER (ORDER BY month_start ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS ma3
FROM (
  SELECT CAST(DATE_TRUNC('month', order_date) AS DATE) AS month_start, COUNT(*) AS orders
  FROM orders
  GROUP BY DATE_TRUNC('month', order_date)
) m
ORDER BY month_start;""", True)
q('Spending quartiles', H, g,
  'Split customers who spent anything (delivered orders) into 4 groups by total spending using NTILE: return <code>customer_id</code>, <code>spent</code> (rounded to 2) and <code>quartile</code> (1 = top spenders).',
  'NTILE(4) OVER (ORDER BY spent DESC, customer_id).',
  """SELECT customer_id, ROUND(spent, 2) AS spent, NTILE(4) OVER (ORDER BY spent DESC, customer_id) AS quartile
FROM (
  SELECT o.customer_id, SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0) AS spent
  FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
  WHERE o.status = 'delivered'
  GROUP BY o.customer_id
) t;""")
q('Three months in a row', H, g,
  'Return <code>customer_id</code> of customers who placed orders in at least 3 consecutive calendar months (e.g. May, June, July 2023).',
  "Distinct months per customer, then compare each month with LAG(month, 2): if it is exactly 2 months earlier, there are 3 in a row.",
  """SELECT DISTINCT customer_id
FROM (
  SELECT customer_id, m,
         LAG(m, 2) OVER (PARTITION BY customer_id ORDER BY m) AS m_minus2
  FROM (SELECT DISTINCT customer_id, CAST(DATE_TRUNC('month', order_date) AS DATE) AS m FROM orders) d
) t
WHERE m_minus2 = CAST(m - INTERVAL '2 months' AS DATE);""")

# ---------------- 9. Business cases ----------------
g = 'Business cases'
q('Welcome cohort', H, g,
  'For customers who signed up in 2023, return <code>signup_month</code> (1–12), <code>signups</code> and <code>ordered_30d</code> = how many of them placed an order within 30 days of signing up. Sort by month.',
  'LEFT JOIN customers to a "first order date" subquery; count with FILTER or CASE.',
  """SELECT EXTRACT(MONTH FROM c.signup_date) AS signup_month,
       COUNT(*) AS signups,
       COUNT(*) FILTER (WHERE f.first_order - c.signup_date <= 30) AS ordered_30d
FROM customers c
LEFT JOIN (SELECT customer_id, CAST(MIN(order_date) AS DATE) AS first_order FROM orders GROUP BY customer_id) f
  ON c.customer_id = f.customer_id
WHERE c.signup_date < '2024-01-01'
GROUP BY EXTRACT(MONTH FROM c.signup_date)
ORDER BY signup_month;""", True)
q('Return rate by brand', H, g,
  "For each brand return <code>return_rate_pct</code> = units in returned orders / units in delivered or returned orders × 100, rounded to 1. Sort by rate from highest, then brand.",
  'SUM(quantity) FILTER (WHERE status = ...) for the top part; integer division again.',
  """SELECT p.brand,
       ROUND(100.0 * SUM(oi.quantity) FILTER (WHERE o.status = 'returned') / SUM(oi.quantity), 1) AS return_rate_pct
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.status IN ('delivered', 'returned')
GROUP BY p.brand
ORDER BY return_rate_pct DESC, p.brand;""", True)
q('Gross profit by category', H, g,
  'For delivered orders, return category <code>name</code>, <code>revenue</code>, <code>cost</code> (quantity × products.cost_price) and <code>profit</code>, all rounded to 2. Sort by profit from highest.',
  'Revenue uses the sold price from order_items; cost uses cost_price from products.',
  """SELECT c.name,
       ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0), 2) AS revenue,
       ROUND(SUM(oi.quantity * p.cost_price), 2) AS cost,
       ROUND(SUM(oi.quantity * oi.unit_price * (100 - oi.discount_pct) / 100.0) - SUM(oi.quantity * p.cost_price), 2) AS profit
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
WHERE o.status = 'delivered'
GROUP BY c.name
ORDER BY profit DESC;""", True)
q('Bought together', H, g,
  'Return the 5 product pairs that appear together in the most orders: <code>product_a</code>, <code>product_b</code> (ids, a < b) and <code>orders</code>. Sort by orders from highest, then product_a, then product_b.',
  'Self-join order_items on order_id with a.product_id < b.product_id, so each pair is counted once.',
  """SELECT a.product_id AS product_a, b.product_id AS product_b, COUNT(*) AS orders
FROM order_items a
JOIN order_items b ON a.order_id = b.order_id AND a.product_id < b.product_id
GROUP BY a.product_id, b.product_id
ORDER BY orders DESC, product_a, product_b
LIMIT 5;""", True)
q('Refund check', H, g,
  'Every returned order should have a refund. Return <code>order_id</code> of returned orders that do NOT have a payment row with status <code>refunded</code>.',
  'NOT EXISTS with status filter.',
  "SELECT o.order_id FROM orders o WHERE o.status = 'returned' AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.order_id AND p.status = 'refunded');")
q('Failed then paid', M, g,
  "Return <code>order_id</code> of orders that have both a 'failed' and a 'paid' payment.",
  "GROUP BY order_id HAVING COUNT(*) FILTER (WHERE status = 'failed') > 0 AND ... 'paid' ...",
  "SELECT order_id FROM payments GROUP BY order_id HAVING COUNT(*) FILTER (WHERE status = 'failed') > 0 AND COUNT(*) FILTER (WHERE status = 'paid') > 0;")
q('Net revenue by month', H, g,
  "For 2024 return <code>month</code> (1–12), <code>paid</code>, <code>refunded</code> and <code>net</code> = paid − refunded, using payment_date. Sort by month.",
  "Conditional aggregation: SUM(amount) FILTER (WHERE status = 'paid'). COALESCE to 0 if a month has no refunds.",
  """SELECT EXTRACT(MONTH FROM payment_date) AS month,
       COALESCE(SUM(amount) FILTER (WHERE status = 'paid'), 0) AS paid,
       COALESCE(SUM(amount) FILTER (WHERE status = 'refunded'), 0) AS refunded,
       COALESCE(SUM(amount) FILTER (WHERE status = 'paid'), 0) - COALESCE(SUM(amount) FILTER (WHERE status = 'refunded'), 0) AS net
FROM payments
WHERE payment_date >= '2024-01-01' AND payment_date < '2025-01-01'
GROUP BY EXTRACT(MONTH FROM payment_date)
ORDER BY month;""", True)
q('Discount cost', M, g,
  'For each discount code return <code>discount_code</code> and <code>discount_given</code> = total CZK given away (list value of the lines minus what was charged), delivered orders only, rounded to 2.',
  'Given away per line = quantity × unit_price × discount_pct / 100.0.',
  """SELECT o.discount_code, ROUND(SUM(oi.quantity * oi.unit_price * oi.discount_pct / 100.0), 2) AS discount_given
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'delivered' AND o.discount_code IS NOT NULL
GROUP BY o.discount_code;""")
q('Dormant VIPs', M, g,
  'Return <code>customer_id</code> and <code>last_order</code> (DATE) of VIP customers whose last order was before 2024-07-01, or who never ordered (last_order NULL).',
  'LEFT JOIN + MAX(order_date), then HAVING MAX(...) < date OR MAX(...) IS NULL.',
  """SELECT c.customer_id, CAST(MAX(o.order_date) AS DATE) AS last_order
FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.is_vip
GROUP BY c.customer_id
HAVING MAX(o.order_date) < '2024-07-01' OR MAX(o.order_date) IS NULL;""")
q('Second highest price', M, g,
  'Return the second highest distinct product price as <code>second_price</code>.',
  'Classic: MAX of prices below the MAX, or DISTINCT ... ORDER BY ... OFFSET 1 LIMIT 1.',
  "SELECT MAX(unit_price) AS second_price FROM products WHERE unit_price < (SELECT MAX(unit_price) FROM products);")
q('Duplicate names', M, g,
  'Some first+last name combinations belong to more than one customer. Return <code>first_name</code>, <code>last_name</code> and <code>people</code> for those names.',
  'GROUP BY two columns HAVING COUNT(*) > 1.',
  "SELECT first_name, last_name, COUNT(*) AS people FROM customers GROUP BY first_name, last_name HAVING COUNT(*) > 1;")
