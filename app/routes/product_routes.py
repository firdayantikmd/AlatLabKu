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

@product_routes.route('/productlist', methods=['GET', 'POST'])
@login_required
def get_productlist():
    from sqlalchemy import and_, or_, func
    from flask import request, render_template, flash

    # Initialize query and conditions
    query = Product.query
    conditions = []

    if request.method == 'POST':
        # Individual filters
        filter_field = request.form.getlist('filter_field[]')
        filter_operator = request.form.getlist('filter_operator[]')
        filter_value = request.form.getlist('filter_value[]')
        filter_logic = request.form.getlist('filter_logic[]')

        # Group filters
        group_filters = []
        group_logic = request.form.getlist('group_logic[]')  # Logic between groups

        # Parse group filters
        for key in request.form:
            if key.startswith('group_filters['):
                group_id = key.split('[')[1].split(']')[0]
                group_field = request.form.getlist(f'group_filters[{group_id}][field][]')
                group_operator = request.form.getlist(f'group_filters[{group_id}][operator][]')
                group_value = request.form.getlist(f'group_filters[{group_id}][value][]')
                group_logic_inside = request.form.getlist(f'group_filters[{group_id}][logic][]')

                group_filters.append({
                    'group_id': group_id,
                    'logic': group_logic_inside,
                    'field': group_field,
                    'operator': group_operator,
                    'value': group_value
                })

        # Function to process individual filters
        def process_filter_rules():
            print("Processing individual filter rules")
            i = 0  # Index for filter_value[]
            for idx in range(len(filter_field)):
                field = filter_field[idx]
                operator = filter_operator[idx]
                logic = filter_logic[idx - 1] if idx > 0 else 'and'

                # For date fields with 'is_between', collect two values
                if field in ['created_at', 'updated_at'] and operator == 'is_between':
                    value = filter_value[i:i+2]
                    i += 2
                else:
                    value = filter_value[i]
                    i += 1

                condition = generate_condition(field, operator, value)
                if condition is not None:
                    conditions.append((condition, logic))

        # Function to process group filters
        def process_group_filters():
            print("Processing group filters")
            for idx, group in enumerate(group_filters):
                group_conditions = []
                group_fields = group['field']
                group_operators = group['operator']
                group_values = group['value']
                group_logic_inside = group['logic']

                i = 0  # Index for group_values[]
                for j in range(len(group_fields)):
                    field = group_fields[j]
                    operator = group_operators[j]
                    logic = group_logic_inside[j - 1] if j > 0 else 'and'

                    # For date fields with 'is_between', collect two values
                    if field in ['created_at', 'updated_at'] and operator == 'is_between':
                        value = group_values[i:i+2]
                        i += 2
                    else:
                        value = group_values[i]
                        i += 1

                    condition = generate_condition(field, operator, value)
                    if condition is not None:
                        group_conditions.append((condition, logic))

        # Function for text-based conditions
        def handle_text_condition(field, operator, value):
            print(f"Handling text condition: field={field}, operator={operator}, value={value}")
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
                return getattr(Product, field) == None
            elif operator == 'is_not_empty':
                return getattr(Product, field) != None
            return None

        # Function for date-based conditions
        def handle_date_condition(field, operator, value):
            print(f"Handling date condition: field={field}, operator={operator}, value={value}")
            if operator == 'is' and value:
                return func.date(getattr(Product, field)) == value
            elif operator == 'is_before' and value:
                return func.date(getattr(Product, field)) < value
            elif operator == 'is_after' and value:
                return func.date(getattr(Product, field)) > value
            elif operator == 'is_between' and isinstance(value, (list, tuple)) and len(value) == 2:
                start_value, end_value = value
                if start_value > end_value:
                    flash("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.", "error")
                    return None
                return func.date(getattr(Product, field)).between(start_value, end_value)
            elif operator == 'is_empty':
                return getattr(Product, field) == None
            elif operator == 'is_not_empty':
                return getattr(Product, field) != None
            return None

        # Function for stock-based conditions
        def handle_stock_condition(operator, value):
            print(f"Handling stock condition: operator={operator}, value={value}")
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
            return None

        # Function for stock status conditions
        def handle_stock_status_condition(operator, value):
            print(f"Handling stock status condition: operator={operator}, value={value}")
            if operator == 'is':
                return Product.stock > 0 if value == 'available' else Product.stock <= 0
            elif operator == 'is_not':
                return Product.stock <= 0 if value == 'available' else Product.stock > 0
            return None

        # Function to generate SQLAlchemy conditions
        def generate_condition(field, operator, value):
            print(f"Generating condition for field: {field}, operator: {operator}, value: {value}")
            if field in ['created_at', 'updated_at']:
                if operator == 'is_between':
                    # 'value' should be a list of two dates
                    if isinstance(value, list) and len(value) == 2:
                        return handle_date_condition(field, operator, value)
                    else:
                        print("Invalid value for 'is_between' operator. Expected list of two dates.")
                        return None
                else:
                    return handle_date_condition(field, operator, value)
            elif field in ['product_name', 'code', 'details', 'category', 'storage']:
                return handle_text_condition(field, operator, value)
            elif field == 'stock':
                return handle_stock_condition(operator, value)
            elif field == 'stock_status':
                return handle_stock_status_condition(operator, value)
            return None

        # Function to combine conditions
        def combine_conditions():
            print(f"Combining conditions: {conditions}")
            if conditions:
                combined_conditions = conditions[0][0]
                for i in range(1, len(conditions)):
                    condition, logic = conditions[i]
                    if logic == 'and':
                        combined_conditions = and_(combined_conditions, condition)
                    elif logic == 'or':
                        combined_conditions = or_(combined_conditions, condition)
                return combined_conditions
            return None

        # Process filters
        process_filter_rules()
        process_group_filters()

        # Combine all conditions and execute query
        final_conditions = combine_conditions()

        if final_conditions is not None:
            print(f"Final conditions applied to query: {final_conditions}")
            query = query.filter(final_conditions)

    # Fetch products
    products = query.all()

    print(f"Query result: {len(products)} products found")

    # Render the template with filtered products
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
