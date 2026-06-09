import io
import asyncio
import logging
import random
import os
import threading
import re
import time
from datetime import datetime
from flask import Flask
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from html import escape as escape_html
from telethon import TelegramClient, events, types, Button, errors

# ==========================================
# 🌐 FLASK KEEP-ALIVE SYSTEM
# ==========================================
app = Flask('')
@app.route('/')
def home(): return "Sovereign Multi-Universe Catcher Core is Online!"

def run_flask(): 
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.ERROR)

# ==========================================
# ⚙️ SYSTEM CONFIGURATIONS & CREDENTIALS
# ==========================================
OWNER_ID = 6015356597
MONGO_URI = "mongodb+srv://khantphyoemin537_db_user:9VRKiaeZkz7rJdpz@cluster0.w6tgi8j.mongodb.net/?appName=Cluster0&tlsAllowInvalidCertificates=true"
APP_ID = 35766004
APP_HASH = 'd15b4226b81724722279bae6af69e22d'
MAIN_BOT_TOKEN = "8575371720:AAEWWV42CGrwooM_joiJXdo2iEw2_7atyXU"
SPECIFIC_CONTROL_GROUP = -1003940667453 

# ==========================================
# 🗄️ DATABASE CONNECTION MATRIX
# ==========================================
client_mongo = AsyncIOMotorClient(MONGO_URI)
db = client_mongo["telegram_bot"]

characters_base_col = db["characters_base_data"]  
users_catcher_col = db["users_catcher_data"]      
groups_counters_col = db["groups_msg_counters"]    
groups_config_col = db["groups_catcher_config"]   
marketplace_col = db["marketplace_data"]          

bot1 = TelegramClient('bot_main_session', APP_ID, APP_HASH)
active_group_spawns = {} 

# ==========================================
# 🎭 RARITY MAPPING MATRIX (1-6 NUMERICAL INDEX)
# ==========================================
RARITY_NUM_MAP = {
    "1": {"name": "👑 LEGENDARY", "value": 500},
    "2": {"name": "⏳ LIMITED-EDITION", "value": 450},
    "3": {"name": "🔮 MYTHIC", "value": 400},
    "4": {"name": "🔥 EPIC", "value": 300},
    "5": {"name": "✨ RARE", "value": 200},
    "6": {"name": "♻️ COMMON", "value": 100}
}

# ==========================================
# 📥 1. PERMANENT DATABASE ADDER WITH NUMERIC RARITY
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/addchar(?:\s+(.+))?'))
async def add_character(event):
    if event.sender_id != OWNER_ID: return

    input_text = event.pattern_match.group(1)
    if not input_text or '|' not in input_text:
        await event.reply(
            "⚠️ <b>FORMAT ERROR / အသုံးပြုပုံမှားယွင်းနေပါသည်!</b>\n"
            "────────────────────────\n"
            "📝 <b>Usage / အသုံးပြုနည်း:</b>\n"
            "<code>/addchar Name | Category | Rarity_Number</code>\n"
            "<i>(Reply to a Photo/Video/Document)</i>\n\n"
            "🔢 <b>Rarity Tiers Matrix (1-6):</b>\n"
            "<code>1</code> = 👑 LEGENDARY (500 PTS)\n"
            "<code>2</code> = ⏳ LIMITED-EDITION (450 PTS)\n"
            "<code>3</code> = 🔮 MYTHIC (400 PTS)\n"
            "<code>4</code> = 🔥 EPIC (300 PTS)\n"
            "<code>5</code> = ✨ RARE (200 PTS)\n"
            "<code>6</code> = ♻️ COMMON (100 PTS)\n"
            "────────────────────────\n"
            "💡 <b>Example:</b> <code>/addchar Dexter Morgan | Series | 1</code>",
            parse_mode='html'
        )
        return

    parts = [p.strip() for p in input_text.split('|')]
    if len(parts) < 3: 
        return await event.reply("⚠️ <b>Missing parameters! Requires 3 segments split by '|'</b>", parse_mode='html')

    char_name, category_name, rarity_num = parts[0], parts[1], parts[2]
    
    if rarity_num not in RARITY_NUM_MAP:
        return await event.reply("❌ <b>Invalid Rarity Index! Choose between 1 to 6 only.</b>", parse_mode='html')

    if not event.is_reply: 
        return await event.reply("❌ <b>Please reply to a valid Media File (Photo/Video/Doc).</b>", parse_mode='html')

    reply_msg = await event.get_reply_message()
    if not reply_msg or not (reply_msg.photo or reply_msg.video or reply_msg.document):
        return await event.reply("❌ <b>No valid media matrix detected in the replied message.</b>", parse_mode='html')

    try:
        # Static Storage Group ဆီသို့ လှမ်းတင်သိမ်းဆည်းခြင်း
        forwarded_msg = await bot1.send_message(SPECIFIC_CONTROL_GROUP, file=reply_msg.media)
        storage_id = forwarded_msg.id
        
        r_info = RARITY_NUM_MAP[rarity_num]
        
        # Unique ID Generator
        while True:
            char_id = f"CH{random.randint(10000, 99999)}"
            exists = await characters_base_col.find_one({"char_id": char_id})
            if not exists: break

        character_data = {
            "char_id": char_id,
            "name": char_name,
            "category": category_name,
            "rarity": r_info["name"],
            "storage_msg_id": storage_id,
            "currency_value": r_info["value"]
        }

        await characters_base_col.insert_one(character_data)
        
        success_msg = (
            f"✅ <b>SOVEREIGN UNIVERSE UPDATED / စနစ်တွင်းသို့ ထည့်သွင်းပြီးပါပြီ</b>\n"
            f"────────────────────────\n"
            f"🆔 <b>Person ID:</b> <code>{char_id}</code>\n"
            f"👤 <b>Name:</b> <code>{char_name}</code>\n"
            f"🌐 <b>Category:</b> <code>{category_name}</code>\n"
            f"🌟 <b>Rarity Class:</b> {r_info['name']}\n"
            f"💎 <b>Value Reward:</b> <code>{r_info['value']} PTS</code>\n"
            f"────────────────────────\n"
            f"<blockquote><b>EN:</b> Person profile successfully integrated via Storage ID {storage_id}.\n"
            f"<b>MM:</b> အချက်အလက်များအား ဗဟိုသိမ်းဆည်းမှု ကွန်ရက်ထဲသို့ အောင်မြင်စွာ ချိတ်ဆက်ပြီးပါပြီ။</blockquote>"
        )
        await event.reply(success_msg, parse_mode='html')

    except Exception as e:
        await event.reply(f"❌ <b>Database Inject Error:</b> <code>{escape_html(str(e))}</code>", parse_mode='html')

