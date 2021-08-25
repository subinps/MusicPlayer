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
try:
    import asyncio
    from pyrogram import Client, idle, filters
    import os
    from config import Config
    from utils import mp, USERNAME, FFMPEG_PROCESSES
    from pyrogram.raw import functions, types
    import os
    import sys
    from time import sleep
    from threading import Thread
    from signal import SIGINT
    import subprocess
    
except ModuleNotFoundError:
    import os
    import sys
    import subprocess
    file=os.path.abspath("requirements.txt")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', file, '--upgrade'])
    os.execl(sys.executable, sys.executable, *sys.argv)


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
def stop_and_restart():
    bot.stop()
    os.system("git pull")
    sleep(10)
    os.execl(sys.executable, sys.executable, *sys.argv)


bot.run(main())
bot.start()

@bot.on_message(filters.command(["restart", f"restart@{USERNAME}"]) & filters.user(Config.ADMINS) & (filters.chat(CHAT) | filters.private))
async def restart(client, message):
    await message.reply_text("🔄 Updating and Restarting...")
    await asyncio.sleep(3)
    try:
        await message.delete()
    except:
        pass
    process = FFMPEG_PROCESSES.get(CHAT)
    if process:
        try:
            process.send_signal(SIGINT)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception as e:
            print(e)
            pass
        FFMPEG_PROCESSES[CHAT] = ""
    Thread(
        target=stop_and_restart
        ).start()    


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
                command="splay",
                description="Play song from JioSaavn, use -a flag to play an album."
            ),
            types.BotCommand(
                command="cplay",
                description="Plays music files from a channel."
            ),
            types.BotCommand(
                command="yplay",
                description="Plays music files from a youtube playlist."
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
                command="clearplaylist",
                description="Clears the current playlist"
            ),
            types.BotCommand(
                command="shuffle",
                description="Shuffle the playlist"
            ),
            types.BotCommand(
                command="export",
                description="Export current playlist as json file for future use."
            ),
            types.BotCommand(
                command="import",
                description="Import a previously exported playlist."
            ),
            types.BotCommand(
                command="upload",
                description="Upload current playing song as audio file."
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
                command="volume",
                description="Set volume between 0-200"
            ),
            types.BotCommand(
                command="unmute",
                description="Unmute in VC"
            ),
            types.BotCommand(
                command="restart",
                description="Update and restart the bot"
            )
        ]
    )
)

idle()
bot.stop()
