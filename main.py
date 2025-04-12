
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, JobQueue
from datetime import datetime, time
import asyncio

# Инициализация логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "7764468557:AAEy1S3TybWK_8t0LIRSVM8t78jjqTqtYL8"

user_data = {}

# === Команды фазы 1 ===

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
        reply = "
".join(user_data[uid]["signals"])
        await update.message.reply_text("Сигналы:
" + reply)
    else:
        await update.message.reply_text("Журнал пуст, брат.")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отчёт по сделкам пока готовится. Скоро будет.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не понял команду, брат. Проверь или используй /about.")

# === Фаза 2: Учебный модуль ===

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%d.%m.%Y")
    text = (
        f"Урок на {today}:
"
        "- Найди зону ликвидности.
"
        "- Отметь ордер-блок.
"
        "- Определи направление тренда.
"
        "Ответ пришли вручную или используй команду /entry для фиксации точки входа."
    )
    await update.message.reply_text(text)

# === Фаза 4: Автографик и автоурок по расписанию ===

async def scheduled_chart(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data
    today = datetime.now().strftime("%d.%m.%Y")
    await context.bot.send_message(
        chat_id=user_id,
        text=(
            f"Урок на {today}:
"
            "- Посмотри на текущую цену BTC и ETH.
"
            "- Найди зоны интереса и неэффективности.
"
            "- Отметь, где возможен возврат цены.
"
            "Ответ зафиксируй через /entry."
        )
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

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

    # Расписание автоурока (фаза 4) в 8:30
    target_time = time(hour=8, minute=30)
    app.job_queue.run_daily(scheduled_chart, time=target_time, data=7764468557)

    app.run_polling()

if __name__ == "__main__":
    main()
