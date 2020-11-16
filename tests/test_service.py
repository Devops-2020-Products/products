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
from json import dumps

SHOPCART_ENDPOINT = os.getenv('SHOPCART_ENDPOINT', 'http://localhost:5000/shopcarts')
######################################################################
#  T E S T   C A S E S
######################################################################
class TestProductServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        init_db()
        app.debug = False
        app.testing = True
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config["TEST_DATABASE_URI"]

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

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

    def test_create_product_with_bad_request(self):
        """ Create a new Product with bad request"""
        test_product = ProductFactory()
        logging.debug(test_product)
        test_product.category = ""
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

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
        test_product_name = test_product.name
        test_product_description = test_product.description
        test_product_price = test_product.price
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

        # create an update request with partial information
        part_product = resp.get_json()
        part_product["category"] = ""
        resp = self.app.put(
            "/products/{}".format(part_product["id"]),
            json=part_product,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product["category"], "Education")

        part_product = resp.get_json()
        part_product["name"] = ""
        resp = self.app.put(
            "/products/{}".format(part_product["id"]),
            json=part_product,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product["name"], test_product_name)

        part_product = resp.get_json()
        part_product["description"] = ""
        resp = self.app.put(
            "/products/{}".format(part_product["id"]),
            json=part_product,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product["description"], test_product_description)

        part_product = resp.get_json()
        part_product["price"] = ""
        resp = self.app.put(
            "/products/{}".format(part_product["id"]),
            json=part_product,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product["price"], test_product_price)

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

    def test_get_product_list(self):
        """ Get a list of Products """
        self._create_products(5)
        resp = self.app.get("/products")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_query_product_list_by_category(self):
        """ Query Products by Category """
        products = self._create_products(10)
        test_category = products[0].category
        category_products = [product for product in products if product.category == test_category]
        resp = self.app.get("/products", query_string="category={}".format(test_category))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(category_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["category"], test_category)

    def test_query_product_list_by_name(self):
        """ Query Products by Name """
        products = self._create_products(10)
        test_name = products[0].name
        name_products = [product for product in products if product.name == test_name]
        resp = self.app.get("/products", query_string="name={}".format(test_name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(name_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["name"], test_name)

    def test_query_product_list_by_description(self):
        """ Query Products by Description """
        products = self._create_products(10)
        test_description = products[0].description
        description_products = [product for product in products if product.description == test_description]
        resp = self.app.get("/products", query_string="description={}".format(test_description))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(description_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["description"], test_description)

    def test_query_product_by_price(self):
        """ Query Products by Price Range """
        products = self._create_products(10)
        test_max_price = products[0].price * 10
        test_min_price = products[0].price / 10
        price_products = [product for product in products if product.price >= test_min_price and product.price <= test_max_price]
        resp = self.app.get("/products/price", query_string="minimum={}&maximum={}".format(test_min_price, test_max_price))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(price_products))

    def test_query_product_by_price_bad_request(self):
        """ Query Products by Price Range """
        products = self._create_products(10)
        test_max_price = products[0].price * 10
        test_min_price = products[0].price / 10
        resp = self.app.get("/products/price", query_string="minimum={}".format(test_min_price))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = self.app.get("/products/price", query_string="maximum={}".format(test_max_price))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = self.app.get("/products/price", query_string="minimum={}&maximum={}".format(test_min_price, ""))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = self.app.get("/products/price", query_string="minimum={}&maximum={}".format("", test_max_price))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_purchase_product_shopcart_exists(self):
        '''Purchase a Product shopcart exists successfull'''
        user_id = 101
        with patch('requests.get') as get_shopcart_by_userid_mock:
            get_shopcart_by_userid_mock.return_value.status_code = 200
            get_shopcart_by_userid_mock.return_value.json.return_value = [{"create_time": "2020-11-15T19:36:28.302839","id": 6,"update_time": "2020-11-15T19:36:28.302839","user_id": 101}]
            with patch('requests.post') as post_shopcart_item_mock:
                post_shopcart_item_mock.return_value.status_code=201
                json = {"user_id": user_id, "amount": 4}
                product = self._create_products(1)
                resp = self.app.post("/products/{}/purchase".format(product[0].id), json=json, content_type="application/json")
                self.assertEqual(resp.status_code, status.HTTP_200_OK)
                self.assertEqual(resp.data, b'Product successfully added into the shopping cart')

    def test_purchase_product_shopcart_no_exist(self):
        '''Purchase a Product shopcart doesn't exist'''
        user_id = 101
        with patch('requests.get') as get_shopcart_by_userid_mock:
            get_shopcart_by_userid_mock.return_value.status_code = 200
            get_shopcart_by_userid_mock.return_value.json.return_value = []
            with patch('requests.post') as post_shopcart_mock:
                post_shopcart_mock.return_value.status_code=201
                with patch('requests.post') as post_shopcartitem_mock:
                    post_shopcartitem_mock.return_value.status_code=201
                    json = {"user_id": user_id, "amount": 4}
                    product = self._create_products(1)
                    resp = self.app.post("/products/{}/purchase".format(product[0].id), json=json, content_type="application/json")
                    self.assertEqual(resp.status_code, status.HTTP_200_OK)
                    self.assertEqual(resp.data, b'Product successfully added into the shopping cart')
    
    def test_purchase_product_not_found(self):
        '''Purchase a Product that's not found'''
        user_id = 101
        with patch('requests.get') as get_shopcart_by_userid_mock:
                get_shopcart_by_userid_mock.return_value.status_code = 200
                get_shopcart_by_userid_mock.return_value.json.return_value = [{"create_time": "2020-11-15T19:36:28.302839","id": 6,"update_time": "2020-11-15T19:36:28.302839","user_id": 101}]
                with patch('requests.post') as post_shopcart_item_mock:
                    post_shopcart_item_mock.return_value.status_code=201
                    json = {"user_id": user_id, "amount": 4}
                    resp = self.app.post("/products/1/purchase", json=json, content_type="application/json")
                    self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_purchase_product_cannot_add_shopcart(self):
        '''Purchase a Product not added into shopcart (shopcart exists) '''
        user_id = 101
        with patch('requests.get') as get_shopcart_by_userid_mock:
            get_shopcart_by_userid_mock.return_value.status_code = 200
            get_shopcart_by_userid_mock.return_value.json.return_value = [{"create_time": "2020-11-15T19:36:28.302839","id": 6,"update_time": "2020-11-15T19:36:28.302839","user_id": 101}]
            with patch('requests.post') as post_shopcart_item_mock:
                post_shopcart_item_mock.return_value.status_code=400
                json = {"user_id": user_id, "amount": 4}
                product = self._create_products(1)
                resp = self.app.post("/products/{}/purchase".format(product[0].id), json=json, content_type="application/json")
                self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
                self.assertEqual(resp.data, b'Product was not added in the shopping cart because of an error')

    def test_purchase_unsuccessful_product_shopcart_no(self):
        '''Purchase a Product shopcart doesn't exist'''
        user_id = 101
        with patch('requests.get') as get_shopcart_by_userid_mock:
            get_shopcart_by_userid_mock.return_value.status_code = 200
            get_shopcart_by_userid_mock.return_value.json.return_value = []
            with patch('requests.post') as post_shopcart_mock:
                post_shopcart_mock.return_value.status_code=400
                json = {"user_id": user_id, "amount": 4}
                product = self._create_products(1)
                resp = self.app.post("/products/{}/purchase".format(product[0].id), json=json, content_type="application/json")
                self.assertEqual(resp.status_code,status.HTTP_400_BAD_REQUEST)
                self.assertEqual(resp.data, b'Cannot create shopcart so cannot add product into shopping cart')
    
    # def test_purchase_product_shopcart_no_exist(self):
    #     '''Purchase a Product shopcart doesn't exist'''
    #     user_id = 101
    #     with patch('requests.get') as get_shopcart_by_userid_mock:
    #         get_shopcart_by_userid_mock.return_value.status_code = 200
    #         get_shopcart_by_userid_mock.return_value.json.return_value = []
    #         with patch('requests.post') as post_shopcart_mock:
    #             post_shopcart_mock.return_value.status_code=201
    #             with patch('requests.post') as post_shopcartitem_mock:
    #                 post_shopcartitem_mock.return_value.status_code=400
    #                 json = {"user_id": user_id, "amount": 4}
    #                 product = self._create_products(1)
    #                 resp = self.app.post("/products/{}/purchase".format(product[0].id), json=json, content_type="application/json")
    #                 self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    #                 self.assertEqual(resp.data, b'Product not successfully added into the shopping cart')