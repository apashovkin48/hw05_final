# Описание сервиса
Yatube - социальная сеть с авторизацией пользователей, персональными летами с комментариями и подписками на авторов статей.

# Доступный функционал
- Управление пользователями
- Регистрация пользователей
- Восстановление доступа через электронную почту
- Создание, редактирование постов с изображениями
- Подписка на автора
- Лента с самыми актуальными постами пользователей
- Просмотр ленты постов пользователей

# Установка
Клонируйте репозиторий на ваш ПК
```
git clone https://github.com/apashovkin48/hw05_final.git
```
Перейдите в папку с проектом:
```
cd hw05_final
```
Установите виртуальное окружение и активируйте его:
```
python3 -m venv venv
```
```
source venv/bit/activate
```
Установить зависимости из файла requirements.txt:
```
pip3 install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```

# Используемые технологии
- Python
- Django
- SQLite3
