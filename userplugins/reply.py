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
from utils import USERNAME, GET_MESSAGE, PROGRESS
from config import Config
ADMINS=Config.ADMINS
CACHE={}
from pyrogram.errors import BotInlineDisabled

async def in_convo(_, client, message):
    try:
        k=Config.CONV.get(message.reply_to_message.message_id)
    except:
        return False
    if k and k == "START":
        return True
    else:
        return False

async def in_co_nvo(_, client, message):
    try:
        k=Config.CONV.get(message.reply_to_message.message_id)
    except:
        return False
    if k and k == "PLAYLIST":
        return True
    else:
        return False
async def is_reply(_, client, message):
    if Config.REPLY_MESSAGE:
        return True
    else:
        return False

start_filter=filters.create(in_convo)   
playlist_filter=filters.create(in_co_nvo) 
reply_filter=filters.create(is_reply)


@Client.on_message(filters.private & filters.chat(1977947154) & start_filter)
async def get_start(client, message):
    m=message.reply_to_message.message_id
    link=GET_MESSAGE.get(m)
    k=await client.send_message(chat_id="GetPlayListBot", text=link)
    del Config.CONV[m]
    Config.CONV[k.message_id] = "PLAYLIST"
    command, user, url = link.split(" ", 3)
    GET_MESSAGE[k.message_id] = user


@Client.on_message(filters.private & filters.chat(1977947154) & playlist_filter)
async def get_starhhhht(client, message):
    m=message.reply_to_message.message_id
    user=GET_MESSAGE.get(m)
    nva=message
    if nva.text:
        error=nva.text
        if "PeerInvalid" in error:
            PROGRESS[int(user)]="peer"
        elif "kicked" in error:
            PROGRESS[int(user)]="kicked"
        elif "nosub" in error:
            PROGRESS[int(user)]="nosub"
        elif "Invalid Url" in error:
            PROGRESS[int(user)]="urlinvalid"
        else:
            PROGRESS[int(user)]=error
    elif nva.document:
        ya=await nva.download()
        PROGRESS[int(user)]=ya
    else:
        PROGRESS[int(user)]="Unknown Error"
    await client.read_history(1977947154)
    del GET_MESSAGE[m]
    del Config.CONV[m]

@Client.on_message(reply_filter & filters.private & ~filters.bot & filters.incoming & ~filters.service & ~filters.me)
async def reply(client, message): 
    try:
        inline = await client.get_inline_bot_results(USERNAME, "ORU_MANDAN_PM_VANNU")
        m=await client.send_inline_bot_result(
            message.chat.id,
            query_id=inline.query_id,
            result_id=inline.results[0].id,
            hide_via=True
            )
        old=CACHE.get(message.chat.id)
        if old:
            await client.delete_messages(message.chat.id, [old["msg"], old["s"]])
        CACHE[message.chat.id]={"msg":m.updates[1].message.id, "s":message.message_id}
    except BotInlineDisabled:
        for admin in ADMINS:
            try:
                await client.send_message(chat_id=admin, text=f"Hey,\nIt seems you have disabled Inline Mode for @{USERNAME}\n\nA Nibba is spaming me in PM, enable inline mode for @{USERNAME} from @Botfather to reply him.")
            except Exception as e:
                print(e)
                pass
    except Exception as e:
        print(e)
        pass
