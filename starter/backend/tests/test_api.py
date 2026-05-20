import pytest
from backend.app import app, in_memory_storage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

def test_add_order_api_success(client):
    order_data = {
        "order_id": "API001", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 201
    assert response.json['order_id'] == "API001"

def test_get_order_api_success(client):
    client.post('/api/orders', json={
        "order_id": "GET001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.get('/api/orders/GET001')
    assert response.status_code == 200
    assert response.json['order_id'] == "GET001"

def test_get_order_api_not_found(client):
    response = client.get('/api/orders/NONEXISTENT')
    assert response.status_code == 404

def test_update_order_status_api_success(client):
    client.post('/api/orders', json={
        "order_id": "UPDATE001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.put('/api/orders/UPDATE001/status', json={"new_status": "shipped"})
    assert response.status_code == 200
    assert response.json['status'] == "shipped"

def test_list_all_orders_api_with_data(client):
    client.post('/api/orders', json={"order_id": "LST001", "item_name": "Item A", "quantity": 1, "customer_id": "C1"})
    client.post('/api/orders', json={"order_id": "LST002", "item_name": "Item B", "quantity": 2, "customer_id": "C2"})
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert len(response.json) == 2

def test_list_orders_by_status_api_matching(client):
    client.post('/api/orders', json={"order_id": "S001", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"})
    client.post('/api/orders', json={"order_id": "S002", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"})
    response = client.get('/api/orders?status=pending')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['order_id'] == "S001"

# ==================== FILTER BY CUSTOMER ID TESTS ====================

def test_list_orders_by_customer_api_returns_matching_orders(client):
    """Tests GET /api/orders?customer_id= returns only that customer's orders."""
    client.post('/api/orders', json={"order_id": "C001", "item_name": "A", "quantity": 1, "customer_id": "CUST_A", "status": "pending"})
    client.post('/api/orders', json={"order_id": "C002", "item_name": "B", "quantity": 2, "customer_id": "CUST_B", "status": "shipped"})
    client.post('/api/orders', json={"order_id": "C003", "item_name": "C", "quantity": 3, "customer_id": "CUST_A", "status": "delivered"})

    response = client.get('/api/orders?customer_id=CUST_A')
    assert response.status_code == 200
    assert len(response.json) == 2
    assert all(order['customer_id'] == 'CUST_A' for order in response.json)

def test_list_orders_by_customer_and_status_api(client):
    """Tests GET /api/orders?customer_id=&status= returns correctly filtered orders."""
    client.post('/api/orders', json={"order_id": "CS001", "item_name": "A", "quantity": 1, "customer_id": "CUST_X", "status": "pending"})
    client.post('/api/orders', json={"order_id": "CS002", "item_name": "B", "quantity": 2, "customer_id": "CUST_X", "status": "shipped"})
    client.post('/api/orders', json={"order_id": "CS003", "item_name": "C", "quantity": 3, "customer_id": "CUST_Y", "status": "pending"})

    response = client.get('/api/orders?customer_id=CUST_X&status=pending')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['order_id'] == "CS001"

def test_list_orders_by_customer_api_returns_empty_list_for_unknown_customer(client):
    """Tests that an unknown customer_id returns an empty list with 200."""
    client.post('/api/orders', json={"order_id": "CE001", "item_name": "A", "quantity": 1, "customer_id": "CUST_A"})

    response = client.get('/api/orders?customer_id=UNKNOWN')
    assert response.status_code == 200
    assert response.json == []

def test_list_orders_by_customer_api_invalid_status_returns_400(client):
    """Tests that combining customer_id with an invalid status returns 400."""
    response = client.get('/api/orders?customer_id=CUST_A&status=bad_status')
    assert response.status_code == 400
    assert 'error' in response.json

# ==================== DELETE ORDER TESTS ====================

def test_delete_order_api_success(client):
    """Tests that deleting an existing order returns 200 with a confirmation message."""
    client.post('/api/orders', json={"order_id": "DEL001", "item_name": "Item", "quantity": 1, "customer_id": "C1"})

    response = client.delete('/api/orders/DEL001')
    assert response.status_code == 200
    assert 'message' in response.json

def test_delete_order_api_order_no_longer_exists_after_deletion(client):
    """Tests that a deleted order can no longer be retrieved."""
    client.post('/api/orders', json={"order_id": "DEL002", "item_name": "Item", "quantity": 1, "customer_id": "C1"})
    client.delete('/api/orders/DEL002')

    response = client.get('/api/orders/DEL002')
    assert response.status_code == 404

def test_delete_order_api_not_found_returns_404(client):
    """Tests that deleting a non-existent order returns 404."""
    response = client.delete('/api/orders/NONEXISTENT')
    assert response.status_code == 404
    assert 'error' in response.json

def test_delete_order_api_does_not_affect_other_orders(client):
    """Tests that deleting one order does not remove other orders."""
    client.post('/api/orders', json={"order_id": "DEL003", "item_name": "Item A", "quantity": 1, "customer_id": "C1"})
    client.post('/api/orders', json={"order_id": "DEL004", "item_name": "Item B", "quantity": 2, "customer_id": "C2"})

    client.delete('/api/orders/DEL003')

    response = client.get('/api/orders')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['order_id'] == "DEL004"
