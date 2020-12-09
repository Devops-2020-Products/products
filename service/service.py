"""
My Service

Describe what your service does here
"""

import os
#import sys
#import logging
#import json
import requests
from flask import jsonify, request, make_response, abort, render_template
from flask_api import status  # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
#from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api, Resource, fields, reqparse
from service.models import Product, DataValidationError

# Import Flask application
from . import app

SHOPCART_ENDPOINT = os.getenv('SHOPCART_ENDPOINT', 'https://nyu-shopcart-service-f20.us-south.cf.appdomain.cloud/api/shopcarts')

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Product REST API Service',
          description='This is a Product server.',
          default='products',
          default_label='Product operations',
          doc='/apidocs',
          prefix='/api'
          )

# Define the model so that the docs reflect what can be sent
create_model = api.model('Product', {
    'name': fields.String(required=True,
                          description='The name of the Product'),
    'category': fields.String(required=True,
                              description='The category of Product (e.g., food, technology, etc.)'),
    'description': fields.String(required=True,
                                 description='The description of the Product'),
    'price': fields.Float(required=True,
                          description='The price of the Product')
})

product_model = api.model('Product', {
    'name': fields.String(required=True,
                          description='The name of the Product'),
    'category': fields.String(required=True,
                              description='The category of Product (e.g., food, technology, etc.)'),
    'description': fields.String(required=True,
                                 description='The description of the Product'),
    'price': fields.Float(required=True,
                          description='The price of the Product'),
    'id': fields.String(readOnly=True,
                            description='The unique id assigned internally by service')
})


purchase_model = api.model('Purchase', {
    'id': fields.Integer(required=True,
                        description='The id of the Product'),
    'user_id': fields.Integer(required=True,
                              description='The user id of the person purchasing the Product'),
    'amount': fields.Integer(required=True,
                             description='The amount of the Product')
})

# query string arguments
product_args = reqparse.RequestParser()
product_args.add_argument('name', type=str, required=False, help='List Products by name')
product_args.add_argument('category', type=str, required=False, help='List Products by category')
product_args.add_argument('description', type=str, required=False, help='List Products by description')
product_args.add_argument('minimum', type=float, required=False, help='The minimum of the query price range')
product_args.add_argument('maximum', type=float, required=False, help='The maximum of the query price range')


######################################################################
# Error Handlers
######################################################################

@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad requests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=message
        ),
        status.HTTP_400_BAD_REQUEST,
    )

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_404_NOT_FOUND, error="Not Found", message=message
        ),
        status.HTTP_404_NOT_FOUND,
    )

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=str(error),
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )

@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=str(error),
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    app.logger.error(str(error))
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=str(error),
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return render_template('index.html')

@api.route('/products/<product_id>', strict_slashes=False)
@api.param('product_id', 'The Product identifier')
class ProductResource(Resource):
    """
    ProductResource class
    Allows the manipulation of a single Product
    GET /product{id} - Returns a Product with the id
    PUT /product{id} - Update a Product with the id
    DELETE /product{id} -  Deletes a Product with the id
    """

    #------------------------------------------------------------------
    # RETRIEVE A PRODUCT
    #------------------------------------------------------------------
    @api.doc('get_products')
    @api.response(404, 'Product not found')
    @api.response(400, 'Invalid Product ID')
    @api.marshal_with(product_model)
    def get(self, product_id):
        """
        Retrieve a product
        This endpoint will return a product based on its id
        """
        app.logger.info("Request for product with id: %s", product_id)
        try:
            product_id = int(product_id)
        except ValueError:
            app.logger.info("Invalid Product ID.")
            api.abort(status.HTTP_400_BAD_REQUEST, "Invalid Product ID.")

        product = Product.find(product_id)
        if not product:
            app.logger.info("Product with id [%s] was not found.", product_id)
            api.abort(status.HTTP_404_NOT_FOUND, "Product with id '{}' was not found.".format(product_id))

        app.logger.info("Returning product with id [%s].", product.id)
        return product.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT
    #------------------------------------------------------------------
    @api.doc('update_products')
    @api.response(404, 'Product not found')
    @api.response(400, 'The posted Product data was not valid')
    @api.expect(product_model)
    @api.marshal_with(product_model)
    def put(self, product_id):
        """
        Update a product
        This endpoint will update a product based on the request body
        """
        app.logger.info("Request to update product with id: %s", product_id)
        check_content_type("application/json")
        try:
            product_id = int(product_id)
        except ValueError:
            app.logger.info("Invalid Product ID.")
            api.abort(status.HTTP_400_BAD_REQUEST, "Invalid Product ID.")

        product = Product.find(product_id)
        if not product:
            app.logger.info("Product with id [%s] was not found.", product_id)
            api.abort(status.HTTP_404_NOT_FOUND, "Product with id '{}' was not found.".format(product_id))

        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        try:
            if 'price' in data and data['price'] != "":
                data['price'] = float(data['price'])
        except ValueError:
            api.abort(status.HTTP_400_BAD_REQUEST, "Incorrect format for price")
        if 'name' in data and data['name'] != "":
            product.name = data['name']
        if 'category' in data and data['category'] != "":
            product.category = data['category']
        if 'description' in data and data['description'] != "":
            product.description = data['description']
        if 'price' in data and data['price'] != "":
            product.price = data['price']
        product.update()
        app.logger.info("Product with id [%s] updated.", product.id)
        return product.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A PRODUCT
    #------------------------------------------------------------------
    @api.doc('delete_products')
    @api.response(204, 'Product deleted')
    def delete(self, product_id):
        """
        Delete a Product
        This endpoint will delete a product based the id specified in the path
        """
        app.logger.info("Request to delete product with id: %s", product_id)
        try:
            product_id = int(product_id)
        except ValueError:
            app.logger.info("Invalid Product ID.")
            api.abort(status.HTTP_400_BAD_REQUEST, "Invalid Product ID.")

        product = Product.find(product_id)
        if product:
            product.delete()
        app.logger.info("Product with id [%s] delete complete.", product_id)
        return make_response(jsonify(message = ''), status.HTTP_204_NO_CONTENT)

