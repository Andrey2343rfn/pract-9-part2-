from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable, KeepTogether

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "docs" / "Practice9_2_Report.pdf"
metric = json.loads((BASE / "artifacts" / "local_validation.json").read_text())
regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
mono = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
pdfmetrics.registerFont(TTFont("DejaVu", regular))
pdfmetrics.registerFont(TTFont("DejaVuB", bold))
pdfmetrics.registerFont(TTFont("Mono", mono))
PAGE_W, PAGE_H = A4
NAVY = colors.HexColor("#16263E")
TEAL = colors.HexColor("#157C7A")
LIGHT = colors.HexColor("#EFF6F9")
MUTED = colors.HexColor("#526578")
RULE = colors.HexColor("#D8E5EB")
BLUE = colors.HexColor("#2C5C8A")

styles = {
    "title": ParagraphStyle("cover", fontName="DejaVuB", fontSize=22, leading=29, textColor=NAVY, spaceAfter=13),
    "sub": ParagraphStyle("sub", fontName="DejaVu", fontSize=12, leading=17, textColor=TEAL, spaceAfter=10),
    "h1": ParagraphStyle("h1", fontName="DejaVuB", fontSize=17, leading=24, spaceAfter=13, textColor=NAVY),
    "h2": ParagraphStyle("h2", fontName="DejaVuB", fontSize=11, leading=16, spaceBefore=12, spaceAfter=6, textColor=BLUE),
    "body": ParagraphStyle("body", fontName="DejaVu", fontSize=9.1, leading=14.3, spaceAfter=8, textColor=NAVY),
    "small": ParagraphStyle("small", fontName="DejaVu", fontSize=8.1, leading=12.1, spaceAfter=6, textColor=MUTED),
    "table": ParagraphStyle("table", fontName="DejaVu", fontSize=8.0, leading=11, textColor=NAVY),
    "tableh": ParagraphStyle("tableh", fontName="DejaVuB", fontSize=8.0, leading=11, textColor=colors.white),
    "mono": ParagraphStyle("mono", fontName="Mono", fontSize=7.8, leading=13, textColor=colors.HexColor("#26334A")),
    "label": ParagraphStyle("label", fontName="DejaVuB", fontSize=9, leading=13, textColor=TEAL, spaceAfter=8),
}

story=[]
def P(t, style="body"):
    story.append(Paragraph(t, styles[style]))
def H(t): P(t,"h1")
def H2(t): P(t,"h2")
def S(n=1): story.append(Spacer(1,n*mm))
def bullet(t): P("<font color='#157C7A'>●</font> " + t)
def code(*lines):
    data = [[Paragraph(line.replace(" ","&nbsp;"), styles["mono"])] for line in lines]
    t=Table(data,colWidths=[174*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F2F5F8")),("BOX",(0,0),(-1,-1),0.5,RULE),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),9)]))
    story.append(t)
def tbl(headers, rows, widths=None):
    data = [[Paragraph(str(x),styles["tableh"]) for x in headers]]
    data.extend([[Paragraph(str(x), styles["table"]) for x in row] for row in rows])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),7),("GRID",(0,0),(-1,-1),0.3,RULE)]))
    story.append(t)
def pic(name, width=172):
    from PIL import Image as PILImage
    src=BASE/"docs"/name
    img=PILImage.open(src)
    h=width*img.height/img.width
    story.append(Image(str(src),width=width*mm,height=h*mm))
def page(): story.append(PageBreak())

