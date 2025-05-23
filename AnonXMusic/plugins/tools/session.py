import re
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import SessionPasswordNeeded

from AnonXMusic import app
from config import BANNED_USERS

PHONE_REGEX = re.compile(r"^\+?\d{10,15}$")


@app.on_message(filters.command("gensession") & filters.private & ~BANNED_USERS)
async def generate_string_session(client: Client, message: Message):
    user_id = message.chat.id

    try:
        # Phone number
        for _ in range(3):
            response = await client.ask(
                user_id,
                "Please enter your **phone number** with country code (e.g., `+1234567890`) or type `exit` to cancel:",
                timeout=300
            )
            if not response.text:
                await message.reply_text("Invalid input. Please enter a valid phone number.")
                continue
            if response.text.lower() == "exit":
                return await message.reply_text("Session generation cancelled.")
            phone_number = response.text.strip()
            if PHONE_REGEX.match(phone_number):
                break
            await message.reply_text("Invalid phone number format. Try again.")
        else:
            return await message.reply_text("Too many invalid attempts. Cancelled.")

        await message.reply_text("Sending code request...")

        temp_app = Client(name="gen_session", api_id=app.api_id, api_hash=app.api_hash, in_memory=True)
        await temp_app.connect()

        try:
            code_info = await temp_app.send_code(phone_number)
        except Exception as e:
            await temp_app.disconnect()
            return await message.reply_text(f"Failed to send code:\n`{e}`")

        # OTP
        for _ in range(3):
            response = await client.ask(user_id, "Enter the **OTP** you received (you can include spaces), or type `exit` to cancel:", timeout=300)
            if not response.text:
                await message.reply_text("Invalid input. Please enter the OTP.")
                continue
            if response.text.lower() == "exit":
                await temp_app.disconnect()
                return await message.reply_text("Session generation cancelled.")
            otp = response.text.replace(" ", "")
            if otp.isdigit():
                break
            await message.reply_text("OTP must be numeric. Try again.")
        else:
            await temp_app.disconnect()
            return await message.reply_text("Too many invalid OTP attempts. Cancelled.")

        # Login
        try:
            await temp_app.sign_in(phone_number, code_info.phone_code_hash, otp)
        except SessionPasswordNeeded:
            try:
                hint = await temp_app.get_password_hint()
                if not hint:
                    hint = "No hint is set for this account."
            except Exception:
                hint = "Unable to retrieve password hint."

            for _ in range(3):
                response = await client.ask(user_id, f"2FA is enabled.\nPassword hint: `{hint}`\nEnter your **Telegram password** or type `exit` to cancel:", timeout=300)
                if not response.text:
                    await message.reply_text("Invalid input.")
                    continue
                if response.text.lower() == "exit":
                    await temp_app.disconnect()
                    return await message.reply_text("Session generation cancelled.")
                try:
                    await temp_app.check_password(response.text.strip())
                    break
                except Exception as e:
                    await message.reply_text(f"Incorrect password: `{e}`")
            else:
                await temp_app.disconnect()
                return await message.reply_text("Too many failed password attempts. Cancelled.")
        except Exception as e:
            await temp_app.disconnect()
            return await message.reply_text(f"Login failed:\n`{e}`")

        # Done
        string_session = await temp_app.export_session_string()
        await temp_app.send_message("me", f"**Your Pyrogram String Session:**\n`{string_session}`")
        await message.reply_text(f"**Your Pyrogram String Session:**\n`{string_session}`\n\nThis has also been sent to your Saved Messages.")
        await temp_app.disconnect()

    except Exception as e:
        await message.reply_text(f"An unexpected error occurred:\n`{e}`")
