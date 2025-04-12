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
import datetime

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Пользовательские данные
user_data = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, брат! Я с тобой на связи.")

# Команда /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я твой трейдинг-бот. Сигналы, анализ, обучение, сопровождение — всё будет.")

# Команда /setmode
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

# Команда /signal
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = " ".join(context.args)
    if uid in user_data:
        user_data[uid]["signals"].append(text)
        await update.message.reply_text("Сигнал записан.")
    else:
        await update.message.reply_text("Сначала установи режим через /setmode")

# Команда /entry
async def entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_data:
        user_data[uid]["current_trade"]["entry"] = update.message.date
        await update.message.reply_text("Вход зафиксирован.")
    else:
        await update.message.reply_text("Сначала установи режим через /setmode")

# Команда /exit
async def exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_data and "entry" in user_data[uid]["current_trade"]:
        user_data[uid]["current_trade"]["exit"] = update.message.date
        await update.message.reply_text("Выход зафиксирован. Пока расчёт прибыли заглушен.")
    else:
        await update.message.reply_text("Сначала зафиксируй вход через /entry")

# Команда /journal
async def journal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_data and user_data[uid]["signals"]:
        reply = "\n".join(user_data[uid]["signals"])
        await update.message.reply_text("Сигналы:\n" + reply)
    else:
        await update.message.reply_text("Журнал пуст, брат.")

# Команда /report
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отчёт по сделкам пока готовится. Скоро будет.")

# Уведомление о неизвестной команде
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не понял команду, брат. Проверь или используй /about.")

# Автосигналы по расписанию
async def scheduled_signal(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    message = f"АВТОСИГНАЛ ({now})\nBTCUSDT зона интереса от 67200 до 67550. Возможен лонг с коротким стопом."
    for uid in user_data:
        await context.bot.send_message(chat_id=uid, text=message)

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
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Автосигнал в 8:30 каждый день
    app.job_queue.run_daily(scheduled_signal, time=datetime.time(hour=8, minute=30))

    app.run_polling()

if __name__ == "__main__":
    main()
