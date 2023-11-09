from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models.loan import Loan, LoanStatus
from models.product import Product
from models.user import User
from helpers import login_required

loan_routes = Blueprint('loan_routes', __name__)

@loan_routes.route('/loanlist', methods=['GET'])
@login_required
def get_loanlist():
    loans = Loan.query.all()
    return render_template('loanlist.html', loans=loans, LoanStatus=LoanStatus)

@loan_routes.route('/addloan', methods=['GET', 'POST'])
@login_required
def add_loan():
    logged_in_user = User.query.get(session.get('user_id'))

    full_name = logged_in_user.full_name
    student_id = logged_in_user.student_id

    products = Product.query.all()

    if request.method == 'GET':
        return render_template('addloan.html', products=products, full_name=full_name, student_id=student_id)

    elif request.method == 'POST':
        product_name = request.form.get('product_name')
        product_name, code = product_name.split(" - ")
        quantity = int(request.form.get('quantity'))
        
        user = User.query.filter_by(full_name=full_name, student_id=student_id).first()
        product = Product.query.filter_by(product_name=product_name, code=code).first()

        if product.stock < quantity:
            flash("Not enough stock available", "danger")
            return redirect(url_for('loan_routes.add_loan'))
        
        existing_loan = Loan.query.filter_by(user_id=user.id, product_id=product.id).first()

        if existing_loan:
            existing_loan.quantity += quantity
            product.stock -= quantity
        else:
            loan = Loan(user_id=user.id, product_id=product.id, quantity=quantity)
            product.stock -= quantity
            db.session.add(loan)
        
        db.session.commit()

        flash("Loan created successfully", "success")
        return redirect(url_for('loan_routes.get_loanlist'))

    return render_template('addloan.html')

@loan_routes.route('/editloan/<int:loan_id>', methods=['GET', 'POST'])
@login_required
def edit_loan(loan_id):

    loan = Loan.query.get(loan_id)

    if not loan:
        flash("Loan not found", "error")
        return redirect(url_for('loan_routes.get_loanlist'))

    if request.method == 'GET':
        return render_template('editloan.html', loan=loan, LoanStatus=LoanStatus)

    if request.method == 'POST':
        status_str = request.form.get('status')

        # Convert the string value to LoanStatus enum
        try:
            status_enum = LoanStatus[status_str]
            loan.status = status_enum
        except KeyError:
            flash("Invalid loan status", "error")
            return redirect(url_for('loan_routes.edit_loan', loan_id=loan.id))

        db.session.commit()

        flash("Loan updated successfully!", "success")
        return redirect(url_for('loan_routes.get_loanlist'))

@loan_routes.route('/deleteloan/<int:loan_id>', methods=['POST'])
@login_required
def delete_loan(loan_id):
    loan = Loan.query.get(id=loan_id)
    
    if not loan:
        flash("Loan not found", "error")
        return redirect(url_for('loan_routes.get_loanlist'))
        
    db.session.delete(loan)
    db.session.commit()
        
    flash("Loan deleted successfully", "success")
    return redirect(url_for('loan_routes.get_loanlist'))

