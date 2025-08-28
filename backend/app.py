from flask import Flask
from flask_cors import CORS
from .config import Config
from .db import db, init_db
from .auth import auth_bp
from .routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)

    init_db(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

if __name__ == "__main__":
    from .config import Config
    app = create_app()
    app.run(host=Config.APP_HOST, port=Config.APP_PORT, debug=True)
