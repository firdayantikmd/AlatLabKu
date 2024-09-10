from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy import String, Integer, Enum, DateTime, cast
from models.product import Product, ProductType
from database import db
from sqlalchemy import inspect, and_, or_, func

import os
from werkzeug.utils import secure_filename

from helpers import login_required

from flask import current_app

product_routes = Blueprint('product_routes', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_routes.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'GET':
        return render_template('addproduct.html')

    elif request.method == 'POST':
        product_name = request.form.get('product_name')
        product_image_file = request.files.get('product_image')
        code = request.form.get('code')
        category = request.form.get('category', 'Bahan')
        storage = request.form.get('storage')
        stock = request.form.get('stock')
        details = request.form.get('details')

        product_image_path = None

        # Save the product image if provided
        if product_image_file and allowed_file(product_image_file.filename):
            filename = secure_filename(product_image_file.filename)
            product_image_path = os.path.join(current_app.config['UPLOAD_FOLDER_PRODUCT'], filename)
            product_image_file.save(product_image_path)

        product_by_code = Product.query.filter_by(code=code).first()

        if product_by_code:
            flash('Product code already exists. Choose another one.')
            return redirect(url_for('product_routes.add_product'))

        # Store product details in database
        new_product = Product(
            product_name=product_name,
            product_image=product_image_path,
            code=code,
            category=category,
            storage=storage,
            stock=stock,
            details=details
        )
        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully!')
        return redirect(url_for('product_routes.get_productlist'))

    return render_template('addproduct.html',  products=products, pagination=pagination)

@product_routes.route('/productlist', methods=['GET'])
@login_required
def get_productlist():
    filter_field = request.args.get('filter_field')
    filter_operator = request.args.get('filter_operator')
    filter_value = request.args.get('filter_value')
    filter_value_start = request.args.get('filter_value_start')
    filter_value_end = request.args.get('filter_value_end')

    print(f"Filter Field: {filter_field}")
    print(f"Filter Operator: {filter_operator}")
    print(f"Filter Value: {filter_value}")
    print(f"Filter Value Start: {filter_value_start}")
    print(f"Filter Value End: {filter_value_end}")

    query = Product.query

    if filter_field:
        if filter_field in ['product_name', 'code', 'details']:
            if filter_operator == 'is':
                query = query.filter(getattr(Product, filter_field) == filter_value)
            elif filter_operator == 'is_not':
                query = query.filter(getattr(Product, filter_field) != filter_value)
            elif filter_operator == 'contains':
                query = query.filter(getattr(Product, filter_field).ilike(f'%{filter_value}%'))
            elif filter_operator == 'does_not_contain':
                query = query.filter(~getattr(Product, filter_field).ilike(f'%{filter_value}%'))
            elif filter_operator == 'starts_with':
                query = query.filter(getattr(Product, filter_field).ilike(f'{filter_value}%'))
            elif filter_operator == 'ends_with':
                query = query.filter(getattr(Product, filter_field).ilike(f'%{filter_value}'))
            elif filter_operator == 'is_empty':
                query = query.filter(getattr(Product, filter_field) == None)
            elif filter_operator == 'is_not_empty':
                query = query.filter(getattr(Product, filter_field) != None)

        elif filter_field in ['category', 'storage']:
            if filter_operator == 'is':
                query = query.filter(getattr(Product, filter_field) == filter_value)
            elif filter_operator == 'is_not':
                query = query.filter(getattr(Product, filter_field) != filter_value)
            elif filter_operator == 'is_empty':
                query = query.filter(getattr(Product, filter_field) == None)
            elif filter_operator == 'is_not_empty':
                query = query.filter(getattr(Product, filter_field) != None)

        elif filter_field == 'stock':
            if filter_operator == '=':
                query = query.filter(Product.stock == filter_value)
            elif filter_operator == '!=':
                query = query.filter(Product.stock != filter_value)
            elif filter_operator == '>':
                query = query.filter(Product.stock > filter_value)
            elif filter_operator == '<':
                query = query.filter(Product.stock < filter_value)
            elif filter_operator == '>=':
                query = query.filter(Product.stock >= filter_value)
            elif filter_operator == '<=':
                query = query.filter(Product.stock <= filter_value)
            elif filter_operator == 'is_empty':
                query = query.filter(Product.stock == None)
            elif filter_operator == 'is_not_empty':
                query = query.filter(Product.stock != None)

        elif filter_field == 'stock_status':
            if filter_operator == 'is':
                if filter_value == 'available':
                    query = query.filter(Product.stock > 0)
                else:
                    query = query.filter(Product.stock <= 0)
            elif filter_operator == 'is_not':
                if filter_value == 'available':
                    query = query.filter(Product.stock <= 0)
                else:
                    query = query.filter(Product.stock > 0)

        elif filter_field in ['created_at', 'updated_at']:
            if filter_operator == 'is':
                query = query.filter(getattr(Product, filter_field) == filter_value_start)
            elif filter_operator == 'is_before':
                query = query.filter(getattr(Product, filter_field) < filter_value_start)
            elif filter_operator == 'is_after':
                query = query.filter(getattr(Product, filter_field) > filter_value_start)
            elif filter_operator == 'is_between':
                query = query.filter(getattr(Product, filter_field).between(filter_value_start, filter_value_end))
            elif filter_operator == 'is_empty':
                query = query.filter(getattr(Product, filter_field) == None)
            elif filter_operator == 'is_not_empty':
                query = query.filter(getattr(Product, filter_field) != None)

    products = query.all()

    return render_template('productlist.html', products=products)

@product_routes.route('/productdetails/<int:id>')
@login_required
def product_details(id):
    product = Product.query.get(id)
    if not product:
        flash("Product not found", "error")
        return redirect(url_for('product_routes.get_productlist'))

    return render_template('productdetails.html', product=product)

@product_routes.route('/editproduct/<int:id>', methods=['GET', 'POST'])
@login_required
def editproduct(id):

    product = Product.query.get(id)

    if not product:
        flash("Product not found", "error")
        return redirect(url_for('product_routes.get_productlist'))
    
    if request.method == 'GET':
        return render_template('editproduct.html', product=product)
    
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        code = request.form.get('code')
        category =  request.form.get('category')
        storage = request.form.get('storage')
        stock = request.form.get('stock')
        details = request.form.get('details')

        product.product_name = product_name if product_name else product.product_name
        product.code = code if code else product.code
        product.category = category
        product.storage = storage
        product.stock = stock
        product.details = details

        product_image = request.files.get('product_image')

        if product_image and allowed_file(product_image.filename):
            if product.product_image and os.path.exists(product.product_image):
                os.remove(product.product_image)
                
            filename = secure_filename(product_image.filename)
            product_image_path = os.path.join(current_app.config['UPLOAD_FOLDER_PRODUCT'], filename)
            product_image.save(product_image_path)
            product.product_image = product_image_path
        
        db.session.commit()

        flash("Product updated successfully!", "success")
        return redirect(url_for('product_routes.get_productlist'))

@product_routes.route('/delete_product/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_product(id):
    product = Product.query.get(id)
    
    if not product:
        flash("Product not found", "error")
        return redirect(url_for('product_routes.get_productlist'))

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully!", "success")
    return redirect(url_for('product_routes.get_productlist'))
