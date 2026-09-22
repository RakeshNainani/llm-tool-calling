"""Tool execution logic."""

import json
from typing import Any
import logging
import time

from llm_tool_calling.tools.exceptions import ToolExecutionError
from llm_tool_calling.tools.registry import TOOL_REGISTRY
from pydantic import ValidationError

logger = logging.getLogger(__name__)

def execute_tool(
    tool_name: str,
    raw_arguments: str,
    *,
    request_id: str | None = None,
) -> Any:
    """Validate and execute a registered tool."""

    tool = TOOL_REGISTRY.get(tool_name)

    if tool is None:
        logger.warning(
            "Tool execution rejected: "
            "tool=%s request_id=%s error_type=unknown_tool",
            tool_name,
            request_id,
        )

        raise ToolExecutionError(
            f"Unknown tool: {tool_name}",
            error_type="unknown_tool",
            tool_name=tool_name,
        )

    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        logger.warning(
            "Tool execution rejected: "
            "tool=%s request_id=%s error_type=malformed_arguments",
            tool_name,
            request_id,
        )

        raise ToolExecutionError(
            "Tool arguments contain malformed JSON.",
            error_type="malformed_arguments",
            tool_name=tool_name,
        ) from exc

    validator = tool["validator"]

    try:
        validated_args = validator.model_validate(arguments)
    except ValidationError as exc:

        logger.warning(
            "Tool execution rejected: "
            "tool=%s request_id=%s error_type=invalid_arguments",
            tool_name,
            request_id,
        )

        raise ToolExecutionError(
            "Tool arguments failed validation.",
            error_type="invalid_arguments",
            tool_name=tool_name,
        ) from exc

    function = tool["function"]
    start_time = time.perf_counter()

    try:
        result = function(**validated_args.model_dump())

        duration_ms = ( time.perf_counter() - start_time) * 1000
        logger.info(
            "Tool execution succeeded: tool=%s request_id=%s duration_ms=%.2f",
            tool_name, 
            request_id,
            duration_ms,
        )

        return result

    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.exception(
            "Tool execution failed: "
            "tool=%s request_id=%s "
            "error_type=execution_failed duration_ms=%.2f",
            tool_name,
            request_id,
            duration_ms,
        )

        raise ToolExecutionError(
            "Tool execution failed.",
            error_type="execution_failed",
            tool_name=tool_name,
        ) from exc