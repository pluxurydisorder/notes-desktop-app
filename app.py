"""Десктопное приложение «Заметки» на Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from notes_storage import NoteStore


class NotesApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Заметки")
        self.root.geometry("900x580")
        self.root.minsize(720, 440)
        self.root.bind("<Control-n>", lambda _event: self.new_note())
        self.root.bind("<Control-s>", lambda _event: self.save_note())

        self.store = NoteStore()
        self.current_note_id: str | None = None
        self.visible_notes: list[dict] = []

        self._build_ui()
        self.refresh_notes()
        self._set_status("Готово")

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(1, weight=1)

        ttk.Label(main, text="Мои заметки", font=("TkDefaultFont", 15, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        ttk.Label(main, text="Редактор", font=("TkDefaultFont", 15, "bold")).grid(
            row=0, column=1, sticky="w", padx=(14, 0), pady=(0, 8)
        )

        left = ttk.Frame(main)
        left.grid(row=1, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(3, weight=1)

        self.search_var = tk.StringVar()
        ttk.Label(left, text="Поиск по заметкам").grid(row=0, column=0, sticky="w")
        search = ttk.Entry(left, textvariable=self.search_var)
        search.grid(row=1, column=0, sticky="ew", pady=(4, 8))
        self.search_var.trace_add("write", lambda *_: self.refresh_notes())

        ttk.Button(left, text="＋ Новая заметка", command=self.new_note).grid(
            row=2, column=0, sticky="ew", pady=(0, 8)
        )

        list_frame = ttk.Frame(left)
        list_frame.grid(row=3, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.note_list = tk.Listbox(list_frame, exportselection=False, activestyle="dotbox")
        self.note_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.note_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.note_list.configure(yscrollcommand=scrollbar.set)
        self.note_list.bind("<<ListboxSelect>>", self._on_select)

        editor = ttk.Frame(main)
        editor.grid(row=1, column=1, sticky="nsew", padx=(14, 0))
        editor.columnconfigure(0, weight=1)
        editor.rowconfigure(3, weight=1)

        ttk.Label(editor, text="Название").grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(editor, textvariable=self.title_var)
        self.title_entry.grid(row=1, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(editor, text="Текст заметки").grid(row=2, column=0, sticky="w")
        self.content_text = tk.Text(editor, wrap="word", undo=True, height=15)
        self.content_text.grid(row=3, column=0, sticky="nsew", pady=(4, 10))

        buttons = ttk.Frame(editor)
        buttons.grid(row=4, column=0, sticky="w")
        ttk.Button(buttons, text="Сохранить", command=self.save_note).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Удалить", command=self.delete_note).grid(row=0, column=1)

        self.status_var = tk.StringVar()
        ttk.Label(main, textvariable=self.status_var, anchor="w", relief="sunken").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def refresh_notes(self, select_id: str | None = None) -> None:
        query = self.search_var.get().strip().casefold() if hasattr(self, "search_var") else ""
        notes = self.store.list_notes()
        self.visible_notes = [
            note for note in notes
            if query in note.get("title", "").casefold()
            or query in note.get("content", "").casefold()
        ]

        self.note_list.delete(0, tk.END)
        selected_index = None
        for index, note in enumerate(self.visible_notes):
            self.note_list.insert(tk.END, note.get("title", "Без названия"))
            if note.get("id") == (select_id or self.current_note_id):
                selected_index = index

        if selected_index is not None:
            self.note_list.selection_set(selected_index)
            self.note_list.activate(selected_index)
            self.note_list.see(selected_index)

    def _on_select(self, _event: tk.Event | None = None) -> None:
        selection = self.note_list.curselection()
        if not selection:
            return
        note = self.visible_notes[selection[0]]
        self.current_note_id = note["id"]
        self.title_var.set(note.get("title", ""))
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", note.get("content", ""))
        self._set_status(f"Открыта заметка: {note.get('title', '')}")

    def new_note(self) -> None:
        self.current_note_id = None
        self.note_list.selection_clear(0, tk.END)
        self.title_var.set("")
        self.content_text.delete("1.0", tk.END)
        self.title_entry.focus_set()
        self._set_status("Новая заметка")

    def save_note(self) -> None:
        title = self.title_var.get().strip()
        content = self.content_text.get("1.0", "end-1c")
        if not title:
            messagebox.showwarning("Не указано название", "Введите название заметки.", parent=self.root)
            self.title_entry.focus_set()
            return
        try:
            note = self.store.save(title, content, self.current_note_id)
        except (OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror("Ошибка сохранения", str(exc), parent=self.root)
            return
        self.current_note_id = note["id"]
        self.refresh_notes(select_id=note["id"])
        self._set_status("Заметка сохранена")

    def delete_note(self) -> None:
        if not self.current_note_id:
            self._set_status("Сначала выберите заметку для удаления")
            return
        if not messagebox.askyesno("Удаление", "Удалить выбранную заметку?", parent=self.root):
            return
        try:
            self.store.delete(self.current_note_id)
        except (OSError, RuntimeError) as exc:
            messagebox.showerror("Ошибка удаления", str(exc), parent=self.root)
            return
        self.new_note()
        self.refresh_notes()
        self._set_status("Заметка удалена")


def main() -> None:
    root = tk.Tk()
    NotesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
