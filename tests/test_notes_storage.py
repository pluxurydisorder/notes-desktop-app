"""Автоматические тесты для слоя хранения заметок."""

import json
import tempfile
import unittest
from pathlib import Path

from notes_storage import NoteStore


class NoteStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "notes.json"
        self.store = NoteStore(self.file_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_save_and_get_note(self) -> None:
        note = self.store.save("Первая заметка", "Текст заметки")
        loaded = self.store.get(note["id"])
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["title"], "Первая заметка")
        self.assertEqual(loaded["content"], "Текст заметки")

    def test_update_note_does_not_create_duplicate(self) -> None:
        note = self.store.save("Название", "Старый текст")
        updated = self.store.save("Новое название", "Новый текст", note["id"])
        self.assertEqual(updated["id"], note["id"])
        self.assertEqual(len(self.store.list_notes()), 1)
        self.assertEqual(self.store.get(note["id"])["content"], "Новый текст")

    def test_delete_note(self) -> None:
        note = self.store.save("Временная", "Удалить меня")
        self.assertTrue(self.store.delete(note["id"]))
        self.assertIsNone(self.store.get(note["id"]))
        self.assertFalse(self.store.delete(note["id"]))

    def test_empty_title_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.store.save("   ", "Текст")

    def test_data_is_saved_as_utf8_json(self) -> None:
        self.store.save("Заметка", "Привет, мир")
        raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        self.assertEqual(raw[0]["content"], "Привет, мир")


if __name__ == "__main__":
    unittest.main()
