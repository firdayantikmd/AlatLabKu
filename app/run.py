from flask import Flask, session, g
from database import init_db
from routes import user_routes, base_routes, product_routes, loan_routes, return_routes

import models

app = Flask(__name__, static_folder='static')
app.secret_key = 'pirda_cantik_suka_marah_marah'

app.config['UPLOAD_FOLDER'] = 'static/photo'

import logging

@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    logging.error('DEBUG')
    logging.error(user_id)
    if user_id:
        g.logged_in_user = models.user.User.query.get(user_id)
    else:
        g.logged_in_user = None

    # Check if logged_in_user is not None before trying to access its attributes
    if g.logged_in_user:
        logging.error(g.logged_in_user.role)
    else:
        logging.error("No logged in user")

    return dict(logged_in_user=g.logged_in_user)

init_db(app)

app.register_blueprint(user_routes)
app.register_blueprint(base_routes)
app.register_blueprint(product_routes)
app.register_blueprint(loan_routes)
app.register_blueprint(return_routes)

if __name__ == "__main__":
    app.run(debug=True)
