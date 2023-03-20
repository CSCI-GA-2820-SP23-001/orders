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
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        self.assertIsNotNone(orders[0].id)
         
        # Make sure id header is set
        location = resp.headers.get("location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = resp.get_json()
        self.assertEqual(new_order["name"], order.name, "Names does not match")
        self.assertEqual(new_order["street"], order.street, "Address does not match")
        
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
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], order.name)

    def test_get_order_not_found(self):
        """It should not Read an Order that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    
    ######################################################################
    #  TESTS FOR UPDATE ORDER
    ######################################################################
    
    def test_update_order(self):
        """It should Update an existing Order"""
        # create an Order to update
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_order = resp.get_json()
        new_order["name"] = "Happy-Happy Joy-Joy"
        new_order_id = new_order["id"]
        resp = self.client.put(f"{BASE_URL}/{new_order_id}", json=new_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["name"], "Happy-Happy Joy-Joy")
    
    def test_update_nonexistant_order(self):
        """It should not Update an Order that is not found"""
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        new_order = resp.get_json()
        new_order_id = "1234"
        resp = self.client.put(f"{BASE_URL}/{new_order_id}", json=new_order)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    ######################################################################
    #  TESTS FOR DELETE ORDER
    ######################################################################

    def test_delete_order(self):
        """It should Delete an Order"""
        # get the id of an order
        order = self._create_orders(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_nonexistant_order(self):
        """It should not Delete an Order that is not found"""
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        new_order2 = resp.get_json()
        new_order2_id = "1234"
        resp = self.client.delete(f"{BASE_URL}/{new_order2_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


    ######################################################################
    #  TESTS FOR LIST ORDERS
    ######################################################################

    def test_get_order_list(self):
        """It should Get a list of Orders"""
        self._create_orders(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_order_by_name(self):
        """It should Get an Order by Name"""
        orders = self._create_orders(3)
        resp = self.client.get(BASE_URL, query_string=f"name={orders[1].name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], orders[1].name)

    def test_list_nonexistant_order(self):
        """It should not List an Order that is not found"""
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        new_order3 = resp.get_json()
        new_order3_id = "1234"
        resp = self.client.get(f"{BASE_URL}/{new_order3_id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_order_by_nonexistant_name(self):
        test_order = OrderFactory()
        resp = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        new_order4 = resp.get_json()
        new_order4_name = "fake name"
        resp = self.client.get(f"{BASE_URL}/{new_order4_name}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    ######################################################################
    #  TESTS FOR CREATE ITEM
    ######################################################################

    ######################################################################
    # /\/\/\/   TESTS FOR CREATE ITEM GO HERE
    ######################################################################



    ######################################################################
    #  TESTS FOR READ ITEM
    ######################################################################

    ######################################################################
    # /\/\/\/   TESTS FOR READ ITEM GO HERE
    ######################################################################



    ######################################################################
    #  TESTS FOR UPDATE ITEM
    ######################################################################

    ######################################################################
    # /\/\/\/   TESTS FOR UPDATE ITEM GO HERE
    ######################################################################



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
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{item.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure address is not there
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_nonexistant_item(self):
        """It should Not Delete an Item that doesn't exist"""
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = "1234"

        #send delete request
        resp = self.client.delete(
           f"{BASE_URL}/{item.id}/items/{item_id}",
           content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    ######################################################################
    #  TESTS FOR LIST ITEMS
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
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        #  retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["sku"], item.sku)

    ######################################################################
    # /\/\/\/   TESTS FOR LIST ITEM GO HERE
    ######################################################################

    def test_get_items_list(self):
        """It should Get a list of Items"""
        order = self._create_orders(1)[0]
        item_list = ItemFactory.create_batch(2)
        
        #add two items to account and list
    
        # Create item 1
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items", json=item_list[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.client.post(
            f"{BASE_URL}/{order.id}/items", json=item_list[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        #get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{order.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    ######################################################################
    #  M I S C  T E S T S
    ######################################################################

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_index(self):
         """It should call the Home Page"""
         resp = self.client.get("/")
         self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_method_not_allowed(self):
         """It should not allow an illegal method call"""
         resp = self.client.put(BASE_URL, json={"not": "today"})
         self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)
        return orders

    ######################################################################
    #  I T E M  M E T H O D S
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
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["item_price"], item.item_price)
        self.assertEqual(data["sku"], item.sku)


    ######################################################################
    #  S A M P L E    A C C O U N T   T E S T   C A S E S
    ######################################################################

    # def test_index(self):
    #     """It should call the Home Page"""
    #     resp = self.client.get("/")
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # def test_get_account_list(self):
    #     """It should Get a list of Accounts"""
    #     self._create_accounts(5)
    #     resp = self.client.get(BASE_URL)
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     data = resp.get_json()
    #     self.assertEqual(len(data), 5)

    # def test_get_account_by_name(self):
    #     """It should Get an Account by Name"""
    #     accounts = self._create_accounts(3)
    #     resp = self.client.get(BASE_URL, query_string=f"name={accounts[1].name}")
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     data = resp.get_json()
    #     self.assertEqual(data[0]["name"], accounts[1].name)


    # ######################################################################
    # #  A D D R E S S   T E S T   C A S E S
    # ######################################################################

    # def test_get_address_list(self):
    #     """It should Get a list of Addresses"""
    #     # add two addresses to account
    #     account = self._create_accounts(1)[0]
    #     address_list = AddressFactory.create_batch(2)

    #     # Create address 1
    #     resp = self.client.post(
    #         f"{BASE_URL}/{account.id}/addresses", json=address_list[0].serialize()
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    #     # Create address 2
    #     resp = self.client.post(
    #         f"{BASE_URL}/{account.id}/addresses", json=address_list[1].serialize()
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    #     # get the list back and make sure there are 2
    #     resp = self.client.get(f"{BASE_URL}/{account.id}/addresses")
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)

    #     data = resp.get_json()
    #     self.assertEqual(len(data), 2)



   
    # def test_update_address(self):
    #     """It should Update an address on an account"""
    #     # create a known address
    #     account = self._create_accounts(1)[0]
    #     address = AddressFactory()
    #     resp = self.client.post(
    #         f"{BASE_URL}/{account.id}/addresses",
    #         json=address.serialize(),
    #         content_type="application/json",
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    #     data = resp.get_json()
    #     logging.debug(data)
    #     address_id = data["id"]
    #     data["name"] = "XXXX"

    #     # send the update back
    #     resp = self.client.put(
    #         f"{BASE_URL}/{account.id}/addresses/{address_id}",
    #         json=data,
    #         content_type="application/json",
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)

    #     # retrieve it back
    #     resp = self.client.get(
    #         f"{BASE_URL}/{account.id}/addresses/{address_id}",
    #         content_type="application/json",
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)

    #     data = resp.get_json()
    #     logging.debug(data)
    #     self.assertEqual(data["id"], address_id)
    #     self.assertEqual(data["account_id"], account.id)
    #     self.assertEqual(data["name"], "XXXX")

    # def test_delete_address(self):
    #     """It should Delete an Address"""
    #     account = self._create_accounts(1)[0]
    #     address = AddressFactory()
    #     resp = self.client.post(
    #         f"{BASE_URL}/{account.id}/addresses",
    #         json=address.serialize(),
    #         content_type="application/json",
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    #     data = resp.get_json()
    #     logging.debug(data)
    #     address_id = data["id"]

    #     # send delete request
    #     resp = self.client.delete(
    #         f"{BASE_URL}/{account.id}/addresses/{address_id}",
    #         content_type="application/json",
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    #     # retrieve it back and make sure address is not there
    #     resp = self.client.get(
    #         f"{BASE_URL}/{account.id}/addresses/{address_id}",
    #         content_type="application/json",
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
