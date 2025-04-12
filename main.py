import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Состояние пользователя
user_data = {}

# Умная проверка на ошибки (заглушка)
def analyze_trade(entry_time, exit_time):
    duration = (exit_time - entry_time).total_seconds() / 60
    if duration < 1:
        return "Слишком короткая сделка. Возможно, поспешил."
    elif duration > 180:
        return "Очень длинная сделка. Возможно, упустил момент."
    return "Ты сделал всё по системе. Минус — часть игры. Идём дальше."

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
    signal_text = " ".join(context.args)
    if uid in user_data:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
        full_signal = f"[{timestamp}] {signal_text}"
        user_data[uid]["signals"].append(full_signal)
        await update.message.reply_text("Сигнал записан.")
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
        entry_time = user_data[uid]["current_trade"]["entry"]
        exit_time = user_data[uid]["current_trade"]["exit"]
        analysis = analyze_trade(entry_time, exit_time)
        await update.message.reply_text(f"Выход зафиксирован.
{analysis}")
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
    await update.message.reply_text("Отчёт по сделкам скоро будет с таблицей. Следим за твоим прогрессом.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не понял команду, брат. Проверь или используй /about.")

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

    app.run_polling()

if __name__ == "__main__":
    main()
