"""Exceptions raised during tool execution."""


class ToolExecutionError(Exception):
    """Raised when a tool request cannot be safely executed."""

    def __init__(
        self,
        message: str,
        *,
        error_type: str,
        tool_name: str,
    ) -> None:
        super().__init__(message)

        self.error_type = error_type
        self.tool_name = tool_name