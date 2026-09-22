"""Order-related tools."""


def get_order_status(order_id: str) -> dict:
    """Return the current status of an order."""

    orders = {
        "12345": {
            "order_id": "12345",
            "status": "shipped",
            "estimated_delivery": "2026-09-25",
        },
        "67890": {
            "order_id": "67890",
            "status": "processing",
            "estimated_delivery": "2026-09-28",
        },
    }

    return orders.get(
        order_id,
        {
            "order_id": order_id,
            "status": "not_found",
        },
    )