from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from recommender.db.init_db import init_db
from recommender.routes.api import main

SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"

def create_app():
    app = Flask(__name__)
    CORS(app)

    # init_db()
    print("Database initialized.")

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={"app_name": "Summoner Recommender"}
    )

    app.register_blueprint(main)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app