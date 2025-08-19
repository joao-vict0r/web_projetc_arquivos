from .convert import convert_bp
from .zip import zip_bp
from .cleanup import cleanup_bp

def register_routes(app):
    app.register_blueprint(convert_bp)
    app.register_blueprint(zip_bp)
    