# ==========================================
# 🛰️ 2. OVERRIDE FORCE SPAWN ENGINE (/Haii)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/[Hh]aii$'))
async def force_spawn_by_owner(event):
    if event.sender_id != OWNER_ID: return
    await trigger_dynamic_spawn(event.chat_id)

# ==========================================
# 📢 3. EQUAL CHANCE AUTOMATIC SPAWN PROCESSOR
# ==========================================
@bot1.on(events.NewMessage(incoming=True))
async def global_message_counter_handler(event):
    if event.is_private or event.chat_id == SPECIFIC_CONTROL_GROUP: return
    
    chat_id = event.chat_id
    group_config = await groups_config_col.find_one({"chat_id": chat_id})
    spawn_target = group_config.get("spawn_target", 50) if group_config else 50
    
    counter_doc = await groups_counters_col.find_one_and_update(
        {"chat_id": chat_id}, {"$inc": {"counter": 1}}, upsert=True, return_document=ReturnDocument.AFTER
    )
    
    if counter_doc["counter"] >= spawn_target:
        await groups_counters_col.update_one({"chat_id": chat_id}, {"$set": {"counter": 0}})
        await trigger_dynamic_spawn(chat_id)

async def trigger_dynamic_spawn(chat_id):
    try:
        characters_list = await characters_base_col.find().to_list(length=None)
        if not characters_list: return
        
        chosen_char = random.choice(characters_list)
        storage_msg = await bot1.get_messages(SPECIFIC_CONTROL_GROUP, ids=chosen_char["storage_msg_id"])
        if not storage_msg or not storage_msg.media: return
        
        spawn_msg = await bot1.send_message(
            chat_id, 
            f"✨ <b>⚠️ MYSTERIOUS PERSON DETECTED / အမည်မသိ ပုဂ္ဂိုလ်တစ်ဦး ပေါ်ထွက်လာသည်! ⚠️</b>\n"
            f"────────────────────────\n"
            f"<blockquote><b>EN:</b> Who is this mysterious individual? Reply to this message with <code>/who</code> to inspect database clues!\n\n"
            f"<b>MM:</b> ဤပုဂ္ဂိုလ်သည် မည်သူမည်ဝါ ဖြစ်နိုင်မည်နည်း? သဲလွန်စအချက်အလက်များကို ရယူရန် ဤပိုစ့်အား <code>/who</code> ဖြင့် Reply ပြန်၍ စစ်ဆေးပါ။</blockquote>\n"
            f"────────────────────────",
            parse_mode='html',
            file=storage_msg.media
        )
        
        active_group_spawns[chat_id] = {
            "spawn_msg_id": spawn_msg.id,
            "char_id": chosen_char["char_id"],
            "name": chosen_char["name"],
            "category": chosen_char["category"],
            "value": chosen_char["currency_value"],
            "rarity": chosen_char["rarity"],
            "spawn_time": time.time(),
            "revealed": False,
            "claimed": False
        }
    except Exception as e:
        print(f"Spawn Error Tracker: {e}")

