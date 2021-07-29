#MIT License

#Copyright (c) 2021 OXYOP

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

@Client.on_message(filters.command(["radio", f"radio@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT) | filters.private))
async def radio(client, message: Message):
    if 1 in RADIO:
        k=await message.reply_text("Kindly stop existing Radio Stream /stopradio")
        await mp.delete(k)
        await message.delete()
        return
    await mp.start_radio()
    k=await message.reply_text(f"Started Radio: <code>{STREAM}</code>")
    await mp.delete(k)
    await message.delete()

@Client.on_message(filters.command(['stopradio', f"stopradio@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT) | filters.private))
async def stop(_, message: Message):
    if 0 in RADIO:
        k=await message.reply_text("Kindly start Radio First /radio")
        await mp.delete(k)
        await message.delete()
        return
    await mp.stop_radio()
    k=await message.reply_text("Radio stream ended.")
    await mp.delete(k)
    await message.delete()
