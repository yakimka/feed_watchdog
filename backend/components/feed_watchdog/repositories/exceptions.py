class ValueExistsError(Exception):
    """Exception raised when a value already exists in the storage."""

    def __init__(self, value: str, field: str) -> None:
        message = (
            f"Object with value '{value}' in field '{field}' already exists in"
            " storage."
        )
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value
