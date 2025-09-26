import random
from datetime import datetime, timedelta

# ======================
# CONFIGURATION
# ======================
OUTPUT_FILE = "seed_data.sql"
WEEKS = 52
TOTAL_SALES_TARGET = 1_000_000  # ~ $1M
PEAK_DAYS = 2
MENU_ITEMS_COUNT = 20

# Editable product list
# BASE_PRODUCTS = [
#     "Espresso", "Americano", "Latte", "Cappuccino", "Mocha", "Flat White", "Cold Brew",
#     "Iced Coffee", "Chai Latte", "Matcha Latte", "Hot Chocolate", "Black Tea", "Green Tea",
#     "Bagel", "Croissant", "Muffin", "Ham & Cheese Sandwich", "Turkey Sandwich",
#     "Chicken Panini", "Caesar Salad", "Greek Salad", "Protein Bar", "Yogurt Parfait",
#     "Oatmeal", "Cookie", "Brownie"
# ]

# TODO: rename to menu_items instead (make sure you change all the variable mentions too )
BASE_PRODUCTS = ["Classic Pearl Milk Tea", "Honey Pearl Milk Tea", "Coffee Creama",
               "Thai Pearl Milk Tea", "Mango Green Milk Tea", "Taro Pearl Milk Tea",
               "Hokkaido Pearl Milk Tea", "Cocounut Pearl Milk Tea", "Mango Green Tea",
               "Berry Lychee Burst", "Honey Lemonade", "Wintermelon Lemonade",
               "Halo Halo", "Matcha Pearl Milk Tea", "Strawberry Matcha Fresh Milk",
               "Mango Matcha Fresh Milk", "Oreo w/ Pearl", "Taro w/ Pudding",
               "Lava Flow", "Peach Tea w/ Lychee Jelly", "Boba", "Coffee Jelly",
               "Pudding", "Lychee Jelly", "Honey Jelly", "Crystal Boba", "Mango Popping Boba",
               "Strawberry Popping Boba", "Ice Cream", "Crema", "Regular Ice", 
               "Less Ice", "No Ice", "Normal Sweetness", "Less Sweetness", "Half Sweetness",
               "Light Sweetness", "No Sugar"]


# ======================
# GENERATE MENU ITEMS
# ======================
def generate_menu_items():
    chosen = random.sample(BASE_PRODUCTS, MENU_ITEMS_COUNT)
    menu_items = []
    for i, product in enumerate(chosen, start=1):
        price = round(random.uniform(2.0, 10.0), 2)
        menu_items.append({
            "id": i,
            "name": product,
            "price": price,
            "description": f"Delicious {product.lower()}", # changed order
            "is_mod": False
        })
    return menu_items

# ======================
# GENERATE INVENTORY
# ======================
def generate_inventory(menu_items):
    inventory = []
    # Ingredients / supplies per menu item
    for i, item in enumerate(menu_items, start=1):
        inventory.append({
            "id": i,
            "name": f"{item['name']} Ingredient",
            "quantity": random.randint(50, 500),
            "restock_price": round(random.uniform(0.5, 5.0), 2)
        })
    # Add common items 
    # TODO: replace with actual ingredients
    extra_items = ["Cups", "Straws", "Napkins", "Bags"]
    for j, extra in enumerate(extra_items, start=len(inventory)+1):
        inventory.append({
            "id": j,
            "name": extra,
            "quantity": random.randint(500, 2000),
            "restock_price": round(random.uniform(0.01, 0.1), 2)
        })
    return inventory

# ======================
# GENERATE ORDERS
# ======================
def generate_orders(menu_items):
    start_date = datetime.now() - timedelta(weeks=WEEKS)
    end_date = datetime.now()

    orders = []
    current_id = 1

    days = (end_date - start_date).days
    avg_sales_per_day = TOTAL_SALES_TARGET / days

    # Pick peak days
    peak_days = random.sample(range(days), PEAK_DAYS)

    for d in range(days):
        date = start_date + timedelta(days=d)
        # Base daily sales
        sales_today = avg_sales_per_day * random.uniform(0.6, 1.4)
        if d in peak_days:
            sales_today *= 3  # Spike sales

        daily_total = 0
        while daily_total < sales_today:
            item = random.choice(menu_items)
            qty = random.randint(1, 3)
            order_total = round(item["price"] * qty, 2)

            orders.append({
                "id": current_id,
                "customer_id": random.randint(1, 500),
                "complete_time": date + timedelta(
                    hours=random.randint(8, 20),
                    minutes=random.randint(0, 59)
                ),
                "order_total_price": order_total,
                "pearls_earned": int(order_total // 5),
                "employee_id": random.randint(1, 20)
            })

            daily_total += order_total
            current_id += 1

    return orders

# ======================
# WRITE SQL
# ======================
def write_sql(menu_items, inventory, orders):
    with open(OUTPUT_FILE, "w") as f:
        # Menu Items
        for item in menu_items:
            f.write(f"INSERT INTO menu_items (id, name, price, is_mod, description) "
                    f"VALUES ({item['id']}, '{item['name']}', {item['price']}, "
                    f"{'TRUE' if item['is_mod'] else 'FALSE'}, '{item['description']}');\n")

        f.write("\n")

        # Inventory
        for item in inventory:
            f.write(f"INSERT INTO inventory (id, name, quantity, restock_price) "
                    f"VALUES ({item['id']}, '{item['name']}', {item['quantity']}, {item['restock_price']});\n")

        f.write("\n")

        # Orders
        for order in orders:
            f.write(f"INSERT INTO orders (id, customer_id, complete_time, order_total_price, pearls_earned, employee_id) "
                    f"VALUES ({order['id']}, {order['customer_id']}, "
                    f"'{order['complete_time'].strftime('%Y-%m-%d %H:%M:%S')}', "
                    f"{order['order_total_price']}, {order['pearls_earned']}, {order['employee_id']});\n")

    print(f"SQL data written to {OUTPUT_FILE}")

# ======================
# MAIN
# ======================
if __name__ == "__main__":
    menu_items = generate_menu_items()
    inventory = generate_inventory(menu_items)
    orders = generate_orders(menu_items)
    write_sql(menu_items, inventory, orders)
