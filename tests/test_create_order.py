"""
Order API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase, skip
from tests.factories import ItemFactory, OrderFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Order, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

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

    def test_create_order_simple(self):
        """
        Makes sure that creating an order through the API creates 
        an order in the database.
        """
        resp = self.client.post(
            "/orders", 
            json={
                "name": "o1",
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
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        orders = Order.all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].name, "o1")
        self.assertIsNotNone(orders[0].id)
        
    def test_create_order_missing_info(self):
        """
        Creating an order should fail it has some missing information.
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

    @skip("not sure if this test is valid.")
    def test_create_order_with_valid_items(self):
        """
        Creating an order with items in it should pass.
        """
        resp = self.client.post(
            "/orders",
            json={
                "name": "o1",
                "street": "35th Street",
                "city": "Manhattan",
                "state": "New York",
                "postal_code": 78912,
                "shipping_price": 12,
                "date_created": "2023-03-14",
                "items": [
                    {"item_price": 12, "sku": 12345},
                ]
            }, 
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        orders = Order.all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(len(orders[0].items), 1)