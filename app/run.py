from flask import Flask
from database import init_db
from routes import user_routes, base_routes

import models

app = Flask(__name__)
app.secret_key = 'pirda_cantik_suka_marah_marah'

init_db(app)

app.register_blueprint(user_routes)
app.register_blueprint(base_routes)

if __name__ == "__main__":
    app.run()
