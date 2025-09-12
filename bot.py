import os
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# 🔐 Your Telegram Bot Token
BOT_TOKEN = "8291559832:AAGqbzjc40KjTgLEs8zpvxTF2lgfZienx-E"

# 🧠 Global Data Stores
launched_tokens = {}
user_notes = {}
referrals = {}
premium_users = set()

# 🪙 Token Launch
async def launchtoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("🪙 Usage: `/launchtoken NAME SYMBOL`", parse_mode="Markdown")
        return
    name, symbol = args[0], args[1].upper()
    if symbol in launched_tokens:
        await update.message.reply_text(f"❌ Token `{symbol}` already exists.", parse_mode="Markdown")
        return
    launched_tokens[symbol] = {
        "name": name,
        "symbol": symbol,
        "price": 0.0001,
        "volume": 0,
        "supply": 1_000_000_000,
        "decimals": 9,
        "creator": user.username or user.first_name,
        "launch_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    await update.message.reply_text(
        f"🪙 *Token Launched: {name} ({symbol})*\n💰 Price: $0.0001\n📦 Supply: 1B\n🔢 Decimals: 9",
        parse_mode="Markdown"
    )

# 💸 Buy Token
async def buytoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("💸 Usage: `/buytoken SYMBOL AMOUNT`", parse_mode="Markdown")
        return
    symbol = args[0].upper()
    try:
        amount = int(args[1])
    except:
        await update.message.reply_text("❌ Amount must be a number.", parse_mode="Markdown")
        return
    token = launched_tokens.get(symbol)
    if not token:
        await update.message.reply_text(f"❌ Token `{symbol}` not found.", parse_mode="Markdown")
        return
    token["volume"] += amount
    token["price"] += 0.000001 * amount
    await update.message.reply_text(
        f"✅ Bought {amount} of *{symbol}*\n💰 New Price: ${token['price']:.6f}\n📊 Volume: {token['volume']:,}",
        parse_mode="Markdown"
    )

# 🧠 Gatekeeper Report
async def gatekeeper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("🧠 Usage: `/gatekeeper SYMBOL`", parse_mode="Markdown")
        return
    symbol = args[0].upper()
    token = launched_tokens.get(symbol)
    if not token:
        await update.message.reply_text(f"❌ Token `{symbol}` not found.", parse_mode="Markdown")
        return
    score = random.randint(0, 100)
    risk = "🟢 Safe" if score > 80 else "🟡 Moderate" if score > 50 else "🔴 Risky"
    await update.message.reply_text(
        f"*🧠 Gatekeeper Report: {symbol}*\n💰 Price: ${token['price']:.6f}\n📦 Supply: {token['supply']:,}\n🧪 Risk Score: {score}/100\n⚠️ {risk}",
        parse_mode="Markdown"
    )

# 📝 Notes
async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    note_text = ' '.join(context.args)
    if not note_text:
        await update.message.reply_text("📝 Usage: `/note Buy DOGS at dip`", parse_mode="Markdown")
        return
    user_notes.setdefault(user_id, []).append(note_text)
    await update.message.reply_text(f"✅ Note saved! You now have {len(user_notes[user_id])} notes.")

async def memepad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    notes = user_notes.get(user_id, [])
    if not notes:
        await update.message.reply_text("📭 Your Memepad is empty.", parse_mode="Markdown")
        return
    message = "*🧠 Your Memepad:*\n\n" + '\n'.join([f"{i+1}. {note}" for i, note in enumerate(notes)])
    await update.message.reply_text(message, parse_mode="Markdown")

async def deletenote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        index = int(context.args[0]) - 1
        removed = user_notes[user_id].pop(index)
        await update.message.reply_text(f"🗑️ Removed note: {removed}", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Invalid note number.", parse_mode="Markdown")

# 💼 Subscribe
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    premium_users.add(user_id)
    await update.message.reply_text("🎉 You’re now Premium! Enjoy all features.")

# 📈 Trending
async def trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trending = sorted(launched_tokens.items(), key=lambda x: x[1]["volume"], reverse=True)[:5]
    if not trending:
        await update.message.reply_text("📉 No trending tokens yet.")
        return
    message = "*📈 Trending Tokens:*\n\n"
    for symbol, data in trending:
        message += f"{symbol} – Volume: {data['volume']:,} – Price: ${data['price']:.6f}\n"
    await update.message.reply_text(message, parse_mode="Markdown")

# 🚀 Bot Startup
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("launchtoken", launchtoken))
    app.add_handler(CommandHandler("buytoken", buytoken))
    app.add_handler(CommandHandler("gatekeeper", gatekeeper))
    app.add_handler(CommandHandler("note", note))
    app.add_handler(CommandHandler("memepad", memepad))
    app.add_handler(CommandHandler("deletenote", deletenote))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("trend", trend))
    app.run_polling()

if __name__ == "__main__":
    main()