from flask import Flask
from database import init_db
from routes import user_routes, base_routes, product_routes, loan_routes

import models

app = Flask(__name__, static_folder='static')
app.secret_key = 'pirda_cantik_suka_marah_marah'

app.config['UPLOAD_FOLDER'] = 'static/photo'

init_db(app)

app.register_blueprint(user_routes)
app.register_blueprint(base_routes)
app.register_blueprint(product_routes)
app.register_blueprint(loan_routes)

if __name__ == "__main__":
    app.run(debug=True)
