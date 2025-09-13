import os
import random
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Telegram Bot Token
BOT_TOKEN = "8291559832:AAGqbzjc40KjTgLEs8zpvxTF2lgfZienx-E"

# 🧠 Global Data Stores
launched_tokens = {}
user_notes = {}
premium_users = set()
user_wallets = {}

# 👋 Welcome Message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to TonBotX!\n\nUse /launchtoken to create your meme token.\nUse /connectwallet to link your TON wallet.\nUse /memepad to save notes.\nUse /subscribe to unlock premium features.\nLet’s build something legendary 🚀"
    )

# 🔗 Connect TON Wallet (via TonConnect deep link)
async def connectwallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tonconnect_link = f"https://app.tonkeeper.com/ton-connect?session={user_id}"
    user_wallets[user_id] = tonconnect_link  # Placeholder for real wallet connection
    await update.message.reply_text(
        f"🔗 Connect your TON wallet:\n[Click to connect]({tonconnect_link})",
        parse_mode="Markdown"
    )

# 🪙 Launch Token
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
    contract_address = f"0:{random.randint(10**15, 10**16)}"
    launched_tokens[symbol] = {
        "name": name,
        "symbol": symbol,
        "price": 0.0001,
        "volume": 0,
        "supply": 1_000_000_000,
        "decimals": 9,
        "creator": user.username or user.first_name,
        "launch_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "contract": contract_address
    }
    await update.message.reply_text(
        f"🪙 *Token Launched: {name} ({symbol})*\n💰 Price: $0.0001\n📦 Supply: 1B\n🔢 Decimals: 9\n📜 Contract: `{contract_address}`",
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

# 📝 Save Note
async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    note_text = ' '.join(context.args)
    if not note_text:
        await update.message.reply_text("📝 Usage: `/note Buy DOGS at dip`", parse_mode="Markdown")
        return
    user_notes.setdefault(user_id, []).append(note_text)
    await update.message.reply_text(f"✅ Note saved! You now have {len(user_notes[user_id])} notes.")

# 📒 View Notes
async def memepad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    notes = user_notes.get(user_id, [])
    if not notes:
        await update.message.reply_text("📭 Your Memepad is empty.", parse_mode="Markdown")
        return
    message = "*🧠 Your Memepad:*\n\n" + '\n'.join([f"{i+1}. {note}" for i, note in enumerate(notes)])
    await update.message.reply_text(message, parse_mode="Markdown")

# 🗑️ Delete Note
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

# 📈 Trending Tokens
async def trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trending = sorted(launched_tokens.items(), key=lambda x: x[1]["volume"], reverse=True)[:5]
    if not trending:
        await update.message.reply_text("📉 No trending tokens yet.")
        return
    message = "*📈 Trending Tokens:*\n\n"
    for symbol, data in trending:
        message += f"{symbol} – Volume: {data['volume']:,} – Price: ${data['price']:.6f}\n"
    await update.message.reply_text(message, parse_mode="Markdown")

# 🛒 Buy via DeDust (placeholder)
async def buydedust(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("🛒 Usage: `/buydedust SYMBOL AMOUNT`", parse_mode="Markdown")
        return
    symbol = args[0].upper()
    amount = args[1]
    await update.message.reply_text(
        f"🛒 Buying {amount} of {symbol} via DeDust...\n(Feature coming soon with real trading integration)",
        parse_mode="Markdown"
    )

# 🚨 Pump Alert (placeholder)
async def pumpalert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 Pump alert system is under development.\nSoon you'll get real-time alerts for trending tokens!",
        parse_mode="Markdown"
    )

# 🚀 Bot Startup
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("connectwallet", connectwallet))
    app.add_handler(CommandHandler("launchtoken", launchtoken))
    app.add_handler(CommandHandler("buytoken", buytoken))
    app.add_handler(CommandHandler("gatekeeper", gatekeeper))
    app.add_handler(CommandHandler("note", note))
    app.add_handler(CommandHandler("memepad", memepad))
    app.add_handler(CommandHandler("deletenote