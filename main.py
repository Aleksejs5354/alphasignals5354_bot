
import logging
import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Хранилище данных
user_data = {}

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
    uid = update.effective_user.id
    signal_text = ' '.join(context.args)
    if uid in user_data:
        user_data[uid]["signals"].append(signal_text)
        await update.message.reply_text("Сигнал принят.")
    else:
        await update.message.reply_text("Сначала установи режим через /setmode")

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

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today().isoformat()
    text = f"""Урок на {today}:

Сегодня мы рассматриваем основы ордер-блоков.
1. Найди импульсное движение.
2. Отметь последнюю свечу перед этим импульсом.
3. Это и есть ордер-блок.

Попробуй найти такой на текущем графике BTC. Задача: пришли скрин с отмеченным блоком.""" 
    await update.message.reply_text(text)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не понял команду, брат. Проверь или используй /about.")

# Основная функция
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
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()

if __name__ == "__main__":
    main()
