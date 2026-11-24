#Descrição: Refatoração da aplicação Flaskr para arquitetura MVC utilizando Flask-SQLAlchemy, Bootstrap 5, upload de arquivos e cálculos financeiros em memória
#Nome_arquivo: models.py
#Nome_exercicio: Prova Desenvolvimento Web 2 - 24/11/2026
#Nome: Eduardo Rodrigues de Novaes
#email: eduardo.novaes@aluno.cps.sp.gov.br
#Turma: 2º turma DSM Fatec Olimpia

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)

    # Relacionamento: um usuário pode ter vários posts
    posts = db.relationship("Post", back_populates="author", lazy=True)


class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    imagem_post = db.Column(db.String(255), nullable=True)

    # Relacionamento inverso para acessar post.author.username facilmente nos templates
    author = db.relationship("User", back_populates="posts")