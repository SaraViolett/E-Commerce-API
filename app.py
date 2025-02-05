from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from sqlalchemy import ForeignKey, Table, Column, String, DateTime, select, Float
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from typing import List
import datetime
# Initialize Flask app
app = Flask(__name__)
# MySQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:leaRning1!@localhost/ecommerce_api'

# Base Model
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy(manage database coonnections) and Marshmallow(serialization, deserialization, and validation)   
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

# Order-Product Association Table for orders and products for many to many associations
order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"),primary_key=True), 
    Column("product_id", ForeignKey("products.id"),primary_key=True)
)

#==============================MODELS===================================================================
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    #one to many relationship for user to orders:
    orders:Mapped[List["Order"]] = relationship(back_populates="users")
    
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    #one-to-one relationship with user
    users:Mapped["User"] = relationship(back_populates="orders")
    #One-to-Many relationship from this order to a list of product objects
    products: Mapped[List["Product"]] = relationship("Product", secondary=order_product, back_populates="orders")
    
class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float(10), nullable=False)
    # One-to-Many relationship, one product can be related to a list of orders
    orders: Mapped[List["Order"]] = relationship("Order", secondary=order_product, back_populates="products")    

#================================== SCHEMAS =============================================================
# User Schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
# User Schema
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
# User Schema
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        
# ============================ Initialize Schemas ========================================================
user_schema = UserSchema() #Can serialize one User object
users_schema = UserSchema(many=True) #Can serialize many User objects (a list of them)
order_schema = OrderSchema() #Can serialize one Product object 
orders_schema = OrderSchema(many=True) #Can serialize many Product objects (a list of them)
product_schema = ProductSchema() #Can serialize one Order object
products_schema = ProductSchema(many=True) #Can serialize many Order objects (a list of them)

#===========================CRUD endpoints=============================================================
#===========================User Endpoints==============================================
#GET/users: Retieve all users
@app.route('/users', methods=['GET']) #retrieves ALL users form users table within database as endpoint
def get_users(): 
    query = select(User) #Constructs a SQL query to select all records from the User table.
    users = db.session.execute(query).scalars().all() # Executes the query and retrieves all user records from the database as a list.
    return users_schema.jsonify(users), 200 #Serializes the list of users into JSON format. Returns the list of users with a 200 status code indicating success.

#GET /users/<id>: Retrieve a user by ID
@app.route('/users/<int:id>', methods=['GET']) #retrieves one user by id form users table within database as endpoint
def get_user(id):
    user = db.session.get(User, id) # Queries the database to retrieve the user object based on the provided id.
    return user_schema.jsonify(user), 200 #user data serialized to return the user object in JSON format. The route responds with a 200 status code indicating a successful operation.

#POST /users: Create a new user
@app.route('/users', methods=['POST']) #users table in database as endpoint
def create_user():
    try:
        user_data = user_schema.load(request.json) #Retrieves the JSON data from the incoming request
    except ValidationError as e: #Catches validation errors and returns error message
        return jsonify(e.messages), 400 
    new_user = User(name=user_data['name'], address=user_data['address'], email=user_data['email']) #Creates a new User object with the validated data.
    db.session.add(new_user) #Adds the new user to the database.
    db.session.commit() #Saves the new user to the database.
    return user_schema.jsonify(new_user), 201 #Returns the newly created user in JSON format with a 201 status.

#PUT /users/<id>: Update a user by ID
@app.route('/users/<int:id>', methods=['PUT']) #user by id in users table in database as endpoint
def update_user(id):
    user = db.session.get(User, id) # Queries the database to retrieve the user object based on the provided id.
    if not user:
        return jsonify({"message": "Invalid user id"}), 400 #if user object not valid this message is returned
    try:
        user_data = user_schema.load(request.json) #Retrieves the JSON data from the incoming request
    except ValidationError as e: #Catches validation errors and returns error message
        return jsonify(e.messages), 400
    user.name = user_data['name'] #update field
    user.address = user_data['address'] #update field
    user.email = user_data['email'] #update field
    db.session.commit() #saves updates
    return user_schema.jsonify(user), 200 # returns the updated user in JSON format with a 200 status code.

#DELETE /users/<id>: Delete a user by ID
@app.route('/users/<int:id>', methods=['DELETE']) #user by id in users table in database as endpoint
def delete_user(id):
    user = db.session.get(User, id) # Queries the database to retrieve the user object based on the provided id.
    if not user:
        return jsonify({"message": "Invalid user id"}), 400 #if user object not valid this message is returned
    db.session.delete(user) #delete user
    db.session.commit() #save change
    return jsonify({"message": f"succefully deleted user {id}"}), 200 #Returns a success message and a 200 status code.

#================================Product Endpoints=========================================
#GET /products: Retrieve all products
@app.route('/products', methods=['GET']) #retrieves ALL products form products table within database as endpoint
def get_products(): 
    query = select(Product) #Constructs a SQL query to select all records from the product table.
    products = db.session.execute(query).scalars().all() # Executes the query and retrieves all product records from the database as a list.
    return products_schema.jsonify(products), 200 #Serializes the list of products into JSON format. Returns the list of products with a 200 status code indicating success.

