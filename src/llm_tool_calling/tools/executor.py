"""Tool execution logic."""

import json
from typing import Any

from llm_tool_calling.tools.registry import TOOL_REGISTRY


def execute_tool(
    tool_name: str,
    raw_arguments: str,
) -> Any:
    """Validate and execute a registered tool."""

    tool = TOOL_REGISTRY.get(tool_name)

    if tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    arguments = json.loads(raw_arguments)

    validator = tool["validator"]
    validated_args = validator.model_validate(arguments)

    function = tool["function"]

    return function(**validated_args.model_dump())