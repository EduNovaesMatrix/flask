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
    url_for,
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from .auth import allowed_file, login_required
from .models import Post, db

bp = Blueprint("blog", __name__)


def save_post_image(image_file):
    if image_file and image_file.filename:
        if not allowed_file(image_file.filename):
            return None, "Formato de imagem inválido. Use PNG, JPG, JPEG, GIF ou WEBP."
        safe_name = secure_filename(image_file.filename)
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        image_file.save(save_path)
        return unique_name, None
    return None, None


@bp.route("/")
def index():
    posts = Post.query.order_by(Post.created.desc()).all()
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"].strip()
        body = request.form["body"].strip()
        image_file = request.files.get("imagem_post")
        error = None

        if not title:
            error = "O título é obrigatório."

        image_filename = None
        if error is None:
            image_filename, img_error = save_post_image(image_file)
            if img_error:
                error = img_error

        if error is not None:
            flash(error, "danger")
        else:
            post = Post(
                title=title,
                body=body,
                author_id=g.user.id,
                imagem_post=image_filename,
            )
            db.session.add(post)
            db.session.commit()
            flash("Post publicado com sucesso!", "success")
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


def get_post(id, check_author=True):
    post = db.session.get(Post, id)

    if post is None:
        abort(404, f"Post id {id} não existe.")

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"].strip()
        body = request.form["body"].strip()
        image_file = request.files.get("imagem_post")
        error = None

        if not title:
            error = "O título é obrigatório."

        new_image = None
        if error is None:
            new_image, img_error = save_post_image(image_file)
            if img_error:
                error = img_error

        if error is not None:
            flash(error, "danger")
        else:
            post.title = title
            post.body = body
            if new_image:
                post.imagem_post = new_image
            db.session.commit()
            flash("Post atualizado com sucesso!", "success")
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    flash("Post excluído.", "info")
    return redirect(url_for("blog.index"))