# ==========================================
# 💡 4. IDENTITY REVEAL ENGINE (/who)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/who$'))
async def who_reveal_handler(event):
    if event.is_private: return
    chat_id = event.chat_id
    
    if chat_id not in active_group_spawns:
        return await event.reply(
            "❌ <b>NO ACTIVE TARGET / ဤကဏ္ဍတွင် လက်ရှိ တက်ကြွနေသော ပုဂ္ဂိုလ်မရှိပါ!</b>", parse_mode='html'
        )
        
    spawn_data = active_group_spawns[chat_id]
    if not event.is_reply or event.reply_to_msg_id != spawn_data["spawn_msg_id"]:
        return await event.reply(
            "⚠️ <b>INSIGNIFICANT TARGET / ပေါ်လာသော ပိုစ့်အား တိုက်ရိုက် Reply ပြန်ပေးရန် လိုအပ်ပါသည်။</b>", parse_mode='html'
        )
        
    reveal_text = (
        f"🎯 <b>PERSON TARGET SCAN COMPLETED / သဲလွန်စ ရှာဖွေတွေ့ရှိမှု</b>\n"
        f"────────────────────────\n"
        f"🌐 <b>Universe Domain:</b> <code>{spawn_data['category']}</code>\n"
        f"🌟 <b>Rarity Class:</b> {spawn_data['rarity']}\n\n"
        f"⚡ <b>CAPTURE PAYLOAD / ဖမ်းယူရန် လှှို့ဝှက်ကုဒ်:</b>\n"
        f"<code>/catch {spawn_data['name']}</code>\n"
        f"────────────────────────\n"
        f"<blockquote><b>EN:</b> Execute the payload swiftly above to secure the claim!\n"
        f"<b>MM:</b> ပိုင်ဆိုင်ခွင့် ရရှိနိုင်ရန် အထက်ပါကုဒ်အား အမြန်ဆုံး ကူးယူရိုက်နှိပ်ပါ။</blockquote>"
    )
    await event.reply(reveal_text, parse_mode='html')

# ==========================================
# 🎯 5. CLAIM ENGINE CORE (/catch)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/catch\s+(.*)$'))
async def catch_handler(event):
    if event.is_private: return
    chat_id = event.chat_id
    user_id = event.sender_id
    catch_name = event.pattern_match.group(1).strip().lower()
    
    if chat_id not in active_group_spawns:
        return await event.reply("🛸 <b>No active entity detected in this sector dimension.</b>", parse_mode='html')
        
    spawn_data = active_group_spawns[chat_id]
    
    if time.time() - spawn_data["spawn_time"] > 60:
        del active_group_spawns[chat_id]
        return await event.reply(
            "⏱️ <b>TARGET ESCAPED / သတ်မှတ်ချိန် ကျော်လွန်သဖြင့် ထွက်ခွာသွားပါပြီ။</b>", parse_mode='html'
        )
        
    if spawn_data["claimed"]: return
    if catch_name != spawn_data["name"].lower(): return
        
    active_group_spawns[chat_id]["claimed"] = True 
    sender = await event.get_sender()
    fullname = f"@{sender.username}" if sender and getattr(sender, 'username', None) else (getattr(sender, 'first_name', None) or "Hunter")
    mention = f"<a href='tg://user?id={user_id}'>{escape_html(fullname)}</a>"
    
    await users_catcher_col.update_one(
        {"user_id": user_id},
        {"$inc": {f"harem.{spawn_data['char_id']}": 1, "total_caught": 1, "wallet_balance": spawn_data["value"]},
         "$set": {"fullname": mention}},
        upsert=True
    )
    
    del active_group_spawns[chat_id]
    
    success_text = (
        f"🎯 <b>CAPTURE CONCLUDED / ဖမ်းယူမှု အောင်မြင်ခြင်း</b>\n"
        f"────────────────────────\n"
        f"👑 {mention}\n"
        f"<blockquote><b>EN:</b> Has successfully synchronized and captured this person!\n"
        f"<b>MM:</b> မှ ဤပုဂ္ဂိုလ်အား အောင်မြင်စွာ ဖမ်းယူသိမ်းပိုက် သွားနိုင်ခဲ့ပါပြီ။</blockquote>\n"
        f"👤 <b>Identity/Name:</b> <code>{escape_html(spawn_data['name'])}</code>\n"
        f"🆔 <b>Person ID:</b> <code>{spawn_data['char_id']}</code>\n"
        f"💰 <b>Asset Bonus:</b> <code>+{spawn_data['value']} PTS</code>\n"
        f"────────────────────────"
    )
    await bot1.send_message(chat_id, success_text, parse_mode='html')

# ==========================================
# 🗂️ 6. STACKED COLLECTION MATRIX WITH RARITY FILTER (/hai & /haimode)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/hai(?:@\w+)?$'))
async def hai_initial_handler(event):
    if event.is_private: return
    await render_harem_matrix(event.chat_id, event.sender_id, filter_rarity=None, current_index=0, target_msg=None)

