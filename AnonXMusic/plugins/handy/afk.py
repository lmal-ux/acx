from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from datetime import datetime
from AnonXMusic.core.mongo import mongodb
from AnonXMusic import app
# --- In-memory AFK cache ---
afk_users = {}
afkdb = mongodb.afk

# --- Helper Functions ---
def get_afk_user_duration(since):
    delta = datetime.now() - since
    seconds = int(delta.total_seconds())
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days: duration.append(f"{days}d")
    if hours: duration.append(f"{hours}h")
    if minutes: duration.append(f"{minutes}m")
    duration.append(f"{seconds}s")
    return " ".join(duration)

def format_afk_message(user_first_name, reason, duration):
    duration_fmt = f"<code>{duration}</code>"
    if reason:
        return f"{user_first_name} is AFK: {reason} (since {duration_fmt})."
    else:
        return f"{user_first_name} is AFK (since {duration_fmt})."

async def set_afk(user, reason=None):
    afk_data = {
        "user": {
            "id": user.id,
            "first_name": user.first_name,
        },
        "reason": reason,
        "since": datetime.now()
    }
    # In-memory
    afk_users[user.id] = afk_data
    # Persistent (upsert)
    await afkdb.update_one(
        {"user.id": user.id},
        {"$set": afk_data},
        upsert=True
    )

async def get_afk(user_id):
    # In-memory check first
    data = afk_users.get(user_id)
    if data:
        return data

    # Check MongoDB if not in-memory
    data = await afkdb.find_one({"user.id": user_id})
    if data:
        # MongoDB stores "since" as a datetime object — ensure correct type
        if isinstance(data["since"], str):
            data["since"] = datetime.fromisoformat(data["since"])
        afk_users[user_id] = data
    return data

async def remove_afk(user_id):
    # Remove from both
    afk_users.pop(user_id, None)
    await afkdb.delete_one({"user.id": user_id})

# --- AFK Command Handler ---
@app.on_message(filters.command("afk") & filters.group,2)
async def afk_command(_, message: Message):
    user = message.from_user
    reason = " ".join(message.command[1:]).strip() or None

    await set_afk(user, reason)
    response = f"{user.mention} is now AFK."
    if reason:
        response += f"\nReason: {reason}"
    await message.reply(response)

# --- Main AFK Checker ---
@app.on_message(filters.all & ~filters.service & filters.group,2)
async def afk_user_handler(_, message: Message):
    
    user = getattr(message, "from_user", None)
    
    # Check if sender was AFK
    if user:
        afk_data = await get_afk(user.id)
        if afk_data:
            await remove_afk(user.id)
            duration = get_afk_user_duration(afk_data["since"])
            duration_fmt = f"<code>{duration}</code>"
            await message.reply(
                f"Welcome back, {user.mention}! You were AFK for {duration_fmt}."
            )
            # return

    # Check if replied user is AFK
    if message.reply_to_message:
        replied_user = message.reply_to_message.from_user
        if replied_user:
            afk_data = await get_afk(replied_user.id)
            if afk_data:
                duration = get_afk_user_duration(afk_data["since"])
                text = format_afk_message(
                    replied_user.mention, afk_data["reason"], duration
                )
                await message.reply(text)
                # return

    # Check mentioned users
    mentioned_users = []
    if message.entities:
        for entity in message.entities:
            if entity.type == MessageEntityType.TEXT_MENTION:
                mentioned_users.append(entity.user)
            elif entity.type == MessageEntityType.MENTION:
                username = message.text[entity.offset : entity.offset + entity.length]
                try:
                    mentioned_user = await app.get_users(username)
                    if mentioned_user:
                        mentioned_users.append(mentioned_user)
                except Exception:
                    pass

    for u in mentioned_users:
        afk_data = await get_afk(u.id)
        if afk_data:
            duration = get_afk_user_duration(afk_data["since"])
            text = format_afk_message(
                u.mention, afk_data["reason"], duration
            )
            await message.reply(text)
            # break  # stop after first AFK mention
