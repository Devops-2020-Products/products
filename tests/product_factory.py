import factory
from factory.fuzzy import FuzzyChoice
from service.models import Product

class ProductFactory(factory.Factory):
	""" Creates fake products used for testing"""
	class Meta:
		model = Product 

	id = None
	name = FuzzyChoice(choices = ["iPhone","Fire Hydrant Toy", "Doll", "Bananas", "Apples"])

	description = FuzzyChoice(choices = ["Black iPhone"," Red Fire Hydrant Toy", "American Girl Doll", "Ripe Bananas", "Ripe Apples"])

	category = FuzzyChoice(choices = ["Technology", "Toy", "Food"])

	price = FuzzyChoice(choices = [999.99, 12.99, 5.99, 1.99])


if __name__ == '__main__':
    for _ in range(10):
        product = ProductFactory()
        print(product.serialize())
