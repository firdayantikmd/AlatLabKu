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

def handle_text_condition(field, operator, value):
    """Generate SQLAlchemy condition for text fields."""
    print(f"Handling text condition: field={field}, operator={operator}, value={value}")
    column = getattr(Product, field)
    if operator == 'is':
        return column == value
    elif operator == 'is_not':
        return column != value
    elif operator == 'contains':
        return column.ilike(f'%{value}%')
    elif operator == 'does_not_contain':
        return ~column.ilike(f'%{value}%')
    elif operator == 'starts_with':
        return column.ilike(f'{value}%')
    elif operator == 'ends_with':
        return column.ilike(f'%{value}')
    elif operator == 'is_empty':
        return column.is_(None)
    elif operator == 'is_not_empty':
        return column.is_not(None)
    return None

def handle_date_condition(field, operator, value):
    """Generate SQLAlchemy condition for date fields."""
    print(f"Handling date condition: field={field}, operator={operator}, value={value}")
    column = func.date(getattr(Product, field))
    if operator == 'is' and value:
        return column == value
    elif operator == 'is_before' and value:
        return column < value
    elif operator == 'is_after' and value:
        return column > value
    elif operator == 'is_between' and isinstance(value, list) and len(value) == 2:
        start_value, end_value = value
        if start_value > end_value:
            flash("Start date cannot be after end date.", "error")
            return None
        return column.between(start_value, end_value)
    elif operator == 'is_empty':
        return column.is_(None)
    elif operator == 'is_not_empty':
        return column.is_not(None)
    return None

def handle_stock_condition(operator, value):
    """Generate SQLAlchemy condition for the stock field."""
    print(f"Handling stock condition: operator={operator}, value={value}")
    if not value:
        return None
    try:
        value = int(value)
    except ValueError:
        flash("Invalid value for stock. Please enter a number.", "error")
        return None
    column = Product.stock
    operators = {
        '=': column == value,
        '!=': column != value,
        '>': column > value,
        '<': column < value,
        '>=': column >= value,
        '<=': column <= value
    }
    return operators.get(operator)

def handle_stock_status_condition(operator, value):
    """Generate SQLAlchemy condition for stock status."""
    print(f"Handling stock status condition: operator={operator}, value={value}")
    column = Product.stock
    is_available = column > 0
    is_unavailable = column <= 0
    if operator == 'is':
        return is_available if value == 'available' else is_unavailable
    elif operator == 'is_not':
        return is_unavailable if value == 'available' else is_available
    return None

def generate_condition(field, operator, value):
    """Generate SQLAlchemy condition based on field, operator, and value."""
    print(f"Generating condition for field={field}, operator={operator}, value={value}")
    if field in ['created_at', 'updated_at']:
        return handle_date_condition(field, operator, value)
    elif field in ['product_name', 'code', 'details', 'category', 'storage']:
        return handle_text_condition(field, operator, value)
    elif field == 'stock':
        return handle_stock_condition(operator, value)
    elif field == 'stock_status':
        return handle_stock_status_condition(operator, value)
    return None

def build_condition(conditions_list):
    """Recursively build SQLAlchemy conditions from a list."""
    if not conditions_list:
        return None
    combined_condition = None
    for logic, condition in conditions_list:
        if isinstance(condition, list):
            condition = build_condition(condition)
        if combined_condition is None:
            combined_condition = condition
        else:
            if logic == 'and':
                combined_condition = and_(combined_condition, condition)
            elif logic == 'or':
                combined_condition = or_(combined_condition, condition)
            else:
                combined_condition = and_(combined_condition, condition)
    return combined_condition

def process_filter_rules(fields, operators, values, logics):
    """Process individual filters and return conditions."""
    conditions = []
    value_index = 0
    for idx, field in enumerate(fields):
        operator = operators[idx]
        logic = logics[idx - 1] if idx > 0 else None
        operator_requires_value = operator not in ['is_empty', 'is_not_empty']
        if field in ['created_at', 'updated_at'] and operator == 'is_between':
            if value_index + 1 < len(values):
                value = values[value_index:value_index + 2]
                value_index += 2
            else:
                flash("Please provide both start and end dates.", "error")
                return []
        elif operator_requires_value:
            if value_index < len(values):
                value = values[value_index]
                value_index += 1
            else:
                flash(f"Missing value for '{field}' with operator '{operator}'.", "error")
                return []
        else:
            value = None
        condition = generate_condition(field, operator, value)
        if condition is not None:
            conditions.append((logic, condition))
    return conditions

def process_group_filters(groups, group_logics):
    """Process group filters and return conditions."""
    conditions = []
    for idx, group in enumerate(groups):
        group_conditions = []
        fields = group['field']
        operators = group['operator']
        values = group['value']
        logics_inside = group['logic']
        value_index = 0
        for j, field in enumerate(fields):
            operator = operators[j]
            logic = logics_inside[j - 1] if j > 0 else None
            operator_requires_value = operator not in ['is_empty', 'is_not_empty']
            if field in ['created_at', 'updated_at'] and operator == 'is_between':
                if value_index + 1 < len(values):
                    value = values[value_index:value_index + 2]
                    value_index += 2
                else:
                    flash("Please provide both start and end dates.", "error")
                    return []
            elif operator_requires_value:
                if value_index < len(values):
                    value = values[value_index]
                    value_index += 1
                else:
                    flash(f"Missing value for '{field}' with operator '{operator}'.", "error")
                    return []
            else:
                value = None
            condition = generate_condition(field, operator, value)
            if condition is not None:
                group_conditions.append((logic, condition))
        if idx == 0:
            logic_between_groups = group_logics[0] if group_logics else None
        else:
            logic_between_groups = group_logics[idx] if idx < len(group_logics) else 'and'
        conditions.append((logic_between_groups, group_conditions))
    return conditions

@product_routes.route('/productlist', methods=['GET', 'POST'])
@login_required
def get_productlist():
    """Display and filter the product list."""
    query = Product.query
    if request.method == 'POST':
        filter_fields = request.form.getlist('filter_field[]')
        filter_operators = request.form.getlist('filter_operator[]')
        filter_values = request.form.getlist('filter_value[]')
        filter_logics = request.form.getlist('filter_logic[]')

        group_filters = []
        group_logics = request.form.getlist('group_logic[]')
        for key in request.form:
            if key.startswith('group['):
                group_id = key.split('[')[1].split(']')[0]
                fields = request.form.getlist(f'group[{group_id}][field][]')
                operators = request.form.getlist(f'group[{group_id}][operator][]')
                values = request.form.getlist(f'group[{group_id}][value][]')
                logics_inside = request.form.getlist(f'group[{group_id}][logic][]')
                group_filters.append({
                    'group_id': group_id,
                    'logic': logics_inside,
                    'field': fields,
                    'operator': operators,
                    'value': values
                })

        individual_conditions = process_filter_rules(filter_fields, filter_operators, filter_values, filter_logics)
        group_conditions = process_group_filters(group_filters, group_logics)

        combined_conditions = []
        if individual_conditions:
            individual_condition = build_condition(individual_conditions)
            combined_conditions.append(individual_condition)
        
        if group_conditions:
            group_condition = build_condition(group_conditions)
            combined_conditions.append(group_condition)

        # Combine both individual and group conditions using `or_`
        if combined_conditions:
            final_condition = or_(*combined_conditions)
            query = query.filter(final_condition)

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
