from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os
import json

OWNER_ID = 1927883599
USERS_FILE = 'users.json'
LOG_FILE_EXTENSION = '.txt'

# Load user IDs from a JSON file
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return []

# Save user IDs to a JSON file
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    users = load_users()

    if user_id == OWNER_ID:
        pass
    elif user_id not in users:
        await update.message.reply_text(f"সবাগত! আপনর ইউজর আইডি: {user_id}.")
        await update.message.reply_text("আপনর কাছে এই বট ব্যবহারের অনুমতি নেই।")
        return

    keyboard = [[InlineKeyboardButton("ডোমেইন অনুসন্ধান করুন", callback_data='search_domain')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("আপনার ডোমেইন অনুসন্ধান করতে নিচের বাটনে ক্লিক করুন:", reply_markup=reply_markup)

def find_matching_lines(domain: str) -> list:
    files = [f for f in os.listdir('.') if f.endswith(LOG_FILE_EXTENSION)]

    if not files:
        return None  # No log files found

    matches = []
    for file_name in files:
        with open(file_name, 'r', encoding='utf-8', errors='ignore') as input_file:
            for line in input_file:
                if domain in line:
                    matches.append(line.strip())

    return matches

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    users = load_users()

    if user_id != OWNER_ID and user_id not in users:
        await update.message.reply_text("আপনর কাছে এই বট ব্যবহারের অনুমতি নেই।")
        return

    domain = update.message.text.strip()

    # Send "please wait, filtering..." message
    wait_message = await update.message.reply_text("দয়া করে অপেক্ষা করুন, ফিল্টারিং হচ্ছে...")

    matches = find_matching_lines(domain)

    if matches is None:
        await update.message.reply_text("কোনো লগ ফাইল পাওয়া যায়নি।")
        await wait_message.delete()
        return

    if matches:
        result_text = "\n".join(matches)
        output_file_name = f"s14m_69_{domain}.txt"
        with open(output_file_name, 'w') as file:
            file.write(result_text)

        with open(output_file_name, 'rb') as file:
            await update.message.reply_document(file, filename=output_file_name)

        os.remove(output_file_name)

        keyboard = [[InlineKeyboardButton("পুনরায় অনুসন্ধান", callback_data='re_search')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("আপনার লগ ফাইল পাঠানো হয়েছে। আপনি কি পুনরায় অনুসন্ধান করতে চান?", reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"{domain} এর জন্য কোনো লগ পাওয়া যায়নি।")

    # Delete the "please wait" message
    await wait_message.delete()

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    if query.data == 're_search':
        await query.message.reply_text("আমাকে একটি ডোমেইন নাম প্রদান করুন।")
    elif query.data == 'search_domain':
        await query.message.reply_text("অনুগ্রহ করে একটি ডোমেইন নাম প্রদান করুন।")

async def user_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("আপনর কাছে এই কমান্ড ব্যবহারের অনুমতি নেই।")
        return

    if context.args:
        new_user_id = int(context.args[0])
        users = load_users()

        if new_user_id not in users:
            users.append(new_user_id)
            save_users(users)
            await update.message.reply_text(f"ব্যবহারকারী {new_user_id} যোগ করা হয়েছে।")
        else:
            await update.message.reply_text("ব্যবহারকারী ইতিমধ্যেই তালিকায় রয়েছে।")
    else:
        await update.message.reply_text("ব্যবহারকারীর আইডি সরবরাহ করুন।")

async def user_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("আপনর কাছে এই কমান্ড ব্যবহারের অনুমতি নেই।")
        return

    if context.args:
        remove_user_id = int(context.args[0])
        users = load_users()

        if remove_user_id in users:
            users.remove(remove_user_id)
            save_users(users)
            await update.message.reply_text(f"ব্যবহারকারী {remove_user_id} সরানো হয়েছে।")
        else:
            await update.message.reply_text("ব্যবহারকারী তালিকায় নেই।")
    else:
        await update.message.reply_text("ব্যবহারকারীর আইডি সরবরাহ করুন।")

async def delete_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("আপনর কাছে এই কমান্ড ব্যবহারের অনুমতি নেই।")
        return

    files = [f for f in os.listdir('.') if f.endswith(LOG_FILE_EXTENSION)]
    if files:
        for file_name in files:
            os.remove(file_name)
        await update.message.reply_text("সকল লগ ফাইল সফলভাবে মুছে ফেলা হয়েছে।")
    else:
        await update.message.reply_text("কোনো লগ ফাইল পাওয়া যায়নি।")

def main() -> None:
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN_HERE").build()  # Replace with your actual bot token

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("user_add", user_add))
    app.add_handler(CommandHandler("user_remove", user_remove))
    app.add_handler(CommandHandler("delete", delete_logs))  # Add the delete command
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_button))

    app.run_polling()

if __name__ == "__main__":
    main()
