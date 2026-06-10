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
# ⚡ PREMIUM MATHEMATICAL BOLD SERIF FONT CONVERTER
# ==========================================
def f(text):
    """Converts regular English text to premium Bold Serif Unicode Font"""
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    bold = "𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫"
    trans = str.maketrans(normal, bold)
    return text.translate(trans)

# ==========================================
# 🔍 SMART TEXT NORMALIZER FOR TEXT MATCHING
# ==========================================
def normalize_name(text):
    if not text: return ""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ==========================================
# 🌐 FLASK KEEP-ALIVE SYSTEM
# ==========================================
app = Flask('')
@app.route('/')
def home(): return "Sovereign Core Hub Status: Running Perfect! 🔥"

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
# 🎭 RARITY MAPPING MATRIX
# ==========================================
RARITY_NUM_MAP = {
    "1": {"name": f"👑 {f('LEGENDARY')}", "value": 500},
    "2": {"name": f"⏳ {f('LIMITED')}", "value": 450},
    "3": {"name": f"🔮 {f('MYTHIC')}", "value": 400},
    "4": {"name": f"🔥 {f('EPIC')}", "value": 300},
    "5": {"name": f"✨ {f('RARE')}", "value": 200},
    "6": {"name": f"♻️ {f('COMMON')}", "value": 100}
}

# ==========================================
# 📥 1. PERMANENT DATABASE ADDER
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/addchar(?:\s+(.+))?'))
async def add_character(event):
    if event.sender_id != OWNER_ID: return

    input_text = event.pattern_match.group(1)
    if not input_text or '|' not in input_text:
        await event.reply(
            f"⚠️ <b>{f('Format Wrong နေတယ် Bro!')}</b>\n"
            f"⚡ ━━━━━━━━━━━━━━━━━━━━ ⚡\n"
            f"📌 <b>{f('Usage / အသုံးပြုနည်း')}:</b>\n"
            f"<code>/addchar Name | Category | Rarity_Number</code>\n"
            f"<i>(Media File တစ်ခုခုကို Reply ပြန်ပြီး သုံးပေးပါ)</i>\n\n"
            f"🔢 <b>{f('Rarity Tiers (1-6)')}:</b>\n"
            f"<code>1</code> = 👑 LEGENDARY (500 PTS)\n"
            f"<code>2</code> = ⏳ LIMITED-EDITION (450 PTS)\n"
            f"<code>3</code> = 🔮 MYTHIC (400 PTS)\n"
            f"<code>4</code> = 🔥 EPIC (300 PTS)\n"
            f"<code>5</code> = ✨ RARE (200 PTS)\n"
            f"<code>6</code> = ♻️ COMMON (100 PTS)\n"
            f"⚡ ━━━━━━━━━━━━━━━━━━━━ ⚡\n"
            f"💡 <b>{f('Example')}:</b> <code>/addchar Dexter Morgan | Series | 1</code>",
            parse_mode='html'
        )
        return

    parts = [p.strip() for p in input_text.split('|')]
    if len(parts) < 3: 
        return await event.reply(f"❌ <b>{f('Segment တွေလိုနေသေးတယ် Bro! 3 ပိုင်း ခွဲပေးပါ။')}</b>", parse_mode='html')

    char_name, category_name, rarity_num = parts[0], parts[1], parts[2]
    
    if rarity_num not in RARITY_NUM_MAP:
        return await event.reply(f"❌ <b>{f('Rarity Number မှားနေတယ်! 1 ကနေ 6 ထိပဲ ရွေးပါ။')}</b>", parse_mode='html')

    if not event.is_reply: 
        return await event.reply(f"❌ <b>{f('Media တစ်ခုခုကို Reply ပြန်ပေးဦးလေ Boss!')}</b>", parse_mode='html')

    reply_msg = await event.get_reply_message()
    if not reply_msg or not (reply_msg.photo or reply_msg.video or reply_msg.document):
        return await event.reply(f"❌ <b>{f('ထည့်သွင်းဖို့ Valid ဖြစ်တဲ့ Media ရှာမတွေ့ဘူး Bro!')}</b>", parse_mode='html')

    try:
        forwarded_msg = await bot1.send_message(SPECIFIC_CONTROL_GROUP, file=reply_msg.media)
        storage_id = forwarded_msg.id
        
        r_info = RARITY_NUM_MAP[rarity_num]
        
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
            "currency_value": r_info["value"],
            "spawn_count": 0
        }

        await characters_base_col.insert_one(character_data)
        
        success_msg = (
            f"🔥 <b>{f('DATABASE INJECTED / စနစ်ထဲ ထည့်ပြီးပြီ')}</b>\n"
            f"⚡ ━━━━━━━━━━━━━━━━━━━━ ⚡\n"
            f"🆔 <b>{f('Character ID')}:</b> <code>{char_id}</code>\n"
            f"👤 <b>{f('Name')}:</b> <code>{char_name}</code>\n"
            f"🌐 <b>{f('Category')}:</b> <code>{category_name}</code>\n"
            f"🌟 <b>{f('Rarity')}:</b> {r_info['name']}\n"
            f"💎 <b>{f('Worth')}:</b> <code>{r_info['value']} PTS</code>\n"
            f"⚡ ━━━━━━━━━━━━━━━━━━━━ ⚡\n"
            f"<blockquote><b>{f('Status')}:</b> Storage ID {storage_id} နဲ့ အိုင်တမ်အသစ်ကို Database ထဲ အောင်မြင်စွာ ချိတ်ဆက်ပြီးပါပြီ Boss! 😎🎧</blockquote>"
        )
        await event.reply(success_msg, parse_mode='html')

    except Exception as e:
        await event.reply(f"❌ <b>{f('Database Inject Error')}:</b> <code>{escape_html(str(e))}</code>", parse_mode='html')

# ==========================================
# 🛰️ 2. OVERRIDE FORCE SPAWN ENGINE (/fspawn & /haii)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/(fspawn|haii)(?:@\w+)?$'))
async def force_spawn_by_owner(event):
    if event.sender_id != OWNER_ID: return
    await trigger_dynamic_spawn(event.chat_id)

