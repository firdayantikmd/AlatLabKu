from flask import Blueprint

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/hello', methods=['GET'])
def hello():
    return "Hello!!"

@user_routes.route('/register', methods=['GET', 'POST'])
def register():
    pass

@user_routes.route('/login', methods=['GET', 'POST'])
def login():
    pass

@user_routes.route('/users', methods=['GET'])
def get_users():
    pass