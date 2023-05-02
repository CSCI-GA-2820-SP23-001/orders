"""
My Service

Describe what your service does here
"""

from flask import url_for, jsonify, request, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Order, Item

# Import Flask application
from . import app


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return make_response(jsonify(status=200, message="OK"), status.HTTP_200_OK)


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
# CREATE A NEW ORDER
######################################################################


@app.route("/orders", methods=["POST"])
def create_order():
    """
    Creates an Order
    This endpoint will create an Order based the data in the body that is posted
    """
    app.logger.info("Request to create an Order")
    check_content_type("application/json")

    # Create the order
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    order = Order()
    order.deserialize(request.get_json())
    order.create()
    app.logger.info("Order with new id [%s] saved!", order.id)

    # Create a message to return
    message = order.serialize()
    location_url = url_for("get_orders", order_id=order.id, _external=True)

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# READ AN ORDER
######################################################################


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_orders(order_id):
    """
    Retrieve a single Order
    This endpoint will return an Order based on its id
    """
    app.logger.info("Request for Order with id: %s", order_id)

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )
    app.logger.info("Returning order: %s", order.name)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# LIST ALL ORDERS
######################################################################


@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all of the Orders"""
    app.logger.info("Request for Order list By Status")

    # Process the query string if any by name and status
    name_query = request.args.get("name")
    status_query = request.args.get("status")

    if name_query and status_query:
        orders = Order.find_by_name_and_status(name_query, status_query)
    elif name_query:
        orders = Order.find_by_name(name_query)
    elif status_query:
        orders = Order.find_by_status(status_query)
    else:
        orders = Order.all()

    # Return as an array of dictionaries
    results = [order.serialize() for order in orders]
    app.logger.info("[%s] Orders returned", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING ORDER
######################################################################


@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update an Order
    This endpoint will update an Order based the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND,
              f"Order with id '{order_id}' was not found.")

    # Update from the json in the body of the request
    data = request.get_json()
    app.logger.info(data)
    order.deserialize(request.get_json())
    order.id = order_id
    order.update()

    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE AN EXISTING ORDER
######################################################################


@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    """
    Delete an Order
    This endpoint will delete an order based the id specified in the path
    """
    app.logger.info("Request to delete an order with id: %s", order_id)

    # Retrieve the order to delete and delete it if it exists
    order = Order.find(order_id)
    if order:
        order.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# CANCEL AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/cancel", methods=["PUT"])
def cancel_order(order_id):
    """Canceling an order changes its status to Cancelled"""
    app.logger.info("Request to cancel an order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND,
              f"Order with id '{order_id}' was not found.")
    if not order.status == "Open":
        abort(
            status.HTTP_409_CONFLICT,
            f"Order with id '{order_id}' is already shipped or fulfilled and cannot be cancelled.",
        )
    # Set order to Cancelled
    app.logger.info("Order ID %s  cancelled", order_id)
    order.status = "Cancelled"
    order.update()
    return order.serialize(), status.HTTP_200_OK


# ---------------------------------------------------------------------
#                ITEMS   M E T H O D S
# ---------------------------------------------------------------------

######################################################################
# CREATE/ADD AN ITEM TO AN ORDER
######################################################################


@app.route("/orders/<int:order_id>/items", methods=["POST"])
def create_items(order_id):
    """
    Create an Item on an Order
    This endpoint will add an item to an order
    """
    app.logger.info(
        "Request to create an Item for Order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Create an item from the json data
    item = Item()
    item.deserialize(request.get_json())

    # Append the item to the order
    order.items.append(item)
    order.update()

    # Prepare a message to return
    message = item.serialize()

    return make_response(jsonify(message), status.HTTP_201_CREATED)


######################################################################
# LIST ORDER ITEMS
######################################################################


@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_items(order_id):
    """Returns all of the Items for an Order"""
    app.logger.info("Request for all Items for an Order with id: %s", order_id)

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Get the items for the account
    results = [item.serialize() for item in order.items]

    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE AN ITEM FROM AN ORDER
######################################################################


@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_items(order_id, item_id):
    """
    Get an Address
    This endpoint returns just an address
    """
    # pylint: disable=logging-too-few-args
    app.logger.info(
        "Request to retrieve Address %s for Account id: %s", (
            item_id, order_id)
    )

    # See if the address exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Account with id '{item_id}' could not be found.",
        )

    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE AN ORDER ITEM
######################################################################


@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_items(order_id, item_id):
    """
    Update an Item
    This endpoint will update an Item based the body that is posted
    """
    # pylint: disable=logging-too-few-args
    app.logger.info("Request to update Item %s for Order id: %s",
                    (item_id, order_id))
    check_content_type("application/json")

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{item_id}' could not be found.",
        )

    # Update from the json in the body of the request
    item.deserialize(request.get_json())
    item.id = item_id
    item.update()

    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE AN ORDER ITEM
######################################################################


@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(order_id, item_id):
    """
    Delete an Order Item
    This endpoint will delete an item based the id specified in the path
    """
    # pylint: disable=logging-too-few-args
    app.logger.info("Request to delete item %s for order id: %s",
                    (order_id, item_id))

    # See if the item exists and delete it if it does
    item = Item.find(item_id)
    if item:
        item.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
