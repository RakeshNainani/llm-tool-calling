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
    }
]