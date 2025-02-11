Title: Module 3 E-Commerce API Project
Discription: For this Coding Temple project I created an e-commerce API using Flask, Flask-SQLAlchemy, Flask-Marshmallow, and MySQL. The API manages Users, Orders, and Products with relationships, including One-to-Many and Many-to-Many associations.
How to run app.py: 
1. Set up the virtual environment:
    python3 -m venv venv
2. Activate the virtual environment:
    venv\Scripts\activate
3. Installed dependencies:
    pip install Flask Flask-SQLAlchemy Flask-Marshmallow marshmallow-sqlalchemy mysql-connector-python
    See requirements.txt for full list of apps for setting up the virtual environment.
5. Run postman requests. *Wait to use "DELETE" method until the corresponding user, order or product has been created. The date will autopoplate when creating an order, only the user_id is needed as input. 