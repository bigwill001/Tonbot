import requests
from datetime import datetime
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

# 🔐 Your bot token
BOT_TOKEN = "8291559832:AAGqbzjc40KjTgLEs8zpvxTF2lgfZienx-E"

# 🧠 Track returning users
visited_users = set()

# 🌞 Time-based emoji
def get_greeting_emoji():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "🌞"
    elif 12 <= hour < 18:
        return "🌤️"
    else:
        return "🌙"

# 🔒 Trust Score logic
def calculate_trust_score(coin):
    score = 0
    name = coin["name"].lower()
    symbol = coin["symbol"].lower()
    if "not" in name or "not" in symbol:
        score += 20
    if coin.get("market_cap", 0) > 1_000_000:
        score += 20
    if coin.get("total_volume", 0) > 100_000:
        score += 15
    if abs(coin.get("price_change_percentage_24h", 0)) < 20:
        score += 15
    if coin.get("circulating_supply", 0) > 1_000_000:
        score += 10
    if coin.get("fully_diluted_valuation"):
        score += 10
    return min(score, 100)

# 📊 Get memecoin data
def get_memecoin_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "category": "ton-meme-coins",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    return response.json()

# 🚨 Detect pump/dump signals
def check_for_pumps():
    data = get_memecoin_data()
    alerts = []
    for coin in data:
        name = coin["name"]
        symbol = coin["symbol"].upper()
        change = coin.get("price_change_percentage_24h")
        if change is not None:
            if change > 10:
                alerts.append(f"🚀 *{name}* ({symbol}) is pumping! +{round(change, 2)}% in 24h")
            elif change < -10:
                alerts.append(f"💀 *{name}* ({symbol}) is dumping! {round(change, 2)}% in 24h")
    return alerts

# 🔔 Scheduled alert sender
async def send_price_alerts(app):
    alerts = check_for_pumps()
    if alerts:
        message = "*⚠️ Memecoin Alert!*\n\n" + "\n".join(alerts)
        for chat_id in visited_users:
            try:
                await app.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            except Exception as e:
                print(f"Failed to send alert to {chat_id}: {e}")

# 👋 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    emoji = get_greeting_emoji()

    reply_keyboard = [["/topmemes", "/dedust", "/pumpalert", "/newmemes", "/trade"]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)

    inline_keyboard = [
        [InlineKeyboardButton("💼 Open TON Wallet", url="https://t.me/wallet")],
        [InlineKeyboardButton("🔐 Explore TON Space", url="https://ton.org/wallets")],
        [InlineKeyboardButton("💱 Trade Memecoins", url="https://tonbotx.vercel.app")]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)

    visited_users.add(user_id)

    message = f"Hey {user_first_name}! {emoji} I'm your TON bot.\nChoose a command below to get started 👇"
    await update.message.reply_text(message, reply_markup=reply_markup)
    await update.message.reply_text("🔐 Need a wallet or want to trade? Tap below:", reply_markup=inline_markup)

# 🔥 /topmemes command
async def topmemes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "*🔥 Top Memecoins (Sep 2025)*\n\n"
        "🐸 *Notcoin (NOT)*\n"
        "🐶 *DOGS*\n"
        "🔁 *REDO*\n"
        "🧠 *BERT*\n"
        "🧨 *PEPE*\n"
        "💀 *USELESS*\n"
        "🐧 *APC*\n"
        "🐸 *FWOG*\n"
        "📖 *BOME*\n"
        "🐕 *MAXI*\n"
        "💼 *WEPE*\n"
        "🧬 *PEPENODE*\n\n"
        "Tap /dedust to see live prices 📈"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# 📈 /dedust command with trust scores
async def dedust(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = get_memecoin_data()
        message = "*📊 DeDust Memecoin Snapshot:*\n\n"
        for coin in data:
            name = coin["name"]
            symbol = coin["symbol"].upper()
            price = round(coin["current_price"], 6)
            change = round(coin["price_change_percentage_24h"], 2)
            emoji = "📈" if change > 0 else "📉"
            trust = calculate_trust_score(coin)
            message += (
                f"{emoji} *{name}* ({symbol}): `${price}` ({change}%)\n"
                f"🔒 Trust Score: {trust}/100\n\n"
            )

        keyboard = [
            [
                InlineKeyboardButton("📈 View Charts", url="https://dedust.io"),
                InlineKeyboardButton("📖 Coin Info", url="https://tonviewer.com")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error fetching data: {e}")

# 🚨 /pumpalert command
async def pumpalert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alerts = check_for_pumps()
    if alerts:
        message = "\n".join(alerts)
    else:
        message = "😴 No memecoin pumps or dumps detected right now."
    await update.message.reply_text(message, parse_mode="Markdown")

# 🆕 /newmemes command
async def newmemes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url)
        data = response.json()

        meme_keywords = ["meme", "dog", "pepe", "not", "frog", "useless", "redo"]
        new_coins = [coin for coin in data if any(k in coin["name"].lower() for k in meme_keywords)]
        new_coins = new_coins[-10:]

        message = "*🆕 Newly Launched Memecoins:*\n\n"
        for coin in new_coins:
            name = coin["name"]
            symbol = coin["symbol"].upper()
            message += f"🚨 *{name}* ({symbol}) — Just launched!\n"

        message += "\nUse /dedust to check live prices 📈"
        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error fetching new coins: {e}")

# 💱 /trade command
async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "*💱 TonBotX Trading Engine*\n\n"
        "Ready to trade memecoins on TON?\n"
        "Tap the button below to open the trading interface and connect your wallet securely."
    )
    keyboard = [
        [InlineKeyboardButton("🚀 Launch Trading App", url="https://tonbotx.vercel.app")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")

# 🚀 Set up the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("topmemes", topmemes))
app.add_handler(CommandHandler("
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