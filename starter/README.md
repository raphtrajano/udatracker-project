# Udatracker Starter Code

## Reflection
- **Design decision**: In the API routes, I used `try/catch` blocks to handle errors in a centralized way, instead of checking each case manually. For some specific errors, following the API Contract Reference, I matched the message string to return the correct status code (e.g. 404 vs 400). The trade-off is that string matching is fragile; a better approach would be using custom error classes.
- **Testing insight**: Naming tests descriptively like `test_list_all_orders_returns_all_orders` or `test_update_order_status_raises_error_if_status_invalid` made them act as documentation on their own. When a test failed, the name alone made it clear where the contract was broken, without having to dig into the implementation to understand what was expected.
- **Next steps**: I would add persistent storage so data survives server restarts, implement authentication, and full CRUD for Customers. I'd also restrict order creation to existing users only (using a select instead of free text input), improve error message placement so they appear closer to the buttons, add sortable table columns, and a dedicated order details page.

## Project Structure
This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

---

## Running Locally with Docker

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running

### Option 1 — Docker Compose

```bash
docker compose up --build
```

The app will be available at `http://127.0.0.1:8000`.

To stop:

```bash
docker compose down
```

### Option 2 — Docker CLI

```bash
# Build the image
docker build -t udatracker .

# Run the container
docker run -p 8000:8000 udatracker
```

---

## API Reference

Base URL: `http://127.0.0.1:8000`

Valid status values: `pending` , `processing` , `shipped` , `delivered` , `cancelled`

---

### POST `/api/orders` — Add an order

Request body (JSON):

| Field | Type | Required |
| --- | --- | --- |
| `order_id` | string | Yes |
| `item_name` | string | Yes |
| `quantity` | integer (> 0) | Yes |
| `customer_id` | string | Yes |
| `status` | string | No (default: `pending`) |

Responses:

| Code | Meaning |
| --- | --- |
| `201` | Order created - returns the order object |
| `400` | Validation error (missing/invalid field) |
| `409` | Order ID already exists |

```bash
curl -s -X POST "http://127.0.0.1:8000/api/orders" \
  -H "Content-Type: application/json" \
  -d '{"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001"}'
```

---

### GET `/api/orders/<order_id>` — Get a single order

Responses:

| Code | Meaning |
| --- | --- |
| `200` | Returns the order object |
| `400` | Invalid/empty order ID |
| `404` | Order not found |

```bash
curl -s "http://127.0.0.1:8000/api/orders/ORD001"
```

---

### PUT `/api/orders/<order_id>/status` — Update order status

Request body (JSON):

| Field | Type | Required |
| --- | --- | --- |
| `new_status` | string | Yes |

Responses:

| Code | Meaning |
| --- | --- |
| `200` | Returns the updated order object |
| `400` | Invalid status value |
| `404` | Order not found |

```bash
curl -s -X PUT "http://127.0.0.1:8000/api/orders/ORD001/status" \
  -H "Content-Type: application/json" \
  -d '{"new_status": "shipped"}'
```

---

### DELETE `/api/orders/<order_id>` — Delete an order

Responses:

| Code | Meaning |
| --- | --- |
| `200` | Order deleted — returns a confirmation message |
| `400` | Invalid/empty order ID |
| `404` | Order not found |

```bash
curl -s -X DELETE "http://127.0.0.1:8000/api/orders/ORD001"
```

---

### GET `/api/orders` — List orders

Supports optional query parameters that can be used independently or combined.

Query parameters:

| Param | Type | Description |
| --- | --- | --- |
| `status` | string | Filter by order status |
| `customer_id` | string | Filter by customer ID |

Responses:

| Code | Meaning |
| --- | --- |
| `200` | Returns a list of order objects (empty list if none match) |
| `400` | Invalid status value |

```bash
# All orders
curl -s "http://127.0.0.1:8000/api/orders"

# Filter by status
curl -s "http://127.0.0.1:8000/api/orders?status=pending"

# Filter by customer
curl -s "http://127.0.0.1:8000/api/orders?customer_id=CUST001"

# Filter by customer AND status
curl -s "http://127.0.0.1:8000/api/orders?customer_id=CUST001&status=shipped"
```
