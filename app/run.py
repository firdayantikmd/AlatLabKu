from flask import Flask
from database import init_db
from routes import user_routes

import models

app = Flask(__name__)

init_db(app)

app.register_blueprint(user_routes)

if __name__ == "__main__":
    app.run()
