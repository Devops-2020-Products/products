"""
Models for Product

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import InvalidRequestError


# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Product(db.Model):
    """
    Class that represents a product
    """

    logger = logging.getLogger(__name__)
    app = None
    ##################################################
    # Table Schema
    ##################################################

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(63), nullable=False)
    price = db.Column(db.Float, nullable=False)

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return "<<Product> %r id=[%s] %r %r %f >" % (self.name, self.id, self.description, self.category, self.price)

    def create(self):
        """
        Creates a Product to the data store
        """
        self.logger.info("Creating %s", self.name)
        self.id = None
        db.session.add(self)
        try:
            db.session.commit()
        except InvalidRequestError:
            db.session.rollback()


    def update(self):
        """
        Updates a Product to the data store
        """
        self.logger.info("Updating %s", self.name)
        if not self.id:
            self.logger.info("Update called with empty ID field")
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except InvalidRequestError:
            db.session.rollback()

    def delete(self):
        """ Removes a Product from the data store """
        self.logger.info("Deleting %r", self.name)
        db.session.delete(self)
        try:
            db.session.commit()
        except InvalidRequestError:
            db.session.rollback()

    def serialize(self):
        """ Serializes a Product into a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "description" : self.description,
            "category": self.category,
            "price": self.price
        }

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.description = data["description"]
            self.category = data["category"]
            self.price = data["price"]

        except KeyError as error:
            raise DataValidationError("Invalid product : missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid product: body of request contained bad or no data"
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Products in the database """
        cls.logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, product_id: int):
        """Finds a Product by its ID
        :param product_id: the id of the product to find
        :type product_id: int
        :return: an instance with the product_id, or None if not found
        :rtype: Product
        """
        cls.logger.info("Processing lookup for id %s ...", product_id)
        return cls.query.get(product_id)

    @classmethod
    def find_by_name(cls, name: str):
        """Returns all Products with the given name
        :param name: the name of the Products you want to match
        :type name: str
        :return: a collection of Products with that name
        :rtype: list
        """
        cls.logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_category(cls, category: str):
        """Returns all of the Products in a category
        :param category: the category of the Products you want to match
        :type category: str
        :return: a collection of Products in that category
        :rtype: list
        """
        cls.logger.info("Processing category query for %s ...", category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def find_by_description(cls, description: str):
        """Returns all of the Products match the description
        :param description: the description of the Products you want to match
        :type description: str
        :return: a collection of Products match the description
        :rtype: list
        """
        cls.logger.info("Processing description query for %s ...", description)
        return cls.query.filter(cls.description == description)

    @classmethod
    def query_by_price(cls, minimum: float, maximum: float):
        """Returns all of the Products match the price in range from minimum to maximum
        :param description: the minimum and maximum of the Products you want to match
        :type description: two floats
        :return: a collection of Products match the price range
        :rtype: list
        """
        Product.logger.info("Searching for all products within the price range of minimum to maximum")
        return Product.query.filter((Product.price.between(minimum, maximum)))
