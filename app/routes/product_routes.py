from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.product import Product, ProductType
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

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
        category = request.form.get('category', 'Bahan')
        storage = request.form.get('storage')
        stock = request.form.get('stock')
        details = request.form.get('details')

        product_image_path = None

        # Save the product image if provided
        if product_image_file and allowed_file(product_image_file.filename):
            filename = secure_filename(product_image_file.filename)
            product_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            product_image_file.save(product_image_path)

        product_by_product_name = Product.query.filter_by(product_name=product_name).first()

        if product_by_product_name:
            flash('Product name already exists. Choose another one.')
            return redirect(url_for('product_routes.add_product'))

        # Store product details in database
        new_product = Product(
            product_name=product_name,
            product_image=product_image_path,
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
    products = Product.query.all()
    return render_template('productlist.html', products=products)
    # page = request.args.get('page', 1, type=int)
    # per_page = request.args.get('per_page', 10, type=int)

    # search_term = request.args.get('search', '')
    # query = Product.query

    # if search_term:
    #     search_pattern = f"%{search_term}%"
    #     query = query.filter(
    #         Product.product_name.ilike(search_pattern) |
    #         Product.category.ilike(search_pattern)
    #     )

    # pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    # products = pagination.items

    # return render_template('productlist.html', products=products, pagination=pagination)

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
        category =  request.form.get('category')
        storage = request.form.get('storage')
        stock = request.form.get('stock')
        details = request.form.get('details')

        product.product_name = product_name if product_name else product.product_name
        product.category = category
        product.storage = storage
        product.stock = stock
        product.details = details

        product_image = request.files.get('product_image')

        if product_image and allowed_file(product_image.filename):
            if product.product_image and os.path.exists(product.product_image):
                os.remove(product.product_image)
                
            filename = secure_filename(product_image.filename)
            product_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
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