#GET /products/<id>: Retrieve a product by ID
@app.route('/products/<int:id>', methods=['GET']) #retrieves one product by id form products table within database as endpoint
def get_product(id):
    product = db.session.get(Product, id) # Queries the database to retrieve the product object based on the provided id.
    return product_schema.jsonify(product) #user data serialized to return the product object in JSON format. The route responds with a 200 status code indicating a successful operation.

#POST /products: Create a new product 
@app.route('/products', methods=['POST']) #products table in database as endpoint
def create_product():
    try:
        product_data = product_schema.load(request.json) #Retrieves the JSON data from the incoming request
    except ValidationError as e: #Catches validation errors and returns error message
        return jsonify(e.messages), 400
    new_product = Product(product_name=product_data['product_name'], price=product_data['price']) #Creates a new produst object with the validated data.
    db.session.add(new_product) #adds new product to the database
    db.session.commit() #returns new product to the database
    return product_schema.jsonify(new_product), 201 #Returns the newly created product in JSON format with a 201 status.

#PUT /products/<id>: Update a product by ID
@app.route('/products/<int:id>', methods=['PUT']) #product by id in products table in database as endpoint
def update_product(id):
    product = db.session.get(Product, id) # Queries the database to retrieve the product object based on the provided id.
    if not product:
        return jsonify({"message": "Invalid product id"}), 400 #if product object not found this message is returned
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e: #Catches validation errors and returns error message
        return jsonify(e.messages), 400
    product.product_name = product_data['product_name'] #update field
    product.price = product_data['price'] #update field
    db.session.commit() #saves update
    return product_schema.jsonify(product), 200 #Returns the updated product in JSON format with a 200 status.

#DELETE /products/<id>: Delete a product by ID
@app.route('/products/<int:id>', methods=['DELETE']) #product by id in products table in database as endpoint
def delete_product(id):
    product = db.session.get(Product, id) # Queries the database to retrieve the product object based on the provided id.
    if not product:
        return jsonify({"message": "Invalid product id"}), 400 #if product object not found this message is returned
    db.session.delete(product) #delete product
    db.session.commit() #save change
    return jsonify({"message": f"succefully deleted product {id}"}), 200 #Returns a success message and a 200 status code.

#===============================Order Endpoints======================================================
#POST /orders: Create a new order (requires user ID and order date)
@app.route('/orders', methods=['POST']) 
def create_order():
    try:
        order_data = order_schema.jsonify(request.json) #Retrieves the JSON data from the incoming request
    except ValidationError as e: #catches validation error and returns error message
        return jsonify(e.messages), 400
    new_order = Order(user_id=order_data['user.id']) #Creates a new order object with the validated data.
    db.session.add(new_order) #adds new order to database
    db.session.commit() #saves new order
    return order_schema.jsonify(new_order), 201 #Returns the newly created oreder in JSON format with a 201 status.       
    
#GET /orders/<order_id>/add_product/<product_id>: Add a product to an order (prevent duplicates)
@app.route('/orders/<order_id>/add_product/<product_id>', methods=['GET']) #associates a product with an order
def add_product_2_order(order_id, product_id):
    order = db.session.get(Order, order_id) #retrieves order from database
    product = db.session.get(Product, product_id) #retrieves product from database
    order.products.append(product) #adds the product to the list of products for that order
    db.session.commit() #saves the change
    return jsonify({"message": f"{product.product_name} at ${product.price} was added the order (Order id: {order.id}, User_id: {order.user_id})"})

#DELETE /orders/<order_id>/remove_product: Remove a product from an order
@app.route('/orders/<order_id>/remove_product', methods=['Delete']) #associates a product with an order
def remove_product_from_order(order_id, product_id):
    order = db.session.get(Order, order_id) #retrieves order from database
    product = db.session.get(Product, product_id) #retrieves product from database
    order.products.remove(product) #removes the product from the list of products for that order
    db.session.commit() #saves the change
    return jsonify({"message": f"{product.product_name} at ${product.price} was removed from the order (Order id: {order.id}, User_id: {order.user_id})"})

#GET /orders/user/<user_id>: Get all orders for a user
@app.route('/orders/user/<user_id>', methods=['GET'])
def get_orders_from_user(id):
    user = db.session.get(User, id)
    for order in user.orders:
        return jsonify({"message": f"{user.name} has made the following orders(id): {order.id}"})
    
#GET /orders/<order_id>/products: Get all products for an order
@app.route('/orders/<order_id>/products', methods=['GET'])
def get_products_from_order(id):
    order = db.session.get(Order, id)
    for product in order.products:
        return jsonify({"message": f"{order.id} order has contains the following products: {product.product_name}"})
#=====================================================================================================================================================

if __name__ == "__main__":
    with app.app_context():
            db.create_all()  
    app.run(debug=True)

