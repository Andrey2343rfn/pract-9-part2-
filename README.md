# Практична робота 9.2. Smart Factory Monitoring System

**Дисципліна:** Технології IoT та SMART-технології  
**Варіант:** 1, Smart Factory Monitoring System  
**Студент:** Свидан Андрій Андрійович  
**Група:** вписати перед здачею

## Призначення

Шість сенсорів передають дані через MQTT. Edge Processor перевіряє порогові значення, виконує локальні дії та зберігає повідомлення в SQLite. Cloud Connector приймає показники, записує їх в InfluxDB, обчислює статистику і надає REST API. Вебпанель показує графіки та дозволяє надсилати команди Edge.

## Перед запуском

Установити **Docker Desktop** на macOS або Windows. Запустити Docker Desktop і дочекатися стану Engine running. Використовується `docker compose` (з пробілом).

Відкрити папку `Practice9_2` у VS Code, відкрити Terminal → New Terminal.

```bash
docker --version
docker compose version
docker compose up --build -d
docker compose ps
```

Під час першого запуску Docker завантажить образи з інтернету. Усі шість сервісів повинні мати стан `Up` (або `running`).

## Відкрити інтерфейс

- Панель моніторингу: http://localhost:8080
- API: http://localhost:8080/api/summary
- Історія: http://localhost:8080/api/history?limit=10
- Аномалії: http://localhost:8080/api/alerts
- Агрегація: http://localhost:8080/api/aggregate?period=minute
- InfluxDB: http://localhost:8086, логін `student`, пароль з `.env`

Оновлення вебпанелі відбувається кожні три секунди. Натисніть кнопку зупинки або запуску лінії. Надсилання команди підтверджується у журналі Edge і списку виконаних дій.

## Логи всіх етапів

```bash
docker compose logs --tail=20 sensor-simulator
docker compose logs --tail=20 edge-processor
docker compose logs --tail=20 cloud-connector
```

Для безперервного перегляду:

```bash
docker compose logs -f edge-processor
```

Вихід з перегляду логів: `Ctrl+C`. Контейнери продовжать працювати.

## Перевірка відмовостійкості

1. Переконатися, що у `http://localhost:8080` зростає лічильник записів.
2. Зупинити тільки Cloud Connector.

```bash
docker compose stop cloud-connector
docker compose logs --tail=15 edge-processor
```

3. Дочекатися нових повідомлень `EDGE ALERT` або `EDGE processed`, перевірити, що Edge працює.
4. Показати кількість записів, які очікують синхронізації:

```bash
docker compose exec edge-processor python -c "import sqlite3; c=sqlite3.connect('/app/data/edge.db'); print('Pending:', c.execute('SELECT COUNT(*) FROM pending').fetchone()[0])"
```

5. Відновити Cloud Connector та переглянути синхронізацію.

```bash
docker compose start cloud-connector
docker compose logs --tail=20 cloud-connector
docker compose exec edge-processor python -c "import sqlite3; c=sqlite3.connect('/app/data/edge.db'); print('Pending:', c.execute('SELECT COUNT(*) FROM pending').fetchone()[0])"
```

6. Перевірити API й оновлення графіків. Кількість `Pending` після відновлення має поступово зменшитися. Для надійності Edge повторно відправляє записи, доки Cloud не підтвердить збереження через MQTT-тему `cloud/ack`. Дублікати відсікаються у Cloud за `event_id`.

## Управління

```bash
docker compose ps
docker compose restart
docker compose down
```

Для повного скидання з видаленням накопичених даних:

```bash
docker compose down -v
```

## Структура проєкту

```text
Practice9_2/
├── docker-compose.yml
├── .env
├── mosquitto/mosquitto.conf
├── sensors/Dockerfile
├── sensors/patterns.py
├── sensors/simulator.py
├── edge/Dockerfile
├── edge/config.json
├── edge/rules.py
├── edge/processor.py
├── cloud/Dockerfile
├── cloud/analytics.py
├── cloud/connector.py
├── dashboard/Dockerfile
├── dashboard/nginx.conf
├── dashboard/index.html
├── dashboard/style.css
├── dashboard/app.js
├── tests/test_project.py
├── docs/Practice9_2_Report.pdf
└── docs/VIDEO_SCRIPT.md
```

## Реалізація

### Sensor Simulator

Генерує шість показників: `vibration`, `bearing_temp`, `motor_current`, `rpm`, `noise_db`, `pressure`. Враховує коливання протягом доби та робочого тижня. Параметр `FAULT_RATE` у `.env` регулює ймовірність штучної несправності. MQTT-тема `sensors/factory/telemetry`.

### Edge Processor

Підписується на MQTT, перевіряє пороги з `edge/config.json`, формує оповіщення, публікує команду в `actuators/factory`, зберігає локальну чергу у файлі SQLite на Docker volume `edge-data`. В InfluxDB пише вимірювання `edge_measurements`. Команди надходять через `cloud/commands`. Записи для Cloud передаються через `cloud/upload`.

### Cloud Connector

Слухає `cloud/upload`, веде SQLite-журнал у Docker volume `cloud-data`, зберігає часові ряди `cloud_measurements` в InfluxDB, відповідає через `cloud/ack`. Надає API `/api/health`, `/api/summary`, `/api/history`, `/api/aggregate`, `/api/alerts`, `/api/actions`, `/api/commands`.

### Dashboard

Nginx віддає HTML, CSS та JavaScript, проксує `/api/` до Cloud Flask, оновлює показники через polling. Не потребує зовнішнього CDN. Функціональні кнопки надсилають MQTT-команди через REST API.

## Локальні тести без Docker

```bash
python3 -m unittest discover -s tests -v
```

Покривається генерація шести сенсорів, шість несправностей, нормальні показники, критичні пороги, середні значення та погодинна/похвилинна агрегація. Повний запуск Docker Compose необхідно перевірити на власному комп'ютері з Docker Desktop. Результати інтеграційного тестування впишіть у звіт після запуску.

## Налаштування безпеки

MQTT без авторизації та тестові облікові дані призначені тільки для локальної навчальної демонстрації. Порти 1883, 8080, 8086 прив'язані до `127.0.0.1`. Не публікувати цей проєкт у відкритому інтернеті без автентифікації, TLS та зміни паролів.

## Декларація використання ШІ

- **Інструмент:** ChatGPT (OpenAI).
- **Мета:** допомога з архітектурою Docker-проєкту, написанням початкових версій Python-файлів, конфігурації Docker Compose, вебпанелі, інструкцій, тестів та звіту.
- **Запит:** «теперь брат точно так же нужно сделать и эту практическую». У попередньому обговоренні були умови виконати завдання за списком, обрати простий варіант, писати код без коментарів і підготувати звіт.
- **Згенеровані фрагменти:** початковий код у `sensors/`, `edge/`, `cloud/`, `dashboard/`, `docker-compose.yml`, тести та документація.
- **Самостійне доопрацювання:** студент заповнює цей пункт після власної перевірки запуску, виправлення помилок, фіксації результатів та підготовки відео. Не заявляйте про перевірки, яких не проводили.
