# Inicialização do pacote app
from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes.zip import zip_bp
    app.register_blueprint(zip_bp)

    # Registre outros blueprints se necessário
    # from .routes.convert import convert_bp
    # app.register_blueprint(convert_bp)

    return app