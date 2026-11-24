#Descrição: Refatoração da aplicação Flaskr para arquitetura MVC utilizando Flask-SQLAlchemy, Bootstrap 5, upload de arquivos e cálculos financeiros em memória
#Nome_arquivo: auth.py
#Nome_exercicio: Prova Desenvolvimento Web 2 - 24/11/2026
#Nome: Eduardo Rodrigues de Novaes
#email: eduardo.novaes@aluno.cps.sp.gov.br
#Turma: 2º turma DSM Fatec Olimpia

import functools
import os
import uuid
from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from .models import User, db

bp = Blueprint("auth", __name__, url_prefix="/auth")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        avatar_file = request.files.get("avatar")
        error = None

        if not username:
            error = "O nome de usuário é obrigatório."
        elif not password:
            error = "A senha é obrigatória."
        elif User.query.filter_by(username=username).first() is not None:
            error = f"O usuário '{username}' já está cadastrado."

        avatar_filename = None
        if error is None and avatar_file and avatar_file.filename:
            if allowed_file(avatar_file.filename):
                safe_name = secure_filename(avatar_file.filename)
                avatar_filename = f"{uuid.uuid4().hex}_{safe_name}"
                save_path = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], avatar_filename
                )
                avatar_file.save(save_path)
            else:
                error = "Formato de avatar inválido. Use PNG, JPG, JPEG, GIF ou WEBP."

        if error is None:
            new_user = User(
                username=username,
                password=generate_password_hash(password),
                avatar=avatar_filename,
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
            return redirect(url_for("auth.login"))

        flash(error, "danger")

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        error = None

        user = User.query.filter_by(username=username).first()

        if user is None:
            error = "Usuário incorreto."
        elif not check_password_hash(user.password, password):
            error = "Senha incorreta."

        if error is None:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

        flash(error, "danger")

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view