@api.route('/products', strict_slashes=False)
class ProductCollection(Resource):
    """ Handles all interactions with collections of Products """
    ######################################################################
    # ADD A NEW PRODUCT
    ######################################################################
    @api.doc('create_products')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Product created successfully')
    @api.marshal_with(product_model, code=201)
    def post(self):
        """
        Creates a Product
        This endpoint will create a Product based on the data in the body that is posted
        """
        app.logger.info("Request to create a product")
        check_content_type("application/json")
        product = Product()
        product.deserialize(api.payload)
        if product.id == "" or product.name == "" or product.description == "" or product.price == "" or product.category == "":
            app.logger.info("Fields cannot be empty.")
            return api.abort(status.HTTP_400_BAD_REQUEST, "Fields cannot be empty.")
        product.create()
        app.logger.info("Product with id [%s] created.", product.id)
        location_url = api.url_for(ProductResource, product_id=product.id, _external=True)
        return product.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

    ######################################################################
    # LIST ALL PRODUCTS OR QUERY PRODUCTS
    ######################################################################
    @api.doc('list_products')
    @api.expect(product_args, validate=True)
    @api.response(400, 'Minimum and Maximum cannot be empty')
    @api.marshal_list_with(product_model)
    @app.route("/products", methods=["GET"])
    def get(self):
        """ Returns all of the queried Products """
        app.logger.info("Request for product list")
        products = []
        args = product_args.parse_args()
        category = args.get('category')
        name = args.get('name')
        description = args.get('description')
        minimum = args.get('minimum')
        maximum = args.get('maximum')

        if minimum and maximum:
            if name and category and description:
                products = Product.find_by_name_category_description_price(name, category, description, minimum, maximum)
            elif name and category:
                products = Product.find_by_name_category_price(name, category, minimum, maximum)
            elif name and description:
                products = Product.find_by_name_description_price(name, description, minimum, maximum)
            elif name:
                products = Product.find_by_name_price(name, minimum, maximum)
            elif category and description:
                products = Product.find_by_category_description_price(category, description, minimum, maximum)
            elif category:
                products = Product.find_by_category_price(category, minimum, maximum)
            elif description:
                products = Product.find_by_description_price(description, minimum, maximum)
            else:
                products = Product.query_by_price(minimum, maximum)
        elif minimum is None and maximum is None:
            if name and category and description:
                products = Product.find_by_name_category_description(name, category, description)
            elif name and category:
                products = Product.find_by_name_category(name, category)
            elif name and description:
                products = Product.find_by_name_description(name, description)
            elif name:
                products = Product.find_by_name(name)
            elif category and description:
                products = Product.find_by_category_description(category, description)
            elif category:
                products = Product.find_by_category(category)
            elif description:
                products = Product.find_by_description(description)
            else:
                products = Product.all()
        else:
            app.logger.info("Minimum and Maximum cannot be empty.")
            return api.abort(status.HTTP_400_BAD_REQUEST, "Minimum and Maximum cannot be empty.")

        results = [product.serialize() for product in products]
        app.logger.info("Returning %d products.", len(results))
        return results, status.HTTP_200_OK