@bot1.on(events.NewMessage(pattern=r'^/haimode(?:@\w+)?$'))
async def haimode_filter_panel(event):
    if event.is_private: return
    buttons = [
        [Button.inline("👑 LEGEND", data=f"filter_legend_0"), Button.inline("⏳ LIMITED", data=f"filter_limit_0")],
        [Button.inline("🔮 MYTHIC", data=f"filter_mythic_0"), Button.inline("🔥 EPIC", data=f"filter_epic_0")],
        [Button.inline("✨ RARE", data=f"filter_rare_0"), Button.inline("♻️ ALL ITEMS", data=f"filter_all_0")]
    ]
    await event.reply(
        f"🎭 <b>VAULT FILTER REGISTRY / စစ်ထုတ်မှု ပန်နယ်</b>\n"
        f"────────────────────────\n"
        f"<blockquote><b>EN:</b> Select the specific rarity classification you wish to view, Chief.\n\n"
        f"<b>MM:</b> သင့်ပြခန်းထဲမှ မည်သည့် Rarity အမျိုးအစားကို သီးသန့် စစ်ထုတ်ကြည့်ရှုလိုပါသလဲ Chief?</blockquote>", 
        buttons=buttons, 
        parse_mode='html'
    )

async def render_harem_matrix(chat_id, user_id, filter_rarity, current_index, target_msg=None):
    user_doc = await users_catcher_col.find_one({"user_id": user_id})
    if not user_doc or not user_doc.get("harem"):
        msg = "🎒 <b>VAULT IS EMPTY / သင့်ထံတွင် မည်သည့်ပိုင်ဆိုင်မှုမှ မရှိသေးပါ!</b>\n<blockquote>/catch ဖြင့် အရင်ဆုံး ဖမ်းယူစုဆောင်းပါ။</blockquote>"
        if target_msg: await target_msg.edit(msg, parse_mode='html')
        else: await bot1.send_message(chat_id, msg, parse_mode='html')
        return

    raw_harem = user_doc["harem"] 
    owned_ids = [k for k, v in raw_harem.items() if v > 0]
    
    if not owned_ids:
        return await bot1.send_message(chat_id, "🎒 <b>Vault Matrix returns 0 owned assets.</b>", parse_mode='html')

    db_chars = await characters_base_col.find({"char_id": {"$in": owned_ids}}).to_list(length=None)
    
    if filter_rarity:
        db_chars = [c for c in db_chars if filter_rarity.lower() in c["rarity"].lower()]

    total_chars = len(db_chars)
    if total_chars == 0:
        msg = "❌ <b>NO ASSETS FOUND / ဤ Tier တွင် သင့်ထံ၌ စုဆောင်းထားခြင်း မရှိသေးပါ။</b>"
        if target_msg: await target_msg.answer(msg, alert=True)
        else: await bot1.send_message(chat_id, msg, parse_mode='html')
        return

    if current_index >= total_chars: current_index = 0
    elif current_index < 0: current_index = total_chars - 1

    target_char = db_chars[current_index]
    count = raw_harem.get(target_char["char_id"], 1)
    
    try:
        storage_msg = await bot1.get_messages(SPECIFIC_CONTROL_GROUP, ids=target_char["storage_msg_id"])
        media_file = storage_msg.media if storage_msg else None
    except: media_file = None

    fullname = user_doc.get("fullname", f"Agent {user_id}")
    filter_label = filter_rarity.upper() if filter_rarity else "GLOBAL ALL"
    
    view_text = (
        f"⬢ {fullname}'s <b>SHOWREEL VAULT</b>\n"
        f"⚙️ Grid Filter: <code>[{filter_label}]</code> — Index ({current_index + 1}/{total_chars})\n"
        f"────────────────────────\n"
        f"👤 <b>Name/Identity:</b> <code>{escape_html(target_char['name'])}</code> <b>(x{count})</b>\n"
        f"🆔 <b>Person ID:</b> <code>{target_char['char_id']}</code>\n"
        f"🌐 <b>Domain Category:</b> <code>{target_char['category']}</code>\n"
        f"🌟 <b>Rarity Class:</b> {target_char['rarity']}\n"
        f"💎 <b>Power Multiplier:</b> <code>{target_char['currency_value']} PTS</code>\n"
        f"────────────────────────\n"
        f"<blockquote><b>EN:</b> Switch via the matrix directional buttons below.\n"
        f"<b>MM:</b> အခြားပိုင်ဆိုင်မှုများကို အောက်ပါ လမ်းညွှန်ခလုတ်များဖြင့် ရွှေ့ပြောင်းကြည့်ရှုပါ။</blockquote>"
    )

    f_key = filter_rarity if filter_rarity else "all"
    buttons = [
        [Button.inline("◀️ Previous Matrix", data=f"nav_prev_{f_key}_{current_index}"), 
         Button.inline("Next Matrix ▶️", data=f"nav_next_{f_key}_{current_index}")],
        [Button.switch_inline("⛩️ INLINE SHOWCASE ⛩️", query=f"hai.{user_id}", same_peer=True)]
    ]

    if target_msg:
        try:
            await target_msg.edit(view_text, parse_mode='html', file=media_file, buttons=buttons)
        except Exception:
            await target_msg.delete()
            await bot1.send_message(chat_id, view_text, parse_mode='html', file=media_file, buttons=buttons)
    else:
        await bot1.send_message(chat_id, view_text, parse_mode='html', file=media_file, buttons=buttons)

