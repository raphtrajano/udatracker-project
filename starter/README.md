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
