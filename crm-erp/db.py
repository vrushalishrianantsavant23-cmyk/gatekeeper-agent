import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def get_contact_by_handle(handle):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM contacts WHERE instagram_handle = %s", (handle,))
        return cur.fetchone()


def get_product_stock(sku):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT sku, stock_qty FROM products WHERE sku = %s", (sku,))
        return cur.fetchone()


def create_order(contact_id, items):
    """
    items: [{"sku": "HOOD-BLK-M", "quantity": 2}, ...]
    Runs as one transaction — if any item is out of stock, nothing is written
    at all. FOR UPDATE locks the product row so two simultaneous orders can't
    both oversell the same last unit.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                total_amount = 0
                order_lines = []

                for item in items:
                    cur.execute(
                        "SELECT id, price, stock_qty FROM products WHERE sku = %s FOR UPDATE",
                        (item["sku"],)
                    )
                    product = cur.fetchone()
                    if product is None:
                        raise ValueError(f"Unknown product SKU: {item['sku']}")
                    if product["stock_qty"] < item["quantity"]:
                        raise ValueError(
                            f"Insufficient stock for {item['sku']}: "
                            f"requested {item['quantity']}, available {product['stock_qty']}"
                        )
                    order_lines.append((product["id"], item["quantity"], product["price"]))
                    total_amount += product["price"] * item["quantity"]

                cur.execute(
                    "INSERT INTO orders (contact_id, status, total_amount) "
                    "VALUES (%s, 'pending', %s) RETURNING id",
                    (contact_id, total_amount)
                )
                order_id = cur.fetchone()["id"]

                for product_id, quantity, unit_price in order_lines:
                    cur.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
                        "VALUES (%s, %s, %s, %s)",
                        (order_id, product_id, quantity, unit_price)
                    )
                    cur.execute(
                        "UPDATE products SET stock_qty = stock_qty - %s WHERE id = %s",
                        (quantity, product_id)
                    )

                return order_id
    finally:
        conn.close()


def update_deal_stage(contact_id, new_stage):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE deals SET stage = %s, updated_at = now() WHERE contact_id = %s RETURNING id",
            (new_stage, contact_id)
        )
        return cur.fetchone()