@bot1.on(events.CallbackQuery(pattern=r'^(filter|nav)_(.*)$'))
async def handle_matrix_callbacks(event):
    data_parts = event.data.decode('utf-8').split('_')
    user_id = event.sender_id
    
    if data_parts[0] == "filter":
        r_type = data_parts[1]
        filter_key = None if r_type == "all" else r_type
        await event.delete()
        await render_harem_matrix(event.chat_id, user_id, filter_key, 0, target_msg=None)
        
    elif data_parts[0] == "nav":
        action = data_parts[1]
        f_key = data_parts[2]
        c_idx = int(data_parts[3])
        filter_key = None if f_key == "all" else f_key
        
        new_idx = c_idx + 1 if action == "next" else c_idx - 1
        await render_harem_matrix(event.chat_id, user_id, filter_key, new_idx, target_msg=event)
    await event.answer()

# ==========================================
# 🔍 7. SPECIFIC CHARACTER CHECK (/check)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/check\s+(.+)$'))
async def check_character_id_handler(event):
    char_id = event.pattern_match.group(1).strip().upper()
    character = await characters_base_col.find_one({"char_id": char_id})
    
    if not character:
        return await event.reply("❌ <b>DATABASE MISMATCH / မှန်ကန်သော Person ID ကို ရိုက်ထည့်ပါ။ (e.g., CH12345)</b>", parse_mode='html')
        
    try:
        storage_msg = await bot1.get_messages(SPECIFIC_CONTROL_GROUP, ids=character["storage_msg_id"])
        media_file = storage_msg.media if storage_msg else None
    except: media_file = None
        
    info_text = (
        f"🔍 <b>DATABASE PROFILE ARCHIVE / အချက်အလက် စစ်ဆေးမှု</b>\n"
        f"────────────────────────\n"
        f"🆔 <b>Person ID:</b> <code>{character['char_id']}</code>\n"
        f"👤 <b>Identity Name:</b> <code>{character['name']}</code>\n"
        f"🌐 <b>Domain Category:</b> <code>{character['category']}</code>\n"
        f"🌟 <b>Rarity Class:</b> {character['rarity']}\n"
        f"💎 <b>Central Value:</b> <code>{character['currency_value']} PTS</code>\n"
        f"────────────────────────\n"
        f"<blockquote><b>EN:</b> Query successful against quantum matrix archives.\n"
        f"<b>MM:</b> ဗဟိုအချက်အလက်သိုလှောင်ရုံမှ ဒေတာစစ်ဆေးမှု ပြီးမြောက် အောင်မြင်ပါသည်။</blockquote>"
    )
    await event.reply(info_text, parse_mode='html', file=media_file)

# ==========================================
# 💰 8. WALLET BALANCE CHECKER (/checkp)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/checkp(?:@\w+)?$'))
async def check_points_balance(event):
    user_doc = await users_catcher_col.find_one({"user_id": event.sender_id})
    balance = user_doc.get("wallet_balance", 0) if user_doc else 0
    await event.reply(
        f"💳 <b>SOVEREIGN WALLET MATRIX / ရမှတ်လက်ကျန်</b>\n"
        f"────────────────────────\n"
        f"💰 <b>Central Value / လက်ရှိရမှတ်ဗဟိုတန်ဖိုး:</b>\n"
        f"<blockquote><code>{balance} PTS</code></blockquote>\n"
        f"────────────────────────", 
        parse_mode='html'
    )

# ==========================================
# 🎁 9. PEER-TO-PEER ASSET TRANSFER (/gift)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/gift\s+(.+)$'))
async def gift_asset_handler(event):
    if not event.is_reply: 
        return await event.reply("❌ <b>INCOMPLETE TARGET / လက်ဆောင်ပေးလိုသူ၏ မက်ဆေ့ခ်ျအား Reply ပြန်၍ ရိုက်ပါ။</b>", parse_mode='html')
        
    char_id = event.pattern_match.group(1).strip().upper()
    sender_id = event.sender_id
    reply_msg = await event.get_reply_message()
    receiver_id = reply_msg.sender_id
    
    if sender_id == receiver_id: 
        return await event.reply("❌ <b>LOOP ERROR / မိမိကိုယ်ကို ပြန်လည် Gift ပေး၍ မရနိုင်ပါ။</b>", parse_mode='html')

    sender_doc = await users_catcher_col.find_one({"user_id": sender_id})
    if not sender_doc or sender_doc.get("harem", {}).get(char_id, 0) <= 0:
        return await event.reply("❌ <b>TRANSACTION REFUSED / သင့်ထံတွင် ၎င်းပိုင်ဆိုင်မှု လုံလောက်စွာ မရှိပါ။</b>", parse_mode='html')

    await users_catcher_col.update_one({"user_id": sender_id}, {"$inc": {f"harem.{char_id}": -1}})
    
    receiver_sender = await reply_msg.get_sender()
    r_fullname = f"@{receiver_sender.username}" if receiver_sender and getattr(receiver_sender, 'username', None) else "Agent Target"
    r_mention = f"<a href='tg://user?id={receiver_id}'>{escape_html(r_fullname)}</a>"

    await users_catcher_col.update_one(
        {"user_id": receiver_id},
        {"$inc": {f"harem.{char_id}": 1, "total_caught": 1}, "$set": {"fullname": r_mention}},
        upsert=True
    )
    await event.reply(
        f"🎁 <b>ASSET TRANSFER SUCCESSFUL / လက်ဆောင်ပေးပို့မှု အောင်မြင်သည်</b>\n"
        f"────────────────────────\n"
        f"<blockquote><b>EN:</b> Person Asset <code>{char_id}</code> has been securely gifted to {r_mention}.\n\n"
        f"<b>MM:</b> ပုဂ္ဂိုလ်ရေးဆိုင်ရာ ကတ် <code>{char_id}</code> အား {r_mention} ထံသို့ အပြီးသတ် လွှဲပြောင်းပေးအပ်ပြီးပါပြီ။</blockquote>\n"
        f"────────────────────────", 
        parse_mode='html'
    )

