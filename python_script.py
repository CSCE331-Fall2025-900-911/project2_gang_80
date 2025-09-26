#!/usr/bin/env python3
"""
generate_seed_sql_team5.py

Generates:
  - seed_data.sql           (DDL + INSERTs + UPDATE inventory per sale)
  - verification_queries.sql (15 queries including the 4 special queries)

Defaults tuned for a TEAM OF 5:
  weeks = 52, total_million = 1.0, peaks = 2, menu_items = 20

Usage:
  python generate_seed_sql_team5.py
  python generate_seed_sql_team5.py --weeks 52 --million 1.0 --peaks 2 --menu 20 --seed 123

Notes:
  - The SQL uses types compatible with SQLite/Postgres/MySQL for the most part.
  - The queries file includes both SQLite-compatible and PostgreSQL variants (where necessary) as comments.
"""
import argparse
import math
import random
from datetime import datetime, timedelta, time

# ---------- Helpers ----------
def sql_string(s):
    return "'" + s.replace("'", "''") + "'"

def insert_stmt(table, cols, vals):
    return f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(vals)});"

def now_iso():
    return datetime.now().isoformat()

# ---------- Data pools ----------
BASE_PRODUCTS = [
    "Espresso", "Americano", "Latte", "Cappuccino", "Mocha", "Flat White", "Cold Brew",
    "Iced Coffee", "Chai Latte", "Matcha Latte", "Hot Chocolate", "Black Tea", "Green Tea",
    "Bagel", "Croissant", "Muffin", "Ham & Cheese Sandwich", "Turkey Sandwich",
    "Chicken Panini", "Caesar Salad", "Greek Salad", "Protein Bar", "Yogurt Parfait",
    "Oatmeal", "Cookie", "Brownie"
]

BASE_INGREDIENTS = [
    "Espresso Shot", "Whole Beans", "Milk", "Oat Milk", "Almond Milk",
    "Sugar", "Vanilla Syrup", "Caramel Syrup", "Hazelnut Syrup",
    "Cocoa Powder", "Tea Leaves", "Matcha Powder", "Chocolate Sauce",
    "Bagel Dough", "Butter", "Cream Cheese", "Flour", "Eggs", "Cheese", "Ham",
    "Turkey", "Chicken", "Lettuce", "Tomato", "Bread", "Oats", "Granola",
    "Yogurt", "Potato", "Vegetable Oil", "Salt", "Pepper"
]

SUPPLIES = ["Cup (S)", "Cup (M)", "Cup (L)", "Lid", "Straw", "Napkin", "Bag", "Stirrer"]

