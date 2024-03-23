from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from recommender.routes.api import main
from recommender.db.init_db import init_db

SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"


def create_app():
    init_db()

    app = Flask(__name__)
    CORS(app)

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={"app_name": "Summoner Recommender"}
    )

    app.register_blueprint(main)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
