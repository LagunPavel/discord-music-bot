import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import random
from discord.ext.commands import Bot
from dotenv import load_dotenv
import os
from requests import get
import openai
import wikipediaapi
from discord.ext.commands import MemberConverter
import re
import uuid
import json
import requests
import yt_dlp
from discord.voice_client import VoiceClient
from pydub import AudioSegment
from pytube import YouTube
from ytmusicapi import YTMusic
import asyncio
import logging
import glob

from discord import Color
from discord.ext.commands import BucketType
import aiohttp
import io
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
# from googleapiclient.discovery import build
from sympy import symbols, solve, Eq
import asyncpg
import ffmpeg
from upstash_redis import Redis
import redis
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


load_dotenv()

SONG_URLS_FILE = "song_urls.txt" 
ytmusic = YTMusic()
pause = False
MAX_QUEUE_SIZE = 20

discordtoken = os.getenv("TOKEN")
openai_api_key = os.getenv("API_KEY")
openai.api_key = openai_api_key
news_key = os.getenv("NEWS_API_KEY")
weather_key = os.getenv("OPEN_WEATHER_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
API_KEY = os.getenv("GOOGLE_API_KEY")
HUGGING_FACE_API_TOKEN = os.getenv('HUGGING_FACE_API')

intents = discord.Intents.all()
intents.typing = True
intents.presences = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='s.', intents=intents)

queue = asyncio.Queue()


yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = yt_dlp.YoutubeDL(yt_dl_opts)

ffmpeg_options = {'options': "-vn"}

def is_playlist_url(url):
    return bool(re.search(r'list=([0-9A-Za-z_-]+)', url))

def remove_mp4_files():
    for file in os.listdir('.'):
        if file.endswith('.mp4'):
            os.remove(file)


@bot.event
async def on_ready() -> None:
    logging.basicConfig(filename='discordBot.errors', level=logging.ERROR)
    print(f"{bot.user.name} успешно запущен!")
    print("-"*100)


@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.channels, name = "┊🤖┊ну-здарова")
    welcome_channel1 = discord.utils.get(member.guild.channels, name = "выдача-роли")
    welcome_channel2 = discord.utils.get(member.guild.channels, name = "буквы_и_цифры")
    welcome_message = f"Эй, йоу {member.mention} че каво? Ты прибыл на сервер {member.guild}! Ниже есть канал #┊⭐┊выбор-роли"
    welcome_message1 = f"Добро пожаловать {member.mention} на сервер {member.guild}! Мы рады видеть Вас здесь."
    welcome_message2 = f"Че с деньгами {member.mention}? Ты залетел на сервер {member.guild} и теперь должен косарь!"

    if welcome_channel is not None:
        await welcome_channel.send(welcome_message)
    if welcome_channel1 is not None:
        await welcome_channel1.send(welcome_message1)
    if welcome_channel2 is not None:
        await welcome_channel2.send(welcome_message2)



