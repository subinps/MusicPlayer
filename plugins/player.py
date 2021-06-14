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
from youtube_dl import YoutubeDL
from config import Config
from pyrogram import Client, filters, emoji
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pyrogram.types import Message
from utils import mp, RADIO
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Python_ARQ import ARQ
from youtube_search import YoutubeSearch
from pyrogram import Client
from aiohttp import ClientSession
import re

LOG_GROUP=Config.LOG_GROUP

DURATION_LIMIT = Config.DURATION_LIMIT
ARQ_API=Config.ARQ_API
session = ClientSession()
arq = ARQ("https://thearq.tech",ARQ_API,session)
playlist=Config.playlist

ADMINS=Config.ADMINS
CHAT=Config.CHAT
LOG_GROUP=Config.LOG_GROUP
playlist=Config.playlist

@Client.on_message(filters.command("play") | filters.audio & filters.private)
async def yplay(_, message: Message):
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
                yturl=message.text
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
            await message.reply_text("You Didn't gave me anything to play. Send me a audio file or reply /play to an audio file.")
            return
    if 1 in RADIO:
        await mp.stop_radio()
    user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    group_call = mp.group_call
    if not group_call.is_connected:
        await mp.start_call()
    if type=="audio":
        if round(m_audio.audio.duration / 60) > DURATION_LIMIT:
            await message.reply_text(f"❌ Videos longer than {DURATION_LIMIT} minute(s) aren't allowed, the provided video is {round(m_audio.audio.duration/60)} minute(s)")
            return
        if not group_call.is_connected:
            await mp.start_call()
        if playlist and playlist[-1][2] \
                == m_audio.audio.file_id:
            await message.reply_text(f"{emoji.ROBOT} Already added in Playlist")
            return
        data={1:m_audio.audio.title, 2:m_audio.audio.file_id, 3:"telegram", 4:user}
        playlist.append(data)
        if len(playlist) == 1:
            m_status = await message.reply_text(
                f"{emoji.INBOX_TRAY} Downloading and Processing..."
            )
            await mp.download_audio(playlist[0])
            file=playlist[0][1]
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
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        await message.reply_text(pl)
        for track in playlist[:2]:
            await mp.download_audio(track)
        if LOG_GROUP and message.chat.id != LOG_GROUP:
            await mp.send_playlist()
    if type=="youtube" or type=="query":
        if type=="youtube":
            ytquery=yturl
        elif type=="query":
            ytquery=ysearch
        else:
            return
        msg = await message.reply_text("⚡️ **Fetching Song From YouTube...**")
        try:
            results = YoutubeSearch(ytquery, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0]["title"][:40]
            ydl_opts = {
                "geo-bypass": True,
                "nocheckcertificate": True
            }
            ydl = YoutubeDL(ydl_opts)
            info = ydl.extract_info(url, False)
            duration = round(info["duration"] / 60)
        except Exception as e:
            await msg.edit(
                "Song not found.\nTry inline mode.."
            )
            print(str(e))
            return
        if int(duration) > DURATION_LIMIT:
            await message.reply_text(f"❌ Videos longer than {DURATION_LIMIT} minute(s) aren't allowed, the provided video is {duration} minute(s)")
            return

        data={1:title, 2:url, 3:"youtube", 4:user}
        playlist.append(data)
        group_call = mp.group_call
        if not group_call.is_connected:
            await mp.start_call()
        client = group_call.client
        if len(playlist) == 1:
            m_status = await msg.edit(
                f"{emoji.INBOX_TRAY} Downloading and Processing..."
            )
            await mp.download_audio(playlist[0])
            file=playlist[0][1]
            group_call.input_filename = os.path.join(
                client.workdir,
                DEFAULT_DOWNLOAD_DIR,
                f"{file}.raw"
            )

            await m_status.delete()
            print(f"- START PLAYING: {playlist[0][1]}")
        if not playlist:
            pl = f"{emoji.NO_ENTRY} Empty playlist"
        else:
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        await message.reply_text(pl)
        for track in playlist[:2]:
            await mp.download_audio(track)
        if LOG_GROUP and message.chat.id != LOG_GROUP:
            await mp.send_playlist()
            
        
   
@Client.on_message(filters.command("dplay"))
async def deezer(_, message):
    user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if " " in message.text:
        text = message.text.split(" ", 1)
        query = text[1]
    else:
        await message.reply_text("You Didn't gave me anything to play use /dplay <song name>")
        return
    if 1 in RADIO:
        await mp.stop_radio()
    user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    group_call = mp.group_call
    if not group_call.is_connected:
        await mp.start_call()
    msg = await message.reply("⚡️ **Fetching Song From Deezer...**")
    try:
        songs = await arq.deezer(query,1)
        if not songs.ok:
            await msg.edit(songs.result)
            return
        url = songs.result[0].url
        title = songs.result[0].title

    except:
        await msg.edit("No results found")
        return
    data={1:title, 2:url, 3:"deezer", 4:user}
    playlist.append(data)
    group_call = mp.group_call
    if not group_call.is_connected:
        await mp.start_call()
    client = group_call.client
    if len(playlist) == 1:
        m_status = await msg.edit(
            f"{emoji.INBOX_TRAY} Downloading and Processing..."
        )
        await mp.download_audio(playlist[0])
        file=playlist[0][1]
        group_call.input_filename = os.path.join(
            client.workdir,
            DEFAULT_DOWNLOAD_DIR,
            f"{file}.raw"
        )
        await m_status.delete()
        print(f"- START PLAYING: {playlist[0][1]}")
    if not playlist:
        pl = f"{emoji.NO_ENTRY} Empty playlist"
    else:
        pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
            for i, x in enumerate(playlist)
            ])
    await message.reply_text(pl)
    for track in playlist[:2]:
        await mp.download_audio(track)
    if LOG_GROUP and message.chat.id != LOG_GROUP:
        await mp.send_playlist()


