from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from models.returnitem import Return, ReturnStatus
from models.user import User, UserRole
from models.product import Product
from models.loan import Loan, LoanStatus
from helpers import login_required

return_routes = Blueprint('return_routes', __name__)


import logging

@return_routes.route('/returnlist', methods=['GET'])
@login_required
def get_returnlist():
    logged_in_user = User.query.get(session.get('user_id'))

    if logged_in_user.role == 'Mahasiswa':
        returns = Return.query.filter_by(user_id=logged_in_user.id).all()
    else:
        returns = Return.query.all()
        
    return render_template('returnlist.html', returns=returns, ReturnStatus=ReturnStatus)

@return_routes.route('/addreturn/<int:loan_id>', methods=['GET', 'POST'])
@login_required
def add_return(loan_id):
    logged_in_user = User.query.get(session.get('user_id'))
    full_name = logged_in_user.full_name
    student_id = logged_in_user.student_id

    loan = Loan.query.get(loan_id)


    logging.error(request.form)

    if request.method == 'GET':
        return render_template('addreturn.html', loan=loan, LoanStatus=LoanStatus, full_name=full_name, student_id=student_id)

    
    elif request.method == 'POST':
        returned_quantity = int(request.form.get('returned_quantity'))

        loan = Loan.query.get(loan_id)
        product = Product.query.get(loan.product.id)

        logging.error(loan)
        logging.error(product)

        if loan and product:
            if loan.quantity < returned_quantity:
                flash("You cannot return more than you borrowed!", "danger")
                return redirect(url_for('return_routes.add_return'))
            
            previous_quantity = loan.quantity
            loan.quantity -= returned_quantity

            product = Product.query.get(loan.product_id)
            product.stock += returned_quantity

            return_entry = Return(user_id=logged_in_user.id, product_id=product.id, loan_id=loan.id, returned_quantity=returned_quantity)
            db.session.add(return_entry)

            status = request.form.get('status')
            
            if loan.quantity == 0:
                loan.status = LoanStatus.RETURNED
            elif loan.quantity < previous_quantity:
                loan.status = LoanStatus.PARTIALLY_RETURNED

            db.session.commit()

            flash("Item returned successfully", "success")
            return redirect(url_for('return_routes.get_returnlist'))

        flash("Invalid loan", "danger")
        return redirect(url_for('return_routes.add_return'))

    return render_template('addreturn.html')

@return_routes.route('/editreturn/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_return(id):

    r = Return.query.get(id)

    if not r:
        flash("Return item not found", "error")
        return redirect(url_for('return_routes.get_returnlist'))

    if request.method == 'GET':
        return render_template('editreturn.html', r=r, ReturnStatus=ReturnStatus)

    if request.method == 'POST':
        status_str = request.form.get('status')
        note = request.form.get('note')

        r.note = note

        try:
            status_enum = ReturnStatus[status_str]
            r.status = status_enum
        except KeyError:
            flash("Invalid return status", "error")
            return redirect(url_for('return_routes.edit_return', id=r.id))
        
        db.session.commit()

        flash("Return updated successfully!", "success")
        return redirect(url_for('return_routes.get_returnlist'))

@return_routes.route('/returnback/<int:id>', methods=['GET', 'POST'])
@login_required
def return_back(id):

    r = Return.query.get(id)

    r.status = ReturnStatus.CONFIRM

    db.session.commit()

    flash("Successfully applied for a return!", "success")
    return redirect(url_for('return_routes.get_returnlist'))

@return_routes.route('/finalize_return/<int:return_id>', methods=['POST'])
@login_required
def finalize_return(return_id):
    return_entry = Return.query.get(return_id)
    
    if return_entry and return_entry.status != ReturnStatus.FINISHED:
        return_entry.status = ReturnStatus.FINISHED
        loan = Loan.query.get(return_entry.loan_id)
        product = Product.query.get(loan.product_id)
        product.stock += loan.quantity  # Add back the returned items to the stock

        db.session.commit()
        flash("Return finalized and stock updated", "success")
    else:
        flash("Invalid return or return already finalized", "danger")

    return redirect(url_for('loan_routes.get_returnlist'))

