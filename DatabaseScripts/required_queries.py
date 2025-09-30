# python script to generate 15 SQL queries that can be run as an input file to verify the low-level design and interactions

OUTPUT_FILE = "available_queries.txt"

# Queries with descriptions
queries = [
    ("Top 10 customers by orders in a given time period",
     "SELECT customer_id, COUNT(*) AS order_count "
     "FROM orders "
     "WHERE timestamp BETWEEN :start_date AND :end_date "
     "GROUP BY customer_id "
     "ORDER BY order_count DESC "
     "LIMIT 10;"),

    ("Top 10 customers by total spending in a given time period",
     "SELECT customer_id, SUM(total_price) AS total_spent "
     "FROM orders "
     "WHERE timestamp BETWEEN :start_date AND :end_date "
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
]

# Write the documentation text file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for description, sql in queries:
        f.write(f"\"{description}\"\n")
        f.write(sql + "\n\n")

print(f"Done! {len(queries)} queries written and documented in '{OUTPUT_FILE}'")
