import random
import datetime



# name of sql query file
OUTPUT_FILE = "seed_data.sql"

# menu_items
# (name, price, description)
MENU_ITEMS = [ #Price between 3.5 and 7.0, in intervals of 0.25
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

# inventory items
INVENTORY_ITEMS = [
    "Black Tea Leaves", "Green Tea Leaves", "Sugar", "Milk", "Condensed Milk",
    "Coconut Milk", "Matcha Powder", "Taro Powder", "Chocolate Syrup", "Mango Syrup",
    "Strawberry Syrup", "Lychee Syrup", "Lemon Juice", "Honey", "Coffee Beans",
    "Whipped Cream", "Oreo Crumbs", "Pudding Mix", "Jelly Mix", "Tapioca Pearls",
    "Ice Cubes", "Cups", "Lids", "Straws", "Napkins"
]

# CONSTANTS
NUM_WEEKS = 52
TOTAL_SALES_TARGET = 1_000_000  # ~ $1M target for team of 5
PEAK_DAYS = 2
NUM_ORDERS = 20000  # adjust until sales ~ 1M


# HELPER FUNCTIONS

# generates random date for orders
def random_date(start, end):
    """Generate random datetime between two datetimes."""
    delta = end - start
    int_delta = delta.days * 24 * 60 * 60
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)



# data generation

menu_item_records = []
inventory_records = []
order_records = []
joint_order_item_records = []
joint_recipe_ingredient_records = []

# IDs start from 1
menu_item_id_map = {}
inventory_item_id_map = {}

# --- Insert Menu Items ---
for i, (name, price, desc) in enumerate(MENU_ITEMS, start=1):
    menu_item_records.append(f"INSERT INTO menu_items (id, name, price, is_mod, description) VALUES ({i}, '{name}', {price}, {False}, '{desc}');")
    menu_item_id_map[name] = i
for i, (name, price, desc) in enumerate(ADDON_ITEMS, start=len(MENU_ITEMS)+1):
    menu_item_records.append(f"INSERT INTO menu_items (id, name, price, is_mod, description) VALUES ({i}, '{name}', {price}, {True}, '{desc}');")
    menu_item_id_map[name] = i

# --- Insert Inventory Items ---
for j, name in enumerate(INVENTORY_ITEMS, 1):
    quantity = random.randint(500, 2000)
    restock_price = round(random.uniform(5, 50), 2)
    inventory_records.append(f"INSERT INTO inventory (id, name, quantity, restock_price) VALUES ({j}, '{name}', {quantity}, {restock_price});")
    inventory_item_id_map[name] = j

# --- Define Recipes (menu_items -> inventory items) ---
for (name, _, _) in MENU_ITEMS:  # main drinks only
    menu_id = menu_item_id_map[name]
    needed_ingredients = random.sample(INVENTORY_ITEMS, random.randint(2, 5))
    for ingr in needed_ingredients:
        qty_used = random.randint(1, 3)
        ingr_id = inventory_item_id_map[ingr]
        joint_recipe_ingredient_records.append(
            f"INSERT INTO joint_recipe_ingredients (menu_item_id, inventory_item_id, quantity_used) VALUES ({menu_id}, {ingr_id}, {qty_used});"
        )

# --- Insert Orders ---
start_date = datetime.datetime.now() - datetime.timedelta(weeks=NUM_WEEKS)
end_date = datetime.datetime.now()

for order_id in range(1, NUM_ORDERS + 1):
    customer_id = random.randint(1, 2000)
    employee_id = random.randint(1, 50)
    complete_time = random_date(start_date, end_date).strftime('%Y-%m-%d %H:%M:%S')
    
    # pick 1-3 items per order
    items = random.sample(MENU_ITEMS, random.randint(1, 3))
    order_total = sum([price for (_, price, _) in items])
    pearls_earned = int(order_total // 2)
    
    order_records.append(
        f"INSERT INTO orders (id, customer_id, complete_time, order_total_price, pearls_earned, employee_id) "
        f"VALUES ({order_id}, {customer_id}, '{complete_time}', {order_total:.2f}, {pearls_earned}, {employee_id});"
    )
    
    # link order -> items
    for (item, _, _) in items:
        item_id = menu_item_id_map[item]
        joint_order_item_records.append(
            f"INSERT INTO joint_order_item (order_id, menu_item_id) VALUES ({order_id}, {item_id});"
        )

# ----------------------------
# Write to .sql file
# ----------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("-- MENU ITEMS\n")
    f.write("\n".join(menu_item_records) + "\n\n")
    print('PASSED MENU ITEMS')
    f.write("-- INVENTORY\n")
    f.write("\n".join(inventory_records) + "\n\n")
    
    f.write("-- RECIPES\n")
    f.write("\n".join(joint_recipe_ingredient_records) + "\n\n")
    
    f.write("-- ORDERS\n")
    f.write("\n".join(order_records) + "\n\n")
    
    f.write("-- ORDER -> ITEMS\n")
    f.write("\n".join(joint_order_item_records) + "\n\n")

print(f"✅ Done! SQL data written to {OUTPUT_FILE}")
