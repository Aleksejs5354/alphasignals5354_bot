import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import pytz

# Токен бота
BOT_TOKEN = "7764468557:AAEy1S3TybWK_8t0LIRSVM8t78jjqTqtYL8"

# Временная зона
LATVIA_TZ = pytz.timezone("Europe/Riga")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Данные пользователя
user_data = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, брат! Я с тобой на связи.")

# Команда /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я твой трейдинг-бот. Сигналы, анализ, обучение, сопровождение — всё будет."
    )

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
            "current_trade": {},
        }
        await update.message.reply_text(
            f"Режим установлен: {mode.upper()} | Объём: {amount} USDT | Плечо: x{leverage}"
        )
    except:
        await update.message.reply_text("Формат команды: /setmode aggressive 300 10")

# Команда /signal
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    signal_text = " ".join(context.args)
    timestamp = datetime.now(LATVIA_TZ).strftime("%Y-%m-%d %H:%M")
    user_data.setdefault(uid, {}).setdefault("signals", []).append(f"{timestamp} — {signal_text}")
    await update.message.reply_text("Сигнал сохранён и готов к сопровождению.")

# Команды /entry и /exit
async def entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data.setdefault(uid, {}).setdefault("current_trade", {})["entry"] = update.message.date
    await update.message.reply_text("Вход в сделку зафиксирован.")

async def exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    trade = user_data.get(uid, {}).get("current_trade", {})
    if "entry" in trade:
        trade["exit"] = update.message.date
        await update.message.reply_text("Выход из сделки зафиксирован.")
    else:
        await update.message.reply_text("Сначала зафиксируй вход через /entry")

# Команда /journal
async def journal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    signals = user_data.get(uid, {}).get("signals", [])
    if signals:
        await update.message.reply_text("Сигналы:
" + "
".join(signals))
    else:
        await update.message.reply_text("Журнал пуст, брат.")

# Команда /report
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отчёт по сделкам скоро будет доступен.")

# Команда /lesson (фаза 2)
async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(LATVIA_TZ).strftime("%Y-%m-%d")
    await update.message.reply_text(
        f"Урок на {today}:

"
        "- Что такое ордер-блок?
"
        "- Как определить зону ликвидности?

"
        "Вопрос: где на графике сейчас потенциальная зона возврата?"
    )

# Команда /autosignal (фаза 3)
async def autosignal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Анализируем рынок...

"
        "🔍 Обнаружено:
"
        "- Имбаланс на BTC 1H
"
        "- Раскорреляция с ETH
"
        "- Потенциальная зона входа: LONG BTC от 66500

"
        "Подтверждаешь? Жду команду /entry если входишь."
    )

# Обработка неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не понял команду, брат. Используй /about.")

# Главная функция
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("setmode", setmode))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("entry", entry))
    app.add_handler(CommandHandler("exit", exit))
    app.add_handler(CommandHandler("journal", journal))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("lesson", lesson))
    app.add_handler(CommandHandler("autosignal", autosignal))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()

if __name__ == "__main__":
    main()
