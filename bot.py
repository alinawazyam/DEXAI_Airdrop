import os, sqlite3, datetime, random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

TOKEN = os.getenv("BOT_TOKEN")   # aap Heroku variables mein daal dena

# ---------- DB ----------
conn = sqlite3.connect("dexai.db", check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                taps INTEGER DEFAULT 0,
                energy INTEGER DEFAULT 1000,
                last_tap TIMESTAMP,
                wallet TEXT,
                invited_by INTEGER,
                tasks TEXT DEFAULT '')""")
conn.commit()

# ---------- /start ----------
def start(update: Update, _):
    uid = update.effective_user.id
    name = update.effective_user.first_name
    ref = update.message.text.split()[1] if len(update.message.text.split())>1 else None
    conn.execute("INSERT OR IGNORE INTO users(id,first_name,invited_by) VALUES(?,?,?)",
                 (uid,name,int(ref) if ref else None))
    conn.commit()
    kb = [[InlineKeyboardButton("🎮 Play Tap Game", callback_data='play')],
          [InlineKeyboardButton("📋 Tasks", callback_data='tasks'),
           InlineKeyboardButton("📊 Stats", callback_data='stats')],
          [InlineKeyboardButton("💼 Wallet", callback_data='wallet')]]
    update.message.reply_text("🎯 Welcome to DEXAI Airdrop!", reply_markup=InlineKeyboardMarkup(kb))

# ---------- Tap Game ----------
def play(update: Update, _):
    uid = update.effective_user.id
    cur = conn.execute("SELECT taps,energy FROM users WHERE id=?",(uid,)).fetchone()
    if cur[1]<=0:
        update.callback_query.answer("⚡ Energy exhausted – wait 24h!", show_alert=True)
        return
    taps,energy = cur[0]+1, cur[1]-1
    conn.execute("UPDATE users SET taps=?,energy=?,last_tap=? WHERE id=?",
                 (taps,energy,datetime.datetime.utcnow(),uid))
    conn.commit()
    update.callback_query.answer(f"💥 +1 DEXAI Point! Energy left: {energy}")

# ---------- Admin Only ----------
def export(update: Update, _):
    if update.effective_user.id != YOUR_ADMIN_ID: return
    rows = conn.execute("SELECT id,taps,wallet FROM users").fetchall()
    csv = "\n".join([f"{r[0]},{r[1]},{r[2]}" for r in rows])
    with open("export.csv","w") as f: f.write(csv)
    update.message.reply_document(open("export.csv","rb"))

# ---------- Handlers ----------
updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CallbackQueryHandler(play, pattern='play'))
# Add other handlers (stats, wallet, tasks) same way
updater.start_polling()