@bot.command(help="Эта команда показывает весь список доступных команд")
async def doc(ctx: commands.Context):
    some_url = "https://discord.com/oauth2/authorize?client_id=1107617102078169128"
    embed = discord.Embed(
        title="⋆.˚✮🎧✮˚.⋆ МУЗЫКАЛЬНЫЙ БОТ КРЯКЛ ⋆.˚✮🎧✮˚.⋆",
        description="👇СПИСОК ДОСТУПНЫХ КОМАНД👇",
        url=some_url,
        color=discord.Color.random(),
    )
    embed.add_field(name=" ", value=" ")
    embed.add_field(name="⌞ s.play ⌝", value=" Воспроизводит трек/видео в голосовом канале, в котором вы находитесь. Используйте: s.play [название трека/YouTube URL]", inline=False)
    #embed.add_field(name="\u200b", value="\u200b")
    embed.add_field(name="⌞ s.stop ⌝", value="Останавливает воспроизводимый трек/видео с YouTube. Используйте: s.stop", inline=False)
    #embed.add_field(name=chr(173), value=chr(173))
    embed.add_field(name="⌞ s.menu ⌝", value="Показывает элементы управления воспроизведением. Используйте: s.menu", inline=False)
    embed.add_field(name="⌞ s.skip ⌝", value="Перелистывает воспроизводимый трек/видео с YouTube на следующий по очереди. Используйте: s.skip", inline=False)
    embed.add_field(name="⌞ s.queue ⌝", value="Показывает очередь треков. Используйте: s.queue", inline=False)
    embed.add_field(name="⌞ s.art ⌝", value="Отправляет изображение по заданному запросу. Используйте: s.art [Запрос]", inline=False)
    #embed.add_field(name="⌞ s.rdog ⌝", value="Эта команда отправляет случайное изображение собачки😅. Используйте: s.rdog", inline=False)
    embed.add_field(name="⌞ s.askwiki ⌝", value="Выводит краткую сводку из Wikipedia по заданному запросу. Используйте: s.askwiki [Запрос]", inline=False)
    embed.add_field(name="⌞ s.news ⌝", value="Эта команда отображает последние новости по заданному ключевому слову. Используйте: s.news [Запрос]", inline=False)
    embed.add_field(name="⌞ s.weather ⌝", value="Эта команда отображает погоду в заданном городе. Используйте: s.weather [Название города]", inline=False)
    embed.add_field(name="⌞ s.rnum  ⌝", value="Эта команда отправляет случайное число в диапазоне от 1 до нужного Вам случайного числа. Используйте: s.rnum [Число]", inline=False)
    #embed.add_field(name="⌞ s.math ⌝", value="Простой калькулятор. Используйте: s.math [Число + | - | * | /  Число]", inline=False)
    #embed.add_field(name="⌞ s.ping ⌝", value="Эта команда позволяет вам проверить задержку бота. Используйте: s.ping", inline=False)
    embed.add_field(name="⌞ s.serverstats ⌝", value="Выводит информацию о сервере. Используйте: s.serverstats", inline=False)
    #embed.add_field(name="⌞ s.vote ⌝", value="Создайте опрос, за который пользователи смогут проголосовать, используя реакции. Используйте: s.vote [Название] [Описание]", inline=False)
    #embed.add_field(name="⌞ s.check_vote ⌝", value="Проверьте количество голосов ЗА и ПРОТИВ у опроса с указанным названием. Используйте: s.check_vote [Название опроса]", inline=False)
    embed.add_field(name=" ", value=" ")
    embed.add_field(name="P.S.", value="Взаимодействие с воспроизведением музыка осуществляется в основном кнопками, но Вы также можете использовать для этого команды, представленные выше", inline=False)
    embed.add_field(name=" ", value=" ")
    embed.add_field(name="Префиксы команд!", value="Начинайте любую команду с префикса s. (иначе команда не запустится!) ПОМНИТЕ ОБ ЭТОМ ПРИ ИСПОЛЬЗОВАНИИ КОМАНД!", inline=False)
    embed.add_field(name=" ", value=" ")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1107806049139953754/1246868489080275016/2.jpg?ex=665df445&is=665ca2c5&hm=9260532836cce325d31b36f94defbeebe6e339b03b94eeced8709bab429d9f01&")
    embed.set_footer(text="Крякл", icon_url="https://cdn.discordapp.com/attachments/1107806049139953754/1246868489080275016/2.jpg?ex=665df445&is=665ca2c5&hm=9260532836cce325d31b36f94defbeebe6e339b03b94eeced8709bab429d9f01&")
    await ctx.send(embed=embed)

queue = asyncio.Queue()
class Track:
    def __init__(self, url):
        self.url = url
        self.id = uuid.uuid4()
        self.filename = None

    async def download(self):
        yt = YouTube(self.url)
        stream = yt.streams.filter(only_audio=True).first()
        self.filename = f"{self.id}.mp4"
        stream.download(filename=self.filename)

async def delete_file(filename):
    if filename and os.path.exists(filename):
        os.remove(filename)


def append_url_to_file(url):
    # Прочитать все существующие URL-адреса из файла
    if os.path.exists(SONG_URLS_FILE):
        with open(SONG_URLS_FILE, 'r') as f:
            urls = f.readlines()
    else:
        urls = []

    # Добавить новый URL в конец списка с добавлением новой строки
    urls.append(f"{url}\n")

    # Если количество URL-адресов превышает 20, удалите самый старый (первый в списке)
    if len(urls) > 20:
        urls.pop(0)

    # Сохранить обновленный список URL-и обратно в файл
    with open(SONG_URLS_FILE, 'w') as f:
        f.writelines(urls)


async def play_track(ctx, track):
    if not track.filename:
        await ctx.send("Ошибка: нет файла для воспроизведения.")
        return

    await ctx.send(f'Воспроизведение: "{YouTube(track.url).title}"')
    view = ControlButtons(ctx, bot)
    await ctx.send("Элементы управления воспроизведением:", view=view)

    source = discord.FFmpegOpusAudio(track.filename)
    ctx.voice_client.play(source)

    while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        await asyncio.sleep(1)
    
    await delete_file(track.filename)
    await play_next(ctx)

