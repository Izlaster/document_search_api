# Work API — Установка и запуск на Debian

**Важно:** В этом проекте зависимости устанавливаются через Poetry, и поддерживается установка без доступа к интернету с использованием локальных папок `packages` и `models`. Все необходимые библиотеки и модели уже доступны по [ссылке](https://drive.google.com/drive/folders/1Iqm3nbFJ1igK0UaeSm7KJMd_qFrHJFyM?usp=sharing).

---

## 1. Установка Python 3.7.3 через pyenv (если требуется)

Если на вашей системе нет нужной версии Python или установлена более новая, рекомендуется использовать **pyenv** для получения Python 3.7.3:

### a. Установка зависимостей для pyenv (Debian)

```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev \
    python-openssl git
```

### b. Установка pyenv

```bash
curl https://pyenv.run | bash
```

### c. Настройка окружения

Добавьте в файл `~/.bashrc` (или другой конфигурационный файл вашего shell) следующие строки:

```bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Перезапустите терминал или выполните:

```bash
source ~/.bashrc
```

### d. Установка Python 3.7.3 и установка локально для проекта:

```bash
pyenv install 3.7.3
pyenv local 3.7.3
```

Проверьте версию:

```bash
python --version
```

---

## 2. Установка Poetry

Убедитесь, что Python 3.7.3 активен (если использовали pyenv), затем установите Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Проверьте установку:

```bash
poetry --version
```

---

## 3. Установка зависимостей

### a. При наличии интернета:

```bash
poetry install
```

### b. Без доступа к интернету:

В офлайн-режиме используйте команду:

```bash
poetry install --no-interaction --no-ansi
```

Poetry попытается установить зависимости, используя пакеты из локальной папки `packages`.

---

## 4. Конфигурация проекта

Перед запуском убедитесь, что файл `config.json` существует и настроен. Пример:

```json
{
  "server": {
    "port": 8000
  },
  "models": [
    { "name": "models/DeepPavlov_rubert-base-cased" },
    { "name": "models/intfloat_multilingual-e5-large" },
    { "name": "models/sentence-transformers_paraphrase-multilingual-mpnet-base-v2" }
  ],
  "active_model_index": 0
}
```

- `models` — список моделей, доступных для загрузки.
- `active_model_index` — индекс активной модели (начинается с 0).
- `server.port` — порт, на котором запускается сервер.

---

## 5. Запуск проекта

```bash
poetry run python server.py
```

Сервер запустится на указанном в `config.json` порту. Пример ответа API:

```
POST /api/vector
Content-Type: application/json

{
  "text": "Пример текста"
}
```

Ответ:

```json
{
  "vector": [0.123, -0.456, ...]
}
```

---

## 6. Логирование

Сервер пишет логи в два потока:
- в файл `server.log`
- и одновременно в консоль

Это позволяет удобно отслеживать работу и отлаживать проект.
