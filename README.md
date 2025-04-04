# Work API — Установка и запуск на Debian

**Важно:** В этом проекте зависимости устанавливаются через Poetry, и поддерживается установка без доступа к интернету с использованием локальной папки `packages`. Все необходимые библиотеки уже доступны по [ссылке](https://drive.google.com/file/d/1CbyzGzI5clUOWdfs_jQQ_LRCtV03xhiX/view?usp=sharing).

## 1. Установка Python 3.7.3 через pyenv (если требуется)

Если на вашей системе нет нужной версии Python или установлена более новая, рекомендуется использовать **pyenv** для получения Python 3.7.3:

### a. Установка зависимостей для pyenv (Debian):

```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev \
    python-openssl git
```

### b. Установка pyenv:

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

## 2. Установка Poetry

Убедитесь, что Python 3.7.3 активен (если использовали pyenv), затем установите Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Проверьте установку:

```bash
poetry --version
```

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

## 4. Запуск проекта

```bash
poetry run python server.py
```

