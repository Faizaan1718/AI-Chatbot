from __future__ import annotations

from flask import Flask

from app.routes.chat import bp as chat_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(chat_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

