# Практическая работа № 4 — Jenkins Pipeline + Docker

Цель: автоматически получить код веб-приложения из GitHub, собрать Docker-образ и запустить контейнер.

## Что добавить в репозиторий

Скопируйте в корень репозитория `notes-desktop-app` следующие три файла из этого архива:

- `Dockerfile` — обязательно хранится в корне репозитория GitHub;
- `.dockerignore` — уменьшает build context и исключает временные/локальные файлы;
- `Jenkinsfile` — Declarative Pipeline для Jenkins.

Приложение Flask из лабораторной работы 2 находится в `practice2_notes/`. Dockerfile копирует именно эту папку в образ; корневой `app.py` — отдельное настольное приложение Tkinter, поэтому он не используется как веб-сервер.

## Требования

- Docker Desktop для Mac (Apple Silicon) запущен, а команда `docker info` успешно работает в macOS Terminal.
- Jenkins LTS установлен на Mac и доступен на `http://localhost:8080`.
- В Jenkins установлены Git plugin и Pipeline plugin (можно использовать установку suggested plugins).
- В GitHub существует публичная ветка `feature/practice-4-jenkins`, в которой закоммичены эти файлы, и сохранена папка `practice2_notes/` из лабораторной работы 2.

## Установка Docker Desktop на Mac M1

Скачайте версию для Apple silicon с официальной страницы https://docs.docker.com/desktop/setup/install/mac-install/ . Запустите Docker Desktop и дождитесь состояния `Engine running`. Проверьте в Terminal:

```bash
docker version
docker info
```

## Установка Jenkins через Homebrew

```bash
brew install jenkins-lts
brew services start jenkins-lts
```

Откройте http://localhost:8080. Для первичной разблокировки попробуйте прочитать пароль:

```bash
cat ~/.jenkins/secrets/initialAdminPassword
```

Завершите мастер установки и установите suggested plugins. Если Jenkins уже установлен, этот шаг повторно проходить не нужно.

## Поместить файлы в GitHub

Команды выполняйте из корня локального репозитория. Предполагается, что ветка лабораторной 2 существует и содержит `practice2_notes/`:

```bash
git status
git switch feature/practice-2-crud
git pull origin feature/practice-2-crud
git switch -c feature/practice-4-jenkins
```

Распакуйте архив отдельно, а затем скопируйте `Dockerfile`, `.dockerignore`, `Jenkinsfile` в корень репозитория. Не заменяйте папку `practice2_notes/` файлами из архива: Dockerfile ссылается на уже существующий код этой папки.

```bash
git add Dockerfile .dockerignore Jenkinsfile
git status
git commit -m "feat: add Jenkins pipeline and Docker image"
git push -u origin feature/practice-4-jenkins
```

Проверьте на GitHub, что все три файла находятся в корне именно этой ветки.

## Настройка Pipeline в Jenkins

1. Откройте http://localhost:8080 и войдите в Jenkins.
2. Выберите **New Item**.
3. Назовите задачу `notes-web-pipeline`, выберите **Pipeline**, нажмите **OK**.
4. В разделе **Pipeline** установите Definition: **Pipeline script from SCM**.
5. SCM: **Git**.
6. Repository URL: `https://github.com/pluxurydisorder/notes-desktop-app.git`.
7. Credentials: оставить `none`, потому что репозиторий публичный.
8. Branch Specifier: `*/feature/practice-4-jenkins`.
9. Script Path: `Jenkinsfile`.
10. Сохраните и нажмите **Build Now**.

Pipeline выполняет этапы:

1. Checkout source from GitHub — получает исходный код;
2. Build Docker image — собирает `notes-web:<номер-сборки>` и тег `notes-web:latest`;
3. Deploy container — заменяет существующий контейнер `notes-web`, сохраняя данные в Docker volume `notes-web-data`;
4. Verify deployed application — проверяет HTTP-ответ приложения.

## Проверка результата

После зелёного статуса сборки откройте http://127.0.0.1:8081/ . В Jenkins откройте Console Output и покажите этапы checkout/build/deploy/verify. В Terminal можно выполнить:

```bash
docker image ls notes-web
docker ps --filter name=notes-web
docker logs notes-web
```

Контейнер использует порт 8081 на Mac, чтобы не конфликтовать с Jenkins, работающим на 8080. SQLite-файл хранится в именованном volume `notes-web-data`, поэтому пересоздание контейнера не стирает заметки.

## Важные замечания

- Pipeline запускается на том же Mac, где работает Jenkins и Docker Desktop. Этот Jenkinsfile предназначен для локальной учебной демонстрации.
- Jenkins-процесс должен видеть Docker CLI. В Jenkinsfile добавлены распространённые пути Docker для macOS; если `docker: command not found`, проверь результат `which docker` в обычном терминале и добавь каталог CLI в PATH процесса Jenkins.
- Если порт 8081 занят, измените `APP_PORT` в `Jenkinsfile` и закоммитьте изменение.
- Если Jenkins при первом запуске не может скачать код, проверьте URL репозитория и точное имя ветки.
- Для публичного учебного репозитория Credentials в Jenkins не нужны. Для приватного репозитория нужно отдельно добавить GitHub credentials.
