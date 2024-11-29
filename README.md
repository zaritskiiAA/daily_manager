### console taskmanager app
Консольное приложение имитирующее работу менеджера задач. Роль хранилища задач выполняет json файл.


#### *Содержание*
1. [Пользовательский интерфейс](#user-interface)
2. [Описание основных сущностей и их интерфейсов](#object-interface)
3. [Запуск и тестирование](#dev)

<br>
### 1. Пользовательский интерфейс <a id="user-interface"></a>
![меню](https://github.com/zaritskiiAA/daily_manager/blob/main/img/menu.PNG)

### 2. Описание основных сущностей и их интерфейсов<a id="object-interface"></a>
В приложение присутствуюет 2 сущности:

#### Сущности

1. *TaskManager* - представляет из себя обработчик запросов, которое обрабатывает запросы пользователя и отправляет их хранилищу. Формирует в удобочитаемый формат данные полученные из архива.
2. *TaskStorage* - хранилище всех существующих задач, в качестве ресурса хранения используется json файл, котороый храниться на жестком диске. Данные хранятся в следующем формате:

```json
[
  {
    "id": 6,
    "title": "new title",
    "description": "new description",
    "category": "unknown",
    "due_date": "2025-01-01",
    "priority": "Низкий",
    "status": "Выполнена"
  },
  {
    "id": 7,
    "title": "Изучить основы FastAPI",
    "description": "Пройти документацию по FastAPI и создать простой проект",
    "category": "Обучение",
    "due_date": "2024-12-30",
    "priority": "высокий",
    "status": "Выполнена"
  },
]
```

#### Описание структуры полей
**id** - уникальный идентификатор задачи
**title** - название задачи формат text
**description** - описание задачи формат text
**category** - категория задачи формат text
**due_date** - дата завершения задачи формат "%Y-%m-%d"
**priority** - приоритет задачи. Фиксированное значение, выбирается из (высокий/средний/низкий)
**status** - текущий статус задачи. Фиксированное значение 'не выполнена'

#### Основные интерфейсы

**add task** - Добавление задачи. Пользователь указывает все поля кроме id и status

![add_cmd](https://github.com/zaritskiiAA/daily_manager/blob/main/img/add_task.PNG)

**delete task** - Удаление задач. Пользователь вводит id задачи или категорию.

![delete_cmd](https://github.com/zaritskiiAA/daily_manager/blob/main/img/delete_task.PNG)

**search task** - Поиск задач. Пользователь может искать задачи по ключевым словам, категориям, статусу

![search_cmd](https://github.com/zaritskiiAA/daily_manager/blob/main/img/search_task.PNG)

**show tasks** - Отображение всех задач.

![all_cmd](https://github.com/zaritskiiAA/daily_manager/blob/main/img/show_tasks.PNG)

**done task** - завершения задачи (изменяет статус на 'Выполнена').

![change_status_cmd](https://github.com/zaritskiiAA/daily_manager/blob/main/img/done_task.PNG)

**edit task** - редактирование задачи.

![change_status_cmd](https://github.com/zaritskiiAA/daily_manager/blob/main/img/edit_task.PNG)

**cmd** - запросить меню с командами и описанием

![меню](https://github.com/zaritskiiAA/daily_manager/blob/main/img/menu.PNG)

**leave** - Выйти из менеджера задач (прервать выполнение скрипта.)

![leave_cmd](https://github.com/zaritskiiAA/daily_manager/blob/main/img/leave.PNG)

### Запуск и тестирование<a id="dev"></a> 
#### Запуск
1. Иметь на машине заранее установленый интерпретатор CPython не ниже 3.9
2. Стянуть на мишану пакет с приложением по http или ssh
3. Из директории daily_manager создать виртуальное окружения
    ```bash
    python -m venv venv
    ```
4. Активировать окружение 
    ```bash
    source venv/Scripts/activated
    ```
5. Установить зависимости (pytest, prettytable) в окружение
    ```bash
    pip install -r requirements.txt
    ```
6. запустить скрипт в формате пакета 
    ```bash
    python -m console_app.manager
    ```

#### Тестирование
1. Действия из подраздела 'Запуск' должны быть выполнены
1. запустить pytest runner из директори daily_manager/
    ```bash
    pytest
    ```