def back(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0,PAGE_H-17*mm,PAGE_W,17*mm,fill=1,stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("DejaVuB",8)
    canvas.drawString(18*mm,PAGE_H-11*mm,"IoT EDGE + CLOUD  |  ПРАКТИЧНА РОБОТА 9.2")
    canvas.setStrokeColor(RULE)
    canvas.line(18*mm,16*mm,PAGE_W-18*mm,16*mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("DejaVu",7.5)
    canvas.drawString(18*mm,10.5*mm,"Свидан Андрій Андрійович · Варіант 1 · Smart Factory Monitoring")
    canvas.drawRightString(PAGE_W-18*mm,10.5*mm,f"{doc.page}")
    canvas.restoreState()

pdf=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=27*mm,bottomMargin=22*mm,title="Практична робота 9.2. IoT Edge Computing + Cloud Integration",author="Свидан Андрій Андрійович")

P("МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ", "label")
S(18)
P("ПРАКТИЧНА РОБОТА № 9.2", "title")
P("IoT Edge Computing + Cloud Integration з Docker", "sub")
S(3)
P("Варіант 1. Smart Factory Monitoring System", "h1")
P("Дисципліна: Технології IoT та SMART-технології")
P("Тема: інтеграція IoT з Edge Computing та Cloud")
S(20)
tbl(["Відомості", "Значення"], [["Студент", "Свидан Андрій Андрійович"],["Група", "_______________________"],["Навчальний рік", "2025/2026"],["Викладач", "О.А. Клименко"]],[49*mm,125*mm])
S(28)
P("Мета: розробити систему IoT моніторингу обладнання з локальною обробкою даних, MQTT-комунікацією, контейнеризацією, хмарною аналітикою та вебвізуалізацією.")
S(12)
P("Звіт підготовлено на основі реалізованого коду, 8 виконаних модульних тестів і локальної перевірки алгоритмів. Повний запуск Docker Compose та скриншоти інтеграції потрібно підтвердити на комп'ютері студента.","small")
page()

H("1. Мета роботи та короткий огляд")
P("Розроблено навчальну систему моніторингу промислової лінії. Симулятор періодично формує показники обладнання. Обчислювальний вузол Edge аналізує дані та відразу реагує на перевищення допустимих значень. Cloud накопичує історію, агрегує показники, надає REST API та вебпанель.")
H2("Основні завдання")
bullet("Сформувати Docker Compose проєкт з шести взаємопов'язаних сервісів.")
bullet("Генерувати показники шести IoT сенсорів із добовими коливаннями та несправностями.")
bullet("Реалізувати MQTT-передавання, локальні правила Edge та автоматичні дії.")
bullet("Забезпечити локальне зберігання і повторне передавання непідтверджених записів.")
bullet("Додати Cloud Connector з InfluxDB, агрегуванням та REST API.")
bullet("Розробити вебпанель з оновленням показників, графіком та віддаленими командами.")
H2("Обґрунтування вибору")
P("Варіант Smart Factory Monitoring System логічно продовжує практичну роботу 9.1, де аналізувалися вібрація, температура підшипників, струм, оберти, шум і тиск. Для швидкого локального реагування використано правила з пороговими значеннями. На відміну від ML, такі правила легко перевірити й пояснити на захисті.")
H2("Результат реалізації")
tbl(["Критерій", "Виконано"], [["Програмні компоненти", "6 Docker-сервісів у конфігурації"],["IoT-показники", "6 типів сенсорів"],["Комунікація", "MQTT QoS 1, HTTP REST"],["Edge автономність", "SQLite-черга та повторна синхронізація"],["Cloud", "InfluxDB, Flask, SQLite-журнал"],["Візуалізація", "HTML, CSS, JavaScript, SVG"],["Локальні тести", "8 із 8 пройдено"]],[57*mm,117*mm])
page()

H("2. Архітектура системи")
P("Використано розділення на Edge та Cloud. Сервіси розміщені у двох Docker bridge-мережах. MQTT брокер та InfluxDB доступні в обох мережах. Симулятор і Edge працюють у сегменті <b>edge-net</b>, а Cloud і вебпанель у сегменті <b>cloud-net</b>.")
S(4)
tbl(["Вузол", "Дані / функції", "Рівень"], [["Sensor Simulator", "Формування 6 вимірювань", "Edge"],["MQTT Broker", "Маршрутизація повідомлень", "Міст"],["Edge Processor", "Пороги, аварійні дії, буфер", "Edge"],["InfluxDB", "Часові ряди edge та cloud", "Спільна БД"],["Cloud Connector", "Підтвердження, статистика, API", "Cloud"],["Dashboard", "Картки, графік, журнал, команди", "Cloud"]],[42*mm,104*mm,28*mm])
H2("Схема передавання даних")
pic("architecture.png",169)
P("Рисунок 1. Архітектура двох рівнів. MQTT передає дані та команди, Edge має локальний буфер.","small")
H2("Ключовий принцип Edge Computing")
P("При критичній температурі чи вібрації Edge самостійно виконує потрібну дію. Для локального рішення йому не потрібна відповідь від Cloud. Це зменшує залежність аварійного реагування від мережі. Cloud використовується для довготривалої аналітики та контролю з браузера.")
page()

H("3. Docker Environment Setup")
P("Конфігурацію системи описано в `docker-compose.yml`. Кожен Python-компонент отримав окремий Dockerfile із базовим образом Python 3.11 slim. Для вебпанелі використано Nginx, для брокера Eclipse Mosquitto 2.0, для часових рядів InfluxDB 2.7.")
H2("Основні параметри")
tbl(["Параметр", "Рішення"], [["Порти", "8080 для вебпанелі, 8086 для InfluxDB, 1883 для MQTT"],["Безпека демонстрації", "Зовнішні порти прив'язані до 127.0.0.1"],["Налаштування", ".env із параметрами InfluxDB та симулятора"],["Мережі", "edge-net та cloud-net"],["Volumes", "mqtt-data, mqtt-logs, edge-data, cloud-data, influx-data, influx-config"],["Автозапуск", "restart: unless-stopped"]],[57*mm,117*mm])
H2("Команди запуску на macOS")
code("docker --version", "docker compose version", "docker compose up --build -d", "docker compose ps")
P("У разі успішного запуску команда `docker compose ps` покаже шість активних сервісів. У цій робочій середовищі Docker Engine відсутній, тому стан контейнерів і мережеву інтеграцію необхідно підтвердити на Mac після запуску Docker Desktop.")
H2("Перевірка журналів")
code("docker compose logs --tail=20 sensor-simulator", "docker compose logs --tail=20 edge-processor", "docker compose logs --tail=20 cloud-connector")
P("Зупинка сервісів виконується командою `docker compose down`. Існуючі дані у Docker volumes залишаються. Команда `docker compose down -v` видаляє також постійне сховище.")
page()

H("4. Реалізація IoT симулятора")
P("Файли `sensors/patterns.py` і `sensors/simulator.py` генерують і надсилають дані в тему `sensors/factory/telemetry`. Інтервал публікації визначає параметр `SENSOR_INTERVAL`, типовий інтервал для демонстрації становить 2 секунди.")
H2("Параметри обладнання")
tbl(["Сенсор", "Одиниця", "Нормальний сценарій"], [["vibration", "мм/с", "Вібрація залежить від навантаження"],["bearing_temp", "°C", "Температура змінюється за добовим циклом"],["motor_current", "A", "Струм корелює з навантаженням"],["rpm", "об/хв", "Оберти зі випадковим відхиленням"],["noise_db", "дБ", "Акустичний шум змінюється з навантаженням"],["pressure", "бар", "Тиск змінюється в невеликому діапазоні"]],[49*mm,24*mm,101*mm])
H2("Генерація несправностей")
P("Параметр `FAULT_RATE=0.10` задає ймовірність штучного збою для одного пакета. Передбачено шість категорій несправностей: перегрів, надмірна вібрація, зменшення обертів, низький тиск, перевантаження струмом і шум. Цільові показники виходять за критичні пороги, що дозволяє перевірити локальні правила.")
pic("chart_temperature.png",165)
P("Рисунок 2. Приклад 420 штучних вимірювань із локального тесту. Це перевірка функції генерації даних, не скриншот Docker.","small")
page()

H("5. Edge Processor та правила реагування")
P("Edge підписується на MQTT-теми `sensors/factory/telemetry`, `cloud/ack` і `cloud/commands`. Кожне вимірювання проходить перевірку порогів із файлу `edge/config.json`. При порушенні правил створюється повідомлення і публікується дія у `actuators/factory`.")
H2("Таблиця критичних значень")
tbl(["Показник", "Умова", "Дія", "Рівень"], [["Температура", "> 82 °C", "cooling_on", "critical"],["Вібрація", "> 3.2 мм/с", "stop_line", "critical"],["Струм", "> 19 A", "reduce_load", "warning"],["Оберти", "< 900 об/хв", "inspect_motor", "warning"],["Шум", "> 87 дБ", "inspect_noise", "warning"],["Тиск", "< 2.4 бар", "inspect_pressure", "critical"]],[51*mm,35*mm,52*mm,36*mm])
H2("Алгоритм локального рішення")
P("Функція `evaluate(values, thresholds)` перевіряє кожен показник. Вона повертає список аномалій із назвою сенсора, фактичним значенням, порогом, пріоритетом і дією. Додатково Edge аналізує різку зміну температури порівняно з попередніми даними в буфері останніх 120 вимірювань.")
H2("Автоматизовані дії")
P("При спрацюванні правила публікується MQTT-команда. `stop_line` переводить стан програмної моделі обладнання в режим зупинки. `cooling_on` і `cooling_off` передають керуючі команди як симуляцію актуаторів. Для реального обладнання потрібні контролери, підтвердження стану та безпечна апаратна інтеграція.")
H2("Оцінювання швидкодії")
P("Вимірюється час виконання локального правила, починаючи від надходження повідомлення до формування рішення. Окремо працюють запис у SQLite, MQTT і InfluxDB. Отже, цей показник не дорівнює повній мережевій затримці від датчика до Cloud.")
page()

H("6. Локальна автономність та відмовостійкість")
P("Для захисту від втрати даних Edge використовує SQLite. Кожен пакет з унікальним `event_id` додається до таблиці `pending` перед надсиланням до Cloud. Непідтверджені записи залишаються на диску у Docker volume `edge-data`.")
H2("Алгоритм синхронізації")
bullet("Крок 1. Edge одержує вимірювання, перевіряє правила та додає його в SQLite.")
bullet("Крок 2. Кожні кілька секунд Edge повторно передає пакети до MQTT-теми `cloud/upload`.")
bullet("Крок 3. Cloud записує повідомлення в журнал і часову базу InfluxDB.")
bullet("Крок 4. Після успішного запису Cloud надсилає `cloud/ack` з ідентифікатором пакета.")
bullet("Крок 5. Edge видаляє з локальної черги тільки підтверджений запис.")
H2("Дедуплікація")
P("В Cloud журнал має первинний ключ `event_id`. Це не дозволяє подвоїти логічні записи при повторному отриманні пакета. Для часових рядів InfluxDB Cloud використовує однакові теги, час вимірювання і значення полів при повторному надсиланні.")
H2("Сценарій перевірки")
code("docker compose stop cloud-connector", "docker compose logs --tail=15 edge-processor", "docker compose start cloud-connector", "docker compose logs --tail=15 cloud-connector")
P("Очікується, що Edge продовжить обробку датчиків, а кількість записів у `pending` під час відключення зростатиме. Після відновлення Cloud та отримання підтверджень черга поступово скорочуватиметься. Цю перевірку потрібно провести на Mac і показати у відео.")
page()

H("7. Cloud Integration та зберігання")
P("Компонент `cloud/connector.py` реалізує Flask API та клієнт MQTT. Дані з Edge надходять у тему `cloud/upload`. Cloud перевіряє їх, записує у SQLite-журнал, створює точки у вимірюванні `cloud_measurements` InfluxDB і після успіху підтверджує Edge.")
H2("Маршрути REST API")
tbl(["HTTP", "Маршрут", "Призначення"], [["GET", "/api/health", "Стан Cloud та кількість записів"],["GET", "/api/summary", "Поточні показники та статистика"],["GET", "/api/history", "Останні вимірювання"],["GET", "/api/aggregate", "Групування за хвилиною, годиною, днем"],["GET", "/api/alerts", "Останні аномалії"],["GET", "/api/actions", "Підтвердження виконаних команд"],["POST", "/api/commands", "Відправлення команди до Edge"]],[19*mm,62*mm,93*mm])
H2("Аналітичні функції")
P("Модуль `cloud/analytics.py` обчислює середнє, мінімальне та максимальне значення кожного сенсора. Функція `aggregate()` групує історію за хвилинами, годинами або днями та повертає кількість вимірювань для кожного періоду.")
H2("Двосторонній обмін")
P("Після натискання кнопки на вебпанелі браузер надсилає HTTP POST на `/api/commands`. Cloud публікує повідомлення у MQTT-тему `cloud/commands`. Edge виконує команду, після чого відповідає у `edge/actions`. Cloud додає результат до журналу, а Dashboard показує останні виконані дії.")
page()

H("8. Dashboard та користувацький інтерфейс")
P("Вебпанель реалізовано без додаткових JavaScript-бібліотек. Nginx на порту 8080 віддає HTML, CSS та JS і проксує запити `/api/` до Flask. Дані оновлюються кожні три секунди через HTTP polling. Графік будується SVG-лінією для останніх 120 значень температури.")
H2("Елементи панелі")
bullet("Чотири показники: синхронізовані записи, кількість попереджень, затримка Edge та стан системи.")
bullet("Шість карток із поточними значеннями датчиків та одиницями вимірювання.")
bullet("Графік зміни температури підшипника за останні вимірювання.")
bullet("Журнал аномалій із назвою датчика, порогом, дією та часом.")
bullet("Кнопки зупинки лінії, запуску лінії, вмикання й вимикання охолодження.")
bullet("Підтверджені команди та повідомлення про втрату з'єднання з Cloud.")
H2("Схема екрану")
tbl(["Блок 1", "Блок 2"],[["Записи Cloud  |  Аномалії", "Latency Edge  |  Стан"],["Вібрація  |  Температура  |  Струм", "Оберти  |  Шум  |  Тиск"],["Графік температури за часом", "Автоматичне оновлення 3 с"],["Журнал аномалій", "Керування обладнанням"]],[87*mm,87*mm])
S(9)
P("Для демонстрації достатньо відкрити <b>http://localhost:8080</b> після запуску Docker. На цій сторінці з'являться реальні дані із симулятора після їх запису до Cloud. Скріншоти працюючої панелі студент повинен отримати на своєму комп'ютері та за потреби додати до звіту.","small")
page()

H("9. Локальні перевірки програмної логіки")
P("Оскільки Docker Engine у середовищі підготовки відсутній, виконано перевірки функцій Python окремо від контейнерної інфраструктури. Тести запускаються без додаткових пакетів командою `python3 -m unittest discover -s tests -v`.")
H2("Результати модульних тестів")
tbl(["Перевірка", "Результат"], [["Наявність 6 датчиків", "PASS"],["Генерація 6 категорій несправностей", "PASS"],["Нормальний набір без оповіщень", "PASS"],["Перегрів викликає cooling_on", "PASS"],["Низький тиск викликає critical alert", "PASS"],["Середнє значення за 3 записами", "PASS"],["Агрегація даних за хвилиною", "PASS"],["Обробка некоректного інтервалу", "PASS"]],[143*mm,31*mm])
H2("Додаткова перевірка синтетичного потоку")
P(f"Локальний симулятор створив <b>{metric['synthetic_samples']}</b> вимірювань, з яких <b>{metric['synthetic_faults']}</b> мали штучно встановлену несправність. Прості правила виявили <b>{metric['rule_true_positives']}</b> із них, хибних спрацювань у цьому тесті не було. Значення precision та recall становили 100%. Це результат контрольованого генератора, а не оцінка на реальному промисловому обладнанні.")
pic("chart_faults.png",158)
P("Рисунок 3. Кількість штучних несправностей за типами в локальному тесті.","small")
page()

H("10. Аналіз затримок, ризиків та обмежень")
P("Виконано локальний замір часу тільки функції `evaluate()` на 2 016 синтетичних пакетах. Середній час становив приблизно <b>%.4f мс</b>, а 95-й процентиль приблизно <b>%.4f мс</b>. Значення залежать від комп'ютера та не включають MQTT, роботу SQLite, запис в InfluxDB і HTTP." % (metric['rule_latency_mean_ms'],metric['rule_latency_p95_ms']))
H2("Що ще необхідно перевірити у Docker")
tbl(["Сценарій", "Критерій успіху"], [["Початковий запуск", "6 контейнерів у стані Up"],["MQTT потік", "Дані потрапляють від Simulator до Edge"],["Cloud storage", "Лічильник API зростає, історія доступна"],["Автоматичні дії", "При аномалії з'являються EDGE ALERT"],["Cloud → Edge", "Кнопка Dashboard викликає action Edge"],["Cloud offline", "Edge продовжує роботу та накопичує pending"],["Cloud restart", "Черга pending поступово спорожнюється"],["Latency", "Затримка локальних рішень відповідає меті < 100 мс"]],[63*mm,111*mm])
H2("Можливі недоліки навчального прототипу")
bullet("MQTT використовує анонімне підключення. Конфігурація призначена для локальної демонстрації.")
bullet("Тестовий Cloud запущено у Docker на тому самому комп'ютері. Це логічне розділення, а не зовнішній інтернет-сервіс.")
bullet("При великій кількості накопичених записів повторна синхронізація потребує додаткової оптимізації.")
bullet("Правила виявлення штучних несправностей поки не перевірені на даних реальних датчиків.")
page()

H("11. Покрокова перевірка і сценарій захисту")
P("Для відео тривалістю 5–7 хвилин достатньо послідовно показати роботу системи, мережевий обмін і локальну автономність.")
tbl(["Час", "Дія"],[["0:00–0:35", "Назва практичної, варіант, мета"],["0:35–1:25", "Архітектура та конфігурація Docker Compose"],["1:25–2:10", "docker compose up --build -d, docker compose ps"],["2:10–3:00", "Логи датчиків та Edge, аварійні правила"],["3:00–3:50", "Вебпанель, графік, команди Cloud → Edge"],["3:50–5:05", "Зупинка Cloud, перевірка pending, запуск Cloud"],["5:05–6:00", "API, результати та висновки"]],[39*mm,135*mm])
H2("Команди автономної перевірки")
code("docker compose stop cloud-connector", "docker compose logs --tail=15 edge-processor", "docker compose start cloud-connector", "docker compose logs --tail=15 cloud-connector")
H2("Дані для внесення після реального запуску")
tbl(["Показник", "Значення після запуску"], [["Контейнери у стані Up", "__________________"],["Кількість повідомлень у Cloud", "__________________"],["Pending під час Cloud offline", "__________________"],["Pending після відновлення", "__________________"],["Середня затримка Edge", "__________________"],["Скріншот Dashboard", "Додати за потреби"]],[83*mm,91*mm])
page()

H("12. Висновки та рекомендації")
P("У ході роботи розроблено структуру системи Smart Factory Monitoring на основі Docker Compose. Реалізовано симулятор шести датчиків, MQTT-передавання, правила локального Edge реагування, локальний буфер SQLite, Cloud Connector, зберігання в InfluxDB і вебпанель українською мовою.")
P("Виконано вісім модульних тестів Python, які завершилися успішно. Синтетичний потік із 2 016 повідомлень підтвердив роботу заданих порогів для контрольованих аномалій. Повна працездатність MQTT, Docker мереж та відмовостійкість потребують окремого тесту після запуску Docker Desktop на комп'ютері студента.")
H2("Переваги обраної архітектури")
bullet("Критичні рішення приймаються на Edge без очікування відповіді Cloud.")
bullet("Локальний SQLite-буфер зберігає повідомлення під час перерв у роботі Cloud.")
bullet("Унікальні event_id і MQTT-підтвердження допомагають уникати втрат і дублювання записів.")
bullet("Cloud API дає доступ до поточних даних, історії, агрегатів і команд.")
H2("Пропозиції щодо розвитку")
bullet("Додати MQTT TLS, паролі та ролі доступу до вебпанелі.")
bullet("Перевірити систему на потоці реальних промислових датчиків.")
bullet("Додати ML-модель із практичної 9.1 для розпізнавання складніших аномалій.")
bullet("Перенести Cloud Connector на окремий сервер та протестувати реальний мережевий розрив.")
H2("Комплект для здачі")
P("Архів ZIP з вихідними Python-файлами, Dockerfile, Docker Compose, вебпанеллю, тестами, README, цим звітом у PDF та сценарієм відео. Відео демонстрації необхідно записати окремо після запуску на Mac.")
H2("Використані матеріали")
P("Методичні вказівки до практичної роботи 9.2 «IoT Edge Computing + Cloud Integration з Docker». Документація Docker Compose, Eclipse Mosquitto, Flask, InfluxDB та paho-mqtt.","small")

pdf.build(story,onFirstPage=back,onLaterPages=back)
print(OUT)
