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

# Example test provided by project instructions
def test_add_order_success(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()

# Example test provided by project instructions
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

    saved_order = mock_storage.save_order.call_args[0][1]
    assert saved_order['status'] == 'pending'

# --- add_order: explicit status ---

def test_add_order_explicit_status_processing(order_tracker, mock_storage):
    """Tests that a new order is saved with 'processing' status when explicitly set."""
    order_tracker.add_order("ORD003", "Charger", 1, "CUST002", status="processing")

    saved_order = mock_storage.save_order.call_args[0][1]
    assert saved_order['status'] == 'processing'

def test_add_order_explicit_status_shipped(order_tracker, mock_storage):
    """Tests that a new order is saved with 'shipped' status when explicitly set."""
    order_tracker.add_order("ORD004", "Headphones", 1, "CUST002", status="shipped")

    saved_order = mock_storage.save_order.call_args[0][1]
    assert saved_order['status'] == 'shipped'

def test_add_order_explicit_status_delivered(order_tracker, mock_storage):
    """Tests that a new order is saved with 'delivered' status when explicitly set."""
    order_tracker.add_order("ORD005", "Phone case", 1, "CUST002", status="delivered")

    saved_order = mock_storage.save_order.call_args[0][1]
    assert saved_order['status'] == 'delivered'

def test_add_order_explicit_status_cancelled(order_tracker, mock_storage):
    """Tests that a new order is saved with 'cancelled' status when explicitly set."""
    order_tracker.add_order("ORD006", "Phone stickers", 4, "CUST002", status="cancelled")

    saved_order = mock_storage.save_order.call_args[0][1]
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

# ==================== GET ORDER BY ID TESTS ====================

# --- get_order_by_id: success cases ---

def test_get_order_by_id_returns_order(order_tracker, mock_storage):
    """Tests that getting an order by ID returns the correct order."""
    expected_order = {
        "order_id": "ORD014",
        "item_name": "Test Item",
        "quantity": 1,
        "customer_id": "CUST006",
        "status": "pending"
    }
    mock_storage.get_order.return_value = expected_order

    order = order_tracker.get_order_by_id("ORD014")
    assert order['order_id'] == "ORD014"
    assert order['item_name'] == "Test Item"
    assert order['quantity'] == 1
    assert order['customer_id'] == "CUST006"
    assert order['status'] == "pending"

# --- get_order_by_id: error cases ---
def test_get_order_by_id_returns_none_for_nonexistent_order(order_tracker):
    """Tests that getting a non-existent order by ID returns None."""
    order = order_tracker.get_order_by_id("ORD999")
    assert order is None

def test_get_order_by_id_raises_error_if_order_id_is_none(order_tracker):
    """Tests that getting an order with None as ID raises a ValueError."""
    with pytest.raises(ValueError, match="Order ID cannot be empty."):
        order_tracker.get_order_by_id(None)

def test_get_order_by_id_raises_error_if_order_id_is_empty(order_tracker):
    """Tests that getting an order with an empty string ID raises a ValueError."""
    with pytest.raises(ValueError, match="Order ID cannot be empty."):
        order_tracker.get_order_by_id("")

# ==================== UPDATE ORDER STATUS TESTS ====================

# --- update_order_status: success cases ---

def test_update_order_status_success(order_tracker, mock_storage):
    """Tests that updating an order's status successfully changes the status."""
    order_id = "ORD015"
    new_status = "shipped"
    mock_storage.get_order.return_value = {"order_id": order_id, "status": "pending"}

    order_tracker.update_order_status(order_id, new_status)

    mock_storage.save_order.assert_called_once_with(order_id, {"order_id": order_id, "status": new_status})

# --- update_order_status: invalid status (fail fast) ---

def test_update_order_status_raises_error_if_status_invalid(order_tracker, mock_storage):
    """Tests that an invalid status raises ValueError before any storage read."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.update_order_status("ORD015", "non_existent_status")

    # Fail fast: storage should never be touched
    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()

# --- update_order_status: non-existent order ---

def test_update_order_status_raises_error_if_order_not_found(order_tracker, mock_storage):
    """Tests that updating a non-existent order raises a ValueError."""
    mock_storage.get_order.return_value = None  

    with pytest.raises(ValueError, match="Order with ID 'ORD111' not found."):
        order_tracker.update_order_status("ORD111", "shipped")

    mock_storage.get_order.assert_called_once_with("ORD111")

# --- update_order_status: empty/None ID ---

def test_update_order_status_raises_error_if_order_id_is_empty(order_tracker, mock_storage):
    """Tests that an empty order ID raises ValueError before any storage read."""
    with pytest.raises(ValueError, match="Order ID cannot be empty."):
        order_tracker.update_order_status("", "shipped")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()

def test_update_order_status_raises_error_if_order_id_is_none(order_tracker, mock_storage):
    """Tests that a None order ID raises ValueError before any storage read."""
    with pytest.raises(ValueError, match="Order ID cannot be empty."):
        order_tracker.update_order_status(None, "shipped")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()

# ==================== LIST ALL ORDERS TESTS ====================

# --- list_all_orders: success cases ---

def test_list_all_orders_returns_all_orders(order_tracker, mock_storage):
    """Tests that listing all orders returns all orders as a list of dicts."""
    order1 = {"order_id": "ORD016", "item_name": "Test Item 16", "quantity": 1, "customer_id": "CUST007", "status": "pending"}
    order2 = {"order_id": "ORD017", "item_name": "Test Item 17", "quantity": 2, "customer_id": "CUST008", "status": "shipped"}
    order3 = {"order_id": "ORD250", "item_name": "Test Item 250", "quantity": 5, "customer_id": "CUST010", "status": "processing"}
    order4 = {"order_id": "ORD999", "item_name": "Test Item 999", "quantity": 3, "customer_id": "CUST009", "status": "delivered"}

    mock_storage.get_all_orders.return_value = {
        "ORD016": order1, "ORD017": order2, "ORD250": order3, "ORD999": order4
    }

    orders = order_tracker.list_all_orders()

    assert isinstance(orders, list)
    assert len(orders) == 4
    assert order1 in orders
    assert order2 in orders
    assert order3 in orders
    assert order4 in orders

# --- list_all_orders: empty storage case ---

def test_list_all_orders_returns_empty_list_when_no_orders(order_tracker, mock_storage):
    """Tests that listing all orders returns an empty list when storage is empty."""
    mock_storage.get_all_orders.return_value = {}

    orders = order_tracker.list_all_orders()

    assert orders == []

# ==================== LIST ORDERS BY STATUS TESTS ====================

# --- list_orders_by_status: success cases ---

def test_list_orders_by_status_returns_only_matching_orders(order_tracker, mock_storage):
    """Tests that listing orders by status returns only orders with that status."""
    order1 = {"order_id": "ORD018", "item_name": "Test Item 18", "quantity": 1, "customer_id": "CUST011", "status": "pending"}
    order2 = {"order_id": "ORD019", "item_name": "Test Item 19", "quantity": 2, "customer_id": "CUST012", "status": "shipped"}
    order3 = {"order_id": "ORD020", "item_name": "Test Item 20", "quantity": 5, "customer_id": "CUST013", "status": "pending"}

    mock_storage.get_all_orders.return_value = {
        "ORD018": order1, 
        "ORD019": order2, 
        "ORD020": order3
    }

    pending_orders = order_tracker.list_orders_by_status("pending")

    assert isinstance(pending_orders, list)
    assert len(pending_orders) == 2
    assert all(order['status'] == 'pending' for order in pending_orders)

# --- list_orders_by_status: no matching orders ---

def test_list_orders_by_status_returns_empty_list_if_no_matching_orders(order_tracker, mock_storage):
    """Tests that listing orders by status returns an empty list if no orders match."""
    order1 = {"order_id": "ORD021", "item_name": "Test Item 21", "quantity": 1, "customer_id": "CUST014", "status": "shipped"}
    order2 = {"order_id": "ORD022", "item_name": "Test Item 22", "quantity": 2, "customer_id": "CUST015", "status": "delivered"}

    mock_storage.get_all_orders.return_value = {
        "ORD021": order1, 
        "ORD022": order2
    }

    pending_orders = order_tracker.list_orders_by_status("pending")

    assert pending_orders == []

# --- list_orders_by_status: empty storage case ---

def test_list_orders_by_status_returns_empty_list_if_no_orders_in_storage(order_tracker, mock_storage):
    """Tests that listing orders by status returns an empty list if storage has no orders."""
    mock_storage.get_all_orders.return_value = {}

    pending_orders = order_tracker.list_orders_by_status("pending")

    assert pending_orders == []

# --- list_orders_by_status: invalid status ---

def test_list_orders_by_status_raises_error_if_status_invalid(order_tracker):
    """Tests that listing orders by an invalid status raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid status: 'non_existent_status'"):
        order_tracker.list_orders_by_status("non_existent_status")

# --- list_orders_by_status: empty status ---

def test_list_orders_by_status_raises_error_if_status_empty(order_tracker):
    """Tests that listing orders by an empty status raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid status: ''"):
        order_tracker.list_orders_by_status("")