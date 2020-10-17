"""
Test cases for product Model

"""
import logging
import unittest
import os
from service.models import Product, DataValidationError, db
from service import app

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres")

######################################################################
# Product  M O D E L   T E S T   C A S E S
######################################################################
class TestProductModel(unittest.TestCase):
    """ Test Cases for Product Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.debug = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI


    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        Product.init_db(app)
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
        product = Product(name="iPhone X",description="Black iPhone",category= "Technology", price = 999.99)
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], None)
        self.assertIn("name", data)
        self.assertEqual(data["name"], "iPhone X")
        self.assertIn("description", data)
        self.assertEqual(data["description"],"Black iPhone")
        self.assertIn("category", data)
        self.assertEqual(data["category"], "Technology")
        self.assertIn("price", data)
        self.assertEqual(data["price"], 999.99)

    def test_deserialize_a_product(self):
        """ Test deserialization of a Product """
        data = {"id": 1, "name": "iPhone X", "description": "Black iPhone","category": "Technology", "price": 999.99}
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
        
    def test_add_a_product(self):
        """ Create a product and add it to the database """
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(name="Cake", description="Chocolate Cake", category="Food", price=10.50)
        self.assertTrue(product != None)
        self.assertEqual(product.id, None)
        product.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(product.id, 1)
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_find_product(self):
        """ Find a Product by ID """
        Product(name="iPhone X",description="Black iPhone",category= "Technology", price = 999.99).create()
        tv = Product(name="TV", description="Black Sony TV",category="Technology", price= 1999.99)
        tv.create()
        product = Product.find(tv.id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, tv.id)
        self.assertEqual(product.name, "TV")
        self.assertEqual(product.description, "Black Sony TV")
        self.assertEqual(product.category,"Technology")
        self.assertEqual(product.price, 1999.99)

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
