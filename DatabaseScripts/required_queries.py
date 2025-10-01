# python script to generate 15 SQL queries that can be run as an input file to verify the low-level design and interactions

OUTPUT_FILE = "available_queries.txt"

# 15 required queries with descriptions
queries = [
    ("Top 10 customers by orders in a given time period",
     "SELECT customer_id, COUNT(*) AS order_count "
     "FROM orders "
     "WHERE timestamp BETWEEN '2025-01-01 00:00:00'::timestamp AND '2025-01-31 23:59:59'::timestamp "
     "GROUP BY customer_id "
     "ORDER BY order_count DESC "
     "LIMIT 10;"),

    ("Top 10 customers by total spending in a given time period",
     "SELECT customer_id, SUM(total_price) AS total_spent "
     "FROM orders "
     "WHERE timestamp BETWEEN '2025-01-01 00:00:00'::timestamp AND '2025-01-31 23:59:59'::timestamp "
     "GROUP BY customer_id "
     "ORDER BY total_spent DESC "
     "LIMIT 10;"),

     ("Top 5 employees handling the most orders", 
     "SELECT employee_id, COUNT(*) AS handled_orders "
     "FROM orders "
     "GROUP BY employee_id "
     "ORDER BY handled_orders DESC "
     "LIMIT 5;"),

    ("Top 5 employees generating the most revenue", 
     "SELECT employee_id, SUM(total_price) AS sales_generated "
     "FROM orders "
     "GROUP BY employee_id "
     "ORDER BY sales_generated DESC "
     "LIMIT 5;"),

    ("Top 10 most popular menu items (by times ordered)", 
     "SELECT menu_item_id, COUNT(*) AS times_ordered "
     "FROM joint_order_items "
     "GROUP BY menu_item_id "
     "ORDER BY times_ordered DESC "
     "LIMIT 10;"),

    ("Top 10 least popular menu items (by times ordered)",
     "SELECT menu_item_id, COUNT(*) AS times_ordered "
     "FROM joint_order_items "
     "GROUP BY menu_item_id "
     "ORDER BY times_ordered ASC "
     "LIMIT 10;"),

    ("Top 5 inventory items running lowest", 
     "SELECT name, quantity FROM inventory ORDER BY quantity ASC LIMIT 5;"),

    ("Top 5 inventory items most in stock",
     "SELECT name, quantity FROM inventory ORDER BY quantity DESC LIMIT 5;"),

    ("Average order value", 
     "SELECT AVG(total_price) AS avg_order_value FROM orders;"),

    ("Top 5 busiest days by order count",
     "SELECT DATE(timestamp) AS order_date, COUNT(*) AS daily_orders "
     "FROM orders "
     "GROUP BY order_date "
     "ORDER BY daily_orders DESC "
     "LIMIT 5;"),

    ("Top 5 days with the lowest sales totals",
     "SELECT DATE(timestamp) AS order_date, SUM(total_price) AS daily_sales "
     "FROM orders "
     "GROUP BY order_date "
     "ORDER BY daily_sales ASC "
     "LIMIT 5;"),

    ("Top 5 menu items that use the most inventory items",
     "SELECT menu_item_id, COUNT(inventory_item_id) AS inventory_count "
     "FROM joint_recipe_ingredients "
     "GROUP BY menu_item_id "
     "ORDER BY inventory_count DESC "
     "LIMIT 5;"),

    ("Top 5 months with the highest sales",
     "SELECT MONTH(timestamp) AS order_month, SUM(total_price) AS monthly_sales "
     "FROM orders "
     "GROUP BY order_month "
     "ORDER BY monthly_sales DESC "
     "LIMIT 5;"),

     ("Top 10 highest revenue-generating menu items",
     "SELECT mi.name, SUM(o.total_price) AS total_revenue "
     "FROM joint_order_items joi "
     "JOIN menu_items mi ON joi.menu_item_id = mi.id "
     "JOIN orders o ON joi.order_id = o.id "
     "GROUP BY mi.name "
     "ORDER BY total_revenue DESC "
     "LIMIT 10;"),

     ("Top 10 most frequently used inventory items in recipes",
      "SELECT i.name, SUM(jri.quantity_used) AS total_used "
      "FROM joint_recipe_ingredients jri "
      "JOIN inventory i ON jri.inventory_item_id = i.id "
      "GROUP BY i.name "
      "ORDER BY total_used DESC "
      "LIMIT 10;"),
]

# 4 special queries
special_queries = [
    # pseudocode: select count of orders grouped by week
    # about: given a specific week, how many orders were placed?
    # example: "week 1 has 98765 orders"
    ("Special Query #1: Weekly Sales History",
     "SELECT EXTRACT(WEEK FROM timestamp) AS week_number, COUNT(*) AS orders_count "
     "FROM orders "
     "WHERE timestamp BETWEEN '2025-01-01 00:00:00'::timestamp AND '2025-12-31 23:59:59'::timestamp "
     "GROUP BY week_number "
     "ORDER BY week_number;"),

    # pseudocode: select count of orders, sum of order total grouped by hour
    # about: given a specific hour of the day, how many orders were placed and what was the total sum of the orders?
    # example: e.g., "12pm has 12345 orders totaling $86753"
    ("Special Query #2: Realistic Sales History",
     "SELECT EXTRACT(HOUR FROM timestamp) AS order_hour, COUNT(*) AS orders_count, SUM(total_price) AS total_sales "
     "FROM orders "
     "WHERE timestamp BETWEEN '2025-01-01 00:00:00'::timestamp AND '2025-12-31 23:59:59'::timestamp "
     "GROUP BY order_hour "
     "ORDER BY order_hour;"),

    # pseudocode: select top 10 sums of order total grouped by day in descending order by order total
    # about: given a specific day, what was the sum of the top 10 order totals?
    # example: "30 August has $12345 of top sales"
    ("Special Query #3: Peak Sales Day",
     "SELECT DATE(timestamp) AS order_date, SUM(total_price) AS daily_total "
     "FROM orders "
     "WHERE timestamp BETWEEN '2025-01-01 00:00:00'::timestamp AND '2025-12-31 23:59:59'::timestamp "
     "GROUP BY order_date "
     "ORDER BY daily_total DESC "
     "LIMIT 10;"),

    # pseudocode: select count of inventory items from inventory and menu grouped by menu item
    # about: given a specific menu item, how many items from the inventory does that menu item use?
    # example: "classic milk tea uses 12 items"
    ("Special Query #4: Menu Item Inventory",
     "SELECT mi.name AS menu_item, COUNT(jri.inventory_item_id) AS num_ingredients "
     "FROM menu_items mi "
     "JOIN joint_recipe_ingredients jri ON mi.id = jri.menu_item_id "
     "WHERE mi.name = 'Classic Pearl Milk Tea' "
     "GROUP BY mi.name;")
]

# Write the documentation text file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("-- 15 REQUIRED QUERIES\n\n")
    for description, sql in queries:
        f.write(f"\"{description}\"\n")
        f.write(sql + "\n\n")
    f.write("\n-- 4 SPECIAL QUERIES\n\n")
    for description, sql in special_queries:
        f.write(f"\"{description}\"\n")
        f.write(sql + "\n\n")

print(f"Done! {len(queries)} queries and {len(special_queries)} special queries written and documented in '{OUTPUT_FILE}'")
