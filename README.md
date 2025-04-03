# Work API - Установка и запуск

Все библиотеки по пути packages: https://drive.google.com/file/d/1CbyzGzI5clUOWdfs_jQQ_LRCtV03xhiX/view?usp=sharing

Этот проект использует Poetry для управления зависимостями и поддерживает установку без доступа к интернету.

## Установка зависимостей

### 1. Установите Python и Poetry
- Убедитесь, что у вас установлен Python 3.7.3 или выше.
- Установите [Poetry](https://python-poetry.org/docs/#installation):
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```
  Или используйте пакетный менеджер вашей системы.

### 2. Скачивание зависимостей

Чтобы подготовить офлайн-установку зависимостей:
```bash
pip download -r <(poetry export -f requirements.txt --without-hashes) -d packages
```
Это создаст папку `packages/`, содержащую все необходимые библиотеки.

### 3. Установка зависимостей (в том числе офлайн)

При наличии интернета выполните:
```bash
poetry install
```

Если требуется установка без интернета:
```bash
poetry install --no-interaction --no-ansi
```
Poetry будет искать пакеты в локальной папке `packages/`.

## Запуск проекта

1. Активируйте виртуальное окружение (если не используется автоматическое активация Poetry):
   ```bash
   poetry shell
   ```
2. Запустите основной скрипт (если есть):
   ```bash
   python main.py
   ```

Проект готов к использованию!

