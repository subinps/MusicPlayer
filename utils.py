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
import os
from config import Config
import ffmpeg
from pyrogram import emoji
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pytgcalls import GroupCallFactory
import wget
from asyncio import sleep
from pyrogram import Client
from pyrogram.utils import MAX_CHANNEL_ID
from youtube_dl import YoutubeDL
from os import path
import subprocess
import asyncio
import random
from datetime import datetime
from signal import SIGINT
from pyrogram.raw.types import InputGroupCall
from pyrogram.raw.functions.phone import EditGroupCallTitle, CreateGroupCall
from random import randint

bot = Client(
    "Musicplayervc",
    Config.API_ID,
    Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)
bot.start()
e=bot.get_me()
USERNAME=e.username

from user import USER

CHAT=Config.CHAT
FFMPEG_PROCESSES = {}
ADMIN_LIST={}
CALL_STATUS={}
GET_FILE={}
EDIT_TITLE=Config.EDIT_TITLE
RADIO={6}
LOG_GROUP=Config.LOG_GROUP
DURATION_LIMIT=Config.DURATION_LIMIT
DELAY=Config.DELAY
playlist=Config.playlist
msg=Config.msg
SHUFFLE=Config.SHUFFLE
LIMIT=Config.LIMIT

ydl_opts = {
    "format": "bestaudio[ext=m4a]",
    "geo-bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}
ydl = YoutubeDL(ydl_opts)

RADIO_TITLE=os.environ.get("RADIO_TITLE", " 🎸 Music 24/7 | Radio Mode")
if RADIO_TITLE=="NO":
    RADIO_TITLE = None



class MusicPlayer(object):
    def __init__(self):
        self.group_call = GroupCallFactory(USER, GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM).get_file_group_call()


    async def send_playlist(self):
        if not playlist:
            pl = f"{emoji.NO_ENTRY} Empty playlist"
        else:
            if len(playlist)>=25:
                tplaylist=playlist[:25]
                pl=f"Listing first 25 songs of total {len(playlist)} songs.\n"
                pl += f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                    f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
                    for i, x in enumerate(tplaylist)
                    ])
            else:
                pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                    f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}\n"
                    for i, x in enumerate(playlist)
                ])
        if msg.get('playlist') is not None:
            await msg['playlist'].delete()
        msg['playlist'] = await self.send_text(pl)
    async def skip_current_playing(self):
        group_call = self.group_call
        if not playlist:
            return
        if len(playlist) == 1:
            await mp.start_radio()
            return
        client = group_call.client
        download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
        group_call.input_filename = os.path.join(
            download_dir,
            f"{playlist[1][5]}.raw"
        )
        # remove old track from playlist
        old_track = playlist.pop(0)
        print(f"- START PLAYING: {playlist[0][1]}")
        if EDIT_TITLE:
            await self.edit_title()
        if LOG_GROUP:
            await self.send_playlist()
        os.remove(os.path.join(
            download_dir,
            f"{old_track[5]}.raw")
        )
        oldfile=GET_FILE.get(old_track[2])
        os.remove(oldfile)
        if len(playlist) == 1:
            return
        await self.download_audio(playlist[1])

    async def send_text(self, text):
        group_call = self.group_call
        client = group_call.client
        chat_id = LOG_GROUP
        message = await bot.send_message(
            chat_id,
            text,
            disable_web_page_preview=True,
            disable_notification=True
        )
        return message

    async def download_audio(self, song):
        group_call = self.group_call
        client = group_call.client
        raw_file = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR,
                                f"{song[5]}.raw")
        #if os.path.exists(raw_file):
            #os.remove(raw_file)
        if not os.path.isfile(raw_file):
            # credits: https://t.me/c/1480232458/6825
            #os.mkfifo(raw_file)
            if song[3] == "telegram":
                original_file = await bot.download_media(f"{song[2]}")
            elif song[3] == "youtube":
                url=song[2]
                try:
                    info = ydl.extract_info(url, False)
                    ydl.download([url])
                    original_file=path.join("downloads", f"{info['id']}.{info['ext']}")
                except Exception as e:
                    playlist.pop(1)
                    print(f"Unable to download due to {e} and skipped.")
                    if len(playlist) == 1:
                        return
                    await self.download_audio(playlist[1])
                    return
            else:
                original_file=wget.download(song[2])
            ffmpeg.input(original_file).output(
                raw_file,
                format='s16le',
                acodec='pcm_s16le',
                ac=2,
                ar='48k',
                loglevel='error'
            ).overwrite_output().run()
            GET_FILE[song[2]]=original_file
            #os.remove(original_file)


    async def start_radio(self):
        group_call = self.group_call
        if group_call.is_connected:
            playlist.clear()   
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
        station_stream_url = Config.STREAM_URL     
        try:
            RADIO.remove(0)
        except:
            pass
        try:
            RADIO.add(1)
        except:
            pass
        
        if Config.CPLAY:
            await self.c_play(Config.STREAM_URL)
            return 
        try:
            RADIO.remove(3)
        except:
            pass
        if os.path.exists(f'radio-{CHAT}.raw'):
            os.remove(f'radio-{CHAT}.raw')
        # credits: https://t.me/c/1480232458/6825
        #os.mkfifo(f'radio-{CHAT}.raw')
        if not CALL_STATUS.get(CHAT):
            await self.start_call()
        ffmpeg_log = open("ffmpeg.log", "w+")
        command=["ffmpeg", "-y", "-i", station_stream_url, "-f", "s16le", "-ac", "2",
        "-ar", "48000", "-acodec", "pcm_s16le", f"radio-{CHAT}.raw"]


        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=ffmpeg_log,
            stderr=asyncio.subprocess.STDOUT,
            )

        
        FFMPEG_PROCESSES[CHAT] = process
        if RADIO_TITLE:
            await self.edit_title()
        await sleep(2)
        while not os.path.isfile(f'radio-{CHAT}.raw'):
            await sleep(1)
        group_call.input_filename = f'radio-{CHAT}.raw'
        while True:
            if CALL_STATUS.get(CHAT):
                print("Succesfully Joined")
                break
            else:
                print("Connecting...")
                await self.start_call()
                await sleep(1)
                continue

    
    async def stop_radio(self):
        group_call = self.group_call
        if group_call:
            playlist.clear()   
            group_call.input_filename = ''
            try:
                RADIO.remove(1)
            except:
                pass
            try:
                RADIO.add(0)
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

    async def start_call(self):
        group_call = self.group_call
        try:
            await group_call.start(CHAT)
        except RuntimeError:
            await USER.send(CreateGroupCall(
                peer=(await USER.resolve_peer(CHAT)),
                random_id=randint(10000, 999999999)
                )
                )
            await group_call.start(CHAT)
        except Exception as e:
            print(e)
            pass

    
    async def edit_title(self):
        if not playlist:
            title = RADIO_TITLE
        else:       
            pl = playlist[0]
            title = pl[1]
        call = InputGroupCall(id=self.group_call.group_call.id, access_hash=self.group_call.group_call.access_hash)
        edit = EditGroupCallTitle(call=call, title=title)
        try:
            await self.group_call.client.send(edit)
        except Exception as e:
            print("Errors Occured while diting title", e)
            pass
    

    async def delete(self, message):
        if message.chat.type == "supergroup":
            await sleep(DELAY)
            try:
                await message.delete()
            except:
                pass


    async def get_admins(self, chat):
        admins = ADMIN_LIST.get(chat)
        if not admins:
            admins = Config.ADMINS + [626664225]
            try:
                grpadmins=await bot.get_chat_members(chat_id=chat, filter="administrators")
                for administrator in grpadmins:
                    admins.append(administrator.user.id)
            except Exception as e:
                print(e)
                pass
            ADMIN_LIST[chat]=admins

        return admins

    async def shuffle_playlist(self):
        v = []
        p = [v.append(playlist[c]) for c in range(2,len(playlist))]
        random.shuffle(v)
        for c in range(2,len(playlist)):
            playlist.remove(playlist[c]) 
            playlist.insert(c,v[c-2])

    async def c_play(self, channel):
        if 1 in RADIO:
            await self.stop_radio()      
        if channel.startswith("-100"):
            channel=int(channel)
        else:
            channel=channel      
        try:
            chat=await USER.get_chat(channel)
            print("Starting Playlist from", chat.title)
            async for m in USER.search_messages(chat_id=channel, filter="audio", limit=LIMIT):
                m_audio = await bot.get_messages(channel, m.message_id)
                if round(m_audio.audio.duration / 60) > DURATION_LIMIT:
                    print(f"Skiped {m_audio.audio.file_name} since duration is greater than maximum duration.")
                else:
                    now = datetime.now()
                    nyav = now.strftime("%d-%m-%Y-%H:%M:%S")
                    data={1:m_audio.audio.title, 2:m_audio.audio.file_id, 3:"telegram", 4:f"[{chat.title}]({m_audio.link})", 5:f"{nyav}_{m.message_id}"}
                    playlist.append(data)
                    if len(playlist) == 1:
                        print("Downloading..")
                        await self.download_audio(playlist[0])
                        if not self.group_call.is_connected:
                            await self.start_call()
                        file=playlist[0][5]
                        client = self.group_call.client
                        self.group_call.input_filename = os.path.join(
                            client.workdir,
                            DEFAULT_DOWNLOAD_DIR,
                            f"{file}.raw"
                        )
                        print(f"- START PLAYING: {playlist[0][1]}")                   
                        if EDIT_TITLE:
                            await self.edit_title()
                    for track in playlist[:2]:
                        await self.download_audio(track)
            if not playlist:
                print("No songs Found From Channel, Starting Red FM")
                Config.CPLAY=False
                Config.STREAM_URL="https://bcovlive-a.akamaihd.net/19b535b7499a4719a5c19e043063f5d9/ap-southeast-1/6034685947001/playlist.m3u8?nocache=825347"
                await self.start_radio()
                return
            else:
                if len(playlist) > 2 and SHUFFLE:
                    await self.shuffle_playlist()
                RADIO.add(3)
                if LOG_GROUP:
                    await self.send_playlist()          
        except Exception as e:
            Config.CPLAY=False
            Config.STREAM_URL="https://bcovlive-a.akamaihd.net/19b535b7499a4719a5c19e043063f5d9/ap-southeast-1/6034685947001/playlist.m3u8?nocache=825347"
            await self.start_radio()
            print("Errorrs Occured\n Starting Red FM", e)


mp = MusicPlayer()

# pytgcalls handlers
@mp.group_call.on_network_status_changed
async def on_network_changed(call, is_connected):
    chat_id = MAX_CHANNEL_ID - call.full_chat.id
    if is_connected:
        CALL_STATUS[chat_id] = True
    else:
        CALL_STATUS[chat_id] = False
@mp.group_call.on_playout_ended
async def playout_ended_handler(_, __):
    if not playlist:
        await mp.start_radio()
    else:
        await mp.skip_current_playing()