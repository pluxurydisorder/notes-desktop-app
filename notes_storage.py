"""Хранилище заметок в JSON-файле (стандартная библиотека Python)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


class NoteStore:
    """Создаёт, читает, обновляет и удаляет заметки."""

    def __init__(self, file_path: str | Path | None = None) -> None:
        # Пользовательские данные хранятся отдельно от исходного кода приложения.
        default_path = Path.home() / ".notes_desktop_app" / "notes.json"
        self.file_path = Path(file_path).expanduser() if file_path else default_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write([])

    def _read(self) -> list[dict[str, Any]]:
        try:
            raw = self.file_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Не удалось прочитать файл заметок: {exc}") from exc
        if not isinstance(data, list):
            raise RuntimeError("Файл заметок имеет неверный формат: ожидался список.")
        return data

    def _write(self, notes: list[dict[str, Any]]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.file_path.with_suffix(self.file_path.suffix + ".tmp")
        temp_path.write_text(
            json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temp_path.replace(self.file_path)

    def list_notes(self) -> list[dict[str, Any]]:
        """Возвращает заметки от новых/недавно изменённых к старым."""
        return sorted(self._read(), key=lambda note: note.get("updated_at", ""), reverse=True)

    def get(self, note_id: str) -> dict[str, Any] | None:
        return next((note for note in self._read() if note.get("id") == note_id), None)

    def save(self, title: str, content: str, note_id: str | None = None) -> dict[str, Any]:
        title = title.strip()
        if not title:
            raise ValueError("Укажите название заметки.")

        notes = self._read()
        now = _now_iso()
        if note_id:
            for note in notes:
                if note.get("id") == note_id:
                    note["title"] = title
                    note["content"] = content
                    note["updated_at"] = now
                    self._write(notes)
                    return note.copy()

        note = {
            "id": str(uuid4()),
            "title": title,
            "content": content,
            "created_at": now,
            "updated_at": now,
        }
        notes.append(note)
        self._write(notes)
        return note.copy()

    def delete(self, note_id: str) -> bool:
        notes = self._read()
        remaining = [note for note in notes if note.get("id") != note_id]
        if len(remaining) == len(notes):
            return False
        self._write(remaining)
        return True
