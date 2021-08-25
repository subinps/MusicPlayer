# Telegram Voice Chat Bot with Channel Support.

A Telegram Bot to Play Audio in Voice Chats With Youtube and Jio Saavn support.
Supports Playing Music files from a telegram channel.
Supports Live streaming from youtube.

```
Please fork this repository don't import code
Made with Python3
(C) @subinps
Copyright permission under MIT License
License -> https://github.com/subinps/MusicPlayer/blob/master/LICENSE

```

## Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/subinps/MusicPlayer)

NOTE: Make sure you have started a VoiceChat in your Group before deploying.
### Deploy to VPS

```sh
git clone https://github.com/subinps/MusicPlayer
cd MusicPlayer
pip3 install -r requirements.txt
# <Create Variables appropriately>
python3 main.py
```

# Vars:
1. `API_ID` : Get From my.telegram.org
2. `API_HASH` : Get from my.telegram.org
3. `BOT_TOKEN` : @Botfather
4. `SESSION_STRING` : Generate From here [![GenerateStringName](https://img.shields.io/badge/repl.it-generateStringName-yellowgreen)](https://repl.it/@subinps/getStringName)
5. `CHAT` : ID of Channel/Group where the bot plays Music.
6. `LOG_GROUP` : Group to send Playlist, if CHAT is a Group
7. `ADMINS` : ID of users who can use admin commands.
8. `STREAM_URL` : Stream URL of radio station or a youtube live video to stream when the bot starts or with /radio command.You can also use a telegram channel as radio station. Just upload all you music files to a telegram channel and add the bot and user account in that channel and use chat_id of channel in STREAM_URL.You can also use any public telegram channels, in that case use the username of such channel in place of STREAM_URL (Bot being admin in public channel not required.)  [Some Streaming Links](https://gist.github.com/subinps/293d0a117fa0b13da41871538f226956)
9. `MAXIMUM_DURATION` : Maximum duration of song to play.(Optional)
10. `REPLY_MESSAGE` : A reply to those who message the USER account in PM. Leave it blank if you do not need this feature. 
11. `ADMIN_ONLY` : Pass `Y` If you want to make /play and /splay commands only for admins of `CHAT`. By default /play and /splay is available for all.

- Enable the worker after deploy the project to Heroku
- Bot will starts radio automatically in given `CHAT` with given `STREAM_URL` after deploy.(24*7 Music even if heroku restarts, radio stream restarts automatically.)  
- To play a song use /play as a reply to audio file or a youtube link.
- Use /play <song name> to play song from youtube and /splay <song name> to play from JioSaavn or /cplay <channel username or channel id> to play music from a telegram channel.
- Use /help to know about other commands.

**Features**

- Playlist, queue.
- Supports Play from Youtube Playlist.
- Change VoiceChat title to current playing song name.
- Supports Live streaming from youtube
- Supports both Jio Saavn and youtube to search songs.
- Play from telegram file supported.
- Play whole music files from a telegram channel.
- Starts Radio after if no songs in playlist.
- Automatically downloads audio for the first two tracks in the playlist to ensure smooth playing
- Automatic restart even if heroku restarts.

### Note

```
Contributions are welcomed, But Kanging and editing a few lines wont make you a Developer.
Fork the repo, Do not Import code.

```
#### Support

Connect Me On [Telegram](https://telegram.dog/subinps_bot)

## Credits 
- [Dash Eclipse's](https://github.com/dashezup) for his [tgvc-userbot](https://github.com/callsmusic/tgvc-userbot).
- [Thuhin](https://github.com/cachecleanerjeet) for his [Jio Saavn API](https://github.com/cachecleanerjeet/JiosaavnAPI).

