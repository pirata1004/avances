import discord
import asyncio
from discord.ext import commands
from discord import FFmpegPCMAudio
from pytube import YouTube


intents = discord.Intents.default()
intents.members = True
intents.message_content = True


bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Conectado como {bot.user.name}')`


@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send(f'Conectado al canal de voz: {channel}')


@bot.command()
async def leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send('Desconectado del canal de voz')
    else:
        await ctx.send('No estoy conectado a un canal de voz')


@bot.command()
async def play(ctx, url):
    voice_client = ctx.guild.voice_client
    if not voice_client:
        await ctx.send('No estoy conectado a un canal de voz')
        return

try:
    video = YouTube(url)
    best_audio = video.streams.get_audio_only()
    url2 = best_audio.url

    audio_source = FFmpegPCMAudio(url2)
    voice_client.play(audio_source)

    await ctx.send('Reproduciendo música de YouTube')

    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()
    await ctx.send('Reproducción finalizada, desconectado del canal de voz')

except Exception as e:
    await ctx.send(f'Error al reproducir música: {str(e)}')



TOKEN = '*******'

