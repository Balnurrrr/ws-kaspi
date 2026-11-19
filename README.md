# Каспи-шаблоны Women'Secret (сайт для коллег)
Запуск у себя: двойной клик по `start.command` → http://localhost:5060 (логин/пароль admin/admin; свои: `WS_USERS="анна:пароль1,олег:пароль2"`).
Бесплатный хостинг: Render (Blueprint из `render.yaml`, план free), в Environment задать `WS_USERS`. Сервис засыпает без трафика, файлы заданий хранятся 24 ч.
Добавить категорию: функция в `ws/cats.py` + запись в `HANDLERS` (ключ = ячейка category в листе values шаблона), словари в `ws/dicts.py`.
Сейчас готовы: Women bras, Women panties. Остальные (пижамы, халаты, блузки, брюки, косметички…) — порт из plx_*.py.
