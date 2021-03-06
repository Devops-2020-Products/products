"""
Test cases for product Model

"""
#import logging
import unittest
#import os
#import json
from unittest.mock import patch
from sqlalchemy.exc import InvalidRequestError
from service.models import Product, DataValidationError, db
from service import app

######################################################################
# Product  M O D E L   T E S T   C A S E S
######################################################################
class TestProductModel(unittest.TestCase):
    """ Test Cases for Product Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.debug = False
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config["TEST_DATABASE_URI"]
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()
        db.create_all()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

######################################################################
#  P L A C E   T E S T   C A S E S   H E R E
######################################################################

    def test_serialize_a_product(self):
        """ Test serialization of a Product """
        product = Product(name="iPhone X", description="Black iPhone", category="Technology", price=999.99)
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], None)
        self.assertIn("name", data)
        self.assertEqual(data["name"], "iPhone X")
        self.assertIn("description", data)
        self.assertEqual(data["description"], "Black iPhone")
        self.assertIn("category", data)
        self.assertEqual(data["category"], "Technology")
        self.assertIn("price", data)
        self.assertEqual(data["price"], 999.99)

    def test_deserialize_a_product(self):
        """ Test deserialization of a Product """
        data = {"id": 1, "name": "iPhone X", "description": "Black iPhone", "category": "Technology", "price": 999.99}
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "iPhone X")
        self.assertEqual(product.description, "Black iPhone")
        self.assertEqual(product.category, "Technology")
        self.assertEqual(product.price, 999.99)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

        data = {"id": 1, "name": "iPhone X", "description": "Black iPhone", "category": "Technology", "price": "a"}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_add_a_product(self):
        """ Create a product and add it to the database """
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50)
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(product.id, 1)
        products = Product.all()
        self.assertEqual(len(products), 1)

    @patch('service.models.db.session.commit')
    def test_add_a_product_commit_error(self,commit):
        """ Create a product and raises an InvalidRequestError """
        commit.side_effect = InvalidRequestError
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50)
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        product.create()
        self.assertEqual(products, [])

    def test_update_a_product(self):
        """ Update a Product """
        product = Product(name="iPhone X", description="Black iPhone", category="Technology", price=999.99)
        product.create()
        self.assertEqual(product.id, 1)
        # Change it and update it
        product.price = 9999.99
        product.description = "White iPhone"
        product.update()
        self.assertEqual(product.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].price, 9999.99)
        self.assertEqual(products[0].description, "White iPhone")

    def test_update_a_product_commit_error(self):
        """ Update a product and raises an InvalidRequestError """
        product = Product(name="iPhone X", description="Black iPhone", category="Technology", price=999.99)
        product.create()
        self.assertEqual(product.id, 1)
        # Change it and update it
        product.price = 9999.99
        product.description = "White iPhone"
        with patch('service.models.db.session.commit') as commit:
            commit.side_effect = InvalidRequestError
            product.update()
            products = Product.all()
            self.assertEqual(len(products), 1)
            self.assertEqual(products[0].price, 999.99)
            self.assertEqual(products[0].description, "Black iPhone")

    def test_update_a_product_empty_id(self):
        """ Update a Product with empty id """
        product = Product(name="iPhone X", description="Black iPhone", category="Technology", price=999.99)
        product.create()
        self.assertEqual(product.id, 1)
        # Change it and update it
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_find_product(self):
        """ Find a Product by ID """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=999.99).create()
        t_v = Product(name="TV", description="Black Sony TV", category="Technology", price=1999.99)
        t_v.create()
        product = Product.find(t_v.id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, t_v.id)
        self.assertEqual(product.name, "TV")
        self.assertEqual(product.description, "Black Sony TV")
        self.assertEqual(product.category, "Technology")
        self.assertEqual(product.price, 1999.99)

    def test_find_by_category(self):
        """ Find Products by Category """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_category("technology")
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_name(self):
        """ Find Products by Name """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_name("iPhone x")
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_description(self):
        """ Find Products by Description """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_description("black")
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_search_by_price(self):
        """ Find Products by Price """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.query_by_price(800, 10000)
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_name_category(self):
        """ Find Products by Name and Category """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_name_category("iPhone x", "technology")
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_name_description(self):
        """ Find Products by Name and Description """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_name_description("iPhone x", "iPhone")
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_name_price(self):
        """ Find Products by Name and Price """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_name_price("iPhone x", 800, 10000)
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_category_description(self):
        """ Find Products by Category and Description """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_category_description("technology", "iPhone")
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_category_price(self):
        """ Find Products by Category and Price """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_category_price("technology", 800, 10000)
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_description_price(self):
        """ Find Products by Description and Price """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_description_price("iPhone", 800, 10000)
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_name_category_description(self):
        """ Find Products by Name, Category and Description """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_name_category_description("iPhone x", "technology", "iPhone")
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_name_category_price(self):
        """ Find Products by Name, Category and Price """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_name_category_price("iPhone x", "technology", 800, 10000)
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_name_description_price(self):
        """ Find Products by Name, Descrption and Price """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_name_description_price("iPhone x", "iPhone", 800, 10000)
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_category_description_price(self):
        """ Find Products by Category, Description and Price """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_category_description_price("technology", "iPhone", 800, 10000)
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_find_by_name_category_description_price(self):
        """ Find Products by Name, Category, Description and Price """
        Product(name="iPhone X", description="Black iPhone", category="Technology", price=9999.99).create()
        Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50).create()
        products = Product.find_by_name_category_description_price("iPhone x", "technology", "iPhone", 800, 10000)
        self.assertEqual(products[0].category, "Technology")
        self.assertEqual(products[0].name, "iPhone X")
        self.assertEqual(products[0].description, "Black iPhone")
        self.assertEqual(products[0].price, 9999.99)

    def test_delete_a_product(self):
        """ Delete a Product """
        product = Product(name="iPhone X", description="Black iPhone", category="Technology", price=999.99)
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_delete_a_product_commit_error(self):
        """ Delete a Product """
        product = Product(name="iPhone X", description="Black iPhone", category="Technology", price=999.99)
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        with patch('service.models.db.session.commit') as commit:
            commit.side_effect = InvalidRequestError
            product.delete()
            self.assertEqual(len(Product.all()), 1)

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
