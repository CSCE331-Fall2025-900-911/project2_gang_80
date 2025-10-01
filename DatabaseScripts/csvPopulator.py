import random
import datetime
import csv

# ----------------------------
# CONFIG
# ----------------------------
NUM_WEEKS = 52
NUM_ORDERS = 20000
OUTPUT_DIR = "./"  # folder where CSVs will be saved

MENU_ITEMS = [ # (name, price, description)
    ("Classic Pearl Milk Tea", 3.5, "yummy Classic Pearl Milk Tea!"),
    ("Honey Pearl Milk Tea", 4.75, "yummy Honey Pearl Milk Tea!"),
    ("Coffee Creama", 4.5, "yummy Coffee Creama!"),
    ("Thai Pearl Milk Tea", 4.25, "yummy Thai Pearl Milk Tea!"),
    ("Mango Green Milk Tea", 4.0, "yummy Mango Green Milk Tea!"),
    ("Taro Pearl Milk Tea", 4.0, "yummy Taro Pearl Milk Tea!"),
    ("Hokkaido Pearl Milk Tea", 6.5, "yummy Hokkaido Pearl Milk Tea!"),
    ("Cocounut Pearl Milk Tea", 3.75, "yummy Cocounut Pearl Milk Tea!"),
    ("Mango Green Tea", 3.5, "yummy Mango Green Tea!"),
    ("Berry Lychee Burst", 6.0, "yummy Berry Lychee Burst!"),
    ("Honey Lemonade", 3.5, "yummy Honey Lemonade!"),
    ("Wintermelon Lemonade", 3.75, "yummy Wintermelon Lemonade!"),
    ("Halo Halo", 5.5, "yummy Halo Halo!"),
    ("Matcha Pearl Milk Tea", 4.5, "yummy Matcha Pearl Milk Tea!"),
    ("Strawberry Matcha Fresh Milk",4.25, "yummy Strawberry Matcha Fresh Milk!"),
    ("Mango Matcha Fresh Milk", 4.0, "yummy Mango Matcha Fresh Milk!"),
    ("Oreo w/ Pearl", 4.75, "yummy Oreo w/ Pearl!"),
    ("Taro w/ Pudding", 4.5, "yummy Taro w/ Pudding!"),
    ("Lava Flow", 6.0, "yummy Lava Flow!"),
    ("Peach Tea w/ Lychee Jelly", 3.5, "yummy Peach Tea w/ Lychee Jelly!"),
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
    ("Crema" , 0.75, "add crema to any drink"),
    ("Less Ice", 0.0, "less ice in any drink"),
    ("No Ice", 0.0, "no ice in any drink"),
    ("Less Sweetness", 0.0, "less sweetness in any drink"),
    ("Half Sweetness", 0.0, "half sweetness in any drink"),
    ("Light Sweetness", 0.0, "light sweetness in any drink"),
    ("No Sugar" , 0.0, "no sugar in any drink"),
]

INVENTORY_ITEMS = [
    "Black Tea Leaves", "Green Tea Leaves", "Sugar", "Milk", "Condensed Milk",
    "Coconut Milk", "Matcha Powder", "Taro Powder", "Chocolate Syrup", "Mango Syrup",
    "Strawberry Syrup", "Lychee Syrup", "Lemon Juice", "Honey", "Coffee Beans",
    "Whipped Cream", "Oreo Crumbs", "Pudding Mix", "Jelly Mix", "Tapioca Pearls",
    "Ice Cubes", "Cups", "Lids", "Straws", "Napkins"
]

# ----------------------------
# HELPERS
# ----------------------------

def random_date(start, end):
    """Generate random datetime between two datetimes."""
    delta = end - start
    int_delta = delta.days * 24 * 60 * 60
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)

# ----------------------------
# DATA GENERATION
# ----------------------------

menu_items = []
inventory = []
orders = []
joint_order_items = []
joint_recipe_ingredients = []

menu_item_id_map = {}
inventory_item_id_map = {}

# --- Menu Items ---
for i, (name, price, desc) in enumerate(MENU_ITEMS, start=1):
    menu_items.append([i, name, price, False, desc])
    menu_item_id_map[name] = i

for i, (name, price, desc) in enumerate(ADDON_ITEMS, start=len(MENU_ITEMS)+1):
    menu_items.append([i, name, price, True, desc])
    menu_item_id_map[name] = i

# --- Inventory ---
for j, name in enumerate(INVENTORY_ITEMS, 1):
    quantity = random.randint(500, 2000)
    restock_price = round(random.uniform(5, 50), 2)
    inventory.append([j, name, quantity, restock_price])
    inventory_item_id_map[name] = j

# --- Recipes ---
for (name, _, _) in MENU_ITEMS:  # only base drinks
    menu_id = menu_item_id_map[name]
    needed_ingredients = random.sample(INVENTORY_ITEMS, random.randint(2, 5))
    for ingr in needed_ingredients:
        qty_used = random.randint(1, 3)
        ingr_id = inventory_item_id_map[ingr]
        joint_recipe_ingredients.append([menu_id, ingr_id, qty_used])

# --- Orders ---
start_date = datetime.datetime.now() - datetime.timedelta(weeks=NUM_WEEKS)
end_date = datetime.datetime.now()

for order_id in range(1, NUM_ORDERS + 1):
    customer_id = random.randint(1, 2000)
    employee_id = random.randint(1, 50)
    complete_time = random_date(start_date, end_date).strftime('%Y-%m-%d %H:%M:%S')

    items = random.sample(MENU_ITEMS, random.randint(1, 3))
    order_total = sum([price for (_, price, _) in items])
    pearls_earned = int(order_total // 2)

    orders.append([order_id, customer_id, complete_time, round(order_total, 2), pearls_earned, employee_id])

    for (item, _, _) in items:
        item_id = menu_item_id_map[item]
        joint_order_items.append([order_id, item_id])

# ----------------------------
# WRITE TO CSV FILES
# ----------------------------

def write_csv(filename, header, rows):
    with open(OUTPUT_DIR + filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

write_csv("menu_items.csv", ["id", "name", "price", "is_mod", "description"], menu_items)
write_csv("inventory.csv", ["id", "name", "quantity", "restock_price"], inventory)
write_csv("orders.csv", ["id", "customer_id", "complete_time", "order_total_price", "pearls_earned", "employee_id"], orders)
write_csv("joint_order_item.csv", ["order_id", "menu_item_id"], joint_order_items)
write_csv("joint_recipe_ingredients.csv", ["menu_item_id", "inventory_item_id", "quantity_used"], joint_recipe_ingredients)

print("✅ Done! CSV files written.")
