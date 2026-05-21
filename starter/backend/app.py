from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage
from backend.exceptions import (
    DuplicateOrderError,
    InvalidQuantityError,
    InvalidStatusError,
    MissingFieldError,
    OrderNotFoundError,
)

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json(silent=True) or {}

    try:
        kwargs = {
            "order_id": data.get("order_id"),
            "item_name": data.get("item_name"),
            "quantity": data.get("quantity"),
            "customer_id": data.get("customer_id"),
        }
        if data.get("status"):
            kwargs["status"] = data.get("status")

        order = order_tracker.add_order(**kwargs)
    except DuplicateOrderError as e:
        return jsonify({"error": str(e)}), 409
    except (MissingFieldError, InvalidQuantityError, InvalidStatusError) as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(order), 201


@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    try:
        order = order_tracker.get_order_by_id(order_id)
    except MissingFieldError as e:
        # Flask never routes an empty string to <string:order_id>, so this
        # branch is defensive against future callers that bypass the route
        # layer.
        return jsonify({"error": str(e)}), 400

    if order is None:
        return jsonify({"error": f"Order with ID '{order_id}' not found."}), 404

    return jsonify(order), 200


@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    data = request.get_json(silent=True) or {}

    try:
        order = order_tracker.update_order_status(order_id, data.get("new_status"))
    except OrderNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except (MissingFieldError, InvalidStatusError) as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(order), 200


@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get("status")
    customer_id = request.args.get("customer_id")

    try:
        if customer_id:
            orders = order_tracker.list_orders_by_customer(customer_id, status or None)
        elif status:
            orders = order_tracker.list_orders_by_status(status)
        else:
            orders = order_tracker.list_all_orders()
    except (MissingFieldError, InvalidStatusError) as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(orders), 200


@app.route('/api/orders/<string:order_id>', methods=['DELETE'])
def delete_order_api(order_id):
    try:
        order_tracker.delete_order(order_id)
    except OrderNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except MissingFieldError as e:
        # Defensive: handles empty/None order_id from non-route callers.
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": f"Order with ID '{order_id}' deleted successfully."}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8000)