@api.route('/products/<product_id>/purchase', strict_slashes=False)
@api.param('product_id', 'The Product identifier')
@api.expect(purchase_model)
class PurchaseResource(Resource):
    """ Purchase actions on Products """
    ######################################################################
    # PURCHASE EXISTING PRODUCTS
    ######################################################################
    @api.doc('purchase_products')
    @api.response(200, 'Product successfully added into the shopping cart')
    @api.response(404, 'Product not found, or Product not successfully added into the shopping cart, or Cannot create shopcart so cannot add product into shopping cart, or Product was not added in the shopping cart because of an error')
    @api.response(400, 'Fields cannot be empty, or Invalid Product ID. Must be Integer, or Invalid User ID. Must be Integer, or Invalid Amount. Must be Integer')
    def post(self, product_id):
        """
        Purchase a product
        This endpoint will purchase a product based on the request body which should include the amount, user id, and shopcart id
        """
        app.logger.info("Request to purchase product with id: %s", product_id)
        check_content_type("application/json")
        request_body = request.get_json()
        if product_id == "" or 'amount' not in request_body or 'user_id' not in request_body or request_body['amount'] == "" or request_body['user_id'] == "":
            api.abort(status.HTTP_400_BAD_REQUEST, "Fields cannot be empty")
        try:
            product_id = int(product_id)
        except ValueError:
            app.logger.info("Invalid Product ID.")
            api.abort(status.HTTP_400_BAD_REQUEST, "Invalid Product ID. Must be Integer")
        product = Product.find(product_id)
        if not product:
            api.abort(status.HTTP_404_NOT_FOUND, "Product with id '{}' was not found.".format(product_id))
        try:
            user_id = int(request_body['user_id'])
        except ValueError:
            app.logger.info("Invalid User ID.")
            api.abort(status.HTTP_400_BAD_REQUEST, "Invalid User ID. Must be Integer")
        try:
            amount_update = int(request_body['amount'])
        except ValueError:
            app.logger.info("Invalid Amount.")
            api.abort(status.HTTP_400_BAD_REQUEST, "Invalid Amount. Must be Integer")
        header = {'Content-Type': 'application/json'}
        resp = requests.get('{}?user_id={}'.format(SHOPCART_ENDPOINT, user_id))
        app.logger.info("Trying to purchase product")
        r_json = resp.json()
        if len(r_json) == 0:
            info_json = {"user_id": user_id}
            create_shopcart_resp = create_shopcart(SHOPCART_ENDPOINT, header, info_json)
            if create_shopcart_resp.status_code == 201:
                message = create_shopcart_resp.json()
                shopcart_id = message['id']
                new_item = {}
                new_item["sku"] = product_id
                new_item["amount"] = amount_update
                product = product.serialize()
                new_item["name"] = product["name"]
                new_item["price"] = product["price"]
                add_into_shopcart = add_item_to_shopcart(SHOPCART_ENDPOINT + "/{}/items".format(shopcart_id), header, new_item)
                if add_into_shopcart.status_code == 201:
                    return make_response(jsonify(message = 'Product successfully added into the shopping cart'), status.HTTP_200_OK)
                return api.abort(status.HTTP_400_BAD_REQUEST, 'Product not successfully added into the shopping cart')
            return api.abort(status.HTTP_400_BAD_REQUEST, 'Cannot create shopcart so cannot add product into shopping cart')
        shopcart_id = r_json[0]['id']
        new_item = {}
        new_item["sku"] = product_id
        new_item["amount"] = amount_update
        product = product.serialize()
        new_item["name"] = product["name"]
        new_item["price"] = product["price"]
        add_into_shopcart = add_item_to_shopcart(SHOPCART_ENDPOINT + "/{}/items".format(shopcart_id), header, new_item)
        if add_into_shopcart.status_code == 201:
            return make_response(jsonify(message = 'Product successfully added into the shopping cart'), status.HTTP_200_OK)
        return api.abort(status.HTTP_404_NOT_FOUND, 'Product was not added in the shopping cart because of an error')

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Product.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))

def create_shopcart(url, header, json_data):
    '''Used to call the create shopcart function'''
    return requests.post(url, headers=header, json=json_data)

def add_item_to_shopcart(url, header, json_data):
    '''Used to call the add item to shopcart function'''
    return requests.post(url, headers=header, json=json_data)
