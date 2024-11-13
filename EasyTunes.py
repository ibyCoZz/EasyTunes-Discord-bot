import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'options': '-vn'}

    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')

    @client.event
    async def on_message(message):
        if message.content.startswith("?play"):
            # Verificar que el usuario está en un canal de voz
            if not message.author.voice:
                await message.channel.send("Debes estar en un canal de voz para usar este comando.")
                return
            
            # Conectar solo si no está ya conectado
            if message.guild.id not in voice_clients or not voice_clients[message.guild.id].is_connected():
                try:
                    voice_client = await message.author.voice.channel.connect()
                    voice_clients[message.guild.id] = voice_client
                except Exception as e:
                    print(e)
                    await message.channel.send("Error al conectar al canal de voz.")
                    return
            
            try:
                url = message.content.split()[1]
                data = await asyncio.to_thread(lambda: ytdl.extract_info(url, download=False))
                song = data['url']
                player = discord.FFmpegPCMAudio(song, **ffmpeg_options)

                # Reproducir la canción
                if not voice_clients[message.guild.id].is_playing():
                    voice_clients[message.guild.id].play(player)
                else:
                    await message.channel.send("El bot ya está reproduciendo audio.")

            except Exception as e:
                print(e)
                await message.channel.send("Hubo un problema al reproducir el audio.")

        if message.content.startswith("?pause"):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)
                await message.channel.send("Hubo un problema al pausar el audio.")

        if message.content.startswith("?resume"):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)
                await message.channel.send("Hubo un problema al volver a reproducir el audio.")

        if message.content.startswith("?stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
            except Exception as e:
                print(e)
                await message.channel.send("Hubo un problema al pausar el audio.")
                
    client.run(TOKEN)
