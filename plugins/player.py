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
import asyncio
import os
from youtube_dl import YoutubeDL
from config import Config
from pyrogram import Client, filters, emoji
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pyrogram.types import Message
from utils import mp, RADIO, USERNAME, FFMPEG_PROCESSES, playlist, GET_FILE
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
from pyrogram import Client
import subprocess
from signal import SIGINT
import re
from datetime import datetime
import requests
import json
import ffmpeg

U=USERNAME
EDIT_TITLE=Config.EDIT_TITLE
LOG_GROUP=Config.LOG_GROUP
ADMIN_ONLY=Config.ADMIN_ONLY
DURATION_LIMIT = Config.DURATION_LIMIT
msg = Config.msg
ADMINS=Config.ADMINS
CHAT=Config.CHAT
LOG_GROUP=Config.LOG_GROUP
GET_THUMB={}
async def is_admin(_, client, message: Message):
    admins = await mp.get_admins(CHAT)
    if message.from_user is None and message.sender_chat:
        return True
    if message.from_user.id in admins:
        return True
    else:
        return False

admin_filter=filters.create(is_admin)   


@Client.on_message(filters.command(["play", f"play@{U}"]) & (filters.chat(CHAT) | filters.private) | filters.audio & filters.private)
async def yplay(_, message: Message):
    if ADMIN_ONLY == "Y":
        admins = await mp.get_admins(CHAT)
        if message.from_user.id not in admins:
            m=await message.reply_sticker("CAADBQADsQIAAtILIVYld1n74e3JuQI")
            await mp.delete(m)
            await mp.delete(message)
            return
    type=""
    yturl=""
    ysearch=""
    if message.audio:
        type="audio"
        m_audio = message
    elif message.reply_to_message and message.reply_to_message.audio:
        type="audio"
        m_audio = message.reply_to_message
    else:
        if message.reply_to_message:
            link=message.reply_to_message.text
            regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
            match = re.match(regex,link)
            if match:
                type="youtube"
                yturl=link
        elif " " in message.text:
            text = message.text.split(" ", 1)
            query = text[1]
            regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
            match = re.match(regex,query)
            if match:
                type="youtube"
                yturl=query
            else:
                type="query"
                ysearch=query
        else:
            d=await message.reply_text("You Didn't gave me anything to play. Send me a audio file or reply /play to an audio file.")
            await mp.delete(d)
            await mp.delete(message)
            return
    user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    group_call = mp.group_call
    if type=="audio":
        if round(m_audio.audio.duration / 60) > DURATION_LIMIT:
            d=await message.reply_text(f"❌ Audios longer than {DURATION_LIMIT} minute(s) aren't allowed, the provided audio is {round(m_audio.audio.duration/60)} minute(s)")
            await mp.delete(d)
            await mp.delete(message)
            return
        if playlist and playlist[-1][2] \
                == m_audio.audio.file_id:
            d=await message.reply_text(f"{emoji.ROBOT} Already added in Playlist")
            await mp.delete(d)
            await mp.delete(message)
            return
        now = datetime.now()
        nyav = now.strftime("%d-%m-%Y-%H:%M:%S")
        data={1:m_audio.audio.title, 2:m_audio.audio.file_id, 3:"telegram", 4:user, 5:f"{nyav}_{message.from_user.id}"}
        playlist.append(data)
        if len(playlist) == 1:
            m_status = await message.reply_text(
                f"{emoji.INBOX_TRAY} Downloading and Processing..."
            )
            await mp.download_audio(playlist[0])
            if 1 in RADIO:
                if group_call:
                    group_call.input_filename = ''
                    RADIO.remove(1)
                    RADIO.add(0)
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
            if not group_call.is_connected:
                await mp.start_call()
            file=playlist[0][5]
            group_call.input_filename = os.path.join(
                _.workdir,
                DEFAULT_DOWNLOAD_DIR,
                f"{file}.raw"
            )

            await m_status.delete()
            print(f"- START PLAYING: {playlist[0][1]}")
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
        if EDIT_TITLE:
            await mp.edit_title()
        if message.chat.type == "private":
            await message.reply_text(pl, disable_web_page_preview=True)        
        elif LOG_GROUP:
            await mp.send_playlist()
        elif not LOG_GROUP and message.chat.type == "supergroup":
            k=await message.reply_text(pl, disable_web_page_preview=True)
            await mp.delete(k)
        for track in playlist[:2]:
            await mp.download_audio(track)


    if type=="youtube" or type=="query":
        if type=="youtube":
            msg = await message.reply_text("⚡️ **Fetching Song From YouTube...**")
            url=yturl
        elif type=="query":
            try:
                msg = await message.reply_text("⚡️ **Fetching Song From YouTube...**")
                ytquery=ysearch
                results = YoutubeSearch(ytquery, max_results=1).to_dict()
                url = f"https://youtube.com{results[0]['url_suffix']}"
                title = results[0]["title"][:40]
            except Exception as e:
                await msg.edit(
                    "Song not found.\nTry inline mode.."
                )
                print(str(e))
                await mp.delete(message)
                await mp.delete(msg)
                return
        else:
            return
        ydl_opts = {
            "geo-bypass": True,
            "nocheckcertificate": True
        }
        ydl = YoutubeDL(ydl_opts)
        try:
            info = ydl.extract_info(url, False)
        except Exception as e:
            print(e)
            k=await msg.edit(
                f"YouTube Download Error ❌\nError:- {e}"
                )
            print(str(e))
            await mp.delete(message)
            await mp.delete(k)
            return
        duration = round(info["duration"] / 60)
        title = info["title"]
        try:
            thumb = info["thumbnail"]
        except:
            thumb="https://telegra.ph/file/181242eab5c4a74916d01.jpg"
            pass
        if int(duration) > DURATION_LIMIT:
            k=await message.reply_text(f"❌ Videos longer than {DURATION_LIMIT} minute(s) aren't allowed, the provided video is {duration} minute(s)")
            await mp.delete(k)
            await mp.delete(message)
            return
        now = datetime.now()
        nyav = now.strftime("%d-%m-%Y-%H:%M:%S")
        data={1:title, 2:url, 3:"youtube", 4:user, 5:f"{nyav}_{message.from_user.id}"}
        GET_THUMB[url]=thumb
        playlist.append(data)
        group_call = mp.group_call
        client = group_call.client
        if len(playlist) == 1:
            m_status = await msg.edit(
                f"{emoji.INBOX_TRAY} Downloading and Processing..."
            )
            await mp.download_audio(playlist[0])
            if 1 in RADIO:
                if group_call:
                    group_call.input_filename = ''
                    RADIO.remove(1)
                    RADIO.add(0)
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
            if not group_call.is_connected:
                await mp.start_call()
            file=playlist[0][5]
            group_call.input_filename = os.path.join(
                client.workdir,
                DEFAULT_DOWNLOAD_DIR,
                f"{file}.raw"
            )

            await m_status.delete()
            print(f"- START PLAYING: {playlist[0][1]}")
        else:
            await msg.delete()
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
        if EDIT_TITLE:
            await mp.edit_title()
        if message.chat.type == "private":
            await message.reply_text(pl, disable_web_page_preview=True)
        if LOG_GROUP:
            await mp.send_playlist()
        elif not LOG_GROUP and message.chat.type == "supergroup":
            k=await message.reply_text(pl, disable_web_page_preview=True)
            await mp.delete(k)
        for track in playlist[:2]:
            await mp.download_audio(track)
    await mp.delete(message)
            
        
   
