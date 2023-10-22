from flask import Blueprint, render_template
from helpers import login_required
base_routes = Blueprint('base_routes', __name__)

@base_routes.route('/', methods=['GET'])
@login_required
def home():
    return render_template("index.html")