async def add_to_queue(ctx, url, prev):
    if queue.qsize() >= MAX_QUEUE_SIZE:
        await ctx.send("Очередь заполнена. Повторите попытку позже.")
        return False

    if ctx.voice_client is None and ctx.author.voice:
        await ctx.author.voice.channel.connect()
    elif ctx.voice_client is None:
        await ctx.send("Вы не в голосовом канале!")
        return False

    track = Track(url)
    try:
        await track.download()
    except Exception as e:
        await ctx.send(f"Ошибка при загрузке: {e}")
        return False

    await queue.put(track)

    # Объявите название воспроизводимого в данный момент трека, если предыдущее значение соответствует действительности
    if prev:
        if ctx.voice_client.is_playing():
            current_track = YouTube(ctx.voice_client.source.title)
            await ctx.send(f'В настоящее время воспроизводится песня: "{current_track.title}"')
    else:
        append_url_to_file(url)

    return True


async def play_next(ctx):
    if not queue.empty():
        next_track = await queue.get()
        if not ctx.voice_client.is_playing():
            await play_track(ctx, next_track)
        queue.task_done()

async def process_playback(ctx, url):
    if is_playlist_url(url):
        playlist_id_match = re.search(r'list=([0-9A-Za-z_-]+)', url)
        if not playlist_id_match:
            await ctx.send("Не удалось прочитать идентификатор плейлиста из URL.")
            return

        playlist_id = playlist_id_match.group(1)
        playlist_info = ytmusic.get_playlist(playlist_id)
        tracks = playlist_info['tracks']
        for track in tracks:
            video_url = f"https://www.youtube.com/watch?v={track['videoId']}"
            success = await add_to_queue(ctx, video_url,False)
            if not success:
                await ctx.send("Очередь заполнена. Прекращение добавление треков.")
                break
    else:
        video_id_match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11}).*', url)
        if video_id_match:
            video_id = video_id_match.group(1)
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            await add_to_queue(ctx, video_url,False)
        else:
            search_results = ytmusic.search(url, filter='songs')
            if search_results:
                first_result = search_results[0]
                video_url = f"https://www.youtube.com/watch?v={first_result['videoId']}"
                await add_to_queue(ctx, video_url ,False)
            else:
                await ctx.send("Песня не найдена.")

    if not ctx.voice_client.is_playing():        
        await play_next(ctx)

class ControlButtons(View):
    def __init__(self, ctx, bot):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        ctx = await self.bot.get_context(interaction.message)
        await interaction.response.defer()
        return True

    @discord.ui.button(label="Воспроизвести", style=discord.ButtonStyle.success, emoji="▶️", custom_id="play_list")
    async def play_list_button(self, interaction: discord.Interaction, button: Button):
        if interaction.guild.voice_client is None:
            if interaction.user.voice:
                await interaction.user.voice.channel.connect()
            else:
                await interaction.response.send_message("Вы должны быть в голосовом канале, чтобы использовать эту команду.", ephemeral=True)
                return
        await play_song_file(interaction)
        await interaction.followup.send("Воспроизведение песен из файла.", ephemeral=True)

    @discord.ui.button(label="Пропустить", style=discord.ButtonStyle.primary, emoji="⏭️", custom_id="skip_button")
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        await interaction.followup.send("Пропуск текущей песни.", ephemeral=True)
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command("skip"))

    @discord.ui.button(label="Остановить", style=discord.ButtonStyle.danger, emoji="⏹️", custom_id="stop_button")
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        await interaction.followup.send("Остановка текущей песни.", ephemeral=True)
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command("stop"))

    @discord.ui.button(label="Очередь", style=discord.ButtonStyle.secondary, emoji="📋", custom_id="queue_button")
    async def queue_button(self, interaction: discord.Interaction, button: Button):
        await interaction.followup.send("Список очереди.", ephemeral=True)
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command("queue"))

#ДОПОЛНИТЕЛЬНЫЕ И ЛИШНИЕ КНОПКИ В МЕНЮ ВОСПРОИЗВЕДЕНИЯ
'''
   @discord.ui.button(label="Список из файла", style=discord.ButtonStyle.secondary, emoji="🗒️", custom_id="playlist_queue_button")
    async def playlist_queue_list_button(self, interaction: discord.Interaction, button: Button):
        await interaction.followup.send("Список очереди из файла плейлиста.", ephemeral=True)
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command("playlist_queue"))

    @discord.ui.button(label="Удалить список", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="del_playlist")
    async def del_playlist_button(self, interaction: discord.Interaction, button: Button):
        await interaction.followup.send("Файл плейлиста удален.", ephemeral=True)
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command("del_playlist"))
'''

