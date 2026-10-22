from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, abort, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("NOTES_DATABASE", BASE_DIR / "notes.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-key-change-before-deployment")

CATEGORIES = ["Учёба", "Работа", "Личное", "Покупки", "Другое"]
PRIORITIES = ["Низкий", "Средний", "Высокий"]
STATUSES = ["Новая", "В работе", "Выполнена"]


def get_db() -> sqlite3.Connection:
    """Open a SQLite connection with row access by column name."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    """Create the notes table on the first application launch."""
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )


def get_note(note_id: int) -> sqlite3.Row:
    with get_db() as connection:
        note = connection.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if note is None:
        abort(404)
    return note


def form_values() -> dict[str, str]:
    return {
        "title": request.form.get("title", "").strip(),
        "author": request.form.get("author", "").strip(),
        "description": request.form.get("description", "").strip(),
        "category": request.form.get("category", "Другое"),
        "priority": request.form.get("priority", "Средний"),
        "status": request.form.get("status", "Новая"),
    }


def validate_values(values: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if not values["title"]:
        errors.append("Введите название заметки.")
    if not values["author"]:
        errors.append("Введите автора заметки.")
    if not values["description"]:
        errors.append("Добавьте описание.")
    if values["category"] not in CATEGORIES:
        errors.append("Выберите категорию из списка.")
    if values["priority"] not in PRIORITIES:
        errors.append("Выберите корректный приоритет.")
    if values["status"] not in STATUSES:
        errors.append("Выберите корректный статус.")
    return errors


def render_note_form(*, page_title: str, submit_label: str, values: dict[str, Any], note_id: int | None = None):
    return render_template(
        "note_form.html",
        page_title=page_title,
        submit_label=submit_label,
        values=values,
        note_id=note_id,
        categories=CATEGORIES,
        priorities=PRIORITIES,
        statuses=STATUSES,
    )


@app.get("/")
def index():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    query = "SELECT * FROM notes"
    params: list[str] = []
    conditions: list[str] = []
    if search:
        conditions.append("(title LIKE ? OR description LIKE ? OR author LIKE ?)")
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])
    if category in CATEGORIES:
        conditions.append("category = ?")
        params.append(category)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY id DESC"
    with get_db() as connection:
        notes = connection.execute(query, params).fetchall()
    return render_template("index.html", notes=notes, search=search, selected_category=category, categories=CATEGORIES)


@app.route("/notes/new", methods=["GET", "POST"])
def create_note():
    if request.method == "POST":
        values = form_values()
        errors = validate_values(values)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_note_form(page_title="Новая заметка", submit_label="Создать заметку", values=values)
        with get_db() as connection:
            connection.execute(
                """INSERT INTO notes (title, author, description, category, priority, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (values["title"], values["author"], values["description"], values["category"], values["priority"], values["status"]),
            )
        flash("Заметка успешно создана.", "success")
        return redirect(url_for("index"))
    defaults = {"title": "", "author": "", "description": "", "category": "Учёба", "priority": "Средний", "status": "Новая"}
    return render_note_form(page_title="Новая заметка", submit_label="Создать заметку", values=defaults)


@app.get("/notes/<int:note_id>")
def view_note(note_id: int):
    return render_template("detail.html", note=get_note(note_id))


@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
def edit_note(note_id: int):
    note = get_note(note_id)
    if request.method == "POST":
        values = form_values()
        errors = validate_values(values)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_note_form(page_title="Редактирование заметки", submit_label="Сохранить изменения", values=values, note_id=note_id)
        with get_db() as connection:
            connection.execute(
                """UPDATE notes SET title = ?, author = ?, description = ?, category = ?, priority = ?, status = ?
                   WHERE id = ?""",
                (values["title"], values["author"], values["description"], values["category"], values["priority"], values["status"], note_id),
            )
        flash("Изменения сохранены.", "success")
        return redirect(url_for("view_note", note_id=note_id))
    values = {key: note[key] for key in ("title", "author", "description", "category", "priority", "status")}
    return render_note_form(page_title="Редактирование заметки", submit_label="Сохранить изменения", values=values, note_id=note_id)


@app.post("/notes/<int:note_id>/delete")
def delete_note(note_id: int):
    get_note(note_id)  # Return 404 if the note does not exist.
    with get_db() as connection:
        connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    flash("Заметка удалена.", "success")
    return redirect(url_for("index"))


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", "5000")))
