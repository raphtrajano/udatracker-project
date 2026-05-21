# Custom exception types for the order management system.
# All exceptions subclass ValueError so any caller that catches
# ValueError continues to work without changes.


class OrderNotFoundError(ValueError):
    """Raised when an order cannot be found by the given ID."""
    pass


class DuplicateOrderError(ValueError):
    """Raised when attempting to create an order with an ID that already exists."""
    pass


class InvalidStatusError(ValueError):
    """Raised when a status value is not one of the recognised valid statuses."""
    pass


class MissingFieldError(ValueError):
    """Raised when a required field is absent or empty."""
    pass


class InvalidQuantityError(ValueError):
    """Raised when an order quantity is not a positive integer."""
    pass
