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
from pyrogram import Client, idle, filters
import os
from config import Config
from utils import mp, USERNAME
from pyrogram.raw import functions, types

CHAT=Config.CHAT
bot = Client(
    "Musicplayer",
    Config.API_ID,
    Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins")
)
if not os.path.isdir("./downloads"):
    os.makedirs("./downloads")
async def main():
    async with bot:
        await mp.start_radio()

bot.run(main())
bot.start()
bot.send(
    functions.bots.SetBotCommands(
        commands=[
            types.BotCommand(
                command="start",
                description="Check if bot alive"
            ),
            types.BotCommand(
                command="help",
                description="Shows help message"
            ),
            types.BotCommand(
                command="play",
                description="Play song from youtube/audiofile"
            ),
            types.BotCommand(
                command="dplay",
                description="Play song from Deezer"
            ),
            types.BotCommand(
                command="player",
                description="Shows current playing song with controls"
            ),
            types.BotCommand(
                command="playlist",
                description="Shows the playlist"
            ),
            types.BotCommand(
                command="skip",
                description="Skip the current song"
            ),
            types.BotCommand(
                command="join",
                description="Join VC"
            ),
            types.BotCommand(
                command="leave",
                description="Leave from VC"
            ),
            types.BotCommand(
                command="vc",
                description="Ckeck if VC is joined"
            ),
            types.BotCommand(
                command="stop",
                description="Stops Playing"
            ),
            types.BotCommand(
                command="radio",
                description="Start radio / Live stream"
            ),
            types.BotCommand(
                command="stopradio",
                description="Stops radio/Livestream"
            ),
            types.BotCommand(
                command="replay",
                description="Replay from beggining"
            ),
            types.BotCommand(
                command="clean",
                description="Cleans RAW files"
            ),
            types.BotCommand(
                command="pause",
                description="Pause the song"
            ),
            types.BotCommand(
                command="resume",
                description="Resume the paused song"
            ),
            types.BotCommand(
                command="mute",
                description="Mute in VC"
            ),
            types.BotCommand(
                command="unmute",
                description="Unmute in VC"
            ),
            types.BotCommand(
                command="restart",
                description="Restart the bot"
            )
        ]
    )
)

idle()
bot.stop()
