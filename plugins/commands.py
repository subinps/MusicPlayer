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
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
import signal
from utils import USERNAME, FFMPEG_PROCESSES, mp
from config import Config
import os
import sys
U=USERNAME
CHAT=Config.CHAT
msg=Config.msg
HOME_TEXT = "<b>Helo, [{}](tg://user?id={})\n\nIam MusicPlayer 2.0 which plays music in Channels and Groups 24*7.\n\nI can even Stream Youtube Live in Your Voicechat.\n\nDeploy Your Own bot from source code below.\n\nHit /help to know about available commands.</b>"
HELP = """

<b>Add the bot and User account in your Group with admin rights.

Start a VoiceChat.

Use /play <song name> or use /play as a reply to an audio file or youtube link.

You can also use /dplay <song name> to play a song from Deezer.</b>

**Common Commands**:

**/play**  Reply to an audio file or YouTube link to play it or use /play <song name>.
**/dplay** Play music from Deezer, Use /dplay <song name>
**/player**  Show current playing song.
**/help** Show help for commands
**/playlist** Shows the playlist.

**Admin Commands**:
**/skip** [n] ...  Skip current or n where n >= 2
**/join**  Join voice chat.
**/leave**  Leave current voice chat
**/vc**  Check which VC is joined.
**/stop**  Stop playing.
**/radio** Start Radio.
**/stopradio** Stops Radio Stream.
**/replay**  Play from the beginning.
**/clean** Remove unused RAW PCM files.
**/pause** Pause playing.
**/resume** Resume playing.
**/mute**  Mute in VC.
**/unmute**  Unmute in VC.
**/restart** Restarts the Bot.
"""



@Client.on_message(filters.command(['start', f'start@{U}']))
async def start(client, message):
    buttons = [
        [
        InlineKeyboardButton('⚙️ About Me', url='https://t.me/FallenAngel_xD'),
        InlineKeyboardButton('🤖 My Owner', url='https://t.me/FallenAngel_xD/122'),
    ],
    [
        InlineKeyboardButton('👨🏼‍💻 Developer', url='https://t.me/FallenAngel_xD'),
        InlineKeyboardButton('🧩 Source', url='https://github.com/OxyNotOp/OxyPlayer'),
    ],
    [
        InlineKeyboardButton('👨🏼‍🦯 Help', callback_data='help'),
        
    ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    m=await message.reply(HOME_TEXT.format(message.from_user.first_name, message.from_user.id), reply_markup=reply_markup)
    await mp.delete(m)
    await message.delete()



@Client.on_message(filters.command(["help", f"help@{U}"]))
async def show_help(client, message):
    buttons = [
        [
            InlineKeyboardButton('⚙️ About Me', url='https://t.me/FallenAngel_xD'),
            InlineKeyboardButton('🤖 My Owner', url='https://t.me/FallenAngel_xD/122'),
        ],
        [
            InlineKeyboardButton('👨🏼‍💻 Developer', url='https://t.me/FallenAngel_xD'),
            InlineKeyboardButton('🧩 Source', url='https://github.com/OxyNotOp/OxyPlayer'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    if msg.get('help') is not None:
        await msg['help'].delete()
    msg['help'] = await message.reply_text(
        HELP,
        reply_markup=reply_markup
        )
    await message.delete()
@Client.on_message(filters.command(["restart", f"restart@{U}"]) & filters.user(Config.ADMINS) & (filters.chat(CHAT) | filters.private))
async def restart(client, message):
    await message.reply_text("🔄 Restarting...")
    await message.delete()
    process = FFMPEG_PROCESSES.get(CHAT)
    if process:
        process.send_signal(signal.SIGTERM) 
    os.execl(sys.executable, sys.executable, *sys.argv)
    
