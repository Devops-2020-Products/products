"""
My Service

Describe what your service does here
"""

import os
#import sys
#import logging
#import json
import uuid
import requests
from functools import wraps
from flask import Flask, jsonify, request, url_for, make_response, abort,render_template
from flask_api import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
#from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api, Resource, fields, reqparse, inputs
from service.models import Product, DataValidationError

# Import Flask application
from . import app

SHOPCART_ENDPOINT = os.getenv('SHOPCART_ENDPOINT', 'https://nyu-shopcart-service-f20.us-south.cf.appdomain.cloud/api/shopcarts')

# authorizations = {
#     'apikey': {
#         'type': 'apiKey',
#         'in': 'header',
#         'name': 'X-Api-Key'
#     }
# }

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
          # authorizations=authorizations,
          prefix='/api'
          )

# Define the model so that the docs reflect what can be sent
product_model = api.model('Product', {
    'id': fields.Integer(readOnly=True,
                         description='The unique id assigned internally by service'),
    'name': fields.String(required=True,
                          description='The name of the Product'),
    'category': fields.String(required=True,
                              description='The category of Product (e.g., food, technology, etc.)'),
    'description': fields.String(required=True,
                              description='The description of the Product'),                         
    'price': fields.Float(required=True,
                                description='The price of the Product')
})

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

# query string arguments
product_args = reqparse.RequestParser()
product_args.add_argument('name', type=str, required=False, help='List Products by name')
product_args.add_argument('category', type=str, required=False, help='List Products by category')
product_args.add_argument('description', type=str, required=False, help='List Products by description')
product_args.add_argument('price', type=float, required=False, help='List Pets by price or price range')


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


# @app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
# def mediatype_not_supported(error):
#     """ Handles unsupported media requests with 415_UNSUPPORTED_MEDIA_TYPE """
#     message = str(error)
#     app.logger.warning(message)
#     return (
#         jsonify(
#             status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#             error="Unsupported media type",
#             message=message,
#         ),
#         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#     )

######################################################################
# Authorization Decorator
######################################################################
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if 'X-Api-Key' in request.headers:
#             token = request.headers['X-Api-Key']

#         if app.config.get('API_KEY') and app.config['API_KEY'] == token:
#             return f(*args, **kwargs)
#         else:
#             return {'message': 'Invalid or missing token'}, 401
#     return decorated

######################################################################
# Function to generate a random API key (good for testing)
######################################################################
# def generate_apikey():
#     """ Helper function used when testing API keys """
#     return uuid.uuid4().hex

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return render_template('index.html')

@api.route('/products/<product_id>')
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
    @api.marshal_with(product_model)
    def get(self,product_id):
        """
        Retrieve a product
        This endpoint will return a product based on its id
        """
        app.logger.info("Request for product with id: %s", product_id)
        product = Product.find(product_id)
        if not product:
            api.abort(status.HTTP_404_NOT_FOUND, "Product with id '{}' was not found.".format(product_id))

        app.logger.info("Returning product: %s", product.name)
        return product.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT
    #------------------------------------------------------------------
    @api.doc('update_pets')
    @api.response(404, 'Pet not found')
    @api.response(400, 'The posted Pet data was not valid')
    @api.expect(product_model)
    @api.marshal_with(product_model)
    def put(self,product_id):
        """
        Update a product
        This endpoint will update a product based on the request body
        """
        app.logger.info("Request to update product with id: %s", product_id)
        check_content_type("application/json")
        product = Product.find(product_id)
        if not product:
            api.abort(status.HTTP_404_NOT_FOUND, "Product with id '{}' was not found.".format(product_id))
        app.logger.debug('Payload = %s', api.payload)
        product_name = product.name
        product_description = product.description
        product_category = product.category
        product_price = product.price
        data = api.payload
        product.deserialize(data)
        product.id = product_id
        if product.name == "":
            product.name = product_name
        if product.description == "":
            product.description = product_description
        if product.price == "":
            product.price = product_price
        if product.category == "":
            product.category = product_category
        product.update()
        app.logger.info("Product with ID [%s] updated.", product.id)
        return product.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A PRODUCT
    #------------------------------------------------------------------
    @api.doc('delete_products')
    @api.response(204, 'Product deleted')
    def delete(self,product_id):
        """
        Delete a Product
        This endpoint will delete a product based the id specified in the path
        """
        app.logger.info("Request to delete product with id: %s", product_id)
        product = Product.find(product_id)
        if product:
            product.delete()
        app.logger.info("Product with ID [%s] delete complete.", product_id)
        return '', status.HTTP_204_NO_CONTENT

