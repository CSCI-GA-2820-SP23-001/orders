"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Order

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
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
    order = Order()
    order.deserialize(request.get_json())
    order.create()

    # Create a message to return
    message = order.serialize()
    # location_url = url_for("get_order", order_id=order.id, _external=True)

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": "TODO"}
    )



# DELETE AN ORDER

@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    """
    Delete an Account
    This endpoint will delete an order based the id specified in the path
    """
    app.logger.info("Request to delete an order with id: %s", order_id)

    # Retrieve the order to delete and delete it if it exists
    order = Order.find(order_id)
    if order:
        order.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------
#                ITEMS   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# DELETE AN ORDER ITEM
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(order_id, item_id):
    """
    Delete an Order Item
    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info(
        "Request to delete item %s for order id: %s", (order_id, item_id)
    )

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
