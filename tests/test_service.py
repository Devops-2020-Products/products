"""
Product API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from flask_api import status  # HTTP Status Codes
from service.models import db, Product
from service.service import app, init_db
from tests.product_factory import ProductFactory

######################################################################
#  T E S T   C A S E S
######################################################################
class TestProductServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        init_db()
        self.app = app.test_client()


    def tearDown(self):
        """ This runs after each test """
        pass

    def _create_products(self, count):
        """ Factory method to create products in bulk """
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            resp = self.app.post(
                "/products", json=test_product.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_product = resp.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

######################################################################
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    
    def test_create_product(self):
        """ Create a new Product """
        test_product = ProductFactory()
        logging.debug(test_product)
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = resp.get_json()
        self.assertEqual(new_product["name"], test_product.name, "Names do not match")
        self.assertEqual(
            new_product["category"], test_product.category, "Categories do not match"
        )
        self.assertEqual(
            new_product["description"], test_product.description, "Descriptions do not match"
        )
        self.assertEqual(
            new_product["price"], test_product.price, "Prices do not match"
        )

        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_product = resp.get_json()
        self.assertEqual(new_product["name"], test_product.name, "Names do not match")
        self.assertEqual(
         new_product["category"], test_product.category, "Categories do not match"
        )
        self.assertEqual(
         new_product["description"], test_product.description, "Descriptions do not match"
        )
        self.assertEqual(
         new_product["price"], test_product.price, "Prices do not match"
        )

    def test_create_product_with_invalid_content_type(self):
        """ Create a new Product with invalid content type"""
        test_product = ProductFactory()
        logging.debug(test_product)
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="text/plain"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_product(self):
        """ Get a single product by its ID """
        # get the id of a product
        test_product = self._create_products(1)[0]
        resp = self.app.get(
            "/products/{}".format(test_product.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_get_product_not_found(self):
        """ Get a product that's not found """
        resp = self.app.get("/products/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_a_product(self):
        """ Delete a Product """
        test_product = self._create_products(1)[0]
        resp = self.app.delete(
            "/products/{}".format(test_product.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "/products/{}".format(test_product.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND) 

    def test_update_product(self):
        """ Update an existing Product """
        # create a product to update
        test_product = ProductFactory()
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = resp.get_json()
        new_product["category"] = "Education"
        resp = self.app.put(
            "/products/{}".format(new_product["id"]),
            json=new_product,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product["category"], "Education")

    def test_update_product_not_found(self):
        """ Update a product that's not found """
        test_product = ProductFactory()
        resp = self.app.put(
            "/products/0",
            json=test_product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_bad_request(self):
        """ Update a product with bad request body """
        # create a product to update
        test_product = ProductFactory()
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # create an update request with bad request body
        new_product = resp.get_json()
        new_product.pop("name")
        resp = self.app.put(
            "/products/{}".format(new_product["id"]),
            json=new_product,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
