# Hacker proxy

Решение [тестового задания](https://github.com/ivelum/job/blob/master/challenges/python.md) создания просто прокси-сервера.

## Запуск

### venv
Установить и запустите приложение можно следующими командами:
```
$ virtualenv venv --python 3.10
$ . venv/bin/activate
$ pip install -r requirements.txt
$ python src/main.py
```

## Настройки проекта
### config.json
Перейдите в папку `src/configuration/`, где есть файл `config.json`. Можно поменять данные тем самым изменив конфигурацию проекта.
# Тесты
Запускаются по следующей команде:
```
$ pytest
```



