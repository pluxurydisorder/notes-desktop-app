# Практическая работа № 5 — Jenkins + Docker + Ansible

## Цель

Дополнить Jenkins Pipeline из практической № 4: после сборки Docker-образа экспортировать его в TAR-архив, передать на Ubuntu-сервер с помощью Ansible, загрузить образ на сервер и запустить контейнер. Ansible playbook хранится в GitHub: `ansible/deploy-container.yml`.

## Файлы в корне репозитория

- `Dockerfile` — сборка веб-версии приложения из `practice2_notes/`.
- `.dockerignore` — исключает локальные файлы из контекста сборки.
- `Jenkinsfile` — checkout, сборка образа, экспорт, вызов Ansible.
- `ansible/deploy-container.yml` — установка Docker на Ubuntu, копирование TAR-архива, `docker load`, запуск контейнера и HTTP-проверка.

## 1. Создать ветку и отправить файлы в GitHub ДО запуска Jenkins

Команды выполняются из корня локального репозитория `notes-desktop-app`. Сохрани незакоммиченные изменения перед переключением веток.

```bash
git status
git switch feature/practice-4-jenkins
git pull origin feature/practice-4-jenkins
git switch -c feature/practice-5-ansible-deploy
```

Распакуй архив практической № 5 в корень репозитория (не внутрь `practice2_notes`):

```bash
unzip -o ~/Downloads/practice5_jenkins_ansible.zip -d .
```

Проверь структуру:

```bash
ls -la Dockerfile Jenkinsfile .dockerignore
ls -la ansible/deploy-container.yml
```

Добавь файлы и отправь ветку:

```bash
git add Dockerfile .dockerignore Jenkinsfile ansible/deploy-container.yml README_PRACTICE5.md
git status
git commit -m "feat: deploy Docker image to Ubuntu using Ansible"
git push -u origin feature/practice-5-ansible-deploy
```

**Проверь файл `ansible/deploy-container.yml` на GitHub до запуска Jenkins** — это отдельное требование задания. Например: `https://github.com/pluxurydisorder/notes-desktop-app/tree/feature/practice-5-ansible-deploy/ansible`.

## 2. Подготовить Ubuntu VM (UTM на Mac M1)

Ubuntu VM должна быть включена, доступна из macOS по SSH и иметь интернет для установки `docker.io`. Для текущей конфигурации UTM IP обычно `192.168.64.2`, но проверь в Ubuntu:

```bash
hostname -I
sudo systemctl status ssh --no-pager
```

На Mac проверь SSH:

```bash
ssh ansible@192.168.64.2
```

Если IP отличается, укажи актуальный адрес в параметре `DEPLOY_HOST` Jenkins.

## 3. Настроить SSH-ключ для Jenkins

На Mac (не передавай приватный ключ в чат и не добавляй в Git):

```bash
ssh-keygen -t ed25519 -C "jenkins-practice5" -f ~/.ssh/jenkins_practice5
```

Для локальной учебной VM можно оставить ключ без passphrase: при запросе passphrase нажми Enter дважды.

Установи публичный ключ в учётную запись Ubuntu `ansible`:

```bash
cat ~/.ssh/jenkins_practice5.pub | ssh ansible@192.168.64.2 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
```

Проверь вход без пароля:

```bash
ssh -i ~/.ssh/jenkins_practice5 ansible@192.168.64.2
```

Если IP отличается — замени его в командах. При первом подключении проверь ключ сервера и подтверди соединение.

## 4. Добавить credentials в Jenkins

Открой `http://localhost:8080` → **Manage Jenkins → Credentials → System → Global credentials → Add Credentials**.

Создай два credential:

### SSH-ключ

- Kind: `SSH Username with private key`
- ID: `notes-ubuntu-ssh`
- Username: `ansible`
- Private Key: `Enter directly`, вставь содержимое файла `~/.ssh/jenkins_practice5`.

Чтобы скопировать ключ в буфер Mac, выполни `pbcopy < ~/.ssh/jenkins_practice5`, затем вставь в поле Jenkins. Не публикуй содержимое ключа.

### Пароль sudo

- Kind: `Secret text`
- ID: `notes-ubuntu-sudo-password`
- Secret: пароль пользователя `ansible` для `sudo` в Ubuntu.

Jenkins использует SSH-ключ для входа и secret text для `become`/sudo. Пароли не хранятся в репозитории.

## 5. Проверить инструменты на Mac, где запущен Jenkins

Установи Ansible, если ещё не установлен:

```bash
brew install ansible
ansible-playbook --version
```

Запусти Docker Desktop и проверь:

```bash
docker info
```

Jenkins должен видеть команды `docker` и `ansible-playbook` в своём `PATH`. В `Jenkinsfile` добавлены типичные каталоги Homebrew/Docker для пользователя `sorrow`. Если Jenkins работает под другим пользователем, скорректируй пути.

## 6. Создать/обновить Pipeline в Jenkins

В Jenkins открой задачу `notes-web-pipeline` (или создай новую `notes-web-ansible-pipeline`):

- Definition: `Pipeline script from SCM`
- SCM: `Git`
- Repository URL: `https://github.com/pluxurydisorder/notes-desktop-app.git`
- Credentials: `none`, если репозиторий публичный
- Branch Specifier: `*/feature/practice-5-ansible-deploy`
- Script Path: `Jenkinsfile`

Сохрани задачу. Нажми **Build with Parameters** или **Build Now**. Параметр `DEPLOY_HOST` по умолчанию `192.168.64.2`; если IP Ubuntu изменился, укажи актуальный.

## 7. Что делает Pipeline

1. Получает из GitHub код приложения, Dockerfile и Ansible playbook.
2. Собирает образ `notes-web:<номер сборки>` для `linux/arm64` (Mac M1 и Ubuntu ARM64).
3. Экспортирует образ в TAR через `docker save`.
4. Вызывает `ansible-playbook`, передавая путь к архиву как extra var.
5. Playbook устанавливает Docker на сервере, копирует TAR-архив, выполняет `docker load`, создаёт постоянный volume, пересоздаёт контейнер `notes-web` и проверяет HTTP 200.
6. После сборки временные TAR и файлы пароля удаляются с Jenkins workspace.

## 8. Проверить результат

В Ubuntu:

```bash
sudo docker ps --filter name=notes-web
sudo docker logs notes-web
sudo systemctl status docker --no-pager
```

С Mac попробуй открыть `http://192.168.64.2:8081/` (используй актуальный IP Ubuntu). Можно проверить командой:

```bash
curl -I --connect-timeout 5 http://192.168.64.2:8081/
```

В Jenkins открой номер сборки → **Console Output**. Успешный результат: все stages завершились без ошибки, а в конце Ansible playbook показал HTTP-проверку с кодом 200.

## Примечания по безопасности

- `ssh-keyscan` в Jenkinsfile добавляет ключ SSH-хоста для удобства локальной лабораторной. В рабочей среде сверяй fingerprint сервера доверенным способом и управляй `known_hosts` централизованно.
- Указанный `flask_secret_key` — тестовое значение. Для реального приложения храни секрет в Jenkins Credentials или другом хранилище секретов.
- Не коммить приватные ключи, пароль sudo, секреты Flask или файлы SQLite в GitHub.
