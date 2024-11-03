
from pyrogram import Client, filters
import aiohttp
import json
import os
import logging
import time  
import schedule
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Store your credentials securely (avoid hardcoding in production)
api_id = '12997033'
api_hash = '31ee7eb1bf2139d96a1147f3553e0364'
bot_token = '7840927612:AAEuphtFALZwxp6MwT36SQw_rQ0TSbKBHOk'

grp_id = -1002308237145
server_ip = "istanbull.falixsrv.me"
api_url = f"https://api.mcsrvstat.us/3/{server_ip}"
webapp_url = "https://t.me/IstanbulSrvXBot/IstanbulServer"

# Initialize Pyrogram client with bot token
app = Client("minecraft_server_checker", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start") & filters.private)
async def bot_online(client, message):
    await message.reply_text("For private use only")
    
@app.on_message(filters.command("start") & filters.chat(grp_id))
async def bot_online(client, message):
    # Define buttons with URL (webapp_url should be defined beforehand)
    buttons = [
        [InlineKeyboardButton("Server", web_app=WebAppInfo(url=webapp_url))]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    
    # Send the message with the keyboard
    await message.reply_text("Glory To The God", reply_markup=keyboard)

@app.on_message(filters.command("check") & filters.chat(grp_id))
async def check_minecraft_server(client, message):
    loading_message = await message.reply("Checking server status...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data. HTTP status code: {response.status}")

                data = await response.json()

        ip_address = data.get("ip", "N/A")
        version = data.get("version", "Unknown")
        players = data.get("players", {})
        player_count = players.get("online", 0)
        max_players = players.get("max", 0)

        result_message = (f"**🖥️ Server Status:**\n"
                          f"**🌐 IP**: {ip_address}\n"
                          f"**🔄 Version**: {version}\n"
                          f"**👥 Players**: {player_count}/{max_players}")

    except Exception as e:
        result_message = "An error occurred while checking the server status."
        logging.error(f"Error while checking server status: {e}")

    await loading_message.edit_text(result_message)

@app.on_message(filters.command("json") & filters.chat(grp_id))
async def get_json_response(client, message):
    loading_message = await message.reply("Fetching JSON response...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data. HTTP status code: {response.status}")

                data = await response.json()

        file_path = "minecraft_server_status.txt"
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        await client.send_document(message.chat.id, file_path, caption="Here is the JSON response.")
        logging.info(f"JSON response saved to {file_path} and sent to user.")
        
        try:
            os.remove(file_path)
        except Exception as e:
            logging.error(f"Failed to delete the file: {e}")

    except Exception as e:
        result_message = "An error occurred while fetching the JSON response."
        logging.error(f"Error while fetching JSON response: {e}")
        await loading_message.edit_text(result_message)

@app.on_message(filters.command("ping") & filters.chat(grp_id))
async def ping_server(client, message):
    loading_message = await message.reply("Pinging the Minecraft Server...")
    
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data. HTTP status code: {response.status}")

        end_time = time.time()
        ping_time = (end_time - start_time) * 1000

        result_message = f"**🏓 Server Ping:** {ping_time:.2f} ms"
        
    except Exception as e:
        result_message = "An error occurred while pinging the server."
        logging.error(f"Error while pinging server: {e}")

    await loading_message.edit_text(result_message)

# Target chat and users list
target_chat_id = -1002308237145  # Ensure this is correct
users = ['username0', 'Whymeleft', 'unknown_whitey', 'px181']
current_user_index = 0
last_message_id = None

# Function to send and delete messages
async def send_and_delete_message():
    global current_user_index, last_message_id

    # Delete previous message if exists
    if last_message_id:
        await app.delete_messages(chat_id=target_chat_id, message_ids=last_message_id)

    # Send a new message tagging the next user
    user_to_tag = users[current_user_index]
    message = await app.send_message(target_chat_id, f"its your turn to 'Add Time', @{user_to_tag}!")
    last_message_id = message.message_id

    # Move to the next user in the list
    current_user_index = (current_user_index + 1) % len(users)

# Schedule to run every 2 hours
schedule.every(2).hours.do(lambda: app.loop.create_task(send_and_delete_message()))

if __name__ == "__main__":
    logging.info("Starting the bot...")

    # Main loop to keep the bot running and check schedule
    app.start()
    while True:
        schedule.run_pending()
        time.sleep(60)
    app.stop()
    logging.info("Bot has been stopped.")