@bot.command(aliases=['Play', 'PLAY', 'играй', 'ИГРАЙ', 'Играй', 'сыграй',
                      'Сыграй', 'СЫГРАЙ', 'здфн', 'Здфн', 'ЗДФН', 'p', 'P',
                      'pl', 'PL', 'Pl', 'з', 'З', 'зд', 'ЗД', 'Зд', 'Плей',
                      'ПЛЕЙ', 'плей', 'Плэй', 'ПЛЭЙ', 'плэй'], help='Воспроизведение песни или плейлиста с YouTube')
async def play(ctx, *, url=""):
    if url:
        await process_playback(ctx, url)

@bot.command(aliases=['queue', 'Queue', 'QUEUE', 'йгугу', 'Йгугу', 'ЙГУГУ', 'очередь',
                      'Очередь', 'ОЧЕРЕДЬ', 'список', 'Список', 'СПИСОК',
                      'list', 'List', 'LIST', 'дшые', 'Дшые', 'ДШЫЕ', 'Лист',
                      'лист', 'ЛИСТ', 'песни', 'Песни', 'ПЕСНИ', 'songs',
                      'Songs', 'SONGS', 'ыщтпы', 'ЫЩТПЫ', 'Ыщтпы', 'q'], help='Отображает следующие песни в очереди')
async def show_queue(ctx):
    if queue.empty():
        await ctx.send("Очередь пуста.")
    else:
        response = [f"{i+1}. {YouTube(track.url).title}" for i, track in enumerate(queue._queue)]
        await ctx.send("\n".join(response))

@bot.command(name='skip', help='Пропускает текущий трек')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await asyncio.sleep(1)        
        await play_next(ctx)
   
@bot.command(aliases=['ps', 'wait', 'wt', 'pause', 'стоп', 'пауза'], help='Останавливает воспроизведение и очищает очередь')
async def stop(ctx):
    
    global should_continue_adding,pause
    pause=True
    should_continue_adding = False
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        await asyncio.sleep(1)
        for mp4_file in glob.glob('*.mp4'):
            os.remove(mp4_file)
    while not queue.empty():
        queue.get_nowait()
    await skip(ctx)


@bot.event
async def on_message(message):
    if message.author == bot.user or not message.content:
        return

    if message.channel.name == "botyjebane":
        ctx = await bot.get_context(message)
        content = message.content.lower()
        if content.startswith("/"):
            command = content[1:]
            if command in ["p", "stop", "skip", "queue", "menu"]:
                await process_command(ctx, command)
                return
        else:
            if message.content in ["p", "stop", "skip", "queue","menu"]:
                command = message.content
                await process_command(ctx, command)
                return
        await process_playback(ctx, message.content)

    await bot.process_commands(message)

async def process_command(ctx, command):
    if command == "p":
        await play(ctx)
    elif command == "stop":
        await stop(ctx)
    elif command == "skip":
        await skip(ctx)
    elif command == "queue":
        await show_queue(ctx)
    elif command == "menu": 
        await menu(ctx)


def read_urls_from_file():
    if not os.path.exists(SONG_URLS_FILE):
        return []
    with open(SONG_URLS_FILE, 'r') as f:
        urls = f.readlines()
    return [url.strip() for url in urls]



@bot.command(name='play_song_file', help='Добавляет песни из файла в очередь и воспроизводит с самого последнего')
async def play_song_file_command(ctx):
       await play_song_file(ctx)



async def play_song_file(ctx_or_interaction):
    global pause
    if isinstance(ctx_or_interaction, discord.Interaction):
        ctx = await bot.get_context(ctx_or_interaction.message)
    else:
        ctx = ctx_or_interaction

    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Вы должны быть в голосовом канале, чтобы использовать эту команду.")
            return

    urls = read_urls_from_file()

    for url in reversed(urls):  # Начните с самых новых записей
        if queue.qsize() >= MAX_QUEUE_SIZE:
            await ctx.send("Очередь заполнена. Прекращение добавление треков.")
            break

        success = await add_to_queue(ctx, url, True)
        if not success:
            break
        if not ctx.voice_client.is_playing() and not queue.empty():
            await play_next(ctx)
        await asyncio.sleep(1)  # Короткий режим ожидания для выполнения других задач

        # Проверьте, должно ли воспроизведение продолжаться
        if  pause:
            
            pause = False 
            break


       