@Client.on_message(filters.command("player"))
async def player(_, m: Message):
    if not playlist:
        await m.reply_text(f"{emoji.NO_ENTRY} No songs are playing")
        return
    else:
        pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
            for i, x in enumerate(playlist)
            ])
    await m.reply_text(
        pl,
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

@Client.on_message(filters.command("skip") & filters.user(ADMINS))
async def skip_track(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await m.reply("Nothing Playing")
        return
    if len(m.command) == 1:
        await mp.skip_current_playing()
        if not playlist:
            pl = f"{emoji.NO_ENTRY} Empty playlist"
        else:
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
            for i, x in enumerate(playlist)
            ])            
        await m.reply_text(pl)
        if LOG_GROUP and m.chat.id != LOG_GROUP:
            await mp.send_playlist()
    else:
        try:
            items = list(dict.fromkeys(m.command[1:]))
            items = [int(x) for x in items if x.isdigit()]
            items.sort(reverse=True)
            text = []
            for i in items:
                if 2 <= i <= (len(playlist) - 1):
                    audio = f"{playlist[i].audio.title}"
                    playlist.pop(i)
                    text.append(f"{emoji.WASTEBASKET} {i}. **{audio}**")
                else:
                    text.append(f"{emoji.CROSS_MARK} {i}")
            await m.reply_text("\n".join(text))
            if not playlist:
                pl = f"{emoji.NO_ENTRY} Empty Playlist"
            else:
                pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                    f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
                    for i, x in enumerate(playlist)
                    ])
            await m.reply_text(pl)
            if LOG_GROUP and m.chat.id != LOG_GROUP:
                await mp.send_playlist()
        except (ValueError, TypeError):
            await m.reply_text(f"{emoji.NO_ENTRY} Invalid input",
                                       disable_web_page_preview=True)


@Client.on_message(filters.command("join") & filters.user(ADMINS))
async def join_group_call(client, m: Message):
    group_call = mp.group_call
    if group_call.is_connected:
        await m.reply_text(f"{emoji.ROBOT} Already joined voice chat")
        return
    await mp.start_call()
    chat = await client.get_chat(CHAT)
    await m.reply_text(f"Succesfully Joined Voice Chat in {chat.title}")


@Client.on_message(filters.command("leave") & filters.user(ADMINS))
async def leave_voice_chat(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await m.reply_text("Not joined any Voicechat yet.")
        return
    playlist.clear()
    group_call.input_filename = ''
    await group_call.stop()
    await m.reply_text("Left the VoiceChat")


@Client.on_message(filters.command("vc") & filters.user(ADMINS))
async def list_voice_chat(client, m: Message):
    group_call = mp.group_call
    if group_call.is_connected:
        chat_id = int("-100" + str(group_call.full_chat.id))
        chat = await client.get_chat(chat_id)
        await m.reply_text(
            f"{emoji.MUSICAL_NOTES} **Currently in the voice chat**:\n"
            f"- **{chat.title}**"
        )
    else:
        await m.reply_text(emoji.NO_ENTRY
                                   + "Didn't join any voice chat yet")


@Client.on_message(filters.command("stop") & filters.user(ADMINS))
async def stop_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await m.reply_text("Nothing playing to stop.")
        return
    group_call.stop_playout()
    await m.reply_text(f"{emoji.STOP_BUTTON} Stopped playing")
    playlist.clear()


@Client.on_message(filters.command("replay") & filters.user(ADMINS))
async def restart_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await m.reply_text("Nothing playing to replay.")
        return
    if not playlist:
        return
    group_call.restart_playout()
    await m.reply_text(
        f"{emoji.COUNTERCLOCKWISE_ARROWS_BUTTON}  "
        "Playing from the beginning..."
    )


@Client.on_message(filters.command("pause") & filters.user(ADMINS))
async def pause_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await m.reply_text("Nothing playing to pause.")
        return
    mp.group_call.pause_playout()
    await m.reply_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} Paused",
                               quote=False)



@Client.on_message(filters.command("resume") & filters.user(ADMINS))
async def resume_playing(_, m: Message):
    if not mp.group_call.is_connected:
        await m.reply_text("Nothing paused to resume.")
        return
    mp.group_call.resume_playout()
    await m.reply_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} Resumed",
                               quote=False)

@Client.on_message(filters.command("clean") & filters.user(ADMINS))
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
    await m.reply_text(f"{emoji.WASTEBASKET} Cleaned {count} files")


@Client.on_message(filters.command("mute") & filters.user(ADMINS))
async def mute(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await m.reply_text("Nothing playing to mute.")
        return
    group_call.set_is_mute(True)
    await m.reply_text(f"{emoji.MUTED_SPEAKER} Muted")


@Client.on_message(filters.command("unmute") & filters.user(ADMINS))
async def unmute(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await m.reply_text("Nothing playing to mute.")
        return
    group_call.set_is_mute(False)
    await m.reply_text(f"{emoji.SPEAKER_MEDIUM_VOLUME} Unmuted")

@Client.on_message(filters.command("playlist"))
async def show_playlist(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        await m.reply_text("No active Voicechat.")
        return
    if not playlist:
        pl = f"{emoji.NO_ENTRY} Empty Playlist"
    else:
        pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
            for i, x in enumerate(playlist)
            ])
    await m.reply_text(pl)

admincmds=["join", "unmute", "mute", "leave", "clean", "vc", "pause", "resume", "stop", "skip", "radio", "stopradio", "replay", "restart", "info"]

@Client.on_message(filters.command(admincmds) & ~filters.user(ADMINS))
async def notforu(_, m: Message):
    await m.reply("Who the hell you are")