# ---------- Generator ----------
def generate_files(filename_sql="seed_data.sql", filename_queries="verification_queries.sql",
                   weeks=52, total_million=1.0, peaks=2, menu_items=20, seed=42):
    random.seed(seed)

    days = weeks * 7
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)

    total_target = total_million * 1_000_000.0
    avg_daily_target = total_target / days

    # pick peak day indexes (clustered near semester starts? randomness is ok)
    peak_indexes = sorted(random.sample(range(days), k=min(peaks, days)))
    peak_mults = {i: random.uniform(2.0, 4.0) for i in peak_indexes}

    # Prepare ingredients/products
    ingredients = BASE_INGREDIENTS.copy()
    # ensure at least 35 ingredients for variety
    while len(ingredients) < 35:
        ingredients.append(f"ExtraIngredient_{len(ingredients)+1}")

    products_base = BASE_PRODUCTS[:]
    while len(products_base) < menu_items:
        products_base.append(f"MenuItem_{len(products_base)+1}")
    products_base = products_base[:menu_items]

    # price function
    def price_for_name(n):
        name = n.lower()
        if any(x in name for x in ["latte", "americano", "espresso", "cappuccino", "mocha", "flat white", "cold brew", "iced", "tea", "chai", "matcha", "hot chocolate"]):
            return round(random.uniform(2.5, 6.0), 2)
        if any(x in name for x in ["bagel", "sandwich", "panini", "salad"]):
            return round(random.uniform(5.0, 12.0), 2)
        if any(x in name for x in ["muffin", "cookie", "brownie", "granola", "yogurt", "oatmeal", "protein bar"]):
            return round(random.uniform(1.5, 6.0), 2)
        return round(random.uniform(2.0, 10.0), 2)

    # build product list and product_ingredients mapping
    products = []
    product_ingredients = []  # tuples (product_id, ingredient_id, qty_per_serving)
    for i, pname in enumerate(products_base):
        pid = i + 1
        price = price_for_name(pname)
        products.append((pid, pname, price))
        # give 2-5 ingredients per product
        ing_count = random.randint(2, 5)
        chosen = random.sample(range(1, len(ingredients)+1), k=ing_count)
        for ing in chosen:
            qty = round(random.uniform(0.05, 2.0), 2)  # units per serving
            product_ingredients.append((pid, ing, qty))

    # supplies mapping
    supplies = [(i+1, s) for i, s in enumerate(SUPPLIES)]

    # --- Start writing seed_data.sql ---
    with open(filename_sql, "w", encoding="utf-8") as f:
        w = f.write
        w("-- seed_data.sql generated on " + now_iso() + "\n")
        w("-- Schema + Inserts + Inventory updates (consumption) for team of 5 default\n\n")

        # DDL
        w("""-- TABLES (compatible with SQLite/Postgres; minor tweaks may be needed for MySQL)
CREATE TABLE IF NOT EXISTS ingredients (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  base_price NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS product_ingredients (
  product_id INTEGER NOT NULL,
  ingredient_id INTEGER NOT NULL,
  qty_per_serving NUMERIC NOT NULL,
  PRIMARY KEY(product_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS supplies (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

-- Inventory stores starting quantities for consumable items (ingredients and supplies)
CREATE TABLE IF NOT EXISTS inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_type TEXT NOT NULL,  -- 'ingredient' or 'supply'
  ref_id INTEGER NOT NULL,  -- references ingredients.id or supplies.id
  quantity NUMERIC NOT NULL
);

-- sales: each row is an order; sale_timestamp stores time of order (temporal requirement)
CREATE TABLE IF NOT EXISTS sales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sale_timestamp TIMESTAMP NOT NULL,
  total NUMERIC NOT NULL
);

-- sale_items: what was sold in each order. store price_at_purchase and quantity
CREATE TABLE IF NOT EXISTS sale_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sale_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  qty INTEGER NOT NULL,
  price_at_purchase NUMERIC NOT NULL
);

-- helpful indexes
CREATE INDEX IF NOT EXISTS idx_sales_timestamp ON sales(sale_timestamp);
CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id);

\n""")

        # insert ingredients
        w("-- INSERT ingredients\n")
        for idx, ing in enumerate(ingredients, start=1):
            w(insert_stmt("ingredients", ["id", "name"], [str(idx), sql_string(ing)]) + "\n")
        w("\n")

        # insert products
        w("-- INSERT products\n")
        for pid, name, price in products:
            w(insert_stmt("products", ["id", "name", "base_price"], [str(pid), sql_string(name), str(price)]) + "\n")
        w("\n")

        # insert product_ingredients
        w("-- INSERT product_ingredients (qty per serving)\n")
        for pid, ing_id, qty in product_ingredients:
            w(insert_stmt("product_ingredients", ["product_id", "ingredient_id", "qty_per_serving"],
                          [str(pid), str(ing_id), str(qty)]) + "\n")
        w("\n")

        # supplies
        w("-- INSERT supplies\n")
        for sid, sname in supplies:
            w(insert_stmt("supplies", ["id", "name"], [str(sid), sql_string(sname)]) + "\n")
        w("\n")

        # initial inventory for ingredients
        w("-- INITIAL INVENTORY (ingredients)\n")
        for ing_id in range(1, len(ingredients)+1):
            qty = random.randint(1000, 8000)  # starting units
            w(insert_stmt("inventory", ["item_type", "ref_id", "quantity"],
                          [sql_string("ingredient"), str(ing_id), str(qty)]) + "\n")
        w("\n")

        # initial inventory for supplies
        w("-- INITIAL INVENTORY (supplies)\n")
        for sid, _ in supplies:
            qty = random.randint(500, 3000)
            w(insert_stmt("inventory", ["item_type", "ref_id", "quantity"],
                          [sql_string("supply"), str(sid), str(qty)]) + "\n")
        w("\n")

        # Build day totals with weekday and peak multipliers. Also create realistic hourly distribution
        # hourly distribution (probability of order by hour) — morning rush (7-10), lunch (11-14), afternoon small, evening low
        base_hour_weights = {h: 0.01 for h in range(24)}
        for h in range(24):
            if 6 <= h <= 9:
                base_hour_weights[h] = 0.09  # morning rush
            elif 11 <= h <= 13:
                base_hour_weights[h] = 0.10  # lunch
            elif 14 <= h <= 16:
                base_hour_weights[h] = 0.06
            elif 16 <= h <= 18:
                base_hour_weights[h] = 0.04
            elif 19 <= h <= 21:
                base_hour_weights[h] = 0.02
            elif h == 12:
                base_hour_weights[h] += 0.01
        # normalize
        s = sum(base_hour_weights.values())
        for h in base_hour_weights:
            base_hour_weights[h] /= s

        # generate raw day totals with noise and peaks
        day_amounts = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            # weekday multiplier: slightly more business on weekdays for campus coffee shop
            wd = day.weekday()  # 0..6
            weekday_mult = 1.0
            if wd < 5:
                weekday_mult = 1.05
            else:
                weekday_mult = 0.9
            base = avg_daily_target * random.uniform(0.6, 1.4) * weekday_mult
            if i in peak_indexes:
                base *= peak_mults[i]
            day_amounts.append((day, base))

        # scale to match total_target
        total_raw = sum(a for _, a in day_amounts)
        scale = total_target / total_raw if total_raw > 0 else 1.0
        day_amounts = [(d, round(a*scale, 2)) for d, a in day_amounts]

        # Now split each day's total into orders with timestamps and sale_items
        sale_id = 0
        total_generated = 0.0
        total_orders = 0

        w("-- SALES and SALE_ITEMS and corresponding INVENTORY updates (inventory consumption)\n")

        for idx_day, (day, day_total) in enumerate(day_amounts):
            # expected orders roughly day_total / avg_order
            avg_order = 6.5
            expected_orders = max(1, int(round(day_total / avg_order)))
            # add randomness
            orders_today = max(1, int(random.gauss(expected_orders, expected_orders * 0.15)))
            # ensure not crazy large
            orders_today = max(1, min(orders_today, expected_orders * 4 + 5))

            # create list of timestamp choices for this day based on hourly weights
            hours = []
            for h in range(24):
                hours += [h] * int(base_hour_weights.get(h, 0.01) * 1000)
            # per-order average target
            target_per_order = day_total / orders_today if orders_today else day_total

            remaining = day_total
            for o in range(orders_today):
                sale_id += 1
                total_orders += 1

                # create timestamp for this order
                hour = random.choice(hours)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                sale_ts = datetime.combine(day, time(hour, minute, second)).isoformat(sep=' ')

                # compute order_total (last order gets remainder)
                if o == orders_today - 1:
                    order_total = round(max(0.5, remaining), 2)
                else:
                    order_total = round(max(0.5, random.gauss(target_per_order, target_per_order * 0.35)), 2)
                    # don't exceed remaining by too much
                    order_total = min(order_total, round(remaining - 0.01*(orders_today - o - 1), 2))
                    if order_total <= 0:
                        order_total = round(max(0.5, remaining / (orders_today - o)), 2)

                # write sale row (explicit id for reproducibility)
                w(insert_stmt("sales", ["id", "sale_timestamp", "total"], [str(sale_id), sql_string(sale_ts), str(order_total)]) + "\n")
                total_generated += order_total

                # split order into 1-4 different product line items
                items_count = random.randint(1, 4)
                chosen_products = random.sample(products, k=min(items_count, len(products)))
                # allocate order_total approximately proportional to base_price for variety
                price_sum = sum(p[2] for p in chosen_products) or 1.0
                allocated = 0.0
                for it_idx, (pid, pname, base_price) in enumerate(chosen_products):
                    if it_idx == len(chosen_products) - 1:
                        # last item gets remainder (rounded)
                        item_total = round(max(0.5, order_total - allocated), 2)
                        # choose qty: at least 1, but if item_total larger, may be multiple
                        qty = 1
                        # price_at_purchase attempt: distribute proportional but allow discount/noise
                        price_each = round(max(0.5, item_total / qty), 2)
                    else:
                        # determine share
                        share = base_price / price_sum
                        item_total_guess = order_total * share * random.uniform(0.7, 1.3)
                        qty = random.randint(1, 2)
                        price_each = round(max(0.5, item_total_guess / qty), 2)
                        item_total = round(price_each * qty, 2)
                        allocated += item_total

                    # record sale_item
                    w(insert_stmt("sale_items", ["sale_id", "product_id", "qty", "price_at_purchase"],
                                  [str(sale_id), str(pid), str(qty), str(price_each)]) + "\n")

                    # INVENTORY UPDATES: for each ingredient used by this product, decrement inventory by qty * qty_per_serving
                    # find relevant ingredients
                    for (ppid, ing_id, qty_per_serving) in product_ingredients:
                        if ppid == pid:
                            # UPDATE inventory useful for testing consumption; use an UPDATE per ingredient per sale item
                            consumed = round(qty * float(qty_per_serving), 3)
                            # Use SQL that decrements the ingredient inventory row matching item_type='ingredient' and ref_id=ing_id
                            w(f"UPDATE inventory SET quantity = quantity - {consumed} WHERE item_type = 'ingredient' AND ref_id = {ing_id};\n")

                remaining = round(max(0.0, remaining - order_total), 2)

        # footer summary comments
        w("\n-- SUMMARY COMMENT\n")
        w(f"-- Days generated: {days}\n")
        w(f"-- Orders generated (approx): {total_orders}\n")
        w(f"-- Total sales amount generated: {round(total_generated,2)}\n")
        w(f"-- Target sales amount: {round(total_target,2)}\n")
        w("-- End of seed file\n")

    print(f"Generated {filename_sql}: {total_orders} orders, total ${round(total_generated,2)} (target ${round(total_target,2)})")

    # ---------- Generate verification_queries.sql ----------
    # We'll produce ε = 15 queries (first θ=4 are special)
    queries = []
    # Special Query #1: Weekly Sales History (count orders grouped by week)
    queries.append((
        "Special Query 1 - Weekly Sales History (count orders grouped by week)",
        "-- SQLite version (week string):\n"
        "SELECT strftime('%Y-%W', sale_timestamp) AS year_week, COUNT(*) AS orders\n"
        "FROM sales\n"
        "GROUP BY year_week\n"
        "ORDER BY year_week;\n\n"
        "-- PostgreSQL version (week starting Monday):\n"
        "-- SELECT to_char(date_trunc('week', sale_timestamp), 'YYYY-MM-DD') AS week_start, COUNT(*) AS orders\n"
        "-- FROM sales\n"
        "-- GROUP BY week_start\n"
        "-- ORDER BY week_start;\n"
        "-- Example: '2024-09 has 987 orders' (format depends on DB)\n"
    ))

    # Special Query #2: Realistic Sales History (group by hour)
    queries.append((
        "Special Query 2 - Sales by hour (count and sum)",
        "-- SQLite version: group by hour of day\n"
        "SELECT strftime('%H', sale_timestamp) AS hour_of_day, COUNT(*) AS orders, ROUND(SUM(total),2) AS total_sales\n"
        "FROM sales\n"
        "GROUP BY hour_of_day\n"
        "ORDER BY CAST(hour_of_day AS INTEGER);\n\n"
        "-- Postgres variant uses date_part or to_char\n"
    ))

    # Special Query #3: Peak Sales Day (top 10 sums grouped by day)
    queries.append((
        "Special Query 3 - Peak Sales Day (top 10 days by total sales)",
        "-- SQLite\n"
        "SELECT date(sale_timestamp) AS day, ROUND(SUM(total),2) AS day_total\n"
        "FROM sales\n"
        "GROUP BY day\n"
        "ORDER BY day_total DESC\n"
        "LIMIT 10;\n\n"
    ))

    # Special Query #4: Menu Item Inventory (how many inventory items does a menu item use)
    queries.append((
        "Special Query 4 - Menu Item Inventory (count of ingredients per product)",
        "-- count of ingredients used per product\n"
        "SELECT p.id, p.name, COUNT(pi.ingredient_id) AS num_ingredients\n"
        "FROM products p\n"
        "JOIN product_ingredients pi ON p.id = pi.product_id\n"
        "GROUP BY p.id, p.name\n"
        "ORDER BY num_ingredients DESC;\n\n"
    ))

    # Additional queries up to epsilon = 15 (we already have 4)
    # Q5: Top selling products by quantity in last 30 days
    queries.append((
        "Q5 - Top selling products by quantity in last 30 days",
        "-- Top products by qty sold in last 30 days (SQLite)\n"
        "SELECT si.product_id, p.name, SUM(si.qty) AS qty_sold\n"
        "FROM sale_items si\n"
        "JOIN sales s ON si.sale_id = s.id\n"
        "JOIN products p ON p.id = si.product_id\n"
        "WHERE date(s.sale_timestamp) >= date('now', '-30 days')\n"
        "GROUP BY si.product_id, p.name\n"
        "ORDER BY qty_sold DESC\n"
        "LIMIT 10;\n\n"
    ))

    # Q6: Daily revenue timeseries for last α weeks (group by day)
    queries.append((
        "Q6 - Daily revenue timeseries (group by day)",
        "-- Daily revenue for the whole period\n"
        "SELECT date(sale_timestamp) AS day, COUNT(*) AS orders, ROUND(SUM(total),2) AS revenue\n"
        "FROM sales\n"
        "GROUP BY day\n"
        "ORDER BY day;\n\n"
    ))

    # Q7: Average basket size by day of week
    queries.append((
        "Q7 - Average order total by day of week",
        "-- SQLite: day of week (0=Sunday..6=Saturday)\n"
        "SELECT strftime('%w', sale_timestamp) AS dow, COUNT(*) AS orders, ROUND(AVG(total),2) AS avg_order_total\n"
        "FROM sales\n"
        "GROUP BY dow\n"
        "ORDER BY CAST(dow AS INTEGER);\n\n"
    ))

    # Q8: Peak hours during a peak day (pick a known peak date from peaks) -- we include example placeholder
    queries.append((
        "Q8 - Hourly breakdown for a peak day",
        "-- Replace 'YYYY-MM-DD' with a peak day found from Special Query #3\n"
        "SELECT strftime('%H', sale_timestamp) AS hour, COUNT(*) AS orders, ROUND(SUM(total),2) AS revenue\n"
        "FROM sales\n"
        "WHERE date(sale_timestamp) = 'YYYY-MM-DD'\n"
        "GROUP BY hour\n"
        "ORDER BY CAST(hour AS INTEGER);\n\n"
    ))

    # Q9: Inventory low-report (ingredients below threshold)
    queries.append((
        "Q9 - Low inventory report (ingredients below threshold)",
        "-- Ingredients with inventory quantity less than X (e.g., 100)\n"
        "SELECT i.ref_id AS ingredient_id, ing.name, i.quantity\n"
        "FROM inventory i\n"
        "JOIN ingredients ing ON i.ref_id = ing.id\n"
        "WHERE i.item_type = 'ingredient' AND i.quantity < 100\n"
        "ORDER BY i.quantity ASC;\n\n"
    ))

    # Q10: Price history demonstration (we store price_at_purchase in sale_items)
    queries.append((
        "Q10 - Price of a product through time (sample product id = 1)",
        "-- Show sampled sale_items price_at_purchase for product_id = 1\n"
        "SELECT s.sale_timestamp, si.qty, si.price_at_purchase\n"
        "FROM sale_items si\n"
        "JOIN sales s ON s.id = si.sale_id\n"
        "WHERE si.product_id = 1\n"
        "ORDER BY s.sale_timestamp\n"
        "LIMIT 50;\n\n"
    ))

    # Q11: Best of the worst (special #5 description asked in assignment). We need to find for each week the day with lowest sales and top seller that day.
    queries.append((
        "Q11 - Best of the Worst (lowest-sales day per week and top seller that day)",
        "-- This multi-step query shows for each week the day with lowest revenue and its top-selling product\n"
        "-- 1) daily totals per day\n"
        "WITH daily AS (\n"
        "  SELECT date(sale_timestamp) AS day, SUM(total) AS revenue\n"
        "  FROM sales\n"
        "  GROUP BY day\n"
        "),\n"
        "weekly_min AS (\n"
        "  SELECT strftime('%Y-%W', day) AS year_week, day, revenue,\n"
        "    ROW_NUMBER() OVER (PARTITION BY strftime('%Y-%W', day) ORDER BY revenue ASC) AS rn\n"
        "  FROM daily\n"
        ")\n"
        "SELECT wm.year_week, wm.day AS lowest_day, wm.revenue AS lowest_revenue,\n"
        "  (SELECT p.name FROM sale_items si JOIN products p ON p.id = si.product_id\n"
        "     JOIN sales s ON s.id = si.sale_id\n"
        "     WHERE date(s.sale_timestamp) = wm.day\n"
        "     GROUP BY p.id, p.name\n"
        "     ORDER BY SUM(si.qty) DESC\n"
        "     LIMIT 1) AS top_seller\n"
        "FROM weekly_min wm\n"
        "WHERE wm.rn = 1\n"
        "ORDER BY wm.year_week;\n\n"
    ))

    # Q12: Top 10 days by count of orders (another perspective)
    queries.append((
        "Q12 - Days with most orders (top 10 by order count)",
        "SELECT date(sale_timestamp) AS day, COUNT(*) AS orders, ROUND(SUM(total),2) AS revenue\n"
        "FROM sales\n"
        "GROUP BY day\n"
        "ORDER BY orders DESC\n"
        "LIMIT 10;\n\n"
    ))

    # Q13: Average number of items per order
    queries.append((
        "Q13 - Average number of sale_items (line items) per order",
        "SELECT AVG(item_count) AS avg_items_per_order FROM (\n"
        "  SELECT sale_id, SUM(qty) AS item_count FROM sale_items GROUP BY sale_id\n"
        ");\n\n"
    ))

    # Q14: Which menu item uses the most distinct ingredients
    queries.append((
        "Q14 - Menu item using most distinct ingredients",
        "SELECT p.id, p.name, COUNT(pi.ingredient_id) AS num_ings\n"
        "FROM products p\n"
        "JOIN product_ingredients pi ON pi.product_id = p.id\n"
        "GROUP BY p.id, p.name\n"
        "ORDER BY num_ings DESC\n"
        "LIMIT 10;\n\n"
    ))

    # Q15: Recreate "sales on game days" example — find sales on dates matching special day list (we don't have teams/games, but user can replace dates)
    queries.append((
        "Q15 - Sales on special dates (game days / holidays) - replace list with actual dates",
        "-- Replace the list in the IN (...) with known special dates (YYYY-MM-DD):\n"
        "SELECT date(sale_timestamp) AS day, COUNT(*) AS orders, ROUND(SUM(total),2) AS revenue\n"
        "FROM sales\n        WHERE date(sale_timestamp) IN ('YYYY-MM-DD', 'YYYY-MM-DD')\n"
        "GROUP BY day\n"
        "ORDER BY day;\n\n"
    ))

    # Write queries to file
    with open(filename_queries, "w", encoding="utf-8") as qf:
        qf.write("-- verification_queries.sql generated on " + now_iso() + "\n")
        qf.write("-- Contains 15 queries (first 4 are required special queries for evaluation)\n\n")
        for title, sql in queries:
            qf.write(f"-- === {title} ===\n")
            qf.write(sql)
            qf.write("\n")

    print(f"Generated {filename_queries} with {len(queries)} queries (first 4 are special queries).")

# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate seed SQL plus verification queries (team of 5 defaults).")
    parser.add_argument("--weeks", type=int, default=52, help="Number of weeks (α). Default 52.")
    parser.add_argument("--million", type=float, default=1.0, help="Target sales in millions (β). Default 1.0.")
    parser.add_argument("--peaks", type=int, default=2, help="Number of peaks φ. Default 2.")
    parser.add_argument("--menu", type=int, default=20, help="Number of menu items δ. Default 20.")
    parser.add_argument("--out", type=str, default="seed_data.sql", help="Output SQL filename.")
    parser.add_argument("--queries", type=str, default="verification_queries.sql", help="Output queries filename.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    generate_files(filename_sql=args.out, filename_queries=args.queries,
                   weeks=args.weeks, total_million=args.million,
                   peaks=args.peaks, menu_items=args.menu, seed=args.seed)
