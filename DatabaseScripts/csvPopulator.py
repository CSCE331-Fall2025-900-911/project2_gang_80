import random
import datetime
import csv

# ----------------------------
# Config
# ----------------------------
NUM_WEEKS = 52
TOTAL_SALES_TARGET = 1_000_000
PEAK_DAYS = 2
NUM_ORDERS = 20000
NUM_CUSTOMERS = 2000
NUM_EMPLOYEES = 15
NUM_MANAGERS = 3

# ----------------------------
# Static data
# ----------------------------
MENU_ITEMS = [
    ("Classic Pearl Milk Tea", 15.5, "yummy Classic Pearl Milk Tea!"),
    ("Honey Pearl Milk Tea", 20.75, "yummy Honey Pearl Milk Tea!"),
    ("Coffee Creama", 20.5, "yummy Coffee Creama!"),
    ("Thai Pearl Milk Tea", 20.25, "yummy Thai Pearl Milk Tea!"),
    ("Mango Green Milk Tea", 20.0, "yummy Mango Green Milk Tea!"),
    ("Taro Pearl Milk Tea", 20.0, "yummy Taro Pearl Milk Tea!"),
    ("Hokkaido Pearl Milk Tea", 30.5, "yummy Hokkaido Pearl Milk Tea!"),
    ("Cocounut Pearl Milk Tea", 15.75, "yummy Cocounut Pearl Milk Tea!"),
    ("Mango Green Tea", 15.5, "yummy Mango Green Tea!"),
    ("Berry Lychee Burst", 30.0, "yummy Berry Lychee Burst!"),
    ("Honey Lemonade", 24.5, "yummy Honey Lemonade!"),
    ("Wintermelon Lemonade", 24.75, "yummy Wintermelon Lemonade!"),
    ("Halo Halo", 25.5, "yummy Halo Halo!"),
    ("Matcha Pearl Milk Tea", 20.5, "yummy Matcha Pearl Milk Tea!"),
    ("Strawberry Matcha Fresh Milk", 20.25, "yummy Strawberry Matcha Fresh Milk!"),
    ("Mango Matcha Fresh Milk", 20.0, "yummy Mango Matcha Fresh Milk!"),
    ("Oreo w/ Pearl", 25.75, "yummy Oreo w/ Pearl!"),
    ("Taro w/ Pudding", 31.5, "yummy Taro w/ Pudding!"),
    ("Lava Flow", 30.0, "yummy Lava Flow!"),
    ("Peach Tea w/ Lychee Jelly", 16.5, "yummy Peach Tea w/ Lychee Jelly!"),
]

ADDON_ITEMS = [
    ("Boba", 0.75, "add boba to any drink"),
    ("Coffee Jelly", 0.75, "add coffee jelly to any drink"),
    ("Pudding", 0.75, "add pudding to any drink"),
    ("Lychee Jelly", 0.75, "add lychee jelly to any drink"),
    ("Honey Jelly", 0.75, "add honey jelly to any drink"),
    ("Crystal Boba", 0.75, "add crystal boba to any drink"),
    ("Mango Popping Boba", 0.75, "add mango popping boba to any drink"),
    ("Strawberry Popping Boba", 0.75, "add strawberry popping boba to any drink"),
    ("Ice Cream", 0.75, "add ice cream to any drink"),
    ("Crema", 0.75, "add crema to any drink"),
    ("Less Ice", 0.0, "less ice in any drink"),
    ("No Ice", 0.0, "no ice in any drink"),
    ("Less Sweetness", 0.0, "less sweetness in any drink"),
    ("Half Sweetness", 0.0, "half sweetness in any drink"),
    ("Light Sweetness", 0.0, "light sweetness in any drink"),
    ("No Sugar", 0.0, "no sugar in any drink"),
]

INVENTORY_ITEMS = [
    "Black Tea Leaves", "Green Tea Leaves", "Sugar", "Milk", "Condensed Milk",
    "Coconut Milk", "Matcha Powder", "Taro Powder", "Chocolate Syrup", "Mango Syrup",
    "Strawberry Syrup", "Lychee Syrup", "Lemon Juice", "Honey", "Coffee Beans",
    "Whipped Cream", "Oreo Crumbs", "Pudding Mix", "Jelly Mix", "Tapioca Pearls",
    "Ice Cubes", "Cups", "Lids", "Straws", "Napkins"
]

