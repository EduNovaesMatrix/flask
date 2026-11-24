import os
import click
from flask import Flask
from .models import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Caminho do banco SQLite dentro da pasta instance e pasta de uploads
    db_path = os.path.join(app.instance_path, "flaskr.sqlite")
    upload_folder = os.path.join(app.root_path, "static", "uploads")

    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=upload_folder,
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    # Garante que as pastas instance e static/uploads existam
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Inicializa o SQLAlchemy com a aplicação
    db.init_app(app)

    # Comando CLI para criar as tabelas via SQLAlchemy
    @app.cli.command("init-db")
    def init_db_command():
        """Cria todas as tabelas mapeadas no SQLAlchemy."""
        db.create_all()
        click.echo("Banco de dados inicializado com SQLAlchemy.")

    # Registra os blueprints (auth, blog e calculos)
    from . import auth, blog, calculos

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(calculos.bp)
    app.add_url_rule("/", endpoint="index")

    return app