# ==========================================
# 🛒 10. DECENTRALIZED MARKETPLACE SYSTEM (/sell & /buy)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/sell\s+([a-zA-Z0-9_]+)\s+(\d+)$'))
async def sell_market_handler(event):
    user_id = event.sender_id
    char_id = event.pattern_match.group(1).upper()
    price = int(event.pattern_match.group(2))
    
    if price <= 0: 
        return await event.reply("❌ <b>INVALID PRICING / စျေးနှုန်းသည် အနည်းဆုံး 1 PTS ရှိရပါမည်။</b>", parse_mode='html')
    
    user_doc = await users_catcher_col.find_one({"user_id": user_id})
    if not user_doc or user_doc.get("harem", {}).get(char_id, 0) <= 0:
        return await event.reply("❌ <b>ESCROW REFUSED / သင့်ထံ၌ ရောင်းချရန် ဤပိုင်ဆိုင်မှု မရှိပါ။</b>", parse_mode='html')
        
    char_data = await characters_base_col.find_one({"char_id": char_id})
    if not char_data: return await event.reply("❌ <b>INVALID ID / Person ID မမှန်ကန်ပါ။</b>", parse_mode='html')

    await users_catcher_col.update_one({"user_id": user_id}, {"$inc": {f"harem.{char_id}": -1}})
    
    listing_id = f"L{random.randint(1000, 9999)}"
    await marketplace_col.insert_one({
        "listing_id": listing_id,
        "seller_id": user_id,
        "char_id": char_id,
        "char_name": char_data["name"],
        "price": price,
        "timestamp": time.time()
    })
    
    await event.reply(
        f"⚖️ <b>MARKETPLACE ESCROW LISTED / စျေးကွက်တင်ရောင်းချမှု</b>\n"
        f"────────────────────────\n"
        f"🆔 <b>Listing ID:</b> <code>{listing_id}</code>\n"
        f"🎬 <b>Asset Name:</b> <code>{char_data['name']}</code> ({char_id})\n"
        f"💰 <b>Listed Price:</b> <code>{price} PTS</code>\n"
        f"────────────────────────\n"
        f"<blockquote><b>EN:</b> Other agents can purchase this listing via:\n"
        f"<b>MM:</b> အခြားအေးဂျင့်များ ဝယ်ယူရန် အောက်ပါအတိုင်း ရိုက်နှိပ်ပါ:</blockquote>\n"
        f"👉 <code>/buy {char_id}</code>",
        parse_mode='html'
    )

@bot1.on(events.NewMessage(pattern=r'^/buy\s+(.+)$'))
async def buy_market_handler(event):
    buyer_id = event.sender_id
    char_id = event.pattern_match.group(1).strip().upper()
    
    cheapest_listing = await marketplace_col.find({"char_id": char_id}).sort("price", 1).to_list(length=1)
    if not cheapest_listing: 
        return await event.reply("❌ <b>OUT OF STOCK / ယခုအချိန်တွင် ဤပုဂ္ဂိုလ်အား ရောင်းချသူမရှိသေးပါ။</b>", parse_mode='html')
    
    listing = cheapest_listing[0]
    price = listing["price"]
    seller_id = listing["seller_id"]
    
    if buyer_id == seller_id: 
        return await event.reply("❌ <b>SELF ACQUISITION INVALID / မိမိပြန်တင်ထားသည်ကို ဝယ်ယူ၍မရပါ။</b>", parse_mode='html')
    
    buyer_doc = await users_catcher_col.find_one({"user_id": buyer_id})
    if not buyer_doc or buyer_doc.get("wallet_balance", 0) < price:
        return await event.reply(f"❌ <b>CREDIT DENIED / ဤပစ္စည်းဝယ်ရန် ရမှတ်မလုံလောက်ပါ။ (လိုအပ်ချက်: {price} PTS)</b>", parse_mode='html')
        
    res = await users_catcher_col.update_one(
        {"user_id": buyer_id, "wallet_balance": {"$gte": price}},
        {"$inc": {"wallet_balance": -price, f"harem.{char_id}": 1, "total_caught": 1}}
    )
    if res.modified_count == 0: return await event.reply("❌ <b>TRANSACTION FAILURE / ငွေကြေးလွှဲပြောင်းမှု ပြဿနာဖြစ်ပွားသည်။</b>", parse_mode='html')
    
    await users_catcher_col.update_one({"user_id": seller_id}, {"$inc": {"wallet_balance": price}})
    await marketplace_col.delete_one({"listing_id": listing["listing_id"]})
    
    await event.reply(
        f"🎉 <b>TRANSACTION SECURED / ဝယ်ယူမှု အောင်မြင်သည်</b>\n"
        f"────────────────────────\n"
        f"🛍️ <b>Acquired Asset:</b> <code>{listing['char_name']}</code> ({char_id})\n"
        f"💰 <b>Total Settled:</b> <code>{price} PTS</code>\n"
        f"────────────────────────\n"
        f"<blockquote><b>EN:</b> The asset has been deposited directly into your personal Showroom Vault.\n\n"
        f"<b>MM:</b> စျေးကွက်မှ ပစ္စည်းအား သင့် Vault ပြခန်းထဲသို့ တိုက်ရိုက် လွှဲပြောင်းထည့်သွင်းပြီးပါပြီ။</blockquote>",
        parse_mode='html'
    )

