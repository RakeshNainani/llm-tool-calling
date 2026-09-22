"""Tool schemas exposed to LLM providers."""


ORDER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": (
                "Get the current fulfillment status and estimated "
                "delivery date for a single order using its order ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Unique order identifier.",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_orders",
            "description": (
                "Get the order IDs associated with a customer "
                "using the customer's unique customer ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Unique customer identifier.",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
]