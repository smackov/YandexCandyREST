# Задание для школы бэкэнд-разработки Yandex 

## Структура приложения

        YandexCandyREST
        ├── YandexCandyREST
        │   ├── __init__.py         # конструктор пакета приложения
        │   ├── asgi.py             # asgi
        │   ├── settings.py         # настройки проекта
        │   ├── urls.py             # главный роутер проекта
        │   └── wsgi.py             # wsgi
        |
        ├── delivery
        |   ├── migrations          # миграции проекта
        |   │    └── ...            # файлы миграций
        │   ├── __init__.py         # конструктор пакета приложения
        │   ├── admin.py            # конфигурация панели администрирования
        │   ├── api.py              # все API VIEWS приложения
        │   ├── apps.py             # некоторые настройки приложения
        │   ├── exceptions.py       # собственные исключения приложения и 
        │   │                       # обработчики исключений валидации данных
        │   ├── models.py           # модели и бизнес-логика приложения
        │   ├── serializers.py      # сериалайзеры приложения
        │   └── urls.py             # роутер приложения
        |  
        ├── .env                    # файл с переменными окружения (нужно создать самому)
        ├── manage.py               # инициализация приложения
        └── requirementes.txt       # зависимости приложения

## Инструкции

### Запуск приложения

Следующие команды выполняются в терминале, находясь в корневой папке приложения.

##### 1.1: Создание и активирование виртуальной среды окружения для Python 3:

	python3 -m venv venv
    source ./venv/bin/activate

##### 1.2: Установить зависимости для python:

	pip install -r requirements.txt

##### 1.3: Установить переменные окружения:

Создать файл `.env` и записать в него необходимые переменные.

	SECRET_KEY=rqr_cjv4igscyu8&&(0ce(=sy=f2)p=f_wn&@0xsp7m$@!kp=d
    ALLOWED_HOSTS=0.0.0.0
    DATABASE_URL=postgres://yandex_rest:BcAZoYWsJbvE7RMgBPzxOCexPRVAq@localhost:5432/yandex_rest_db

`SECRET_KEY` - секретный ключ проекта, никому ему не показывайте. 
`ALLOWED_HOSTS` - список разрешенных адресов, на которых может работать приложение. 
`DATABASE_URL` - адрес базы данных проекта. В примере указана PostgreSQL.

Синтаксис URL для базы данных:
`db_user:db_password@db_host:db_port/db_name`

##### 1.4: Произвести миграцию базы данных:

    ./manage.py migrate

##### 1.5: Запуск приложения

	./manage.py runserver 0.0.0.0:8080


 * `0.0.0.0:8080` - отвечает за адрес и порт, на котором будет работать приложение

### Запуск приложения с помощью Gunicorn и Supervisor

Для запуска приложения с несколькими воркерами воспользуемся python-сервером Gunicorn. Supervisor работает в режиме "демона" и перезапускает процессы Gunicorn, если они вдруг перестают работать по каким-либо причинам, также он запускает все процессы сервера после перезагрузки системы.

##### 2.1: Создание файла конфигурации Gunicorn:

Создайте файл gunicorn_start в корневой папке пользователя, обслуживающего сервис (или в любое другое подходящее место). Запишите в него следующие данные:

    #!/bin/bash

    NAME="YandexRESTService"
    DIR=/home/entrant/YandexCandyREST
    USER=entrant
    GROUP=entrant
    WORKERS=3
    BIND=0.0.0.0:8080
    DJANGO_SETTINGS_MODULE=YandexCandyREST.settings
    DJANGO_WSGI_MODULE=YandexCandyREST.wsgi
    LOG_LEVEL=error

    cd $DIR
    source ./venv/bin/activate

    export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
    export PYTHONPATH=$DIR:$PYTHONPATH

    exec ./venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $WORKERS \
    --user=$USER \
    --group=$GROUP \
    --bind=$BIND \
    --log-level=$LOG_LEVEL \
    --log-file=- 

где:

`NAME` - имя приложения (может быть любым)
`DIR` - расположение приложения
`USER` - пользователь, обслуживающий приложение
`WORKERS` - количество процессов сервера
`BIND` - адрес и порт сервера
`DJANGO_SETTINGS_MODULE` - относительный путь расположения файла настроек приложения
`DJANGO_WSGI_MODULE` - относительный путь расположения *wsgi* файла приложения
`source` - относительный путь расположения виртуальной среды окружения Python 3

##### 2.2: Сделать файл gunicorn_start  исполняемым:

    chmod u+x gunicorn_start

##### 2.3: Создание папок для хранения сокета и логов:

Пример расположения папок в корневой папке пользователя, обслуживающего приложение. Также создать файл логов:

    mkdir run logs
    touch logs/gunicorn.log

##### 2.4: Конфигурирование Supervisor:

Создать новый Supervisor файл:

    sudo vim /etc/supervisor/conf.d/YandexRESTService.conf

Записать в него данные:

    [program:yandex_rest]
    command=/home/entrant/gunicorn_start
    user=entrant
    autostart=true
    autorestart=true
    redirect_stderr=true
    stdout_logfile=/home/entrant/logs/gunicorn.log

##### 2.5: Запуск Supervisor для нашего приложения:

    sudo supervisorctl reread
    sudo supervisorctl update


### Запуск тестов

Следующие команды выполняются в терминале, находясь в корневой папке приложения. Команды представлены для случая, когда активирована виртуальная среда окружения для Python 3.

##### 1: Установить зависимости для python:

	pip install -r requirements.txt

##### 2: Запуск тестов

	./manage.py test

## Зависимости приложения

Приложение для работы использует следующие основные библиотеки и фреймворки:

- `Django` — фреймворк для создания web-приложений на Python
- `djangorestframework` — фреймворк построения приложения REST API
- `dj-database-url` — библиотека для подключения к БД черед URL
- `python-decouple` — библиотека для удобного хранения переменных среды в файле *.env*
- `Gunicorn` — WSGI-сервер



## Описание задания

Чтобы немного скрасить жизнь людей на самоизоляции, вы решаете открыть интернет-магазин по доставке конфет "Сласти от всех напастей".
Ваша задача — разработать на python REST API сервис, который позволит нанимать курьеров на работу, принимать заказы и оптимально распределять заказы между курьерами, попутно считая их рейтинг и заработок.
Сервис необходимо развернуть на предоставленной виртуальной машине на 0.0.0.0:8080.

![](./readme_assets/1.png)
![](./readme_assets/2.png)
![](./readme_assets/3.png)
![](./readme_assets/4.png)
![](./readme_assets/5.png)
![](./readme_assets/6.png)
![](./readme_assets/7.png)
![](./readme_assets/8.png)
![](./readme_assets/9.png)