@bot.command(name='del_playlist', help='Удаляет файл плейлиста')
async def del_playlist(ctx):
    if os.path.exists(SONG_URLS_FILE):
        os.remove(SONG_URLS_FILE)
        await ctx.send("Файл плейлиста был удален.")
    else:
        await ctx.send("Файл плейлиста не существует.")
    
       
@bot.command(name='playlist_queue', help='Отображает список песен в файле плейлиста')
async def playlist_queue(ctx):
    
    if not os.path.exists(SONG_URLS_FILE):
        await ctx.send("Файл плейлиста не существует.")
        return

    urls = read_urls_from_file()
    if not urls:
        await ctx.send("Файл плейлиста пуст.")
        return

    titles = []
    for url in urls:
        yt = YouTube(url)
        titles.append(yt.title)

    response = "\n".join(titles)
    await ctx.send(f"Список песен в файле плейлиста:\n{response}")
    
@bot.command(name='menu', help='Отображает меню с кнопками управления')
async def menu(ctx):
    view = ControlButtons(ctx, bot)
    await ctx.send("Элементы управления воспроизведением:", view=view)


@bot.command(help="Эта команда отправляет случайное изображение собачки😅. Используйте: s.rdog")
async def rdog(ctx):
    try:
        const = requests.get("https://random.dog/woof.json")
        stuff = json.loads(const.text)
        embed = discord.Embed(title=f"URL: {stuff['url']}", color = discord.Color.random())
        embed.set_image(url=f"{stuff['url']}")
        await ctx.send(embed=embed)
    except Exception as e:
        logging.error(f"Ошибка в {ctx.command}: {e}")
        await ctx.send(f"Пожалуйста, убедитесь, что у вас есть подключение к Интернету")



@bot.command(help="Эта команда отображает последние новости по заданному ключевому слову. Используйте: s.news [Запрос]")
async def news(ctx, innews):
    news = requests.get(f"https://newsapi.org/v2/everything?q={innews}&apiKey={news_key}").json()
    thnews = news["articles"]
    if news["status"] == "ok":
        for i , article in enumerate(thnews):
            if i < 5:
                emend = discord.Embed(title=article["title"], description=article["description"], url=article["url"],color=discord.Color.blue())
                await ctx.send(embed=emend)
            else:
                break
    else:
        await ctx.send(f"{innews} не найдено, пожалуйста, попробуйте еще раз")



@bot.command(help="Эта команда отображает погоду в заданном городе. Используйте: s.weather [Название города]")
async def weather(ctx, *, city: str = None):
    try:
        weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&APPID={weather_key}")
        if weather_data.json()['cod'] == '404':
           await ctx.send(f"Город {city} не найден")
        weather = weather_data.json()['weather'][0]['main']
        temp = round(weather_data.json()['main']['temp'])
        country_name = weather_data.json()['sys']['country']
        celsius = (temp - 32) * 5/9
        int_celsius = int(celsius)
        await ctx.send(f"""
    Погода в городе {city}  {weather} , страна: {country_name}
    Температура в городе {city} : {int_celsius}°C
    """)
    except Exception as e:
        logging.error(f"Ошибка в {ctx.command}: {e}")



@bot.command(help="Эта команда отправляет случайное число в диапазоне от 1 до нужного Вам случайного числа. Используйте: s.rnum [Число]")
async def rnum(ctx , *, randeom_num: int = None):
    try:
        randrom_number = random.randint(1, randeom_num)
        await ctx.send(f"Ваше случайное число {randrom_number} ~ {ctx.message.author.mention}")
    except ValueError:
        await ctx.send(f"{randeom_num} это не номер, пожалуйста, повторите попытку с действительным номером {ctx.message.author.mention}")


#КАЛЬКУЛЯТОР


@bot.command(help="Простой калькулятор. Используйте: s.math [Число + | - | * | /  Число]")
async def math(ctx, *,  expression: str = None):
    try:
        await ctx.send(f"{eval(expression)}")
    except SyntaxError:
        await ctx.send(f"{expression} не является допустимым выражением, поддерживаются выражения + для сложения, - для вычитания, * для умножения и / для деления ~ {ctx.message.author.mention}")
    except NameError:
        await ctx.send(f"{expression} Ошибка в имени, пожалуйста убедитесь, что вы используете правильный синтаксис ~ {ctx.message.author.mention}")
    except ZeroDivisionError:
        await ctx.send(f"Делить на 0 нельзя! {ctx.message.author.mention}")