# ==========================================
# 🤝 11. PREMIUM PEER TRADE MATRIX (/trade)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/trade\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)$'))
async def trade_proposal_handler(event):
    if not event.is_reply: 
        return await event.reply("❌ <b>TARGET ERROR / ကုန်သွယ်မည့်သူအား Reply ပြန်၍ ခေါ်ယူပါ။</b>", parse_mode='html')
    
    my_char_id = event.pattern_match.group(1).upper()
    their_char_id = event.pattern_match.group(2).upper()
    
    sender_id = event.sender_id
    reply_msg = await event.get_reply_message()
    target_user_id = reply_msg.sender_id
    
    if sender_id == target_user_id: return
    
    s_doc = await users_catcher_col.find_one({"user_id": sender_id})
    t_doc = await users_catcher_col.find_one({"user_id": target_user_id})
    
    if not s_doc or s_doc.get("harem", {}).get(my_char_id, 0) <= 0:
        return await event.reply(f"❌ သင့်ထံတွင် ID: {my_char_id} မရှိပါ။", parse_mode='html')
    if not t_doc or t_doc.get("harem", {}).get(their_char_id, 0) <= 0:
        return await event.reply(f"❌ ၎င်းထံတွင် ID: {their_char_id} မရှိပါ။", parse_mode='html')
        
    s_char = await characters_base_col.find_one({"char_id": my_char_id})
    t_char = await characters_base_col.find_one({"char_id": their_char_id})
    
    trade_text = (
        f"🤝 <b>ASSET EXCHANGE CONTRACT / ဖလှယ်မှု စာချုပ်</b>\n"
        f"────────────────────────\n"
        f"📤 <b>Sender Offer:</b> <code>{s_char['name']}</code> ({my_char_id})\n"
        f"📥 <b>Target Request:</b> <code>{t_char['name']}</code> ({their_char_id})\n"
        f"────────────────────────\n"
        f"<blockquote><b>EN:</b> The activation authority belongs solely to the target receiver.\n"
        f"<b>MM:</b> စာချုပ်အား အတည်ပြုရန် ဆုံးဖြတ်ပိုင်ခွင့်သည် ကမ်းလှမ်းခံရသူထံ၌သာ ရှိသည်။</blockquote>"
    )
    
    buttons = [[
        Button.inline("🤝 Confirm Contract", data=f"tr_conf_{sender_id}_{target_user_id}_{my_char_id}_{their_char_id}"),
        Button.inline("❌ Void Contract", data=f"tr_canc_{sender_id}_{target_user_id}")
    ]]
    await event.reply(trade_text, parse_mode='html', buttons=buttons)

@bot1.on(events.CallbackQuery(pattern=r'^tr_(conf|canc)_(.*)$'))
async def trade_callback_processor(event):
    action = event.pattern_match.group(1).decode('utf-8')
    data_str = event.pattern_match.group(2).decode('utf-8')
    parts = data_str.split('_')
    
    sender_id = int(parts[0])
    target_id = int(parts[1])
    
    if action == "canc":
        if event.sender_id in [sender_id, target_id]:
            await event.edit("❌ <b>Exchange Contract Voided/Cancelled.</b>")
        return
        
    if action == "conf":
        if event.sender_id != target_id:
            return await event.answer("⚠️ သင်သည် ဤကုန်သွယ်မှုစာချုပ်၏ ကမ်းလှမ်းခံရသူ မဟုတ်ပါ။", alert=True)
            
        my_char_id, their_char_id = parts[2], parts[3]
        
        s_doc = await users_catcher_col.find_one({"user_id": sender_id})
        t_doc = await users_catcher_col.find_one({"user_id": target_id})
        
        if s_doc.get("harem", {}).get(my_char_id, 0) <= 0 or t_doc.get("harem", {}).get(their_char_id, 0) <= 0:
            return await event.edit("❌ <b>CONTRACT FAILED / ပိုင်ဆိုင်မှုများ ပြောင်းလဲသွားသဖြင့် မအောင်မြင်တော့ပါ။</b>")
            
        await users_catcher_col.update_one({"user_id": sender_id}, {"$inc": {f"harem.{my_char_id}": -1, f"harem.{their_char_id}": 1}})
        await users_catcher_col.update_one({"user_id": target_id}, {"$inc": {f"harem.{their_char_id}": -1, f"harem.{my_char_id}": 1}})
        
        await event.edit("🤝 <b>TRADE CONCLUDED / ကတ်လဲလှယ်ခြင်း လုပ်ငန်းစဉ် အောင်မြင်စွာ ပြီးဆုံးပါပြီ။</b>")