# ==========================================
# 📢 3. AUTOMATIC SPAWN PROCESSOR
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
        
        # Increments total spawns across the system
        await characters_base_col.update_one({"char_id": chosen_char["char_id"]}, {"$inc": {"spawn_count": 1}})
        
        spawn_msg = await bot1.send_message(
            chat_id, 
            f"⚡ <b>{f('MYSTERY HAI DETECTED / ဘယ်သူလေး ပေါ်လာတာလဲ...')} 🫣</b>\n"
            f"<blockquote><b>{f('Hey Hunters')}!</b> သူက ဘယ်သူဖြစ်မလဲ? သဲလွန်စတွေ ကြည့်ဖို့ ဒီပိုစ့်ကို <code>/who</code> နဲ့ အမြန်ဆုံး Reply ပြန်ပြီး စစ်ဆေးလိုက်ပါ! 👀🔥</blockquote>\n"
            f"PARADOX Family:BOD",
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
        return await event.reply(f"❌ <b>{f('လက်ရှိ Spawnတဲ့ Hai မရှိသေးပါဘူး Boss!')}</b>", parse_mode='html')
        
    spawn_data = active_group_spawns[chat_id]
    
    if time.time() - spawn_data["spawn_time"] > 60:
        if chat_id in active_group_spawns: del active_group_spawns[chat_id]
        return await event.reply(f"⏱️ <b>{f('TARGET GHOSTED / အချိန်ကုန်သွားလို့ ထွက်ပြေးသွားပြီ!')}😅</b>", parse_mode='html')
        
    if not event.is_reply or event.reply_to_msg_id != spawn_data["spawn_msg_id"]:
        return await event.reply(f"⚠️ <b>{f('ပစ်မှတ်လွဲနေတယ်! ပေါ်လာတဲ့ Drop ပိုစ့်ကို တိုက်ရိုက် Reply ပြန်ပေးပါ Bro!')}</b>", parse_mode='html')
        
    reveal_text = (
        f"🔍 <b>{f('TARGET DATA CLUES FOUND / သဲလွန်စ ရပြီ')}</b>\n"
        f"🌐 <b>{f('Universe Domain')}:</b> <code>{spawn_data['category']}</code>\n"
        f"🌟 <b>{f('Rarity Class')}:</b> {spawn_data['rarity']}\n\n"
        f"🔥 <b>{f('CAPTURE PAYLOAD / အပိုင်ဖမ်းယူရန် ကုဒ်')}:</b>\n"
        f"<code>/catch {spawn_data['name']}</code>\n"
        f"<blockquote><b>{f('Hurry Up')}!</b> အပေါ်က /catch xxx အမြန်ဆုံး Copy ယူပြီး ဦးအောင် ဖမ်းလိုက်တော့ Bestie!</blockquote>"
    )
reply = await event.reply(reveal_text, parse_mode='html')
# ==========================================
# 🎯 5. CLAIM ENGINE CORE (/catch)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/catch\s+(.*)$'))
async def catch_handler(event):
    if event.is_private: return
    chat_id = event.chat_id
    user_id = event.sender_id
    catch_name = event.pattern_match.group(1).strip()
    
    if chat_id not in active_group_spawns:
        return await event.reply(f"🛸 <b>{f('ဒီ Dimension မှာ ဖမ်းစရာ ဘယ်သူမှ မရှိတော့ဘူး Bro!')}</b>", parse_mode='html')
        
    spawn_data = active_group_spawns[chat_id]
    
    if time.time() - spawn_data["spawn_time"] > 180:
        if chat_id in active_group_spawns: del active_group_spawns[chat_id]
        return await event.reply(f"⏱️ <b>{f('TARGET GHOSTED / အချိန်ကုန်သွားလို့ ထွက်ပြေးသွားပြီ!')}😅</b>", parse_mode='html')
        
    if spawn_data["claimed"]: return
    
    if normalize_name(catch_name) != normalize_name(spawn_data["name"]): 
        return await event.reply(f"❌ <b>{f('နာမည်မှားနေတယ် Boss! သေချာပြန်စစ်ပြီး /catch')}</b>", parse_mode='html')
        
    active_group_spawns[chat_id]["claimed"] = True 
    sender = await event.get_sender()
    fullname = f"@{sender.username}" if sender and getattr(sender, 'username', None) else (getattr(sender, 'first_name', None) or "Hunter")
    mention = f"<a href='tg://user?id={user_id}'><b>{escape_html(fullname)}</b></a>"
    
    try:
        await users_catcher_col.update_one(
            {"user_id": user_id},
            {
                "$push": {
                    "harem": {
                        "char_id": spawn_data['char_id'],
                        "caught_date": time.time(),
                        "rarity": spawn_data['rarity']
                    }
                },
                "$inc": {
                    "total_caught": 1, 
                    "wallet_balance": spawn_data["value"],
                    f"group_catches.{str(chat_id)}": 1
                 },
                 "$set": {"fullname": mention}
            },
            upsert=True
        )
        
        if chat_id in active_group_spawns: del active_group_spawns[chat_id]
        
        success_text = (
            f"🎯 <b>{f('CAPTURED SUCCESS / ဖမ်းယူမှု အောင်မြင်ခြင်း')} ✨</b>\n"
            f"👤 <b>{f('Hunter')}:</b> {mention}\n"
            f"🃏 <b>{f('Character')}:</b> <code>{escape_html(spawn_data['name'])}</code>\n"
            f"🆔 <b>{f('Asset ID')}:</b> <code>{spawn_data['char_id']}</code>\n"
            f"🌟 <b>{f('Rarity Class')}:</b> {spawn_data['rarity']}\n"
            f"🪙 <b>{f('Bounty Added')}:</b> <code>+{spawn_data['value']} PTS</code>\n"
            f"<blockquote><b>{f('Mission Secured')}!</b> ဒီHaiကို သင့်ရဲ့ စုဆောင်းမှု Vault ထဲသို့ အပိုင်ဆွဲထည့်လိုက်ပြီနော်Boss!🔥</blockquote>"
        )
        await bot1.send_message(chat_id, success_text, parse_mode='html')
    except Exception as e:
        if chat_id in active_group_spawns: active_group_spawns[chat_id]["claimed"] = False
        await event.reply(f"❌ <b>Catch Logic Fault:</b> <code>{e}</code>", parse_mode='html')

# ==========================================
# 🎒 6. INVENTORY PREFERENCE ENGINE (/fav & /hai)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/fav\s+([a-zA-Z0-9_]+)$'))
async def set_favorite_card(event):
    user_id = event.sender_id
    char_id = event.pattern_match.group(1).upper()
    
    # Check if character exists in structural master database
    card = await characters_base_col.find_one({"char_id": char_id})
    if not card:
        return await event.reply(f"❌ <b>{f('ကတ်ရှာမတွေ့ပါဘူး Bro!')}</b>", parse_mode='html')
        
    user_doc = await users_catcher_col.find_one({"user_id": user_id})
    user_harem = user_doc.get("harem", []) if user_doc else []
    
    # Confirm ownership before pin assignment
    owns_card = any(isinstance(x, dict) and x.get("char_id") == char_id for x in user_harem)
    if not owns_card:
        return await event.reply(f"❌ <b>{f('ဒီကတ်က သင့်ဆီမှာ မရှိသေးပါဘူး Bro!')}</b>", parse_mode='html')
        
    await users_catcher_col.update_one({"user_id": user_id}, {"$set": {"fav_card": char_id}})
    await event.reply(f"⭐️ <b>{escape_html(card['name'])}</b> ({char_id}) <code>{f('ကို Favorite ကတ်အဖြစ် သတ်မှတ်လိုက်ပါပြီ။')}</code>", parse_mode='html')

@bot1.on(events.NewMessage(pattern=r'^/hai(?:@\w+)?$'))
async def display_harem_list(event):
    user_id = event.sender_id
    user_doc = await users_catcher_col.find_one({"user_id": user_id})
    
    if not user_doc or not user_doc.get("harem"):
        return await event.reply(f"🎒 <b>{f('သင့် Vault ထဲမှာ ဘာကတ်မှ မရှိသေးပါဘူး Bro!')}</b>", parse_mode='html')
        
    raw_harem = user_doc.get("harem", [])
    harem_counts = {}
    for item in raw_harem:
        if isinstance(item, dict) and "char_id" in item:
            cid = item["char_id"]
            harem_counts[cid] = harem_counts.get(cid, 0) + 1
            
    owned_ids = list(harem_counts.keys())
    db_chars = await characters_base_col.find({"char_id": {"$in": owned_ids}}).to_list(length=None)
    
    # Group processing sorted by Rarity and names (A-Z)
    categorized = {}
    for c in db_chars:
        r = c.get("rarity", f"♻️ {f('COMMON')}")
        if r not in categorized: categorized[r] = []
        categorized[r].append(c)
        
    sender = await event.get_sender()
    fullname = f"@{sender.username}" if sender and getattr(sender, 'username', None) else (getattr(sender, 'first_name', None) or "Hunter")
    
    output_text = f"🎒 <a href='tg://user?id={user_id}'><b>{escape_html(fullname)}</b></a> <b>{f('s VAULT COLLECTION')}</b>\n"
    output_text += f"Hai Catcher Bot🤪\n\n"
    
    for rarity_tier in sorted(categorized.keys()):
        output_text += f"⚜️ <b><u>{rarity_tier}</u></b>\n"
        sorted_list = sorted(categorized[rarity_tier], key=lambda x: x["name"])
        for card in sorted_list:
            qty = harem_counts.get(card["char_id"], 1)
            output_text += f" ├─➩ {card['name']} — [<code>{card['char_id']}</code>] <b>(x{qty})</b>\n"
        output_text += "\n"
        
    output_text += f"⚡ ━━━━━⚡"
    
    # Media background deployment logic if user has a configured preference
    fav_card_id = user_doc.get("fav_card")
    if fav_card_id:
        fav_card_data = await characters_base_col.find_one({"char_id": fav_card_id})
        if fav_card_data:
            try:
                storage_msg = await bot1.get_messages(SPECIFIC_CONTROL_GROUP, ids=fav_card_data["storage_msg_id"])
                if storage_msg and storage_msg.media:
                    return await bot1.send_message(event.chat_id, output_text, file=storage_msg.media, parse_mode='html')
            except: pass
            
    await event.reply(output_text, parse_mode='html')

# ==========================================
# 🎛️ 7. UNIFIED CALLBACK QUERY MATRIX PROCESSOR
# ==========================================
@bot1.on(events.CallbackQuery)
async def unified_callback_handler(event):
    if not event.data: return
    try: data_str = event.data.decode('utf-8')
    except: return

    data_parts = data_str.split('_')
    action_type = data_parts[0]

    # Handles the premium inline store direct payment execution
    if action_type == "mktbuy":
        listing_id = data_parts[1]
        buyer_id = event.sender_id
        
        listing = await marketplace_col.find_one({"listing_id": listing_id})
        if not listing:
            return await event.answer("❌ ဒီအရောင်းစာရင်းက မရှိတော့ပါဘူး သို့မဟုတ် ရောင်းထွက်သွားပါပြီ။", alert=True)
            
        price = listing["price"]
        seller_id = listing["seller_id"]
        char_id = listing["char_id"]
        
        if buyer_id == seller_id:
            return await event.answer("⚠️ မိမိပစ္စည်းကို မိမိပြန်ဝယ်လို့ မရပါဘူး Bro!", alert=True)
            
        buyer_doc = await users_catcher_col.find_one({"user_id": buyer_id})
        if not buyer_doc or buyer_doc.get("wallet_balance", 0) < price:
            return await event.answer(f"❌ ရမှတ်မလုံလောက်ပါဘူး! လိုအပ်ချက်: {price} PTS", alert=True)
            
        char_data = await characters_base_col.find_one({"char_id": char_id})
        char_rarity = char_data.get("rarity", "Unknown") if char_data else "Unknown"
        
        # Atomically process payment ledger to avoid duplicate claims
        res = await users_catcher_col.update_one(
            {"user_id": buyer_id, "wallet_balance": {"$gte": price}},
            {
                "$inc": {"wallet_balance": -price, "total_caught": 1},
                "$push": {"harem": {"char_id": char_id, "caught_date": time.time(), "rarity": char_rarity}}
            }
        )
        
        if res.modified_count == 0:
            return await event.answer("❌ Transaction System Error!", alert=True)
            
        await users_catcher_col.update_one({"user_id": seller_id}, {"$inc": {"wallet_balance": price}})
        await marketplace_col.delete_one({"listing_id": listing_id})
        
        await event.answer("🎉 ဝယ်ယူမှု အောင်မြင်ပါပြီ!", alert=True)
        await event.edit(f"🤝 <b>{f('DEAL SECURED')}</b>\n\nဒီcharaterကို စျေးကွက်ထဲမှ အောင်မြင်စွာ သိမ်းပိုက်ပြီးပါပြီ။", parse_mode='html')

    elif action_type == "tr":
        sub_action = data_parts[1]
        sender_id = int(data_parts[2])
        target_id = int(data_parts[3])
        
        if sub_action == "canc":
            if event.sender_id in [sender_id, target_id]:
                await event.answer("❌ Transaction Terminated")
                await event.edit(f"❌ <b>{f('Exchange Contract Voided / ကတ်ဖလှယ်မှုကို ပယ်ဖျက်လိုက်ပါပြီ။')}</b>", parse_mode='html')
            else:
                await event.answer("⚠️ သင်က ဒီစာချုပ်ထဲမှာ ပါဝင်သူ မဟုတ်ပါဘူး Bro!", alert=True)
            return
            
        if sub_action == "conf":
            if event.sender_id != target_id:
                return await event.answer("⚠️ သင်က ဒီကုန်သွယ်မှုစာချုပ်ရဲ့ ကမ်းလှမ်းခံရသူ မဟုတ်ပါဘူး Bro!", alert=True)
                
            await event.answer("⚡ Finalizing Contract Matrix...")
            my_char_id, their_char_id = data_parts[4], data_parts[5]
            
            s_doc = await users_catcher_col.find_one({"user_id": sender_id})
            t_doc = await users_catcher_col.find_one({"user_id": target_id})
            
            s_harem = s_doc.get("harem", []) if s_doc else []
            t_harem = t_doc.get("harem", []) if t_doc else []
            
            s_item = next((x for x in s_harem if isinstance(x, dict) and x.get("char_id") == my_char_id), None)
            t_item = next((x for x in t_harem if isinstance(x, dict) and x.get("char_id") == their_char_id), None)
            
            if not s_item or not t_item:
                return await event.edit(f"❌ <b>{f('CONTRACT FAILED / ပိုင်ဆိုင်မှု အခြေအနေ ပြောင်းလဲသွားလို့ မအောင်မြင်တော့ပါ!')}</b>", parse_mode='html')
                
            s_harem.remove(s_item)
            t_harem.remove(t_item)
            
            s_harem.append({"char_id": their_char_id, "caught_date": time.time(), "rarity": t_item.get("rarity", "Unknown")})
            t_harem.append({"char_id": my_char_id, "caught_date": time.time(), "rarity": s_item.get("rarity", "Unknown")})
            
            await users_catcher_col.update_one({"user_id": sender_id}, {"$set": {"harem": s_harem}})
            await users_catcher_col.update_one({"user_id": target_id}, {"$set": {"harem": t_harem}})
            
            await event.edit(f"🤝 <b>{f('TRADE CONCLUDED / ကတ်လဲလှယ်ခြင်း လုပ်ငန်းစဉ် အောင်မြင်စွာ ပြီးဆုံးပါပြီ။ 🔥')}</b>", parse_mode='html')

# ==========================================
# 📊 8. PROFILE SYSTEM CORE (/profile)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/profile(?:@\w+)?$'))
async def profile_handler(event):
    user_id = event.sender_id
    user_doc = await users_catcher_col.find_one({"user_id": user_id})
    
    sender = await event.get_sender()
    fullname = f"@{sender.username}" if sender and getattr(sender, 'username', None) else (getattr(sender, 'first_name', None) or "Hunter")
    
    total_caught = user_doc.get("total_caught", 0) if user_doc else 0
    balance = user_doc.get("wallet_balance", 0) if user_doc else 0
    raw_harem = user_doc.get("harem", []) if user_doc else []
    
    # Calculate exact dynamic count per individual tier inside user vault
    counts = {}
    for i in raw_harem:
        if isinstance(i, dict) and "rarity" in i:
            r_name = i["rarity"]
            counts[r_name] = counts.get(r_name, 0) + 1

    profile_text = (
        f"🌌 <b>{f('SOVEREIGN AGENT DOSSIER')}</b>\n"
        f"👤 <b>{f('Agent Identity')}:</b> {escape_html(fullname)}\n"
        f"🔩 <b>{f('System Core ID')}:</b> <code>{user_id}</code>\n"
        f"🪙 <b>{f('Asset Liquid Capital')}:</b> <code>{balance} PTS</code>\n"
        f"🎒 <b>{f('Gross Captured Units')}:</b> <code>{total_caught} Units</code>\n"
        f"⚡ ━━━━━━⚡\n"
    )
    
    # Only renders strings for rarity tiers that the user actually possesses
    if counts:
        profile_text += f"📊 <b>{f('VAULT QUANTUM SEGMENTS')}:</b>\n"
        for tier, qty in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            profile_text += f" ├─➩ {tier}: <b>{qty} Cards</b>\n"
        profile_text += f"⚡ ━━━━━━ ⚡\n"
        
    await event.reply(profile_text, parse_mode='html')

# ==========================================
# 🔍 9. SPECIFIC CHARACTER METRICS ARCHIVE (/check)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/check\s+([a-zA-Z0-9_]+)$'))
async def check_character_id_handler(event):
    char_id = event.pattern_match.group(1).upper()
    character = await characters_base_col.find_one({"char_id": char_id})
    
    if not character:
        return await event.reply(f"❌ <b>{f('DATABASE MISMATCH / Character ID အမှန်ရိုက်ပါဦး Bro!')}</b>", parse_mode='html')
        
    spawn_count = character.get("spawn_count", 0)
    
    # High-performance aggregation query to sort and retrieve top 10 unique holders
    pipeline = [
        {"$match": {"harem.char_id": char_id}},
        {"$project": {
            "fullname": "$fullname",
            "user_id": "$user_id",
            "count": {
                "$size": {
                    "$filter": {
                        "input": "$harem",
                        "as": "item",
                        "cond": {"$eq": ["$$item.char_id", char_id]}
                    }
                }
            }
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    top_hunters = await users_catcher_col.aggregate(pipeline).to_list(length=10)
    
    leaderboard_str = ""
    for idx, u in enumerate(top_hunters, start=1):
        uname = u.get("fullname") or f"Agent {u['user_id']}"
        leaderboard_str += f" <b>{idx}.</b> {uname} — <code>x{u['count']}</code>\n"
        
    try:
        storage_msg = await bot1.get_messages(SPECIFIC_CONTROL_GROUP, ids=character["storage_msg_id"])
        media_file = storage_msg.media if storage_msg else None
    except: media_file = None
        
    info_text = (
        f"⚜️ <b>{f('DATA MATRIX ANALYTICS')}</b>\n"
        f"🆔 <b>{f('Asset Index')}:</b> <code>{character['char_id']}</code>\n"
        f"👤 <b>{f('Identity Label')}:</b> <code>{character['name']}</code>\n"
        f"🌐 <b>{f('Domain Realm')}:</b> <code>{character['category']}</code>\n"
        f"🌟 <b>{f('Rarity Tier')}:</b> {character['rarity']}\n"
        f"📈 <b>{f('Global Spawn Metrics')}:</b> <code>{spawn_count} Times spawned</code>\n"
        f"🏆 <b>{f('TOP 10 ELITE COLLECTORS')}:</b>\n\n"
        f"{leaderboard_str if leaderboard_str else 'Catcherမရှိသေးပါ။'}"
    )
    await event.reply(info_text, parse_mode='html', file=media_file)

# ==========================================
# 🛒 10. PREMIUM AUCTION MARKETPLACE ENGINE (/sell & /buy)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/sell\s+([a-zA-Z0-9_]+)\s+(\d+)$'))
async def sell_market_handler(event):
    user_id = event.sender_id
    char_id = event.pattern_match.group(1).upper()
    price = int(event.pattern_match.group(2))
    
    if price <= 0: 
        return await event.reply(f"❌ <b>{f('ဈေးနှုန်းက အနည်းဆုံး 1 PTS တော့ ရှိရမယ်လေ Bro!')}</b>", parse_mode='html')
    
    user_doc = await users_catcher_col.find_one({"user_id": user_id})
    user_harem = user_doc.get("harem", []) if user_doc else []
    
    char_item = next((x for x in user_harem if isinstance(x, dict) and x.get("char_id") == char_id), None)
    if not char_item:
        return await event.reply(f"❌ <b>{f('သင့်ဆီမှာ ရောင်းစရာ ဒီလိုကတ် မရှိပါဘူး Bro!')}</b>", parse_mode='html')
        
    char_data = await characters_base_col.find_one({"char_id": char_id})
    if not char_data: return await event.reply(f"❌ <b>{f('Character ID မှားနေတယ် Bro!')}</b>", parse_mode='html')

    # Remove item instantly to escrow to guarantee secure listing safety
    user_harem.remove(char_item)
    await users_catcher_col.update_one({"user_id": user_id}, {"$set": {"harem": user_harem}})
    
    listing_id = f"L{random.randint(1000, 9999)}"
    
    sender = await event.get_sender()
    fullname = f"@{sender.username}" if sender and getattr(sender, 'username', None) else (getattr(sender, 'first_name', None) or "Seller")
    mention = f"<a href='tg://user?id={user_id}'><b>{escape_html(fullname)}</b></a>"

    await marketplace_col.insert_one({
        "listing_id": listing_id,
        "seller_id": user_id,
        "seller_name": mention,
        "char_id": char_id,
        "char_name": char_data["name"],
        "price": price,
        "timestamp": time.time()
    })
    
    await event.reply(
        f"🏪 <b>{f('MARKET ITEM LOCKED IN ESCROW')} 🛒</b>\n"
        f"🎫 <b>{f('Listing Reference')}:</b> <code>{listing_id}</code>\n"
        f"👤 <b>{f('Asset Identity')}:</b> <code>{char_data['name']}</code>\n"
        f"💰 <b>{f('Bounty Evaluation')}:</b> <code>{price} PTS</code>\n"
        f"📦 ━━━━━📦",
        parse_mode='html'
    )

@bot1.on(events.NewMessage(pattern=r'^/buy\s+([a-zA-Z0-9_]+)(?:\s+(\d+))?$'))
async def buy_market_handler(event):
    buyer_id = event.sender_id
    char_id = event.pattern_match.group(1).upper()
    target_seller_id = event.pattern_match.group(2)
    
    # Execution route alternative: Direct peer purchase via /buy [card_id] [user_id]
    if target_seller_id:
        target_seller_id = int(target_seller_id)
        if buyer_id == target_seller_id:
            return await event.reply(f"❌ <b>{f('မိမိပစ္စည်းကို မိမိပြန်ဝယ်၍ မရပါ!')}</b>", parse_mode='html')
            
        listing = await marketplace_col.find_one({"char_id": char_id, "seller_id": target_seller_id})
        if not listing:
            return await event.reply(f"❌ <b>{f('ဒီရောင်းသူထံမှ သတ်မှတ်ထားသော ကတ်အရောင်းစာရင်း ရှာမတွေ့ပါ!')}</b>", parse_mode='html')
            
        price = listing["price"]
        buyer_doc = await users_catcher_col.find_one({"user_id": buyer_id})
        if not buyer_doc or buyer_doc.get("wallet_balance", 0) < price:
            return await event.reply(f"❌ <b>{f('ရမှတ်မလုံလောက်ပါဘူး Bro!')}</b>", parse_mode='html')
            
        char_data = await characters_base_col.find_one({"char_id": char_id})
        char_rarity = char_data.get("rarity", "Unknown") if char_data else "Unknown"
        
        res = await users_catcher_col.update_one(
            {"user_id": buyer_id, "wallet_balance": {"$gte": price}},
            {
                "$inc": {"wallet_balance": -price, "total_caught": 1},
                "$push": {"harem": {"char_id": char_id, "caught_date": time.time(), "rarity": char_rarity}}
            }
        )
        if res.modified_count == 0: return await event.reply("❌ Transaction Error!")
        
        await users_catcher_col.update_one({"user_id": target_seller_id}, {"$inc": {"wallet_balance": price}})
        await marketplace_col.delete_one({"listing_id": listing["listing_id"]})
        
        return await event.reply(f"🎉 <b>{f('Direct Purchase Success!')}</b>", parse_mode='html')

    # Standard execution route: Retrieves sorted list of global market offers (Ascending by price)
    listings = await marketplace_col.find({"char_id": char_id}).sort("price", 1).to_list(length=10)
    if not listings: 
        return await event.reply(f"❌ <b>{f('ဒီကတ်အတွက် လက်ရှိရောင်းချသူ မရှိသေးပါဘူး Bro!')}</b>", parse_mode='html')
        
    market_text = f"🛒 <b>{f('MARKETPLACE LISTINGS FOR')} : {char_id}</b>\n"
    market_text += f"⚠️ <i>နမူနာစနစ်ထက် စျေးအနိမ့်ဆုံးမှ အမြင့်ဆုံးသို့ စနစ်တကျ စီပေးထားပါသည်။</i>\n"
    market_text += f"⚡ ━━━━ ⚡\n\n"
    
    buttons = []
    for item in listings:
        market_text += f"👤 <b>Merchant:</b> {item['seller_name']} [<code>{item['seller_id']}</code>]\n"
        market_text += f"💰 <b>Price Value:</b> <code>{item['price']} PTS</code>\n\n"
        
        buttons.append([Button.inline(f"Buy via {item['price']} PTS", data=f"mktbuy_{item['listing_id']}")])
        
    await event.reply(market_text, parse_mode='html', buttons=buttons)

# ==========================================
# 🏆 11. LEADERBOARD SYSTEM (/top & /gtop)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/top(?:@\w+)?$'))
async def local_group_top_handler(event):
    if event.is_private: return
    chat_id = event.chat_id
    
    cursor = users_catcher_col.find({f"group_catches.{str(chat_id)}": {"$gt": 0}}).sort(f"group_catches.{str(chat_id)}", -1).limit(10)
    top_users = await cursor.to_list(length=10)
    
    if not top_users:
        return await event.reply(f"🏆 <b>{f('ဒီဂရုထဲမှာ Rank စာရင်း မရှိသေးပါဘူး Bro!')}</b>", parse_mode='html')
        
    msg = f"🏆 <b>{f('TOP 10 HUNTERS IN THIS GROUP')}</b>\n"
    msg += f"⚡ ━━━━⚡\n"
    for i, u in enumerate(top_users):
        count = u["group_catches"][str(chat_id)]
        user_display = u.get('fullname') or f"User {u['user_id']}"
        msg += f"<b>{i+1}.</b> {user_display} — <code>{count} ကတ်</code>\n"

    msg += f"⚡PARADOX Family:BOD⚡"
    await event.reply(msg, parse_mode='html')

@bot1.on(events.NewMessage(pattern=r'^/gtop(?:@\w+)?$'))
async def global_top_handler(event):
    cursor = users_catcher_col.find({"total_caught": {"$gt": 0}}).sort("total_caught", -1).limit(10)
    top_users = await cursor.to_list(length=10)
    
    if not top_users:
        return await event.reply(f"🏆 <b>{f('Global Leaderboard မှာ စာရင်းမရှိသေးပါဘူး Bro!')}</b>", parse_mode='html')
        
    msg = f"🌐 <b>{f('GLOBAL TOP 10 HUNTERS')}</b>\n"
    msg += f"⚡ ━━━━━⚡\n"
    for i, u in enumerate(top_users):
        count = u.get("total_caught", 0)
        user_display = u.get('fullname') or f"User {u['user_id']}"
        msg += f"<b>{i+1}.</b> {user_display} — <code>{count} ကတ်</code>\n"
        
    msg += f"⚡PARADOX Family:BOD⚡"
    await event.reply(msg, parse_mode='html') 

# ==========================================
# 💰 12. WALLET BALANCE CHECKER (/checkp)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/checkp(?:@\w+)?$'))
async def check_points_balance(event):
    user_doc = await users_catcher_col.find_one({"user_id": event.sender_id})
    balance = user_doc.get("wallet_balance", 0) if user_doc else 0
    await event.reply(
        f"💳 <b>{f('SOVEREIGN WALLET LEDGER / ရမှတ်လက်ကျန်')}</b>\n"
        f"💰 <b>{f('Current Balance / လက်ရှိရမှတ်ဗဟိုတန်ဖိုး')}:</b>\n"
        f"<blockquote><code>{balance} PTS</code> 🪙</blockquote>\n"
        f"⚡ ━━━━━⚡", 
        parse_mode='html'
    )

# ==========================================
# 🎁 13. PEER-TO-PEER ASSET TRANSFER (/gift)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/gift\s+(.+)$'))
async def gift_asset_handler(event):
    if not event.is_reply: 
        return await event.reply(f"❌ <b>{f('ဘယ်သူ့ကို ပေးမှာလဲ Bro? အဲ့ဒီလူ့စာကို Reply ပြန်ပြီး ကုဒ်ရိုက်ပေးပါဦး!')}</b>", parse_mode='html')
        
    char_id = event.pattern_match.group(1).strip().upper()
    sender_id = event.sender_id
    reply_msg = await event.get_reply_message()
    receiver_id = reply_msg.sender_id
    
    if sender_id == receiver_id: 
        return await event.reply(f"❌ <b>{f('Loop Error! မိမိကိုယ်ကို ပြန်လည် Gift ပေးလို့ မရပါဘူး Bro!')} 💀</b>", parse_mode='html')

    sender_doc = await users_catcher_col.find_one({"user_id": sender_id})
    sender_harem = sender_doc.get("harem", []) if sender_doc else []
    
    char_item = next((x for x in sender_harem if isinstance(x, dict) and x.get("char_id") == char_id), None)
    if not char_item:
        return await event.reply(f"❌ <b>{f('Transaction Refused! သင့် Vault ထဲမှာ ဒီကတ် လုံလောက်အောင် မရှိဘူးနော်!')}</b>", parse_mode='html')

    sender_harem.remove(char_item)
    await users_catcher_col.update_one({"user_id": sender_id}, {"$set": {"harem": sender_harem}})
    
    receiver_sender = await reply_msg.get_sender()
    r_fullname = f"@{receiver_sender.username}" if receiver_sender and getattr(receiver_sender, 'username', None) else "Agent Target"
    r_mention = f"<a href='tg://user?id={receiver_id}'><b>{escape_html(r_fullname)}</b></a>"

    await users_catcher_col.update_one(
        {"user_id": receiver_id},
        {
            "$push": {"harem": {"char_id": char_id, "caught_date": time.time(), "rarity": char_item.get("rarity", "Unknown")}}, 
            "$inc": {"total_caught": 1}, 
            "$set": {"fullname": r_mention}
        },
        upsert=True
    )
    await event.reply(
        f"🎁 <b>{f('ASSET TRANSFER SECURED / လက်ဆောင်ပေးမှု အောင်မြင်သည်')}</b>\n"
        f"⚡PARADOX Family:BOD⚡\n"
        f"<blockquote><b>{f('Successful Sent')}!</b> <code>{char_id}</code> ပိုင်ဆိုင်မှုကတ်ကို {r_mention} ထံသို့ လုံခြုံစိတ်ချစွာ လွှဲပြောင်းပေးအပ်လိုက်ပါပြီ Bestie! ⚡🤝</blockquote>\n"
        f"⚡ ━━━━━⚡", 
        parse_mode='html'
    )

# ==========================================
# 🤝 14. PEER TRADE MATRIX (/trade)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/trade\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)$'))
async def trade_proposal_handler(event):
    if not event.is_reply: 
        return await event.reply(f"❌ <b>{f('Trade လုပ်မယ့်သူရဲ့ စာကို Reply ပြန်ပြီး ခေါ်ယူပေးပါ Bro!')}</b>", parse_mode='html')
    
    my_char_id = event.pattern_match.group(1).upper()
    their_char_id = event.pattern_match.group(2).upper()
    
    sender_id = event.sender_id
    reply_msg = await event.get_reply_message()
    target_user_id = reply_msg.sender_id
    
    if sender_id == target_user_id: return
    
    s_doc = await users_catcher_col.find_one({"user_id": sender_id})
    t_doc = await users_catcher_col.find_one({"user_id": target_user_id})
    
    s_harem = s_doc.get("harem", []) if s_doc else []
    t_harem = t_doc.get("harem", []) if t_doc else []
    
    s_has = any(isinstance(x, dict) and x.get("char_id") == my_char_id for x in s_harem)
    t_has = any(isinstance(x, dict) and x.get("char_id") == their_char_id for x in t_harem)
    
    if not s_has:
        return await event.reply(f"❌ သင့်ထံတွင် ID: <code>{my_char_id}</code> မရှိပါ Bro!", parse_mode='html')
    if not t_has:
        return await event.reply(f"❌ ၎င်းထံတွင် ID: <code>{their_char_id}</code> မရှိပါ Bro!", parse_mode='html')
        
    s_char = await characters_base_col.find_one({"char_id": my_char_id})
    t_char = await characters_base_col.find_one({"char_id": their_char_id})
    
    trade_text = (
        f"🤝 <b>{f('EXCHANGE CONTRACT / ဖလှယ်မှု စာချုပ်')}</b>\n"
        f"⚡PARADOX Family:BOD⚡\n"
        f"📤 <b>{f('Your Offer')}:</b> <code>{s_char['name']}</code> ({my_char_id})\n"
        f"📥 <b>{f('Their Request')}:</b> <code>{t_char['name']}</code> ({their_char_id})\n"
        f"⚡ ━━━━ ⚡\n"
        f"<blockquote><b>{f('Notice')}:</b> ဒီစာချုပ်ကို အတည်ပြုဖို့ ဆုံးဖြတ်ပိုင်ခွင့်က ကမ်းလှမ်းခံရသူထံမှာပဲ ရှိပါတယ်နော် Bro! ⚡👀</blockquote>"
    )
    
    buttons = [[
        Button.inline("🤝 Confirm Contract", data=f"tr_conf_{sender_id}_{target_user_id}_{my_char_id}_{their_char_id}"),
        Button.inline("❌ Void Contract", data=f"tr_canc_{sender_id}_{target_user_id}")
    ]]
    await event.reply(trade_text, parse_mode='html', buttons=buttons)

# ==========================================
# ⚙️ 15. CHANGE SPAWN TIME/COUNT TRIGGER (/changetime)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/changetime\s+(\d+)$'))
async def change_spawn_target_handler(event):
    if event.sender_id != OWNER_ID: return
    new_target = int(event.pattern_match.group(1))
    
    if new_target <= 0:
        return await event.reply(f"❌ <b>{f('Target count must be greater than 0!')}</b>", parse_mode='html')
        
    await groups_config_col.update_one(
        {"chat_id": event.chat_id},
        {"$set": {"spawn_target": new_target}},
        upsert=True
    )
    
    success_text = (
        f"⚙️ <b>{f('SPAWN THRESHOLD UPDATED / သတ်မှတ်ချက် ပြောင်းလဲပြီးပါပြီ')}</b>\n"
        f"<blockquote><b>{f('Config Locked')}!</b> ဒီဂရုမှာ ကတ်အလိုအလျောက်ထွက်မယ့် စာစောင်ရေ အရေအတွက်ကို <code>{new_target}</code> စောင်သို့ ပြောင်းလဲသတ်မှတ်လိုက်ပါပြီ Boss! ⚡🥷</blockquote>\n"
        f"⚡"
    )
    await event.reply(success_text, parse_mode='html')

# ==========================================
# 📜 16. HELPMENU PANELS (/helpp & /owner)
# ==========================================
@bot1.on(events.NewMessage(pattern=r'^/helpp(?:@\w+)?$'))
async def public_help_handler(event):
    help_text = (
        f"🌌 <b>{f('SOVEREIGN MULTI-UNIVERSE HELPMENU')}</b>\n"
        f"⚡ ━━━━━━━━━━━━━━━━━━━━ ⚡\n"
        f"ℹ️ <b>{f('GLOBAL MATRIX COMMANDS / အများသုံးစနစ်များ')}:</b>\n\n"
        f"🔘 <code>/hai</code> — သင့်ပိုင်ဆိုင်မှု Showroom ပြခန်းကို ကြည့်ရန် 🎒\n\n"
        f"🔘 <code>/fav [ID]</code> — မိမိကြိုက်နှစ်သက်ရာ Favorite နောက်ခံ မီဒီယာသတ်မှတ်ရန် ⭐️\n\n"
        f"🔘 <code>/profile</code> — သင့်ရဲ့ User Profile ဒေတာကို စစ်ဆေးရန် 👤\n\n"
        f"🔘 <code>/top</code> — ယခု Group ထဲမှာ ကတ်အများဆုံးရထားတဲ့ Top 10 လူစာရင်း 🏆\n\n"
        f"🔘 <code>/gtop</code> — Bot သုံးထားတဲ့ Group အားလုံးထဲက Top 10 လူစာရင်း 🌐\n\n"
        f"🔘 <code>/who</code> — ပေါ်နေတဲ့ ပုဂ္ဂိုလ်ရဲ့ အချက်အလက် သဲလွန်စကို စစ်ဆေးရန် 👀\n\n"
        f"🔘 <code>/catch [Name]</code> — ပုဂ္ဂိုလ်တွေကို သင့်ရဲ့ Vault ထဲ ဖမ်းယူသိမ်းပိုက်ရန် 🎯\n\n"
        f"🔘 <code>/check [ID]</code> — သတ်မှတ် ID ရှိတဲ့ ပုဂ္ဂိုလ်ရဲ့ ကိုယ်ရေးဒေတာ စစ်ဆေးရန် 🔍\n\n"
        f"🔘 <code>/checkp</code> — သင့်ရဲ့ လက်ရှိ ရမှတ်ဗဟို Wallet Balance ကို ကြည့်ရန် 💳\n\n"
        f"🔘 <code>/gift [ID]</code> — ထိုသူ့ထံသို့ ပိုင်ဆိုင်မှုကတ်ကို လက်ဆောင် လွှဲပြောင်းပေးရန် (Reply) 🎁\n\n"
        f"🔘 <code>/sell [ID] [PTS]</code> — စျေးကွက်ထဲသို့ မိမိကတ်ကို သတ်မှတ်စျေးဖြင့် တင်ရောင်းရန် 🛒\n\n"
        f"🔘 <code>/buy [ID]</code> — စျေးကွက်ထဲက အသက်သာဆုံး တင်ထားတဲ့ ကတ်ကို ဝယ်ယူရန် 🛍️\n\n"
        f"🔘 <code>/trade [MyID] [TheirID]</code> — အချင်းချင်း အပြန်အလှန် ကတ်ချင်း ဖလှယ်ရန် (Reply) 🤝\n"
        f"⚡ ━━━━━━━━━━━━━━━━━━━━ ⚡"
    )
    await event.reply(help_text, parse_mode='html')

@bot1.on(events.NewMessage(pattern=r'^/owner$'))
async def exclusive_owner_panel(event):
    if event.sender_id != OWNER_ID: return
    owner_text = (
        f"👑 <b>{f('WELCOME BACK, DEVELOPER!')} ⚔️</b>\n"
        f"⚡ ━━━━━━━━━━━━━━━━━━━━ ⚡\n"
        f"🛠️ <b>{f('ROOT COMMANDS / ဗဟိုထိန်းချုပ်မှုများ')}:</b>\n\n"
        f"⚙️ <code>/addchar Name | Category | Rarity_Num</code>\n"
        f"<blockquote><b>Database ထဲသို့ ကတ်အသစ်များ အတင်းထည့်သွင်းခြင်း။</b>\n"
        f"Rarity Numbers: 1=Legend, 2=Limit, 3=Mythic, 4=Epic, 5=Rare, 6=Common\n"
        f"<i>(Valid တဲ့ Media ဖိုင်တစ်ခုခုကို Reply ပြန်ပြီး သုံးစွဲရပါမယ်)</i></blockquote>\n"
        f"⚙️ <code>/haii</code> သို့မဟုတ် <code>/fspawn</code>\n"
        f"<blockquote><b>မက်ဆေ့ခ်ျရေတွက်မှုကို ကျော်ဖြတ်ပြီး လက်ရှိဂရုထဲမှာ ကတ်တစ်ခု ချက်ချင်း Force Spawn ထုတ်ခြင်း။</b></blockquote>\n"
        f"⚙️ <code>/changetime [Count]</code>\n"
        f"<blockquote><b>ကတ်အလိုအလျောက် ထွက်မယ့် စာစောင်ရေ သတ်မှတ်ချက်ကို ပြောင်းလဲခြင်း။</b>\n"
        f"ဥပမာ - <code>/changetime 30</code> လို့ ရိုက်လိုက်ရင် စာ ၃၀ ပြည့်တိုင်း ကတ်တစ်ခု ထွက်လာပါလိမ့်မယ်။</blockquote>\n"
        f"⚡ ━━━━━━━━━━━━━━━━━━━━ ⚡"
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