# ----------------------------
# Helpers
# ----------------------------
def random_date(start, end):
    """Generate random datetime between two datetimes."""
    delta = end - start
    int_delta = delta.days * 24 * 60 * 60
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)

# ----------------------------
# Data generation
# ----------------------------
employees = []
customers = []
menu_items = []
inventory = []
orders = []
joint_order_items = []
joint_recipe_ingredients = []

menu_item_id_map = {}
inventory_item_id_map = {}

# Employees
for i in range(1, NUM_EMPLOYEES + 1):
    employees.append([i, f"Employee{i}", f"employee{i}@teaone.com", (i <= NUM_MANAGERS)])

# Customers
for i in range(1, NUM_CUSTOMERS + 1):
    phone_number = random.randint(1000000000, 9999999999)
    pearls = random.randint(0, 200)
    customers.append([i, f"Customer{i}", phone_number, pearls])

# Menu Items
id_counter = 1
for (name, price, desc) in MENU_ITEMS:
    menu_items.append([id_counter, name, price, desc, False])
    menu_item_id_map[name] = id_counter
    id_counter += 1
for (name, price, desc) in ADDON_ITEMS:
    menu_items.append([id_counter, name, price, desc, True])
    menu_item_id_map[name] = id_counter
    id_counter += 1

# Inventory
for j, name in enumerate(INVENTORY_ITEMS, 1):
    quantity = random.randint(500, 2000)
    restock_price = round(random.uniform(5, 50), 2)
    inventory.append([j, name, quantity, restock_price])
    inventory_item_id_map[name] = j

# Recipes
for (name, _, _) in MENU_ITEMS:
    menu_id = menu_item_id_map[name]
    needed_ingredients = random.sample(INVENTORY_ITEMS, random.randint(2, 5))
    for ingr in needed_ingredients:
        qty_used = random.randint(1, 3)
        ingr_id = inventory_item_id_map[ingr]
        joint_recipe_ingredients.append([menu_id, ingr_id, qty_used])

# Orders + Joint Order Items
start_date = datetime.datetime.now() - datetime.timedelta(weeks=NUM_WEEKS)
end_date = datetime.datetime.now()

peaks = [random_date(start_date, end_date).date() for _ in range(PEAK_DAYS)]
for order_id in range(1, NUM_ORDERS + 1):
    customer_id = random.randint(1, NUM_CUSTOMERS)
    employee_id = random.randint(1, NUM_EMPLOYEES)
    complete_time = random_date(start_date, end_date)
    complete_date = complete_time.date()
    complete_time = complete_time.strftime('%Y-%m-%d %H:%M:%S')
    
    items = random.sample(MENU_ITEMS, random.randint(1, 3))
    if complete_date in peaks:
        items = random.sample(MENU_ITEMS, random.randint(3, 9))
    order_total = sum([price for (_, price, _) in items])
    pearls_earned = int(order_total // 2)
    
    orders.append([order_id, customer_id, complete_time, round(order_total, 2), pearls_earned, employee_id])
    
    for (item, _, _) in items:
        joint_order_items.append([order_id, menu_item_id_map[item]])

# ----------------------------
# Write CSV files
# ----------------------------
def write_csv(filename, header, rows):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

write_csv("employees.csv", ["id", "name", "email", "is_manager"], employees)
write_csv("customers.csv", ["id", "name", "phone_number", "pearls"], customers)
write_csv("menu_items.csv", ["id", "name", "price", "description", "is_mod"], menu_items)
write_csv("inventory.csv", ["id", "name", "quantity", "restock_price"], inventory)
write_csv("orders.csv", ["id", "customer_id", "complete_time", "order_total_price", "pearls_earned", "employee_id"], orders)
write_csv("joint_order_items.csv", ["order_id", "menu_item_id"], joint_order_items)
write_csv("joint_recipe_ingredients.csv", ["menu_item_id", "inventory_item_id", "quantity_used"], joint_recipe_ingredients)

print("✅ Done! CSV files generated for all tables.")
