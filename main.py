import io
import asyncio
import logging
import random
import os
import threading
import re
import time
from datetime import datetime
import pytz
from flask import Flask
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from html import escape as escape_html
from telethon import TelegramClient, events, types, Button, errors

# ==========================================
# 🌐 DNS FIX FOR MONGODB
# ==========================================
try:
    import dns.resolver
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8', '1.1.1.1']
except: pass

# ==========================================
# 🌐 FLASK KEEP-ALIVE SYSTEM
# ==========================================
app = Flask('')
@app.route('/')
def home(): return "Sovereign Movie Catcher Core is Online!"

def run_flask(): 
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.ERROR)

# ==========================================
# ⚙️ SYSTEM CONFIGURATIONS & CREDENTIALS
# ==========================================
OWNER_ID = 6015356597
OWNER_USERNAME = "Hello_Im_DexterMorgan"
MONGO_URI = "mongodb+srv://khantphyoemin537_db_user:9VRKiaeZkz7rJdpz@cluster0.w6tgi8j.mongodb.net/?appName=Cluster0&tlsAllowInvalidCertificates=true"
APP_ID = 35766004
APP_HASH = 'd15b4226b81724722279bae6af69e22d'
MAIN_BOT_TOKEN = "8575371720:AAEWWV42CGrwooM_joiJXdo2iEw2_7atyXU"

# 🔒 Target Configurations
SPECIFIC_CONTROL_GROUP = -1003940667453 
TZ = pytz.timezone('Asia/Yangon')

# ==========================================
# 🗄️ DATABASE CONNECTION MATRIX
# ==========================================
client_mongo = AsyncIOMotorClient(MONGO_URI)
db = client_mongo["telegram_bot"]

characters_base_col = db["characters_base_data"]  
users_catcher_col = db["users_catcher_data"]      
groups_counters_col = db["groups_msg_counters"]    
groups_config_col = db["groups_catcher_config"]   

# ==========================================
# 🤖 BOT CLIENT INITIALIZATION
# ==========================================
bot1 = TelegramClient('bot_main_session', APP_ID, APP_HASH)
active_group_spawns = {} 

