#MIT License

#Copyright (c) 2021 SUBIN

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import mp, RADIO, USERNAME
from config import Config
from config import STREAM
CHAT=Config.CHAT
ADMINS=Config.ADMINS

async def is_admin(_, client, message: Message):
    admins = await mp.get_admins(CHAT)
    if message.from_user is None and message.sender_chat:
        return True
    if message.from_user.id in admins:
        return True
    else:
        return False

admin_filter=filters.create(is_admin)   


@Client.on_message(filters.command(["radio", f"radio@{USERNAME}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def radio(client, message: Message):
    if Config.CPLAY:
        if 3 in RADIO:
            k=await message.reply_text("It seems channel play is enabled and playlist is not empty.\nUse /clearplaylist to empty the playlist.")
            await mp.delete(k)
            await mp.delete(message)
            return
        else:
            await mp.start_radio()
            k=await message.reply_text(f"Channel Play from <code>{STREAM}</code> started.")
            await mp.delete(k)
            await mp.delete(message)
            return
    if 1 in RADIO:
        k=await message.reply_text("Kindly stop existing Radio Stream /stopradio")
        await mp.delete(k)
        await mp.delete(message)
        return
    await mp.start_radio()
    k=await message.reply_text(f"Started Radio: <code>{STREAM}</code>")
    await mp.delete(k)
    await mp.delete(message)

@Client.on_message(filters.command(['stopradio', f"stopradio@{USERNAME}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def stop(_, message: Message):
    if Config.CPLAY:
        if 3 not in RADIO:
            k=await message.reply_text("It seems channel play is enabled and playlist is empty.\nUse /radio to restart the playout.")
            await mp.delete(k)
            await mp.delete(message)
            return
        else:
            k=await message.reply_text("It seems channel play is enabled.\nUse /clearplaylist to clear the playlist.")
            await mp.delete(k)
            await mp.delete(message)
            return 
    if 0 in RADIO:
        k=await message.reply_text("Kindly start Radio First /radio")
        await mp.delete(k)
        await mp.delete(message)
        return
    await mp.stop_radio()
    k=await message.reply_text("Radio stream ended.")
    await mp.delete(k)
    await mp.delete(message)