@Client.on_message(filters.command(["splay", f"splay@{U}"]) & (filters.chat(CHAT) | filters.private))
async def deezer(_, message):
    if ADMIN_ONLY == "Y":
        admins = await mp.get_admins(CHAT)
        if message.from_user.id not in admins:
            k=await message.reply_sticker("CAADBQADsQIAAtILIVYld1n74e3JuQI")
            await mp.delete(k)
            await mp.delete(message)
            return
    user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if " " in message.text:
        query=""
        album=""
        text = message.text.split(" ", 2)
        if text[1]=="-a":
            album=text[2]
            query=None        
        else:
            text = message.text.split(" ", 1)
            query=text[1]
            album=None
    else:
        k=await message.reply_text("You Didn't gave me anything to play use /splay <song name>")
        await mp.delete(k)
        await mp.delete(message)
        return
    user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    group_call = mp.group_call
    if album:
        msg = await message.reply("⚡️ **Fetching Album From JioSaavn...**")
        try:
            p = f"https://jiosaavn-api.vercel.app/albumsearch?query={album}"
            n = requests.get(p)
            a = json.loads(n.text)
            y = a[0].get("id")
            np = f"https://jiosaavn-api.vercel.app/album?id={y}"
            n = requests.get(np)
            a = json.loads(n.text)
            songs = a.get("songs")
            for song in songs:
                url = song.get("media_url")
                title = song.get("song")
                try:
                    thumb=song.get("image")
                except:
                    thumb="https://telegra.ph/file/181242eab5c4a74916d01.jpg"
                    pass
                GET_THUMB[url] = thumb
                now = datetime.now()
                nyav = now.strftime("%d-%m-%Y-%H:%M:%S")
                data={1:title, 2:url, 3:"saavn", 4:user, 5:f"{nyav}_{message.from_user.id}"}
                playlist.append(data)
                group_call = mp.group_call
                client = group_call.client
                if len(playlist) == 1:
                    await mp.download_audio(playlist[0])
                    if 1 in RADIO:
                        if group_call:
                            group_call.input_filename = ''
                            RADIO.remove(1)
                            RADIO.add(0)
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
                    if not group_call.is_connected:
                        await mp.start_call()
                    file=playlist[0][5]
                    group_call.input_filename = os.path.join(
                        client.workdir,
                        DEFAULT_DOWNLOAD_DIR,
                        f"{file}.raw"
                    )
                    print(f"- START PLAYING: {playlist[0][1]}")
                    
                    if EDIT_TITLE:
                        await mp.edit_title()
                for track in playlist[:2]:
                    await mp.download_audio(track)

            await msg.delete()
            if not playlist:
                await mp.start_radio()
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
            if message.chat.type == "private":
                await message.reply_text(pl, disable_web_page_preview=True)
            if LOG_GROUP:
                await mp.send_playlist()
            elif not LOG_GROUP and message.chat.type == "supergroup":
                k=await message.reply_text(pl, disable_web_page_preview=True)
                await mp.delete(k)
            await mp.delete(message)
        except Exception as e:
            k=await msg.edit("Could not find that album.")
            print(e)
            await mp.delete(k)
            await mp.delete(message)
            pass
    else:
        msg = await message.reply("⚡️ **Fetching Song From JioSaavn...**")
        try:
            p = f"https://jiosaavn-api.vercel.app/search?query={query}"
            n = requests.get(p)
            a = json.loads(n.text)
            y = a[0].get("id")
            np = f"https://jiosaavn-api.vercel.app/song?id={y}"
            n = requests.get(np)
            a = json.loads(n.text)
            url = a.get("media_url")
            title = a.get("song")
            try:
                thumb=a.get("image")
            except:
                thumb="https://telegra.ph/file/181242eab5c4a74916d01.jpg"
                pass
            GET_THUMB[url] = thumb
        except:
            k=await msg.edit("No results found")
            await mp.delete(k)
            await mp.delete(message)
            return
        now = datetime.now()
        nyav = now.strftime("%d-%m-%Y-%H:%M:%S")
        data={1:title, 2:url, 3:"saavn", 4:user, 5:f"{nyav}_{message.from_user.id}"}
        playlist.append(data)
        group_call = mp.group_call
        client = group_call.client
        if len(playlist) == 1:
            m_status = await msg.edit(
                f"{emoji.INBOX_TRAY} Downloading and Processing..."
            )
            await mp.download_audio(playlist[0])
            if 1 in RADIO:
                if group_call:
                    group_call.input_filename = ''
                    RADIO.remove(1)
                    RADIO.add(0)
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
            if not group_call.is_connected:
                await mp.start_call()
            file=playlist[0][5]
            group_call.input_filename = os.path.join(
                client.workdir,
                DEFAULT_DOWNLOAD_DIR,
                f"{file}.raw"
            )
            await m_status.delete()
            print(f"- START PLAYING: {playlist[0][1]}")
        else:
            await msg.delete()
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
        if message.chat.type == "private":
            await message.reply_text(pl, disable_web_page_preview=True)
        if EDIT_TITLE:
                await mp.edit_title()
        if LOG_GROUP:
            await mp.send_playlist()
        elif not LOG_GROUP and message.chat.type == "supergroup":
            k=await message.reply_text(pl, disable_web_page_preview=True)
            await mp.delete(k)
        for track in playlist[:2]:
            await mp.download_audio(track)
        await mp.delete(message)

   