# ==========================================
# 📜 12. HELPMENU PANELS (/helpp & /owner)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/helpp(?:@\w+)?$'))
async def public_help_handler(event):
    help_text = (
        f"🌌 <b>SOVEREIGN MULTI-UNIVERSE HELPMENU</b>\n"
        f"────────────────────────\n"
        f"ℹ️ <b>GLOBAL MATRIX COMMANDS / အများသုံးစနစ်များ:</b>\n\n"
        f"🔘 <code>/who</code> — Reveal clues of the spawned person (Reply).\n"
        f"💬 စင်ပေါ်ရှိ ပုဂ္ဂိုလ်၏ အချက်အလက် သဲလွန်စအား Reply ဖြင့် စစ်ဆေးရန်။\n\n"
        f"🔘 <code>/catch [Name]</code> — Claim and capture the active target.\n"
        f"💬 ပုဂ္ဂိုလ်များအား မိမိဗဟို Vault ထဲသို့ ဖမ်းယူသိမ်းပိုက်ရန်။\n\n"
        f"🔘 <code>/hai</code> — Display your collection matrix repository.\n"
        f"💬 သင့်ပိုင်ဆိုင်မှု Showroom ပြခန်းအား ကြည့်ရှုရန်။\n\n"
        f"🔘 <code>/haimode</code> — Filter your collection showroom by rarity.\n"
        f"💬 မိမိပြခန်းအား Rarity အလိုက် ဇကာတင်စစ်ထုတ်ရန်။\n\n"
        f"🔘 <code>/check [ID]</code> — Inspect official database profile files.\n"
        f"💬 သတ်မှတ် ID ရှိသော ပုဂ္ဂိုလ်၏ ကိုယ်ရေးဒေတာ စစ်ဆေးရန်။\n\n"
        f"🔘 <code>/checkp</code> — View your central token ledger wallet balance.\n"
        f"💬 သင့်လက်ရှိ ရမှတ်ဗဟို Wallet Balance ကို ကြည့်ရန်။\n\n"
        f"🔘 <code>/gift [ID]</code> — Safe gift an asset card to target player (Reply).\n"
        f"💬 ထိုသူ့ထံသို့ ပိုင်ဆိုင်မှုကတ်အား လက်ဆောင် လွှဲပြောင်းရန်။\n\n"
        f"🔘 <code>/sell [ID] [PTS]</code> — List an asset into the open market ledger.\n"
        f"💬 စျေးကွက်ထဲသို့ မိမိကတ်အား သတ်မှတ်စျေးဖြင့် တင်ရောင်းရန်။\n\n"
        f"🔘 <code>/buy [ID]</code> — Instantly buy cheapest listed match from market.\n"
        f"💬 စျေးကွက်ထဲမှ တင်ထားသော ကတ်ကို ဝယ်ယူရန်။\n\n"
        f"🔘 <code>/trade [MyID] [TheirID]</code> — Propose peer exchange contract (Reply).\n"
        f"💬 အခြားသူနှင့် အပြန်အလှန် ကတ်ချင်း ဖလှယ်ရန်။\n"
        f"────────────────────────"
    )
    await event.reply(help_text, parse_mode='html')

@bot1.on(events.NewMessage(pattern=r'^/owner$'))
async def exclusive_owner_panel(event):
    if event.sender_id != OWNER_ID: return
    owner_text = (
        f"👑 <b>WELCOME BACK, CHIEF DEXTER!</b>\n"
        f"────────────────────────\n"
        f"🛠️ <b>EXCLUSIVITY ROOT COMMANDS / ဗဟိုထိန်းချုပ်မှုများ:</b>\n\n"
        f"⚙️ <code>/addchar Name | Category | Rarity_Num</code>\n"
        f"<blockquote><b>Injects new person into the central database.</b>\n"
        f"Rarity Numbers: 1=Legend, 2=Limit, 3=Mythic, 4=Epic, 5=Rare, 6=Common\n"
        f"<i>(Must reply to valid media array matrix)</i></blockquote>\n"
        f"⚙️ <code>/Haii</code>\n"
        f"<blockquote><b>Bypasses counter logic and forces an instant dynamic spawn inside current domain sectors.</b></blockquote>\n"
        f"⚙️ <code>/changetime [Message Count]</code>\n"
        f"<blockquote><b>Adjust global automated message-trigger thresholds.</b></blockquote>\n"
        f"────────────────────────"
    )
    await event.reply(owner_text, parse_mode='html')

# ==========================================
# ⚡ EXECUTOR INITIALIZER
# ==========================================
if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    print("🛰️ Sovereign Matrix Grid Online...")
    bot1.start(bot_token=MAIN_BOT_TOKEN)
    bot1.run_until_disconnected()

