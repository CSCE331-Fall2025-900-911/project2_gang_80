CREATE TABLE menu_items (
id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
name VARCHAR(64) NOT NULL,
price NUMERIC(10,2) NOT NULL,
description VARCHAR(255),
is_modification bool NOT NULL
);

CREATE TABLE employees (
id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
name VARCHAR(64) NOT NULL,
email VARCHAR(64),
is_manager BOOLEAN NOT NULL
);

CREATE TABLE inventory (
id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
name VARCHAR(64) NOT NULL,
quantity INT NOT NULL,
restock_price NUMERIC(10,2) NOT NULL
);

CREATE TABLE customers (
id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
name VARCHAR(64) NOT NULL,
phone_number VARCHAR(15) NOT NULL,
pearls INT NOT NULL
);

CREATE TABLE orders (
id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
customer_id INT,
timestamp timestamp NOT NULL,
total_price NUMERIC(10,2) NOT NULL,
pearls_earned INT,
employee_id INT NOT NULL,
CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE joint_order_items (
order_id INT NOT NULL,
menu_item_id INT NOT NULL,
CONSTRAINT fk_order_id FOREIGN KEY (order_id) REFERENCES orders(id),
CONSTRAINT fk_menu_item_id FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);

CREATE TABLE joint_recipe_ingredients (
menu_item_id INT NOT NULL,
inventory_item_id INT NOT NULL,
quantity_used INT NOT NULL,
CONSTRAINT fk_menu_item_id FOREIGN KEY (menu_item_id) REFERENCES menu_items(id),
CONSTRAINT fk_inventory_item_id FOREIGN KEY (inventory_item_id) REFERENCES inventory(id)
);