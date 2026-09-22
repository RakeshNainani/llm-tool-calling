"""Registry of tools available to the application."""

from llm_tool_calling.schemas.tools import GetOrderStatusArgs
from llm_tool_calling.tools.order_tools import get_order_status


TOOL_REGISTRY = {
    "get_order_status": {
        "function": get_order_status,
        "validator": GetOrderStatusArgs,
    }
}