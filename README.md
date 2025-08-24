# Telegram Delivery Bot

Этот бот предназначен для управления сменами курьеров и интеграции данных с Google Sheets.

## ✅ Возможности
- Начало смены с кнопкой
- Автоматическое завершение смены через 3 часа
- Запись данных в Google Sheets
- Готов для доработки (учёт заказов, отчёты, статистика)

---

## 🚀 Установка

```bash
git clone https://github.com/YOUR_USERNAME/delivery_bot.git
cd delivery_bot
pip install -r requirements.txt
```

---

## 🔑 Настройка
1. Создайте **сервисный аккаунт** в Google Cloud.
2. Скачайте `credentials.json` и положите его в корень проекта.
3. Дайте доступ сервисному аккаунту к Google Sheets.
4. Укажите:
   - `BOT_TOKEN` в `delivery_bot.py`
   - `TABLE_ID` из URL Google Sheets

---

## ▶ Запуск
```bash
python delivery_bot.py
```

---

## ❗Важно:
- **Не загружайте credentials.json в GitHub!**
- Добавьте его в `.gitignore`
