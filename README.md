# Вебсервис на Django REST framework
Данный вебсервис на `Python3` может:
* показать все варианты перелетов для выбранного маршрута
* получить самый дорогой/дешевый, быстрый/долгий и оптимальный варианты
* показать отличия между результатами двух запросов

Обратите внимание, что данные читаются и парсятся из XML файлов. В "боевом" режиме предполагается, что вместо чтения из файлов будут отправляться запросы на сторонний сервер, который выдает нам данные также в формате XML. Для этого некоторые функции придется переписать.

## Установка
1. Создайте копию данного удаленного репозитория на своем устройстве. В примере ниже клонирование происходит в папку `flights`, но вы можете выбрать любое другое имя
```bash
$ git clone https://github.com/andrepopoff/flights flights
```
2. Переместитесь в директорию `flights`:
```bash
$ cd flights
```
3. Создайте виртуальное окружение и активируйте его:
```bash
$ virtualenv venv
$ source venv/bin/activate
```
4. Установите зависимости
```bash
$ pip install -r requirements.txt
```
5. Переместитесь в директорию `aviatickets`:
```bash
$ cd aviatickets
```
6. Запустите Django сервер:
```bash
$ python manage.py runserver
```
Всё готово к работе!

## Перед началом работы важно помнить
1. При вызове каждого метода происходит обработка XML файлов. То есть данные каждый раз парсятся, как-будто файлы могли поменяться. Поэтому ответы поступают дольше, чем если бы мы получали данные сразу с распарсенных данных.
2. Вебсервис продолжает дорабатываться - это не окончательный вариант.
3. Сервис был написан на операционной системе MacOS Mojave и еще не тестировался на других устройствах.

## Список методов
По умолчанию, сервер запускается по адресу `http://127.0.0.1:8000/`
Там будет стартовая страница, которую мы напишем позже.
Формат ответа всех методов - `JSON`.

Все из нижеперечисленных методов (кроме метода `flights.getDifference`) можно вызвать с параметром `return`.
По умолчанию, все методы обрабатывают XML файл, где есть обратные маршруты.
Если параметр `return=0`, то мы получим данные без обратных маршрутов (в нашем случае, данные будут спарсены из другого XML файла, в котором нет обратных маршрутов).
Если использовать параметр `return=1` - это идентично вызову метода без параметров, т.е. мы получим перелеты с обратными маршрутами.
Если вызвать метод с параметром `return` не равным 1 или 0, придет ошибка (json-объект с ключом `error`)

* Метод `flights.getAll`
Возвращает все варианты перелетов из DXB в BKK.
Для вызова метода без обратных маршрутов используйте параметр `return=0`.
Пример вызова метода с параметром `return`:
```bash
$ http http://127.0.0.1:8000/flights.getAll?return=0
```

* Метод `flights.getMostExpensive`
возвращает самый дорогой перелет (если их несколько, то вернет все самые дорогие перелеты).
Для вызова метода без обратных маршрутов используйте параметр `return=0`.

* Метод `flights.getCheapest`
возвращает самый дешевый перелет (если их несколько, то вернет все самые дешевые перелеты).
Для вызова метода без обратных маршрутов используйте параметр `return=0`.

* Метод `flights.getLongest`
возвращает самый длительный перелет (если их несколько, то вернет все самые длительные перелеты).
Для вызова метода без обратных маршрутов используйте параметр `return=0`.

* Метод `flights.getFastest`
возвращает самый быстрый перелет (если их несколько, то вернет все самые быстрые перелеты).
Для вызова метода без обратных маршрутов используйте параметр `return=0`.

* Метод `flights.getOptimal`
возвращает самый оптмальный перелет (если их несколько, то вернет все самые оптимальные перелеты).
В нашем случае, оптимальный перелет - это перелет, продолжительность которого меньше средней продолжительности всех перелетов и имеющий самую низкую стоимость.
Для вызова метода без обратных маршрутов используйте параметр `return=0`.

* Метод `flights.getDifference`
возвращает разницу между 2 разными запросами (в нашем случае, между 2 xml файлами).
Проверяются только самые важные, на мой взгляд, данные. А именно:
    - Наличие обратных маршрутов.
    - Соответствие дат вылета.
    - Соответствие городов вылета и прилета.
    - Типы пассажиров.

Если эти данные в файлах отличаются, то они будут возвращены.
Например, вызовем метод:
```bash
$ http http://127.0.0.1:8000/flights.getDifference
```
и получим примерно такой ответ:
```bash
HTTP/1.1 200 OK
Allow: GET, HEAD, OPTIONS
Content-Length: 228
Content-Type: application/json
Date: Sun, 06 Jan 2019 17:57:50 GMT
Server: WSGIServer/0.2 CPython/3.6.4
Vary: Accept, Cookie
X-Frame-Options: SAMEORIGIN

{
    "response": {
        "first": {
            "departure_date": "2018-10-27",
            "return_itinerary": 0,
            "type": [
                "SingleAdult",
                "SingleChild",
                "SingleInfant"
            ]
        },
        "second": {
            "departure_date": "2018-10-22",
            "return_itinerary": 1,
            "type": [
                "SingleAdult"
            ]
        }
    }
}
```
Ключ `first` содержит параметры из первого XML файла, ключ `second` из второго.

## В ближайших планах сделать следующие улучшения
* Написать главную страницу со списком всех методов
* Добавить pretty вид при вызове методов с браузера
* Возможно: добавить пагинацию и подключить базу данных