@Client.on_message(filters.command(["player", f"player@{U}"]) & (filters.chat(CHAT) | filters.private))
async def player(_, m: Message):
    if not playlist:
        k=await m.reply_text(f"{emoji.NO_ENTRY} No songs are playing")
        await mp.delete(k)
        await mp.delete(m)
        return
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
    if m.chat.type == "private":
        await m.reply_text(
            pl,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔄", callback_data="replay"),
                        InlineKeyboardButton("⏯", callback_data="pause"),
                        InlineKeyboardButton("⏩", callback_data="skip")
                    
                    ],

                ]
                )
        )
    else:
        if msg.get('playlist') is not None:
            await msg['playlist'].delete()
        msg['playlist'] = await m.reply_text(
            pl,
            disable_web_page_preview=True,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔄", callback_data="replay"),
                        InlineKeyboardButton("⏯", callback_data="pause"),
                        InlineKeyboardButton("⏩", callback_data="skip")
                    
                    ],

                ]
                )
        )
    await mp.delete(m)

@Client.on_message(filters.command(["skip", f"skip@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def skip_track(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply("Nothing Playing")
        await mp.delete(k)
        await mp.delete(m)
        return
    if len(m.command) == 1:
        await mp.skip_current_playing()
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
        if m.chat.type == "private":
            await m.reply_text(pl, disable_web_page_preview=True)
        if EDIT_TITLE:
            await mp.edit_title()
        if LOG_GROUP:
            await mp.send_playlist()
        elif not LOG_GROUP and m.chat.type == "supergroup":
            k=await m.reply_text(pl, disable_web_page_preview=True)
            await mp.delete(k)
    else:
        try:
            items = list(dict.fromkeys(m.command[1:]))
            items = [int(x) for x in items if x.isdigit()]
            items.sort(reverse=True)
            text = []
            for i in items:
                if 2 <= i <= (len(playlist) - 1):
                    audio = f"{playlist[i][1]}"
                    playlist.pop(i)
                    text.append(f"{emoji.WASTEBASKET} Succesfully Removed from Playlist- {i}. **{audio}**")
                else:
                    text.append(f"{emoji.CROSS_MARK} You Cant Skip First Two Songs- {i}")
            k=await m.reply_text("\n".join(text))
            await mp.delete(k)
            if not playlist:
                pl = f"{emoji.NO_ENTRY} Empty Playlist"
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
            if m.chat.type == "private":
                await m.reply_text(pl, disable_web_page_preview=True)
            if EDIT_TITLE:
                await mp.edit_title()
            if LOG_GROUP:
                await mp.send_playlist()
            elif not LOG_GROUP and m.chat.type == "supergroup":
                k=await m.reply_text(pl, disable_web_page_preview=True)
                await mp.delete(k)
        except (ValueError, TypeError):
            k=await m.reply_text(f"{emoji.NO_ENTRY} Invalid input",
                                       disable_web_page_preview=True)
            await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["join", f"join@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def join_group_call(client, m: Message):
    group_call = mp.group_call
    if group_call.is_connected:
        k=await m.reply_text(f"{emoji.ROBOT} Already joined voice chat")
        await mp.delete(k)
        await mp.delete(m)
        return
    await mp.start_call()
    chat = await client.get_chat(CHAT)
    k=await m.reply_text(f"Succesfully Joined Voice Chat in {chat.title}")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["leave", f"leave@{U}"]) & admin_filter)
async def leave_voice_chat(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text("Not joined any Voicechat yet.")
        await mp.delete(k)
        await mp.delete(m)
        return
    playlist.clear()
    if 1 in RADIO:
        await mp.stop_radio()
    group_call.input_filename = ''
    await group_call.stop()
    k=await m.reply_text("Left the VoiceChat")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["vc", f"vc@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def list_voice_chat(client, m: Message):
    group_call = mp.group_call
    if group_call.is_connected:
        chat_id = int("-100" + str(group_call.full_chat.id))
        chat = await client.get_chat(chat_id)
        k=await m.reply_text(
            f"{emoji.MUSICAL_NOTES} **Currently in the voice chat**:\n"
            f"- **{chat.title}**"
        )
    else:
        k=await m.reply_text(emoji.NO_ENTRY
                                   + "Didn't join any voice chat yet")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["stop", f"stop@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def stop_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text("Nothing playing to stop.")
        await mp.delete(k)
        await mp.delete(m)
        return
    if 1 in RADIO:
        await mp.stop_radio()
    group_call.stop_playout()
    k=await m.reply_text(f"{emoji.STOP_BUTTON} Stopped playing")
    playlist.clear()
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["replay", f"replay@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def restart_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text("Nothing playing to replay.")
        await mp.delete(k)
        await mp.delete(m)
        return
    if not playlist:
        k=await m.reply_text("Empty Playlist.")
        await mp.delete(k)
        await mp.delete(m)
        return
    group_call.restart_playout()
    k=await m.reply_text(
        f"{emoji.COUNTERCLOCKWISE_ARROWS_BUTTON}  "
        "Playing from the beginning..."
    )
    await mp.delete(k)
    await mp.delete(m)



@Client.on_message(filters.command(["pause", f"pause@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def pause_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text("Nothing playing to pause.")
        await mp.delete(k)
        await mp.delete(m)
        return
    mp.group_call.pause_playout()
    k=await m.reply_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} Paused",
                               quote=False)
    await mp.delete(k)
    await mp.delete(m)



@Client.on_message(filters.command(["resume", f"resume@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def resume_playing(_, m: Message):
    if not mp.group_call.is_connected:
        k=await m.reply_text("Nothing paused to resume.")
        await mp.delete(k)
        await mp.delete(m)
        return
    mp.group_call.resume_playout()
    k=await m.reply_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} Resumed",
                               quote=False)
    await mp.delete(k)
    await mp.delete(m)

@Client.on_message(filters.command(["clean", f"clean@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def clean_raw_pcm(client, m: Message):
    download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
    all_fn: list[str] = os.listdir(download_dir)
    for track in playlist[:2]:
        track_fn = f"{track[1]}.raw"
        if track_fn in all_fn:
            all_fn.remove(track_fn)
    count = 0
    if all_fn:
        for fn in all_fn:
            if fn.endswith(".raw"):
                count += 1
                os.remove(os.path.join(download_dir, fn))
    k=await m.reply_text(f"{emoji.WASTEBASKET} Cleaned {count} files")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["mute", f"mute@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def mute(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text("Nothing playing to mute.")
        await mp.delete(k)
        await mp.delete(m)
        return
    await group_call.set_is_mute(True)
    k=await m.reply_text(f"{emoji.MUTED_SPEAKER} Muted")
    await mp.delete(k)
    await mp.delete(m)

@Client.on_message(filters.command(["unmute", f"unmute@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def unmute(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text("Nothing playing to mute.")
        await mp.delete(k)
        await mp.delete(m)
        return
    await group_call.set_is_mute(False)
    k=await m.reply_text(f"{emoji.SPEAKER_MEDIUM_VOLUME} Unmuted")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(['volume', f'volume@{U}']) & admin_filter & (filters.chat(CHAT) | filters.private))
async def set_vol(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text("Not yet joined any VC.")
        await mp.delete(k)
        await mp.delete(m)
        return
    if len(m.command) < 2:
        k=await m.reply_text('You forgot to pass volume (1-200).')
        await mp.delete(k)
        await mp.delete(m)
        return
    await group_call.set_my_volume(int(m.command[1]))
    k=await m.reply_text(f"Volume set to {m.command[1]}")
    await mp.delete(k)
    await mp.delete(m)

@Client.on_message(filters.command(["playlist", f"playlist@{U}"]) & (filters.chat(CHAT) | filters.private))
async def show_playlist(_, m: Message):
    if not playlist:
        k=await m.reply_text(f"{emoji.NO_ENTRY} No songs are playing")
        await mp.delete(k)
        await mp.delete(m)
        return
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
    if m.chat.type == "private":
        await m.reply_text(pl, disable_web_page_preview=True)
    else:
        if msg.get('playlist') is not None:
            await msg['playlist'].delete()
        msg['playlist'] = await m.reply_text(pl, disable_web_page_preview=True)
    await mp.delete(m)


@Client.on_message(filters.command(["shuffle", f"shuffle@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def shuffle_play_list(client, m: Message):
    group_call = mp.group_call
    if not playlist:
        k=await m.reply_text(f"{emoji.NO_ENTRY} No Playlist found, Maybe Radio is playing.")
        await mp.delete(k)
        await mp.delete(m)
        return
    else:
        if len(playlist) > 2:
            await mp.shuffle_playlist()
            k=await m.reply_text(f"Playlist Shuffled.")
            await mp.delete(k)
            await mp.delete(m)
        else:
            k=await m.reply_text(f"You cant shuffle playlist with less than 3 songs.")
            await mp.delete(k)
            await mp.delete(m)

@Client.on_message(filters.command(["clearplaylist", f"clearplaylist@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def clear_play_list(client, m: Message):
    group_call = mp.group_call
    if not playlist:
        k=await m.reply_text(f"{emoji.NO_ENTRY} No Playlist found, Maybe Radio is playing.")
        await mp.delete(k)
        await mp.delete(m)
        return
    else:
        group_call.stop_playout()        
        playlist.clear()
        if 3 in RADIO:
            RADIO.remove(3)
        k=await m.reply_text(f"Playlist Cleared.")
        await mp.delete(k)
        await mp.delete(m)


@Client.on_message(filters.command(["cplay", f"cplay@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def channel_play_list(client, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await mp.start_call()
    if len(m.command) < 2:
        k=await m.reply_text('You forgot to pass channel id or channel username.\nExample usage: <code>/cplay Myoosik</code> or <code>/cplay -1002525252525</code>.\n\n⚠️ If you are using channel id, make sure both the bot and user account are member of the given channel.')
        await mp.delete(k)
        await mp.delete(m)
        return
     
    k=await m.reply_text(f"Starting Playing From <code>{m.command[1]}</code>")
    group_call.stop_playout()
    playlist.clear()   
    await mp.c_play(m.command[1])
    await mp.delete(k)
    await mp.delete(m)

@Client.on_message(filters.command(["yplay", f"yplay@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def yt_play_list(client, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await mp.start_call()
    if m.reply_to_message is not None and m.reply_to_message.document:
        if m.reply_to_message.document.file_name != "YouTube_PlayList.json":
            k=await m.reply("Invalid PlayList file given. Use @GetPlayListBot to get a playlist file.")
            await mp.delete(k)
            return
        ytplaylist=await m.reply_to_message.download()
        file=open(ytplaylist)
        try:
            f=json.loads(file.read(), object_hook=lambda d: {int(k): v for k, v in d.items()})
            for play in f:
                playlist.append(play)
                if len(playlist) == 1:
                    m_status = await m.reply_text(
                        f"{emoji.INBOX_TRAY} Downloading and Processing..."
                    )
                    await mp.download_audio(playlist[0])
                    if 1 in RADIO:
                        if group_call:
                            group_call.input_filename = ''
                            RADIO.remove(1)
                            RADIO.add(0)
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
                    if not group_call.is_connected:
                        await mp.start_call()
                    file_=playlist[0][5]
                    group_call.input_filename = os.path.join(
                        client.workdir,
                        DEFAULT_DOWNLOAD_DIR,
                        f"{file_}.raw"
                    )
                    await m_status.delete()
                    print(f"- START PLAYING: {playlist[0][1]}")
                    if EDIT_TITLE:
                        await mp.edit_title()
                if not playlist:
                    k=await m.reply("Invalid File Given")
                    await mp.delete(k)
                    file.close()
                    try:
                        os.remove(ytplaylist)
                    except:
                        pass
                    return                   
                for track in playlist[:2]:
                    await mp.download_audio(track)        
            file.close()
            try:
                os.remove(ytplaylist)
            except:
                pass
        except Exception as e:
            k=await m.reply(f"Errors Occured while reading playlist: {e}")
            await mp.delete(k)
            return
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
        if m.chat.type == "private":
            await m.reply_text(pl, disable_web_page_preview=True)
        if LOG_GROUP:
            await mp.send_playlist()
        elif not LOG_GROUP and m.chat.type == "supergroup":
            k=await m.reply_text(pl, disable_web_page_preview=True)
            await mp.delete(k)
    else:
        if " " in m.text:
            na=m.text
            f, url=na.split(" ")
            if "playlist?list" not in url:
                k=await m.reply("Invalid Playlist Url Given.")
                await mp.delete(k)
                return
            msg=await m.reply("Getting Playlist Info..")
            ytplaylist=await mp.get_playlist(m.from_user.id, url)
            await msg.delete()
            if ytplaylist == "peer":
                markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🤖 GetPlayListBot", url=f"https://telegram.me/GetPlaylistBot?start=subinps_{m.from_user.id}")

                        ]
                    ]
                    )
                k=await m.reply("I was unable to fetch data for you. Plase send /start to @GetPlayListBot and try again.", reply_markup=markup)
                await mp.delete(k)
                return
            elif ytplaylist == "nosub":
                markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("📢 Join My Update Channel", url='https://t.me/subin_works')
                        ],
                        [
                            InlineKeyboardButton("🔄 Try Again", url=f"https://telegram.me/GetPlaylistBot?start=subinps_{m.from_user.id}")

                        ]
                    ]
                    )
                k=await m.reply("You Have Not Subscribed to MY Update Channel, and Please Join My Update Channel to Use This Feature 🤒", reply_markup=markup)
                await mp.delete(k)
                return
            elif ytplaylist == "kicked":
                k=await m.reply("You are banned to use this feature.\nTry @GetPlayListBot")
                await mp.delete(k)
                return
            elif ytplaylist == "urlinvalid":
                k=await m.reply("The Url you gave is Invalid, It should be something like <code>https://youtube.com/playlist?list=PL_rXc1ssylNebemAQVgDaOPijBaXU2gyD</code>")
                await mp.delete(k)
                return
            elif ytplaylist == "timeout":
                k=await m.reply("I was unable to get data within time. Try to get the playlist data from @GetPlaylIstBot")
                await mp.delete(k)
                return
            elif "Error" in ytplaylist:
                k=await m.reply(ytplaylist)
                await mp.delete(k)
                return
            else:
                file=open(ytplaylist)
                try:
                    f=json.loads(file.read(), object_hook=lambda d: {int(k): v for k, v in d.items()})
                    for play in f:
                        playlist.append(play)
                        if len(playlist) == 1:
                            m_status = await m.reply_text(
                                f"{emoji.INBOX_TRAY} Downloading and Processing..."
                            )
                            await mp.download_audio(playlist[0])
                            if 1 in RADIO:
                                if group_call:
                                    group_call.input_filename = ''
                                    RADIO.remove(1)
                                    RADIO.add(0)
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
                            if not group_call.is_connected:
                                await mp.start_call()
                            file_=playlist[0][5]
                            group_call.input_filename = os.path.join(
                                client.workdir,
                                DEFAULT_DOWNLOAD_DIR,
                                f"{file_}.raw"
                            )
                            await m_status.delete()
                            print(f"- START PLAYING: {playlist[0][1]}")
                            if EDIT_TITLE:
                                await mp.edit_title()
                        if not playlist:
                            k=await m.reply("Invalid File Given")
                            await mp.delete(k)
                            file.close()
                            try:
                                os.remove(ytplaylist)
                            except:
                                pass
                            return                   
                        for track in playlist[:2]:
                            await mp.download_audio(track)        
                    file.close()
                    try:
                        os.remove(ytplaylist)
                    except:
                        pass
                except Exception as e:
                    k=await m.reply(f"Errors Occured while reading playlist: {e}")
                    await mp.delete(k)
                    return
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
                if m.chat.type == "private":
                    await m.reply_text(pl, disable_web_page_preview=True)
                if LOG_GROUP:
                    await mp.send_playlist()
                elif not LOG_GROUP and m.chat.type == "supergroup":
                    k=await m.reply_text(pl, disable_web_page_preview=True)
                    await mp.delete(k)
        else:
            k=await m.reply("Reply to a Playlist File Or Pass A YouTube Playlist Url along command.\nUse @GetPlayListBot To Get A PlayList File")
            await mp.delete(k)
            await mp.delete(m)

@Client.on_message(filters.command(["export", f"export@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def export_play_list(client, message: Message):
    if not playlist:
        k=await message.reply_text(f"{emoji.NO_ENTRY} Playlist is Empty")
        await mp.delete(k)
        await mp.delete(message)
        return

    file=f"{message.chat.id}_{message.message_id}.json"
    with open(file, 'w+') as outfile:
        json.dump(playlist, outfile, indent=4)
    await client.send_document(chat_id=message.chat.id, document=file, file_name="PlayList.json", caption=f"Playlist\n\nNumber Of Songs: <code>{len(playlist)}</code>\n\nJoin [XTZ Bots](https://t.me/subin_works)")
    await mp.delete(message)
    try:
        os.remove(file)
    except:
        pass

@Client.on_message(filters.command(["import", f"import@{U}"]) & admin_filter & (filters.chat(CHAT) | filters.private))
async def import_play_list(client, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await mp.start_call()
    if m.reply_to_message is not None and m.reply_to_message.document:
        if m.reply_to_message.document.file_name != "PlayList.json":
            k=await m.reply("Invalid PlayList file given. Use @GetPlayListBot to get a playlist file. Or Export your current Playlist using /export.")
            await mp.delete(k)
            await mp.delete(m)
            return
        myplaylist=await m.reply_to_message.download()
        file=open(myplaylist)
        try:
            f=json.loads(file.read(), object_hook=lambda d: {int(k): v for k, v in d.items()})
            for play in f:
                playlist.append(play)
                if len(playlist) == 1:
                    m_status = await m.reply_text(
                        f"{emoji.INBOX_TRAY} Downloading and Processing..."
                    )
                    await mp.download_audio(playlist[0])
                    if 1 in RADIO:
                        if group_call:
                            group_call.input_filename = ''
                            RADIO.remove(1)
                            RADIO.add(0)
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
                    if not group_call.is_connected:
                        await mp.start_call()
                    file_=playlist[0][5]
                    group_call.input_filename = os.path.join(
                        client.workdir,
                        DEFAULT_DOWNLOAD_DIR,
                        f"{file_}.raw"
                    )
                    await m_status.delete()
                    print(f"- START PLAYING: {playlist[0][1]}")
                    if EDIT_TITLE:
                        await mp.edit_title()
                if not playlist:
                    k=await m.reply("Invalid File Given")
                    await mp.delete(k)
                    file.close()
                    try:
                        os.remove(myplaylist)
                    except:
                        pass
                    return                   
                for track in playlist[:2]:
                    await mp.download_audio(track)        
            file.close()
            try:
                os.remove(myplaylist)
            except:
                pass
        except Exception as e:
            k=await m.reply(f"Errors Occured while reading playlist: {e}")
            await mp.delete(k)
            return
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
        if m.chat.type == "private":
            await m.reply_text(pl, disable_web_page_preview=True)
        if LOG_GROUP:
            await mp.send_playlist()
        elif not LOG_GROUP and m.chat.type == "supergroup":
            k=await m.reply_text(pl, disable_web_page_preview=True)
            await mp.delete(k)
    else:
        k=await m.reply("Reply to a previously exported playlist.")
        await mp.delete(m)
        await mp.delete(k)


@Client.on_message(filters.command(['upload', f'upload@{U}']) & (filters.chat(CHAT) | filters.private))
async def upload(client, message):
    if not playlist:
        k=await message.reply_text(f"{emoji.NO_ENTRY} No songs are playing")
        await mp.delete(k)
        await mp.delete(message)
        return
    url=playlist[0][2]
    if playlist[0][3] == "telegram":
        await client.send_audio(chat_id=message.chat.id, audio=url, caption=f"<b>Song: {playlist[0][1]}\nUploaded Using [MusicPlayer](https://github.com/subinps/MusicPlayer)</b>")
    elif playlist[0][3] == "youtube":
        file=GET_FILE[url]
        thumb=GET_THUMB.get(url)
        if thumb is None:
            thumb="https://telegra.ph/file/181242eab5c4a74916d01.jpg"
        response = requests.get(thumb, allow_redirects=True)
        open(f"{playlist[0][5]}.jpeg", 'wb').write(response.content)
        await message.reply_chat_action("upload_document")
        dur=ffmpeg.probe(file)['format']['duration']
        m=await message.reply_text(f"Starting Uploading {playlist[0][1]}...")
        await client.send_audio(
            chat_id=message.chat.id,
            audio=file,
            file_name=playlist[0][1],
            thumb=f"{playlist[0][5]}.jpeg",
            title=playlist[0][1],
            duration=int(float(dur)),
            performer="MusicPlayer",
            caption=f"<b>Song: [{playlist[0][1]}]({playlist[0][2]})\nUploaded Using [MusicPlayer](https://github.com/subinps/MusicPlayer)</b>"
            )
        await m.delete()
    else:
        file=GET_FILE[url]
        thumb=GET_THUMB.get(url)
        if thumb is None:
            thumb="https://telegra.ph/file/181242eab5c4a74916d01.jpg"
        response = requests.get(thumb, allow_redirects=True)
        open(f"{playlist[0][5]}.jpeg", 'wb').write(response.content)
        await message.reply_chat_action("upload_document")
        cmd=f"cp {file} {playlist[0][5]}.mp3"
        os.system(cmd)
        await asyncio.sleep(2)
        m=await message.reply_text(f"Starting Uploading {playlist[0][1]}...")
        dur=ffmpeg.probe(f"{playlist[0][5]}.mp3")['format']['duration']
        await client.send_audio(
            chat_id=message.chat.id,
            audio=f"{playlist[0][5]}.mp3",
            file_name=f"{playlist[0][1]}",
            thumb=f"{playlist[0][5]}.jpeg",
            title=playlist[0][1],
            duration=int(float(dur)),
            performer="MusicPlayer",
            caption=f"<b>Song: [{playlist[0][1]}]({playlist[0][2]})\nUploaded Using [MusicPlayer](https://github.com/subinps/MusicPlayer)</b>"
            )
        await m.delete()
        try:
            os.remove(f"{playlist[0][5]}.mp3")
        except:
            pass
 

admincmds=["join", "unmute", "yplay", "mute", "leave", "clean", "vc", "pause", "resume", "stop", "skip", "radio", "stopradio", "replay", "restart", "volume", "shuffle", "clearplaylist", "cplay", "export", "import", f"export@{U}", f"import@{U}", f"yplay@{U}" f"cplay@{U}", f"clearplaylist@{U}", f"shuffle@{U}", f"volume@{U}", f"join@{U}", f"unmute@{U}", f"mute@{U}", f"leave@{U}", f"clean@{U}", f"vc@{U}", f"pause@{U}", f"resume@{U}", f"stop@{U}", f"skip@{U}", f"radio@{U}", f"stopradio@{U}", f"replay@{U}", f"restart@{U}"]

@Client.on_message(filters.command(admincmds) & ~admin_filter & (filters.chat(CHAT) | filters.private))
async def notforu(_, m: Message):
    k=await m.reply("Who the hell you are?.")
    await mp.delete(k)
    await mp.delete(m)
allcmd = ["play", "player", "splay", f"splay@{U}", f"play@{U}", f"player@{U}"] + admincmds

@Client.on_message(filters.command(allcmd) & ~filters.chat(CHAT) & filters.group)
async def not_chat(_, m: Message):
    buttons = [
        [
            InlineKeyboardButton('⚡️Make Own Bot', url='https://heroku.com/deploy?template=https://github.com/subinps/MusicPlayer'),
            InlineKeyboardButton('🧩 Source Code', url='https://github.com/subinps/MusicPlayer'),
        ],
        [
            InlineKeyboardButton('How to Make', url='https://youtu.be/iBK-5pP2eHM'),
            InlineKeyboardButton('👨🏼‍🦯 Help', callback_data='help')       
        ]
        ]
    k=await m.reply("<b>You can't use this bot in this group, for that you have to make your own bot from the [SOURCE CODE](https://github.com/subinps/MusicPlayer) below.</b>", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))
    await mp.delete(m)
