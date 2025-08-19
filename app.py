from app.routes import register_routes
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    register_routes(app)

    @app.route("/")
    def home():
        return render_template("index.html")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
