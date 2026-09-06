import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'crm-erp'))
from db import get_product_stock, get_contact_by_handle


def verify_order(instagram_handle, items):
    """
    items: [{"sku": "HOOD-BLK-M", "quantity": 2}, ...]
    Checks a proposed order against real, live data before it's allowed
    to become a real order. Returns APPROVED or REJECTED with a reason.
    """
    contact = get_contact_by_handle(instagram_handle)
    if contact is None:
        return {
            "decision": "REJECTED",
            "reason": f"No known contact for @{instagram_handle}. Escalate to human."
        }

    for item in items:
        product = get_product_stock(item["sku"])
        if product is None:
            return {
                "decision": "REJECTED",
                "reason": f"Unknown SKU: {item['sku']}. This product doesn't exist in our catalog."
            }
        if product["stock_qty"] < item["quantity"]:
            return {
                "decision": "REJECTED",
                "reason": (
                    f"Insufficient stock for {item['sku']}: "
                    f"requested {item['quantity']}, only {product['stock_qty']} available."
                )
            }

    return {
        "decision": "APPROVED",
        "reason": "All items in stock, contact verified. Safe to create order."
    }


if __name__ == "__main__":
    # Test case 1: should APPROVE
    result1 = verify_order("rahul.streetwear", [{"sku": "HOOD-BLK-M", "quantity": 2}])
    print("Test 1 (valid order):", result1)

    # Test case 2: should REJECT - not enough stock
    result2 = verify_order("rahul.streetwear", [{"sku": "SNK-RUN-9", "quantity": 50}])
    print("Test 2 (oversell attempt):", result2)

    # Test case 3: should REJECT - unknown product
    result3 = verify_order("rahul.streetwear", [{"sku": "FAKE-SKU-999", "quantity": 1}])
    print("Test 3 (invalid SKU):", result3)