@api.route('/products', strict_slashes=False)
class ProductCollection(Resource):

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
        Creates a Products
        This endpoint will create a Product based the data in the body that is posted
        """
        app.logger.info("Request to create a product")
        check_content_type("application/json")
        product = Product()
        product.deserialize(api.payload)
        if product.id == "" or product.name == "" or product.description == "" or product.price == "" or product.category == "":
            return request_validation_error("Fields cannot be empty")
        product.create()
        app.logger.info("Product with ID [%s] created.", product.id)
        location_url = api.url_for(ProductResource, product_id=product.id, _external=True)
        return product.serialize(), status.HTTP_201_CREATED, {'Location': location_url}
        
######################################################################
# LIST ALL PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """ Returns all of the Products """
    app.logger.info("Request for product list")
    products = []

    category = request.args.get("category")
    name = request.args.get("name")
    description = request.args.get("description")

    if category:
        products = Product.find_by_category(category)
    elif name:
        products = Product.find_by_name(name)
    elif description:
        products = Product.find_by_description(description)
    else:
        products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# QUERY PRODUCTS BY PRICE RANGE
######################################################################
@app.route("/products/price", methods=["GET"])
def query_product_by_price():
    """ List all the product by their price range """
    app.logger.info("Querying products by provided price range")
    products = []

    minimum = request.args.get('minimum')
    maximum = request.args.get('maximum')
    if maximum is None or minimum is None:
        return request_validation_error("Minimum and Maximum cannot be none")
    if maximum == "" or minimum == "":
        return request_validation_error("Minimum and Maximum cannot be empty")

    products = Product.query_by_price(minimum, maximum)

    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# PURCHASE AN EXISTING PRODUCT
######################################################################
@app.route("/products/<int:product_id>/purchase", methods=["POST"])
def purchase_products(product_id):
    """
    Purchase a product
    This endpoint will purchase a product based on the request body which should include the amount, user id, and shopcart id
    """
    app.logger.info("Request to purchase product with id: %s", product_id)
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        raise NotFound("Product with id '{}' was not found.".format(product_id))
    request_body = request.get_json()
    amount_update = request_body['amount']
    user_id = request_body['user_id']
    header = {'Content-Type': 'application/json'}
    resp = requests.get('{}?user_id={}'.format(SHOPCART_ENDPOINT,user_id))
    r_json = resp.json()
    if len(r_json) == 0:
        info_json = {"user_id": user_id}
        create_shopcart_resp = create_shopcart(SHOPCART_ENDPOINT,header,info_json)
        if create_shopcart_resp.status_code == 201:
            message = create_shopcart.json()
            shopcart_id = message['id']
            new_item = {}
            new_item["sku"] = product_id
            new_item["amount"] = amount_update
            product = product.serialize()
            new_item["name"] = product["name"]
            new_item["price"] = product["price"]
            add_into_shopcart = add_item_to_shopcart(SHOPCART_ENDPOINT + "/{}/items".format(shopcart_id),header,new_item)
            if add_into_shopcart.status_code == 201:
                return make_response("Product successfully added into the shopping cart", status.HTTP_200_OK)
            return make_response("Product not successfully added into the shopping cart", status.HTTP_400_BAD_REQUEST)
        return make_response("Cannot create shopcart so cannot add product into shopping cart", status.HTTP_400_BAD_REQUEST)
    shopcart_id = r_json[0]['id']
    new_item = {}
    new_item["sku"] = product_id
    new_item["amount"] = amount_update
    product = product.serialize()
    new_item["name"] = product["name"]
    new_item["price"] = product["price"]
    add_into_shopcart = add_item_to_shopcart(SHOPCART_ENDPOINT + "/{}/items".format(shopcart_id),header,new_item)
    if add_into_shopcart.status_code == 201:
        return make_response("Product successfully added into the shopping cart", status.HTTP_200_OK)
    return make_response("Product was not added in the shopping cart because of an error", status.HTTP_404_NOT_FOUND)

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

def create_shopcart(url,header,json_data):
    '''Used to call the create shopcart function'''
    return requests.post(url,headers = header,json = json_data)

def add_item_to_shopcart(url,header,json_data):
    '''Used to call the add item to shopcart function'''
    return requests.post(url,headers = header, json = json_data)