@bot.command(help="Эта команда позволяет вам проверить задержку бота. Используйте: s.ping")
async def ping(ctx):
    await ctx.send(f"Задержка бота: {round(bot.latency * 1000)}ms")

#БЕСПОЛЕЗНЫЙ ОПРОС

@bot.command(help="Создайте опрос, за который пользователи смогут проголосовать, используя реакции. Используйте: s.vote [Название] [Описание]")
async def vote(ctx, name,*, svote):
    embend = discord.Embed(title=name, color = discord.Color.random())
    embend.add_field(name=name, value=svote)
    vote_massege = await ctx.send(embed=embend)
    await vote_massege.add_reaction('\N{THUMBS UP SIGN}')
    await vote_massege.add_reaction('\N{THUMBS DOWN SIGN}')

@bot.command(help="s.check_vote", value="Проверьте количество голосов ЗА и ПРОТИВ у опроса с указанным названием. Используйте: s.check_vote [Название опроса]")
async def check_vote(ctx, vote_title):
    try:
        async for message in ctx.channel.history():
            if message.embeds and message.embeds[0].title == vote_title: 
                thumbs_up = 0
                thumbs_down = 0
                for reaction in message.reactions:
                    if str(reaction.emoji) == '👍':
                        thumbs_up = reaction.count - 1 
                    elif str(reaction.emoji) == '👎':
                        thumbs_down = reaction.count - 1
                    await ctx.send(f'Есть ЗА: {thumbs_up}, есть ПРОТИВ: {thumbs_down} и общее количество голосов: {reaction.count - 1}.')
                    return
        await ctx.send(f"{vote_title} не найдено, пожалуйста, попробуйте еще раз")
    except Exception as e:
        logging.error(f"Ошибка в {ctx.command}: {e}")


@bot.command()
async def members(ctx, guild_id: int):
    guild = bot.get_guild(guild_id)
    if guild is None:
        await ctx.send("Invalid Guild ID.")
        return
    member_count = guild.member_count
    await ctx.send(f"Количество участников на сервере: {member_count}.")


@bot.command()
async def askwiki(ctx, *, query):
    try:
        headers = {'User-Agent': 'StarloExo Bot/1.0 (Discord Bot)'}
        wiki_wiki = wikipediaapi.Wikipedia('ru', language='ru', headers=headers)
        page = wiki_wiki.page(query)
        page_summary = page.summary

        if page_summary:
            image_url = f"https://ru.wikipedia.org/wiki/File:{page.title.replace(' ', '_')}.png"

            embed = discord.Embed(title=query, description=page_summary)
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No Wikipedia page found for the given query.")
    except json.JSONDecodeError:
        await ctx.send("Error: Invalid JSON response from the Wikipedia API.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")


@bot.command()
async def serverstats(ctx):
    guild = ctx.guild

    embed = discord.Embed(title="Статистика Сервера:", color=discord.Color.green())

    embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="Имя Сервера:", value=guild.name, inline=True)
    embed.add_field(name="ID Сервера:", value=guild.id, inline=True)
    embed.add_field(name="Владелец:", value=guild.owner.name if guild.owner else "Unknown", inline=True)
    embed.add_field(name="Кол-во Участников:", value=guild.member_count, inline=True)
    embed.add_field(name="Дата Создания:", value=guild.created_at.strftime("%d-%m-%Y %H:%M:%S"), inline=True)

    await ctx.send(embed=embed)


@bot.command(name='art')
async def generate_image(ctx, *, prompt):
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}

    #payload = {
    #    "inputs": prompt,
    #    "options": {
    #        "wait_for_model": True
    #    }
    #}
    def query(payload):
        response = requests.post(api_url, headers=headers, json=payload)

        return response.content

    try:

        bytes = query(
            {
                "inputs": prompt
            }
        )
        import io
        from PIL import Image
        image = Image.open(io.BytesIO(bytes))
        with io.BytesIO() as image_binary:
            image.save(image_binary, 'JPEG')
            image_binary.seek(0)
            await ctx.send(file=discord.File(fp=image_binary, filename='generated_image.jpg'))


    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса API: {e}")
        await ctx.send("Произошла ошибка при выполнении запроса к API.")

    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        await ctx.send("Произошла ошибка при выполнении запроса к API.")


bot.run(discordtoken)