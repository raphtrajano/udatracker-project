import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

# ==================== ADD ORDER TESTS ====================

# --- add_order: success cases ---

# Example test provided by project instrunctions
def test_add_order_success(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()

# Example test provided by project instrunctions
def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

# --- add_order: default status ---

def test_add_order_default_status(order_tracker, mock_storage):
    """Tests that a new order is saved with the default 'pending' status."""
    order_tracker.add_order("ORD002", "Iphone", 2, "CUST002")

    # Inspect what was actually passed to save_order
    saved_order = mock_storage.save_order.call_args[0][0]
    assert saved_order['status'] == 'pending'

# --- add_order: explicit status ---

def test_add_order_explicit_status_processing(order_tracker, mock_storage):
    """Tests that a new order is saved with 'processing' status when explicitly set."""
    order_tracker.add_order("ORD003", "Charger", 1, "CUST002", status="processing")

    saved_order = mock_storage.save_order.call_args[0][0]
    assert saved_order['status'] == 'processing'

def test_add_order_explicit_status_shipped(order_tracker, mock_storage):
    """Tests that a new order is saved with 'shipped' status when explicitly set."""
    order_tracker.add_order("ORD004", "Headphones", 1, "CUST002", status="shipped")

    saved_order = mock_storage.save_order.call_args[0][0]
    assert saved_order['status'] == 'shipped'

def test_add_order_explicit_status_delivered(order_tracker, mock_storage):
    """Tests that a new order is saved with 'delivered' status when explicitly set."""
    order_tracker.add_order("ORD005", "Phone case", 1, "CUST002", status="delivered")

    saved_order = mock_storage.save_order.call_args[0][0]
    assert saved_order['status'] == 'delivered'

def test_add_order_explicit_status_cancelled(order_tracker, mock_storage):
    """Tests that a new order is saved with 'cancelled' status when explicitly set."""
    order_tracker.add_order("ORD006", "Phone stickers", 4, "CUST002", status="cancelled")

    saved_order = mock_storage.save_order.call_args[0][0]
    assert saved_order['status'] == 'cancelled'

# --- add_order: invalid quantity ---

def test_add_order_raises_error_if_quantity_is_zero(order_tracker):
    """Tests that adding an order with a non-positive quantity raises a ValueError."""
    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD007", "Invalid Item", 0, "CUST003")

def test_add_order_raises_error_if_quantity_is_negative(order_tracker):
    """Tests that adding an order with a negative quantity raises a ValueError."""
    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD008", "Invalid Item", -1, "CUST003")
    
def test_add_order_raises_error_if_quantity_is_not_a_number(order_tracker):
    """Tests that adding an order with a non-integer quantity raises a ValueError."""
    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD009", "Invalid Item", "e", "CUST003")

# --- add_order: missing required fields ---

def test_add_order_raises_error_if_missing_order_id(order_tracker):
    """Tests that adding an order with missing order_id raises a ValueError."""
    with pytest.raises(ValueError, match="Missing required field"):
        order_tracker.add_order(None, "Item", 1, "CUST004")

def test_add_order_raises_error_if_missing_item_name(order_tracker):
    """Tests that adding an order with missing item_name raises a ValueError."""
    with pytest.raises(ValueError, match="Missing required field"):
        order_tracker.add_order("ORD010", None, 1, "CUST004")

def test_add_order_raises_error_if_missing_quantity(order_tracker):
    """Tests that adding an order with missing quantity raises a ValueError."""
    with pytest.raises(ValueError, match="Missing required field"):
        order_tracker.add_order("ORD011", "Item", None, "CUST004")

def test_add_order_raises_error_if_missing_customer_id(order_tracker):
    """Tests that adding an order with missing customer_id raises a ValueError."""
    with pytest.raises(ValueError, match="Missing required field"):
        order_tracker.add_order("ORD012", "Item", 1, None, status="pending")

# --- add_order: invalid initial status ---

def test_add_order_raises_error_if_initial_status_invalid(order_tracker):
    """Tests that adding an order with an invalid initial status raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid initial status: 'non_existent_status'"):
        order_tracker.add_order("ORD013", "Item", 1, "CUST005", status="non_existent_status")