# ==========================================
# 📥 1. DATABASE RECRUITER (/addchar)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/addchar\s+(.*)$'))
async def add_character_handler(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    
    if chat_id != SPECIFIC_CONTROL_GROUP: return 
    if user_id != OWNER_ID: return
        
    if not event.is_reply:
        return await event.reply("⚠️ <b>Matrix Error:</b> Please reply to a photo or video to use this command, Chief!")
        
    reply_msg = await event.get_reply_message()
    if not reply_msg.photo and not reply_msg.video and not reply_msg.document:
        return await event.reply("❌ <b>Media Missing:</b> Unsupported format. Only photos and video clips are allowed.")
        
    try:
        input_text = event.pattern_match.group(1)
        parts = [p.strip() for p in input_text.split('|')]
        
        if len(parts) < 3:
            return await event.reply("❌ <b>Invalid Format:</b> Use <code>/addchar Name | Rarity | Value</code>", parse_mode='html')
            
        char_name = parts[0]
        rarity = parts[1].upper()
        currency_value = int(parts[2])
        
        storage_msg_id = reply_msg.id
        char_id = random.randint(10000, 99999)
        media_type = "🎬 VIDEO" if reply_msg.video or (reply_msg.document and reply_msg.document.mime_type.startswith('video/')) else "🖼️ PHOTO"
        
        await characters_base_col.insert_one({
            "char_id": char_id,
            "name": char_name,
            "storage_msg_id": storage_msg_id,
            "rarity": rarity,
            "currency_value": currency_value,
            "media_type": media_type
        })
        
        success_msg = (
            f"🛡️ <b>STAR DATABASE SYNCHRONIZED</b>\n"
            f"────────────────────────\n"
            f"🆔 <b>Star ID:</b> <code>{char_id}</code>\n"
            f"🎬 <b>Identity:</b> <code>{escape_html(char_name)}</code>\n"
            f"👑 <b>Tier:</b> <code>[{rarity}]</code>\n"
            f"💰 <b>Value:</b> <code>{currency_value} PTS</code>\n"
            f"🎞️ <b>Format:</b> <code>{media_type}</code>\n"
            f"────────────────────────"
        )
        await event.reply(success_msg, parse_mode='html')
        
    except Exception as e:
        await event.reply(f"❌ System Crash: {e}")

# ==========================================
# 📢 2. EQUAL CHANCE AUTOMATIC SPAWN ENGINE
# ==========================================
@bot1.on(events.NewMessage(incoming=True))
async def global_message_counter_handler(event):
    if event.is_private: return
    chat_id = event.chat_id
    if chat_id == SPECIFIC_CONTROL_GROUP: return
    
    group_config = await groups_config_col.find_one({"chat_id": chat_id})
    spawn_target = group_config.get("spawn_target", 100) if group_config else 100
    
    group_counter_doc = await groups_counters_col.find_one_and_update(
        {"chat_id": chat_id}, {"$inc": {"counter": 1}}, upsert=True, return_document=ReturnDocument.AFTER
    )
    
    if group_counter_doc["counter"] >= spawn_target:
        characters_list = await characters_base_col.find().to_list(length=None)
        if not characters_list: return 
        
        chosen_char = random.choice(characters_list)
        
        try:
            storage_msg = await bot1.get_messages(SPECIFIC_CONTROL_GROUP, ids=chosen_char["storage_msg_id"])
            if not storage_msg or not storage_msg.media: return
        except: return
            
        active_group_spawns[chat_id] = {
            "char_id": chosen_char["char_id"],
            "name": chosen_char["name"],
            "value": chosen_char["currency_value"],
            "rarity": chosen_char["rarity"],
            "spawn_time": time.time(),
            "claimed": False
        }
        
        spawn_text = (
            f"🎬 <b>CINEMATIC ICON SPOTTED!</b>\n"
            f"────────────────────────\n"
            f"A legendary star has arrived on the stage!\n"
            f"Claim them before they disappear into the shadows.\n\n"
            f"👉 <code>/catch {escape_html(chosen_char['name'])}</code>\n"
            f"────────────────────────\n"
            f"👑 <b>Rarity Tier:</b> <code>[{chosen_char['rarity']}]</code>\n"
            f"⏳ <b>Time Window:</b> <code>60 Seconds</code>\n"
            f"────────────────────────"
        )
        
        await bot1.send_message(chat_id, spawn_text, parse_mode='html', file=storage_msg.media)
        await groups_counters_col.update_one({"chat_id": chat_id}, {"$set": {"counter": 0}})

# ==========================================
# 🎯 3. SECURE CLAIM ENGINE (/catch)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/catch\s+(.*)$'))
async def catch_handler(event):
    if event.is_private: return
    chat_id = event.chat_id
    user_id = event.sender_id
    catch_name = event.pattern_match.group(1).strip().lower()
    
    if chat_id not in active_group_spawns:
        return await event.reply("🛸 <b>Scan Failed:</b> No active star detected in this sector.")
        
    spawn_data = active_group_spawns[chat_id]
    
    if time.time() - spawn_data["spawn_time"] > 60:
        del active_group_spawns[chat_id]
        return await event.reply("⏱️ <b>Timeout:</b> The star has left the red carpet.")
        
    if spawn_data["claimed"]:
        return await event.reply("❌ <b>Intercepted:</b> Another Hunter has already claimed this star.")
        
    if catch_name != spawn_data["name"].lower():
        return await event.reply("❌ <b>Identity Mismatch:</b> Incorrect spelling or name.")
        
    active_group_spawns[chat_id]["claimed"] = True 
    
    sender = await event.get_sender()
    fullname = f"@{sender.username}" if sender and getattr(sender, 'username', None) else (getattr(sender, 'first_name', None) or "Hunter")
    mention = f"<a href='tg://user?id={user_id}'>{escape_html(fullname)}</a>"
    
    await users_catcher_col.update_one(
        {"user_id": user_id},
        {"$push": {"harem": {"char_id": spawn_data["char_id"], "caught_date": time.time(), "rarity": spawn_data["rarity"]}},
         "$inc": {"total_caught": 1, "wallet_balance": spawn_data["value"]},
         "$set": {"fullname": mention}},
        upsert=True
    )
    
    del active_group_spawns[chat_id]
    
    success_text = (
        f"🎯 <b>CAPTURE SUCCESSFUL</b>\n"
        f"────────────────────────\n"
        f"👑 {mention} has successfully added a new star!\n\n"
        f"🎬 <b>Identity:</b> <code>{escape_html(spawn_data['name'])}</code>\n"
        f"📈 <b>Credited:</b> <code>+{spawn_data['value']} PTS</code>\n"
        f"────────────────────────"
    )
    await bot1.send_message(chat_id, success_text, parse_mode='html')

# ==========================================
# ⛩️ 4. EXCLUSIVE COLLECTION SYSTEM (/hai)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/hai(?:@\w+)?$'))
async def hai_initial_handler(event):
    if event.is_private: return
    chat_id = event.chat_id
    user_id = event.sender_id
    
    user_doc = await users_catcher_col.find_one({"user_id": user_id})
    if not user_doc or not user_doc.get("harem"):
        return await event.reply("🎒 <b>Inventory Empty:</b> You haven't captured any stars yet! Use /catch when they appear.")
        
    harem_list = user_doc["harem"]
    total_chars = len(harem_list)
    harem_list.reverse() 
    
    current_index = 0
    target_char = harem_list[current_index]
    char_base = await characters_base_col.find_one({"char_id": target_char["char_id"]})
    if not char_base: return
    
    try:
        storage_msg = await bot1.get_messages(SPECIFIC_CONTROL_GROUP, ids=char_base["storage_msg_id"])
        media_file = storage_msg.media if storage_msg else None
    except: media_file = None
        
    fullname = user_doc.get("fullname", f"User {user_id}")
    hai_text = (
        f"⬢ {fullname}'s <b>SHOWREEL VAULT</b>\n\n"
        f"🎬 <b>Sovereign Cinema Matrix ({current_index + 1}/{total_chars})</b>\n"
        f"────────────────────────\n"
        f"✨ <b>Name:</b> <code>{escape_html(char_base['name'])}</code> (x1)\n"
        f"👑 <b>Tier:</b> <code>[{char_base['rarity']}]</code>\n"
        f"💎 <b>Asset Value:</b> <code>{char_base['currency_value']} PTS</code>\n"
        f"────────────────────────"
    )
    
    buttons = [
        [Button.inline("◀️ Previous", data=f"hai_prev_{current_index}"), Button.inline("Next ▶️", data=f"hai_next_{current_index}")],
        [Button.switch_inline(f"⛩️ FULL CATALOGUE ({total_chars}) ⛩️", query=f"hai.{user_id}", same_peer=True)]
    ]
    await bot1.send_message(chat_id, hai_text, parse_mode='html', file=media_file, buttons=buttons)

@bot1.on(events.CallbackQuery(pattern=r'^hai_(next|prev)_(\d+)$'))
async def hai_pagination_callback(event):
    user_id = event.sender_id
    action = event.pattern_match.group(1).decode('utf-8')
    current_index = int(event.pattern_match.group(2).decode('utf-8'))
    
    user_doc = await users_catcher_col.find_one({"user_id": user_id})
    if not user_doc: return await event.answer("❌ Verification Failed: This session does not belong to you.", alert=True)
        
    harem_list = user_doc["harem"]
    harem_list.reverse()
    total_chars = len(harem_list)
    
    if action == "next":
        new_index = current_index + 1
        if new_index >= total_chars: new_index = 0
    else:
        new_index = current_index - 1
        if new_index < 0: new_index = total_chars - 1

    target_char = harem_list[new_index]
    char_base = await characters_base_col.find_one({"char_id": target_char["char_id"]})
    if not char_base: return
    
    try:
        storage_msg = await bot1.get_messages(SPECIFIC_CONTROL_GROUP, ids=char_base["storage_msg_id"])
        media_file = storage_msg.media if storage_msg else None
        
        fullname = user_doc.get("fullname", f"User {user_id}")
        updated_text = (
            f"⬢ {fullname}'s <b>SHOWREEL VAULT</b>\n\n"
            f"🎬 <b>Sovereign Cinema Matrix ({new_index + 1}/{total_chars})</b>\n"
            f"────────────────────────\n"
            f"✨ <b>Name:</b> <code>{escape_html(char_base['name'])}</code> (x1)\n"
            f"👑 <b>Tier:</b> <code>[{char_base['rarity']}]</code>\n"
            f"💎 <b>Asset Value:</b> <code>{char_base['currency_value']} PTS</code>\n"
            f"────────────────────────"
        )
        
        updated_buttons = [
            [Button.inline("◀️ Previous", data=f"hai_prev_{new_index}"), Button.inline("Next ▶️", data=f"hai_next_{new_index}")],
            [Button.switch_inline(f"⛩️ FULL CATALOGUE ({total_chars}) ⛩️", query=f"hai.{user_id}", same_peer=True)]
        ]
        
        await event.edit(updated_text, parse_mode='html', file=media_file, buttons=updated_buttons)
    except Exception:
        await event.delete()
        await bot1.send_message(event.chat_id, updated_text, parse_mode='html', file=media_file, buttons=updated_buttons)
        
    await event.answer()

# ==========================================
# 📊 5. METRICS & CONFIGURATIONS
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/profile(?:@\w+)?$'))
async def user_profile_handler(event):
    user_id = event.sender_id
    sender = await event.get_sender()
    fullname = f"@{sender.username}" if sender and getattr(sender, 'username', None) else (getattr(sender, 'first_name', None) or "User")
    mention = f"<a href='tg://user?id={user_id}'>{escape_html(fullname)}</a>"
    
    user_doc = await users_catcher_col.find_one({"user_id": user_id})
    if not user_doc: return await event.reply("🎒 <b>No Profile Found:</b> Execute /catch first to initialize your account, Chief.")
        
    profile_text = (
        f"🌟 <b>CINEMA HUNTER DOSSIER</b>\n"
        f"────────────────────────\n"
        f"👤 <b>Agent:</b> {mention}\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        f"💰 <b>Net Worth:</b> <code>{user_doc.get('wallet_balance', 0)} PTS</code>\n"
        f"🎒 <b>Total Captured:</b> <code>{user_doc.get('total_caught', 0)} Stars</code>\n"
        f"────────────────────────"
    )
    await event.reply(profile_text, parse_mode='html')

@bot1.on(events.NewMessage(pattern=r'^/gtop(?:@\w+)?$'))
async def global_leaderboard_handler(event):
    global_top = await users_catcher_col.find().sort("wallet_balance", -1).limit(10).to_list(length=10)
    lb = "🌌 <b>Sovereign Movie Supremacy (Top 10)</b>\n────────────────────────\n"
    for i, u in enumerate(global_top, start=1):
        lb += f"{i}. {u['fullname']} — 💰 <code>{u.get('wallet_balance', 0)} PTS</code> | 🎬 Chars: <code>{u.get('total_caught', 0)}</code>\n"
    lb += "────────────────────────"
    await event.reply(lb, parse_mode='html')

@bot1.on(events.NewMessage(pattern=r'^/changetime(?:\s+(\d+))?'))
async def change_spawn_rate_handler(event):
    if event.is_private or event.sender_id != OWNER_ID: return
    target = event.pattern_match.group(1)
    if not target: return await event.reply("⚙️ <b>Usage:</b> <code>/changetime [Message Count]</code>", parse_mode='html')
    await groups_config_col.update_one({"chat_id": event.chat_id}, {"$set": {"spawn_target": int(target)}}, upsert=True)
    await event.reply(f"⚙️ <b>Configuration Updated:</b> Star drop synchronized at <code>{target}</code> messages.", parse_mode='html')

# ==========================================
# ⚡ EXECUTOR INITIALIZER
# ==========================================
if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    print("🛰️ Sovereign Movie-Matrix Connecting...")
    bot1.start(bot_token=MAIN_BOT_TOKEN)
    print("✅ Full Video-Support & Equal Chance Engine Live, Chief Dexter!")
    bot1.run_until_disconnected()
