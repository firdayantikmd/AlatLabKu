from flask import Blueprint, render_template, session
from helpers import login_required

from models.user import User
from models.product import Product
from models.loan import Loan, LoanStatus
from models.returnitem import Return

base_routes = Blueprint('base_routes', __name__)


import logging

@base_routes.route('/', methods=['GET'])
@login_required
def home():
    logged_in_user = User.query.get(session.get('user_id'))

    if logged_in_user.role == 'Admin Lab':

        total_mahasiswa = User.query.filter(User.role == 'Mahasiswa').count()
        total_admins = User.query.filter(User.role == 'Admin Lab').count()
        total_products = Product.query.count()
        total_loans = Loan.query.count()
        total_returns = Return.query.count()


        unconfirmed_loans = Loan.query.filter(Loan.status == LoanStatus.CONFIRM).join(User).join(Product).add_columns(
            Loan.id, 
            User.full_name, 
            User.student_id,
            Product.product_name, 
            Product.code, 
            Product.category,
            Loan.quantity, 
            Loan.created_at
        ).all()

        return render_template(
            'index.html',
            logged_in_user=logged_in_user,
            total_mahasiswa=total_mahasiswa,
            total_admins=total_admins,
            total_products=total_products, 
            total_loans=total_loans, 
            total_returns=total_returns,
            unconfirmed_loans=unconfirmed_loans
        )


    total_loans = Loan.query.count()
    total_onloan = Loan.query.filter(Loan.status == LoanStatus.ON_LOAN).count()

    onloan_count = Loan.query.filter(Loan.status == LoanStatus.ON_LOAN).join(User).join(Product).add_columns(
            Loan.id,
            Product.product_name, 
            Product.code, 
            Product.category,
            Loan.quantity, 
            Loan.created_at
        ).all()

    return render_template(
            'index_mahasiswa.html',
            logged_in_user=logged_in_user,
            total_loans=total_loans,
            total_onloan=total_onloan,
            onloan_count=onloan_count
        ) 