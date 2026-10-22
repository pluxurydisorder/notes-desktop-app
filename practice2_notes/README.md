# Практическая работа № 2 — приложение «Заметки»

Веб-приложение на Python + Flask + SQLite. Проект продолжает вариант «Заметки» и демонстрирует создание, просмотр, редактирование и удаление записей.

## Возможности

- форма с текстовыми полями: название, автор, описание;
- выпадающие списки: категория, приоритет, статус;
- просмотр списка и отдельной заметки;
- редактирование и удаление записей;
- поиск по названию, автору и описанию, фильтр по категории;
- проверка обязательных полей;
- SQLite-база создаётся автоматически и хранится локально в `notes.db`.

## Запуск на macOS

Понадобятся Python 3 и Git. Проверьте их установку:

```bash
python3 --version
git --version
```

Перейдите в каталог проекта, создайте и активируйте виртуальное окружение:

```bash
cd practice2_notes
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Откройте в браузере `http://127.0.0.1:5000`. Чтобы остановить сервер, вернитесь в терминал и нажмите `Control+C`.

## Git: отдельная ветка для практической работы № 2

Работу выполняйте в собственной ветке, а не напрямую в `main`. Если репозиторий из практической работы № 1 уже существует, используйте первый вариант. Если это новый проект — второй.

### Вариант А. Продолжить репозиторий из практической работы № 1

В терминале перейдите в каталог репозитория и убедитесь, что незакоммиченных нужных изменений нет:

```bash
git status
git switch main
git pull
git switch -c feature/practice-2-crud
```

Если основная ветка у вас называется `master`, вместо `main` используйте `master`. После создания ветки скопируйте в корень репозитория файлы этой работы (`app.py`, `requirements.txt`, `README.md`, `.gitignore`, папки `templates` и `static`). Не удаляйте каталог `.git` и файлы первой практической работы, если они нужны для сдачи.

Создайте коммиты с понятными сообщениями:

```bash
git add app.py requirements.txt .gitignore
git commit -m "feat: add Flask app and SQLite storage"
git add templates
git commit -m "feat: add note list and CRUD forms"
git add static/style.css README.md
git commit -m "style: add responsive UI and setup guide"
```

### Вариант Б. Создать новый репозиторий для этой работы

Из каталога `practice2_notes` выполните команды. Первая фиксация создаёт базу проекта, после чего вся реализация ведётся в отдельной ветке:

```bash
git init
git branch -M main
git add README.md .gitignore
git commit -m "docs: add project setup instructions"
git switch -c feature/practice-2-crud
git add app.py requirements.txt
git commit -m "feat: implement notes backend and SQLite storage"
git add templates
git commit -m "feat: add note list and CRUD pages"
git add static/style.css
git commit -m "style: add responsive interface"
```

В этом варианте итоговый код приложения находится в `feature/practice-2-crud`. При сдаче откройте именно эту ветку на GitHub. При необходимости в настройках репозитория можно выбрать её как ветку по умолчанию.

### Проверка веток и истории

```bash
git status
git branch
git branch -a
git log --oneline --graph --decorate --all
```

- `git branch` показывает локальные ветки; звёздочка обозначает текущую.
- `git log --oneline --graph --decorate --all` показывает коммиты и то, к каким веткам они относятся.
- Перед отправкой проверьте изменения командой `git status`.

### Публикация на GitHub

1. На GitHub создайте пустой репозиторий, например `practice-2-notes` (не добавляйте README, если он уже создан локально).
2. Подставьте URL своего репозитория вместо `YOUR-USERNAME` и отправьте ветку с приложением:

```bash
git remote add origin https://github.com/YOUR-USERNAME/practice-2-notes.git
git push -u origin main
git push -u origin feature/practice-2-crud
```

Если `origin` уже настроен, не выполняйте `git remote add origin` повторно — проверьте адрес командой `git remote -v` и отправьте ветку:

```bash
git push -u origin feature/practice-2-crud
```

## Что показать при сдаче

1. Запустить `python app.py` и открыть `http://127.0.0.1:5000`.
2. Создать заметку, показать её в списке и открыть страницу просмотра.
3. Изменить поля и сохранить, затем удалить тестовую заметку.
4. Показать ветку `feature/practice-2-crud` командой `git branch`.
5. Показать историю коммитов через `git log --oneline --graph --decorate --all`.
6. Открыть репозиторий GitHub и вкладку **Branches**, где видна отдельная ветка.

## Структура проекта

```text
practice2_notes/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── index.html
    ├── note_form.html
    └── detail.html
```
