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
    # Mengambil semua parameter filter dari request
    filter_field = request.args.getlist('filter_field[]')
    filter_operator = request.args.getlist('filter_operator[]')
    filter_value = request.args.getlist('filter_value[]')
    filter_logic = request.args.getlist('filter_logic[]')

    group_filter_logic = request.args.getlist('group_filter_logic[]')
    filter_value_start = request.args.getlist('filter_value_start[]')
    filter_value_end = request.args.getlist('filter_value_end[]')

    query = Product.query

    conditions = []  # Untuk filter rule biasa
    group_conditions = []  # Untuk filter group

    # Fungsi untuk menghasilkan kondisi SQLAlchemy
    def generate_condition(field, operator, value, start_value=None, end_value=None):
        if field in ['created_at', 'updated_at']:
            if operator == 'is' and start_value:
                return func.date(getattr(Product, field)) == start_value
            elif operator == 'is_before' and start_value:
                return func.date(getattr(Product, field)) < start_value
            elif operator == 'is_after' and start_value:
                return func.date(getattr(Product, field)) > start_value
            elif operator == 'is_between' and start_value and end_value:
                if start_value > end_value:
                    flash("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.", "error")
                    return None
                return func.date(getattr(Product, field)).between(start_value, end_value)
            elif operator == 'is_empty':
                return getattr(Product, field).is_(None)
            elif operator == 'is_not_empty':
                return getattr(Product, field).isnot_(None)
        else:
            if field in ['product_name', 'code', 'details']:
                if operator == 'is':
                    return getattr(Product, field) == value
                elif operator == 'is_not':
                    return getattr(Product, field) != value
                elif operator == 'contains':
                    return getattr(Product, field).ilike(f'%{value}%')
                elif operator == 'does_not_contain':
                    return ~getattr(Product, field).ilike(f'%{value}%')
                elif operator == 'starts_with':
                    return getattr(Product, field).ilike(f'{value}%')
                elif operator == 'ends_with':
                    return getattr(Product, field).ilike(f'%{value}')
                elif operator == 'is_empty':
                    return getattr(Product, field).is_(None)
                elif operator == 'is_not_empty':
                    return getattr(Product, field).isnot_(None)
            elif field in ['category', 'storage']:
                if operator == 'is':
                    return getattr(Product, field) == value
                elif operator == 'is_not':
                    return getattr(Product, field) != value
                elif operator == 'is_empty':
                    return getattr(Product, field).is_(None)
                elif operator == 'is_not_empty':
                    return getattr(Product, field).isnot_(None)
            if field == 'stock':
                if value == '' or value is None:
                    return None

                if operator == '=':
                    return Product.stock == value
                elif operator == '!=':
                    return Product.stock != value
                elif operator == '>':
                    return Product.stock > value
                elif operator == '<':
                    return Product.stock < value
                elif operator == '>=':
                    return Product.stock >= value
                elif operator == '<=':
                    return Product.stock <= value
                elif operator == 'is_empty':
                    return getattr(Product, field).is_(None)
                elif operator == 'is_not_empty':
                    return getattr(Product, field).isnot_(None)
            elif field == 'stock_status':
                if operator == 'is':
                    if value == 'available':
                        return Product.stock > 0
                    else:
                        return Product.stock <= 0
                elif operator == 'is_not':
                    if value == 'available':
                        return Product.stock <= 0
                    else:
                        return Product.stock > 0
        return None

    # Menggabungkan kondisi dari filter rule individual
    for i in range(len(filter_field)):
        field = filter_field[i]
        operator = filter_operator[i]
        
        # Periksa apakah nilai yang ingin diakses ada
        value = filter_value[i] if len(filter_value) > i else None
        start_value = filter_value_start[i] if len(filter_value_start) > i else None
        end_value = filter_value_end[i] if len(filter_value_end) > i else None

        if field and operator and (value or start_value):  # Periksa setidaknya salah satu nilai ada
            condition = generate_condition(field, operator, value, start_value, end_value)
            if condition is not None:
                conditions.append(condition)

    # Menangani filter group jika ada
    if len(group_filter_logic) > 0:
        group_conditions = []
        for i, group_logic in enumerate(group_filter_logic):
            group_field = filter_field[i]
            group_operator = filter_operator[i]
            group_value = filter_value[i] if len(filter_value) > i else None
            condition = generate_condition(group_field, group_operator, group_value)
            
            # Periksa apakah condition tidak None
            if condition is not None:
                group_conditions.append(condition)

        # Gabungkan grup filter sesuai logika AND/OR
        if len(group_conditions) > 0:
            combined_group_conditions = group_conditions[0]
            for j in range(1, len(group_conditions)):
                if group_filter_logic[j - 1] == 'and':
                    combined_group_conditions = and_(combined_group_conditions, group_conditions[j])
                elif group_filter_logic[j - 1] == 'or':
                    combined_group_conditions = or_(combined_group_conditions, group_conditions[j])

            # Tambahkan kondisi grup ke dalam kondisi utama
            conditions.append(combined_group_conditions)

    # Jika ada kondisi, gabungkan semua filter dengan logika yang dipilih
    if len(conditions) > 0:
        combined_conditions = conditions[0]
        for i in range(1, len(conditions)):
            if len(filter_logic) > i - 1:  # Pastikan filter_logic cukup panjang
                if filter_logic[i - 1] == 'and':
                    combined_conditions = and_(combined_conditions, conditions[i])
                elif filter_logic[i - 1] == 'or':
                    combined_conditions = or_(combined_conditions, conditions[i])
            else:
                # Jika tidak ada logika untuk menggabungkan, default ke AND
                combined_conditions = and_(combined_conditions, conditions[i])

        query = query.filter(combined_conditions)

    products = query.all()

    # Mengembalikan template dengan produk yang difilter
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
