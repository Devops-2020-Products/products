# products

Repo for the products team for NYU DevOps

## Prerequisite Installation using Vagrant VM

Initiating a development environment requires  **Vagrant** and **VirtualBox**. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Then all you have to do is clone this repo and invoke vagrant to start the base flask app:

```bash
    git clone https://github.com/Devops-2020-Products/products
    cd products
    vagrant up
    vagrant ssh
    cd /vagrant
    FLASK_APP=service:app flask run -h 0.0.0.0
```

The flask app should now be runing, enter the address in a browser to access.

## Structure of the repo

The flask base service is in the ```service``` directory and its tests are in the  ```tests``` directory 

```
├── service
│   ├── models.py
│   └── service.py
├── tests
│   ├── product_factory.py
│   ├── test_models.py
│   └── test_service.py
```
### Database  Fields
| Fields | Type | Description
| :--- | :--- | :--- |
| id | Integer | ID (auto-incremented by database) 
| name | String | Product Name
| description | String | Product Description
| category | String | Product Category
| price | Float | Product Price

## API Documentation
### URLS

 GET /products - Returns a list all of the products

 GET /products/{id} - Returns the product with a given id

 POST /products - creates a new product record in the database with the request body consisting of all the database fields needed

 PUT /products/{id} - updates a product record in the database with the request body consisting of all the database fields needed

 DELETE /products/{id} - deletes a product record in the database  

 GET /products/price - query the database by the price range of products

 POST /products/{id}/purchase - purchases the product with the corresponding id by adding it to user's shopping cart with the request body consisting of user_id, shopcart_id, and the amount you wish to purchase. 

 
## Vagrant shutdown

When you are done, you should exit the virtual machine and shut down the vm with:

```bash
 $ exit
 $ vagrant halt
```

If the VM is no longer needed you can remove it with:

```bash
  $ vagrant destroy
```




