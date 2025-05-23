import re
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pyrogram.errors import SessionPasswordNeeded, ListenerTimeout

from AnonXMusic import app
from config import BANNED_USERS

PHONE_REGEX = re.compile(r"^\+?\d{10,15}$")


@app.on_message(filters.command("gensession") & filters.private & ~BANNED_USERS)
async def generate_string_session(client: Client, message: Message):
    user_id = message.chat.id

    try:
        # Ask phone number
        await message.reply_text(
            "Please enter your **phone number** with country code (e.g., `+1234567890`) or type `exit` to cancel:",
            parse_mode=ParseMode.MARKDOWN
        )

        for _ in range(3):
            phone_msg = await client.listen(chat_id=user_id, user_id=user_id, timeout=300)

            if not phone_msg.text:
                await client.send_message(user_id, "Invalid input. Please send text.", parse_mode=ParseMode.MARKDOWN)
                continue

            phone_number = phone_msg.text.strip()
            if phone_number.lower() == "exit":
                return await client.send_message(user_id, "Session generation cancelled.", parse_mode=ParseMode.MARKDOWN)

            if PHONE_REGEX.match(phone_number):
                break

            await client.send_message(user_id, "Invalid phone number format. Try again:", parse_mode=ParseMode.MARKDOWN)
        else:
            return await client.send_message(user_id, "Too many invalid attempts. Cancelled.", parse_mode=ParseMode.MARKDOWN)

        await client.send_message(user_id, "Sending code request...", parse_mode=ParseMode.MARKDOWN)

        temp_app = Client(
            name="gen_session", api_id=app.api_id, api_hash=app.api_hash, in_memory=True
        )
        await temp_app.connect()

        try:
            code_info = await temp_app.send_code(phone_number)
        except Exception as e:
            await temp_app.disconnect()
            return await client.send_message(user_id, f"Failed to send code:\n`{e}`", parse_mode=ParseMode.MARKDOWN)

        # Ask for OTP
        await client.send_message(
            user_id,
            "Enter the **OTP** you received (you can include spaces), or type `exit` to cancel:",
            parse_mode=ParseMode.MARKDOWN
        )

        for _ in range(3):
            otp_msg = await client.listen(chat_id=user_id, user_id=user_id, timeout=300)

            if not otp_msg.text:
                await client.send_message(user_id, "Invalid input. Please send text.", parse_mode=ParseMode.MARKDOWN)
                continue

            otp = otp_msg.text.replace(" ", "").strip()
            if otp.lower() == "exit":
                await temp_app.disconnect()
                return await client.send_message(user_id, "Session generation cancelled.", parse_mode=ParseMode.MARKDOWN)

            if otp.isdigit():
                break

            await client.send_message(user_id, "OTP must be numeric. Try again:", parse_mode=ParseMode.MARKDOWN)
        else:
            await temp_app.disconnect()
            return await client.send_message(user_id, "Too many invalid OTP attempts. Cancelled.", parse_mode=ParseMode.MARKDOWN)

        # Login
        try:
            await temp_app.sign_in(phone_number, code_info.phone_code_hash, otp)
        except SessionPasswordNeeded:
            try:
                hint = await temp_app.get_password_hint()
                hint = hint or "No hint is set for this account."
            except Exception:
                hint = "Unable to retrieve password hint."

            await client.send_message(
                user_id,
                f"2FA is enabled.\nPassword hint: `{hint}`\nEnter your **Telegram password** or type `exit` to cancel:",
                parse_mode=ParseMode.MARKDOWN
            )

            for _ in range(3):
                pwd_msg = await client.listen(chat_id=user_id, user_id=user_id, timeout=300)

                if not pwd_msg.text:
                    await client.send_message(user_id, "Invalid input. Please send text.", parse_mode=ParseMode.MARKDOWN)
                    continue

                password = pwd_msg.text.strip()
                if password.lower() == "exit":
                    await temp_app.disconnect()
                    return await client.send_message(user_id, "Session generation cancelled.", parse_mode=ParseMode.MARKDOWN)

                try:
                    await temp_app.check_password(password)
                    break
                except Exception as e:
                    await client.send_message(user_id, f"Incorrect password: `{e}`", parse_mode=ParseMode.MARKDOWN)
            else:
                await temp_app.disconnect()
                return await client.send_message(user_id, "Too many failed password attempts. Cancelled.", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await temp_app.disconnect()
            return await client.send_message(user_id, f"Login failed:\n`{e}`", parse_mode=ParseMode.MARKDOWN)

        # Export string session
        string_session = await temp_app.export_session_string()
        await temp_app.send_message("me", f"**Your Pyrogram String Session:**\n`{string_session}`", parse_mode=ParseMode.MARKDOWN)
        await client.send_message(
            user_id,
            f"**Your Pyrogram String Session:**\n`{string_session}`\n\nThis has also been sent to your Saved Messages.",
            parse_mode=ParseMode.MARKDOWN
        )
        await temp_app.disconnect()

    except ListenerTimeout:
        await client.send_message(user_id, "Received no response. Exiting...", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await client.send_message(user_id, f"An unexpected error occurred:\n`{e}`", parse_mode=ParseMode.MARKDOWN)
