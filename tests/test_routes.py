"""
Order API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import ItemFactory, OrderFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Order, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/orders"

######################################################################
#  T E S T   C A S E S
######################################################################


class TestOrderService(TestCase):
    """Order Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once after test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  TESTS FOR CREATE ORDER
    ######################################################################

    def test_create_order_simple(self):
        """
        It should create an order in the database.
        """
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        self.assertIsNotNone(orders[0].id)

        # Make sure id header is set
        location = resp.headers.get("location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = resp.get_json()
        self.assertEqual(new_order["name"], order.name, "Names does not match")
        self.assertEqual(new_order["street"],
                         order.street, "Address does not match")

    def test_create_order_missing_info(self):
        """
        It should fail if the call has some missing information.
        """
        resp = self.client.post(
            "/orders",
            json={
                "street": "35th Street",
                "city": "Manhattan",
                "state": "NY",
                "postal_code": 78912,
                "shipping_price": 12,
                "date_created": "2023-03-14",
                "items": []
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

        orders = Order.all()
        self.assertEqual(len(orders), 0)

    ######################################################################
    #  TESTS FOR READ ORDER
    ######################################################################

    def test_get_order(self):
        """It should Read a single Order"""
        # get the id of an order
        order = self._create_orders(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{order.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["name"], order.name)

    def test_get_order_not_found(self):
        """It should not Read an Order that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, 404)

    ######################################################################
    #  TESTS FOR UPDATE ORDER
    ######################################################################

    def test_update_order(self):
        """It should Update an existing Order"""
        # create an Order to update
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, 201)

        # update the pet
        new_order = resp.get_json()
        new_order["name"] = "Happy-Happy Joy-Joy"
        new_order_id = new_order["id"]
        resp = self.client.put(f"{BASE_URL}/{new_order_id}", json=new_order)
        self.assertEqual(resp.status_code, 200)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["name"], "Happy-Happy Joy-Joy")

    def test_update_nonexistent_order(self):
        """It should not Update an Order that is not found"""
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, 201)

        new_order = resp.get_json()
        new_order_id = "1234"
        resp = self.client.put(f"{BASE_URL}/{new_order_id}", json=new_order)
        self.assertEqual(resp.status_code, 404)

    ######################################################################
    #  TESTS FOR DELETE ORDER
    ######################################################################

    def test_delete_order(self):
        """It should Delete an Order"""
        # get the id of an order
        order = self._create_orders(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{order.id}")
        self.assertEqual(resp.status_code, 204)

    def test_delete_nonexistent_order(self):
        """It should not Delete an Order that is not found"""
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, 201)

        new_order2_id = "1234"
        resp = self.client.delete(f"{BASE_URL}/{new_order2_id}")
        self.assertEqual(resp.status_code, 204)

    ######################################################################
    #  TESTS FOR LIST ORDERS
    ######################################################################

    def test_get_order_list(self):
        """It should Get a list of Orders"""
        self._create_orders(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_order_by_name(self):
        """It should Get an Order by Name"""
        orders = self._create_orders(3)
        resp = self.client.get(BASE_URL, query_string=f"name={orders[1].name}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], orders[1].name)

    def test_list_nonexistent_order(self):
        """It should not List an Order where ID is not found"""
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, 201)

        new_order3_id = "1234"
        resp = self.client.get(f"{BASE_URL}/{new_order3_id}")
        self.assertEqual(resp.status_code, 404)

    def test_get_order_by_nonexistent_name(self):
        """It should not List an Order where name is not found"""
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, 201)

        new_order4_name = "fake name"
        resp = self.client.get(f"{BASE_URL}/{new_order4_name}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
        
    # Test the list_orders() function with the name query parameter
    def test_get_orders_by_name_query(self):
        order1 = OrderFactory(name="Fake Name 1", status="Fake Status 1")
        #order2 = OrderFactory(name="Fake Name 2", status="Fake Status 2"")

        resp = self.client.get(BASE_URL, query_string=f"name")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"]= "Fake Name 1")


    # Test the list_orders() function with the status query parameter
    def test_get_order_by_status(self):
        order1 = OrderFactory(name="Fake Name 1", status="Fake Status 1")
        #order2 = OrderFactory(name="Fake Name 2", status="Fake Status 2"")

        resp = self.client.get(BASE_URL, query_string=f"status")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"]= "Fake Status 1")


    # Test the list_orders() function with both name and status query parameters
    def test_list_orders_with_name_and_status_query_params(self):
        order1 = OrderFactory(name="Fake name 1", status="fake status 1")
        #order2 = OrderFactory(name="Fake name 2", status="fake status 2")

        response = self.client.get(BASE_URL, query_string=f"name", query_string=f"status")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = response.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "fake name 1")
        self.assertEqual(data[0]["status"], "fake status 1")
  
  

    ######################################################################
    #  TESTS FOR CANCEL ORDER
    ######################################################################
   
    def test_cancel_an_order(self):
        """It should Cancel an order"""
        orders = self._create_orders(10)
        open_orders = [order for order in orders if order.status =="Open"]
        order = open_orders[0]
        response = self.client.put(f"{BASE_URL}/{order.id}/cancel")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"{BASE_URL}/{order.id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["status"], "Cancelled")
    
    def test_cancel_order_not_open(self):
        """It should not Cancel an order that is no longer open"""
        orders = self._create_orders(10)
        open_orders = [order for order in orders if order.status == "Shipped"]
        order = open_orders[0]
        response = self.client.put(f"{BASE_URL}/{order.id}/cancel")
        self.assertEqual(response.status_code, 409)


    ######################################################################
    #  TESTS FOR CREATE ITEM
    ######################################################################

    def test_add_item(self):
        """It should Add an item to an order"""
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["item_price"], item.item_price)
        self.assertEqual(data["sku"], item.sku)


    ######################################################################
    #  TESTS FOR READ ITEM
    ######################################################################

    def test_list_items(self):
        """It should Get an item from an order"""

        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        #  retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["sku"], item.sku)

    ######################################################################
    #  TESTS FOR UPDATE ITEM
    ######################################################################

    def test_update_item(self):
        """It should Update an item on an order"""
        # create a known item
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]
        # data["name"] = "XXXX"

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["order_id"], order.id)
        # self.assertEqual(data["name"], "XXXX")

    ######################################################################
    #  TESTS FOR DELETE ITEM
    ######################################################################

    def test_delete_item(self):
        """It should Delete an Item"""
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{item.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 204)

        # retrieve it back and make sure address is not there
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_delete_nonexistent_item(self):
        """It should Not Delete an Item that doesn't exist"""
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        logging.debug(data)
        item_id = "1234"

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{item.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 204)

    ######################################################################
    #  TESTS FOR LIST ITEM GO HERE
    ######################################################################

    def test_get_items_list(self):
        """It should Get a list of Items"""
        order = self._create_orders(1)[0]
        item_list = ItemFactory.create_batch(2)

        # add two items to account and list

        # Create item 1
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items", json=item_list[0].serialize()
        )
        self.assertEqual(resp.status_code, 201)

        # Create item 2
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items", json=item_list[1].serialize()
        )
        self.assertEqual(resp.status_code, 201)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{order.id}/items")
        self.assertEqual(resp.status_code, 200)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    ######################################################################
    #  M I S C  T E S T S
    ######################################################################

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, 400)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code,
                         415)

    def test_index(self):
        """It should call the Home Page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, 405)

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_orders(self, count):
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            order = OrderFactory()
            resp = self.client.post(BASE_URL, json=order.serialize())
            self.assertEqual(
                resp.status_code,
                201,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)
        return orders
