
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import asyncio
from datetime import datetime, time, timedelta

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Состояние пользователя
user_data = {}
analysis_active = True  # Переключатель автoанализа

# Команды

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, брат! Я с тобой на связи.")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я твой трейдинг-бот. Сигналы, анализ, обучение, сопровождение — всё будет.")

async def setmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mode = context.args[0]
        amount = int(context.args[1])
        leverage = int(context.args[2])
        user_data[update.effective_user.id] = {
            "mode": mode,
            "amount": amount,
            "leverage": leverage,
            "signals": [],
            "current_trade": {}
        }
        await update.message.reply_text(f"Режим установлен: {mode.upper()} | Объём: {amount} USDT | Плечо: x{leverage}")
    except:
        await update.message.reply_text("Формат команды неверен. Пример: /setmode aggressive 300 10")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи сигнал в формате: LONG BTC от 65000 до 68000")

async def entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_data:
        user_data[uid]["current_trade"]["entry"] = update.message.date
        await update.message.reply_text("Вход зафиксирован.")
    else:
        await update.message.reply_text("Сначала установи режим через /setmode")

async def exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_data and "entry" in user_data[uid]["current_trade"]:
        user_data[uid]["current_trade"]["exit"] = update.message.date
        await update.message.reply_text("Выход зафиксирован. Пока расчёт прибыли заглушен.")
    else:
        await update.message.reply_text("Сначала зафиксируй вход через /entry")

async def journal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_data and user_data[uid]["signals"]:
        reply = "\n".join(user_data[uid]["signals"])
        await update.message.reply_text("Сигналы:\n" + reply)
    else:
        await update.message.reply_text("Журнал пуст, брат.")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отчёт по сделкам пока готовится. Скоро будет.")

# Урок по команде
async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")
    lesson_text = (
        f"Урок на {today}:
"
        "- Теория: Сегодня разбираем, что такое ордер-блоки.
"
        "- Практика: Посмотри на график BTC и отметь последнюю зону, где цена дала сильный откат.
"
        "(В будущем здесь будет скрин и вопрос для ответа.)"
    )
    await update.message.reply_text(lesson_text)

# Анализ рынка
async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Рынок:
BTC — нейтрально
ETH — бычья структура
Альты — следуем за BTC")

# Управление автоанализом
async def stop_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global analysis_active
    analysis_active = False
    await update.message.reply_text("Автоматический анализ остановлен.")

async def resume_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global analysis_active
    analysis_active = True
    await update.message.reply_text("Автоматический анализ возобновлён.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не понял команду, брат. Проверь или используй /about.")

# Автоматическая отправка урока
async def scheduled_lesson(app):
    while True:
        now = datetime.now()
        lesson_time = datetime.combine(now.date(), time(hour=8, minute=30))
        if now >= lesson_time and now <= lesson_time + timedelta(minutes=1):
            for uid in user_data:
                try:
                    await app.bot.send_message(chat_id=uid, text="(Урок) Теория: сегодня смотрим ордер-блоки.")
                except:
                    pass
            await asyncio.sleep(60)
        await asyncio.sleep(30)

def main():
    app = ApplicationBuilder().token("7764468557:AAEy1S3TybWK_8t0LIRSVM8t78jjqTqtYL8").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("setmode", setmode))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("entry", entry))
    app.add_handler(CommandHandler("exit", exit))
    app.add_handler(CommandHandler("journal", journal))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("lesson", lesson))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("stop_analysis", stop_analysis))
    app.add_handler(CommandHandler("resume_analysis", resume_analysis))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.job_queue.run_once(lambda *_: asyncio.create_task(scheduled_lesson(app)), 1)

    app.run_polling()

if __name__ == "__main__":
    main()

