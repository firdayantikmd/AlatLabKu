from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.product import Product, ProductType, ProductStatus
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

from helpers import login_required

product_routes = Blueprint('product_routes', __name__)

@product_routes.route('/productlist', methods=['GET'])
@login_required
def get_productlist():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    search_term = request.args.get('search', '')
    query = Product.query

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            Product.product_name.ilike(search_pattern) |
            Product.category.ilike(search_pattern)
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    return render_template('productlist.html', products=products, pagination=pagination)