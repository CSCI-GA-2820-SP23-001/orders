"""
Test cases for Order Model

"""
import logging
import unittest
import os
from service import app
from service.models import Order, Item, DataValidationError, db
from tests.factories import OrderFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  Order   M O D E L   T E S T   C A S E S
######################################################################
class TestOrder(unittest.TestCase):
    """Test Cases for Order Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Order.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_order(self):
        """It should Create an Order and assert that it exists"""
        fake_order = OrderFactory()
        # pylint: disable=unexpected-keyword-arg
        order = Order(
            name=fake_order.name,
            street=fake_order.street,
            city=fake_order.city,
            state=fake_order.state,
            postal_code=fake_order.postal_code,
            shipping_price=fake_order.shipping_price,
            date_created=fake_order.date_created
        )
        self.assertIsNotNone(order)
        self.assertEqual(order.id, None)
        self.assertEqual(order.name, fake_order.name)
        self.assertEqual(order.street, fake_order.street)
        self.assertEqual(order.city, fake_order.city)
        self.assertEqual(order.state, fake_order.state)
        self.assertEqual(order.postal_code, fake_order.postal_code)
        self.assertEqual(order.shipping_price, fake_order.shipping_price)
        self.assertEqual(order.date_created, fake_order.date_created)

    def test_add_an_order(self):
        """It should Create an order and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

    def test_read_order(self):
        """It should Read an order"""
        order = OrderFactory()
        order.create()
        # import pdb

        # Read it back
        found_order = Order.find(order.id)
        # pdb.set_trace() 

        print("FOUND ORDER HERE")
        print(found_order)
        print("FOUND ORDER ITEM")
        print(found_order.items)
        self.assertEqual(found_order.id, order.id)
        self.assertEqual(found_order.name, order.name)
        self.assertEqual(found_order.street, order.street)
        self.assertEqual(found_order.city, order.city)
        self.assertEqual(found_order.state, order.state)
        self.assertEqual(found_order.postal_code, order.postal_code)
        self.assertEqual(found_order.shipping_price, order.shipping_price)
        self.assertEqual(found_order.date_created, order.date_created)
        self.assertEqual(found_order.items, [])



    def test_update_order(self):
        """It should Update an order"""
        order = OrderFactory(name="barton consedine")
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        self.assertEqual(order.name, "barton consedine")

        # Fetch it back
        order = Order.find(order.id)
        order.name = "Sienna consedine"
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(order.name, "Sienna consedine")

    def test_delete_an_order(self):
        """It should Delete an order from the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        order = orders[0]
        order.delete()
        orders = Order.all()
        self.assertEqual(len(orders), 0)

    def test_list_all_orders(self):
        """It should List all orders in the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        for order in OrderFactory.create_batch(5):
            order.create()
        # Assert that there are not 5 orders in the database
        orders = Order.all()
        self.assertEqual(len(orders), 5)

    def test_find_by_name(self):
        """It should Find an Order by name"""
        order = OrderFactory()
        order.create()

        # Fetch it back by name
        same_order = Order.find_by_name(order.name)[0]
        self.assertEqual(same_order.id, order.id)
        self.assertEqual(same_order.name, order.name)

    def test_serialize_an_order(self):
        """It should Serialize an order"""
        order = OrderFactory()
        item = ItemFactory()
        order.items.append(item)
        serial_order = order.serialize()
        self.assertEqual(serial_order["id"], order.id)
        self.assertEqual(serial_order["name"], order.name)
        self.assertEqual(serial_order["street"], order.street)
        self.assertEqual(serial_order["city"], order.city)
        self.assertEqual(serial_order["state"], order.state)
        self.assertEqual(serial_order["postal_code"], order.postal_code)
        self.assertEqual(serial_order["date_created"], str(order.date_created))
        self.assertEqual(len(serial_order["items"]), 1)
        items = serial_order["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["order_id"], item.order_id)
        self.assertEqual(items[0]["sku"], item.sku)
        

    def test_deserialize_an_order(self):
        """It should Deserialize an order"""
        order = OrderFactory()
        order.items.append(ItemFactory())
        order.create()
        serial_order = order.serialize()
        new_order = Order()
        new_order.deserialize(serial_order)
        self.assertEqual(new_order.name, order.name)
        self.assertEqual(new_order.street, order.street)
        self.assertEqual(new_order.city, order.city)
        self.assertEqual(new_order.state, order.state)
        self.assertEqual(new_order.postal_code, order.postal_code)
        self.assertEqual(new_order.date_created, order.date_created)
        self.assertEqual(new_order.date_created, order.date_created)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an order with a KeyError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an order with a TypeError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an item with a KeyError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an item with a TypeError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])

    def test_add_order_item(self):
        """It should Create an order with an item and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.items.append(item)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        new_order = Order.find(order.id)
        self.assertEqual(new_order.items[0].item_price, item.item_price)

        item2 = ItemFactory(order=order)
        order.items.append(item2)
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.items), 2)
        self.assertEqual(new_order.items[1].item_price, item2.item_price)

    def test_update_order_item(self):
        """It should Update an orders item"""
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        item = ItemFactory(order=order)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        old_item = order.items[0]
        print("%r", old_item)
        self.assertEqual(old_item.sku, item.sku)
        # Change the sku
        old_item.sku = 123456789
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        item = order.items[0]
        self.assertEqual(item.sku, 123456789)

    def test_delete_order_item(self):
        """It should Delete an orders item"""
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        item = ItemFactory(order=order)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        item = order.items[0]
        item.delete()
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(len(order.items), 0)