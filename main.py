
import logging
import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackContext
)

# === НАСТРОЙКИ ===
TOKEN = "7764468557:AAEy1S3TybWK_8t0LIRSVM8t78jjqTqtYL8"
OWNER_ID = 7764468557

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
mode_settings = {
    "amount": 300,
    "leverage": 10
}

trade_journal = []

# === ОБРАБОТЧИКИ КОМАНД ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, брат")

async def setmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(context.args[0])
        leverage = int(context.args[1])
        if 1 <= leverage <= 125 and 1 <= amount <= 5000:
            mode_settings["amount"] = amount
            mode_settings["leverage"] = leverage
            await update.message.reply_text(
                f"Установлен режим: сумма {amount} USDT, плечо x{leverage}"
            )
        else:
            await update.message.reply_text("Некорректные значения.")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /setmode сумма плечо")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        pair = context.args[0]
        direction = context.args[1]
        entry = float(context.args[2])
        sl = float(context.args[3])
        tp = float(context.args[4])
        response = (
            f"Сигнал по {pair.upper()}:\n"
            f"Направление: {direction.upper()}\n"
            f"Вход: {entry}\n"
            f"Stop Loss: {sl}\n"
            f"Take Profit: {tp}\n"
            f"Объём: {mode_settings['amount']} USDT, Плечо: x{mode_settings['leverage']}"
        )
        await update.message.reply_text(response)
    except (IndexError, ValueError):
        await update.message.reply_text("Формат: /signal BTCUSDT LONG 66000 65200 67500")

async def entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    trade_journal.append({
        "тип": "вход",
        "текст": text,
        "время": str(datetime.datetime.now())
    })
    await update.message.reply_text("Вход зафиксирован.")

async def exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    trade_journal.append({
        "тип": "выход",
        "текст": text,
        "время": str(datetime.datetime.now())
    })
    await update.message.reply_text("Выход зафиксирован.")

async def journal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not trade_journal:
        await update.message.reply_text("Журнал пуст.")
        return
    response = ""
    for entry in trade_journal[-10:]:
        response += f"{entry['тип'].upper()} | {entry['время']} | {entry['текст']}\n"
    await update.message.reply_text(response)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trades = len(trade_journal)
    entries = len([t for t in trade_journal if t['тип'] == 'вход'])
    exits = len([t for t in trade_journal if t['тип'] == 'выход'])
    await update.message.reply_text(f"Сделок: {trades}\nВходов: {entries}\nВыходов: {exits}")

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today().strftime("%d.%m.%Y")
    text = f"Урок на {today}:\n\nСегодняшняя тема: Имбаланс и зоны возврата цены.\nОтметь на графике BTCUSDT последнюю зону неэффективности."
    await update.message.reply_text(text)

# === РАСПИСАНИЕ УРОКОВ ===
async def scheduled_chart(context: CallbackContext):
    today = datetime.date.today().strftime("%d.%m.%Y")
    text = f"Урок на {today}:\n\nСегодняшняя тема: Имбаланс и зоны возврата цены.\nОтметь на графике BTCUSDT последнюю зону неэффективности."
    await context.bot.send_message(chat_id=OWNER_ID, text=text)

# === ГЛАВНАЯ ФУНКЦИЯ ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setmode", setmode))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("entry", entry))
    app.add_handler(CommandHandler("exit", exit))
    app.add_handler(CommandHandler("journal", journal))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("lesson", lesson))

    from datetime import time
    app.job_queue.run_daily(scheduled_chart, time=time(8, 30))

    print("AlphaSignals запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()
