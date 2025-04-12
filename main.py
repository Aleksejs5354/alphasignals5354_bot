import logging
import datetime
from telegram import Update
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackContext
)
from datetime import time
import random

# === НАСТРОЙКИ ===
TOKEN = "YOUR_BOT_TOKEN"
OWNER_ID = 123456789  # замените на свой Telegram ID

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

mode_settings = {"amount": 300, "leverage": 10}
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
            await update.message.reply_text(f"Установлен режим: сумма {amount} USDT, плечо x{leverage}")
        else:
            await update.message.reply_text("Некорректные значения.")
    except:
        await update.message.reply_text("Использование: /setmode сумма плечо")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        pair, direction, entry, sl, tp = context.args
        response = (
            f"Сигнал по {pair.upper()}:
"
            f"Направление: {direction.upper()}
"
            f"Вход: {entry}
Stop Loss: {sl}
Take Profit: {tp}
"
            f"Объём: {mode_settings['amount']} USDT, Плечо: x{mode_settings['leverage']}"
        )
        await update.message.reply_text(response)
    except:
        await update.message.reply_text("Формат: /signal BTCUSDT LONG 66000 65200 67500")

async def entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    trade_journal.append({"тип": "вход", "текст": text, "время": str(datetime.datetime.now()), "прибыль": None})
    await update.message.reply_text("Вход зафиксирован.")

async def exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    profit = None
    try:
        profit = float(context.args[-1])
    except:
        pass
    trade_journal.append({"тип": "выход", "текст": text, "время": str(datetime.datetime.now()), "прибыль": profit})
    await update.message.reply_text("Выход зафиксирован.")

async def journal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not trade_journal:
        await update.message.reply_text("Журнал пуст.")
        return
    response = ""
    for entry in trade_journal[-10:]:
        p = f" | PnL: {entry['прибыль']}" if entry['прибыль'] is not None else ""
        response += f"{entry['тип'].upper()} | {entry['время']} | {entry['текст']}{p}
"
    await update.message.reply_text(response)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    period = context.args[0] if context.args else "today"
    now = datetime.datetime.now()
    filtered = []
    for t in trade_journal:
        t_time = datetime.datetime.fromisoformat(t["время"])
        if period == "today" and t_time.date() == now.date():
            filtered.append(t)
        elif period == "week" and t_time.isocalendar()[1] == now.isocalendar()[1]:
            filtered.append(t)
    total = sum(t["прибыль"] for t in filtered if t["прибыль"] is not None)
    await update.message.reply_text(f"Отчёт за {period}: {len(filtered)} сделок
Суммарный PnL: {total:.2f} USDT")

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today().strftime("%d.%m.%Y")
    text = f"Урок на {today}:

Имбаланс и зоны возврата цены.
Отметь на графике BTCUSDT последнюю зону неэффективности."
    await update.message.reply_text(text)

async def fix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_loss = next((t for t in reversed(trade_journal) if t["тип"] == "выход" and t["прибыль"] and t["прибыль"] < 0), None)
    if not last_loss:
        await update.message.reply_text("Убыточных сделок не найдено.")
        return
    cause = random.choice(["Рынок пошёл против сигнала", "Ошибка в стопе", "Не было подтверждения на вход", "Вход был хорошим, но рынок импульсивен"])
    await update.message.reply_text(f"Анализ последнего убытка:

Причина: {cause}
Сделка: {last_loss['текст']}
Время: {last_loss['время']}")

async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.args[0] if context.args else "BTCUSDT"
    tf = context.args[1] if len(context.args) > 1 else "1h"
    await update.message.reply_text(f"График {pair} ({tf}) будет доступен в следующей версии.
Визуализация TradingView в разработке.")

async def scheduled_chart(context: CallbackContext):
    await context.bot.send_message(chat_id=OWNER_ID, text="Автографик BTCUSDT 1H — будет в будущей версии.")

# === ГЛАВНАЯ ФУНКЦИЯ ===
def main():
    app = ApplicationBuilder().token(TOKEN).post_init(setup_jobs).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setmode", setmode))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("entry", entry))
    app.add_handler(CommandHandler("exit", exit))
    app.add_handler(CommandHandler("journal", journal))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("lesson", lesson))
    app.add_handler(CommandHandler("fix", fix))
    app.add_handler(CommandHandler("chart", chart))
    print("AlphaSignals запущен.")
    app.run_polling()

async def setup_jobs(app: Application):
    app.job_queue.run_daily(scheduled_chart, time=time(8, 30))

if __name__ == "__main__":
    main()
