# Сборка

Нужны Python 3.12 и Google Chrome. Команды запускаются из корня репозитория.

```bash
python -m venv .venv
```

```bash
.venv/Scripts/python -m pip install -r "00 Основа/source/requirements.txt"
```

```bash
.venv/Scripts/python "00 Основа/source/render_kit.py"
```

```bash
.venv/Scripts/python "00 Основа/source/build.py"
```

```bash
.venv/Scripts/python "00 Основа/source/finalize.py"
```

```bash
.venv/Scripts/python "00 Основа/source/render_scenes.py"
```

```bash
.venv/Scripts/python "00 Основа/source/make_release.py"
```

| Файл | Что делает |
|---|---|
| `render_kit.py` | Превью и PDF Командного кита |
| `build.py` | Макеты, иконки, модули, книга, гиды, галерея. Палитры и тексты направлений лежат в `CONFIG` |
| `engine.py` | Рисование и знак (метод `logo`) |
| `finalize.py` | Логотипы, подписи, обзор, картинки для README, README направлений |
| `render_scenes.py` | Сцены из раздела «В работе» |
| `make_release.py` | `dist/SHA256SUMS.txt` и `dist/derigava-logos.zip` для релиза |

Проверить клон по файлу из релиза:

```bash
sha256sum -c SHA256SUMS.txt
```
