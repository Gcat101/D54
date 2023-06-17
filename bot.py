# IMPORTS

# Discord api
import discord
from discord import ui
from discord.enums import ButtonStyle
from discord.ext import tasks
from discord.commands.context import ApplicationContext

# Standard modules
import random
from datetime import date, datetime
from math import ceil, floor
from os import getenv

# Other
from RandomWordGenerator import RandomWord
from text_to_speech import speak
from langdetect import detect
from pytube import Channel
from feedparser import parse

# DATA

# Variables
rw = RandomWord(50,
                constant_word_size=False,
                include_digits=False,
                special_chars=r"",
                include_special_chars=False) # Barsik generator
i = 1 # Needed for task

client = discord.Bot(intents=discord.Intents.all()) # Discord client

# Constants
VERSION = '1.1.2' # Version
DONBASS_ID = 764470795967528971 # Discord server id
GUILDS = (DONBASS_ID, 764838645374648350)

COMMANDS = {"ping":"Pong!", 
    'donbass':'Хвалит случайного донбассовца', 
    'logo':'Присылает лого',
    'catboy (текст)':'Превращает текст в кетбойский',
    'avatar [ник]':'Показывает ваш аватар, или аватар любого человека',
    'rate (вещь для оценки)':'Оценивает предмет (для #обзоры)',
    'goroskop':'Получи гороскоп от самого Квареца!',
    'hype':'Вводите когда POGCHAMP',
    'hymn':'Па, пара па па пам па парарам...',
    'like (вещь)':'Любить (для #обожаю___)',
    'hate (вещь)':'Ненавидить (для #ненавижу___)',
    'gm': 'С ДОБРЫМ УТРОМ ДОНБААААААА-',
    'barsik':f'Присылает "{rw.generate()}"',
    'emoji (кастомное эмоджи)':'Присылает емоджи в пнг формате',
    'say (сообщение)':'Подчиняет вам в рабы моего бота',
    'tts (текст)':'Присылает текст ту спич',
    'latest (название канала{g_cat/quarez})':'Присылает ссылку на последнее видео',
    'tarot':'Присылает рандомную карту таро',
    'anekdot':'Присылает рандомный анек из канала #анекдоты-и-пасты',
    'frog':'фрогге',
    'help [страница]':'Вы здесь'} # Command list

COMMANDS2 = {} # Command list without options
for key, value in zip(COMMANDS.keys(), COMMANDS.values()): COMMANDS2[key.split(' ')[0]] = value

# EVENTS

@client.event
async def on_ready(): # On login
    donbass = client.get_guild(764470795967528971)
    aneki = donbass.get_channel(775834036735049748)
    print(await aneki.create_invite())

    print(f'\nLogged in as {client.user}\n')
    change_status.start()
    # death.start()

@client.event
async def on_member_join(member:discord.Member): # Greet member
    global DONBASS_ID

    newbed = discord.Embed(title=f'Добро пожаловать, {member.name}!', description='Добро пожаловать! Добро пожаловать на Донбасс-54. Сами вы его выбрали, или его выбрали за вас — это лучший сервер из оставшихся. Я такого высокого мнения о Донбассе-54, что решил разместить свое правительство здесь, в Библиотеке, столь заботливо предоставленной нашими Модераторами. Я горжусь тем, что называю Донбасс-54 своим домом. Итак, собираетесь ли вы остаться здесь, или же вас ждут неизвестные дали, добро пожаловать на Донбасс-54. Здесь безопаснее.', color=discord.Color.dark_blue())
    newbed.set_image(url = member.avatar)

    if member.guild.id == DONBASS_ID:
        await client.get_channel(764470796776767510).send(embed=newbed)

# Send avatar when changed (for users)
@client.event
async def on_user_update(before:discord.User, after:discord.User):
    if not before.avatar:
        Avabed = discord.Embed(title=f'{before.name} поменял аву:', color=discord.Color.dark_gold())
        Avabed.set_image(url=after.avatar.url)

        await client.get_channel(817070462273060926).send(embed=Avabed)

# Join thread when created
@client.event
async def on_thread_join(thread:discord.Thread): await thread.join()

@client.event
async def on_message(message:discord.Message):
    if any(word in message.content.lower() for word in ('d54', 'd-54', 'д54', 'д-54')): # D-54 reaction
        if not message.author.bot: await message.add_reaction("<:d54:859494896112631828>")
    if ('@everyone' in message.content) or ('@here' in message.content): await message.channel.send("stfu") # @everyone reaction

# Button reaction
@client.event
async def on_interaction(ctx : discord.Interaction):
    try:
        buttonid = ctx.data['custom_id']

        if 'page' in buttonid: # Help page change
            await help2(ctx, page=int(buttonid.split(' ')[1]))
    except KeyError: pass

    await client.process_application_commands(ctx)

# TASKS

@tasks.loop(seconds=5)
async def change_status(): # Change status every 5 secs
    global i
    msg = '⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Донбасс⠀54!⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀'

    await client.change_presence(activity=discord.Game(msg[i - 1:i + 10]))
    if i!=len(msg) - 10: i += 1
    else: i=1

@tasks.loop(seconds=1)
async def death(): # Change death msg every 1 sec
    msg = await client.get_channel(764475455033835560).fetch_message(1013402634645930095)
    time = datetime.fromisoformat('2022-11-28') - datetime.now()
    await msg.edit(embed=discord.Embed(title=f"🪦 {(f'{time.days} дней, {floor(time.seconds/3600)} часов, {floor(time.seconds/60)%60} минут, {time.seconds%60} секунд')}", description="...до того как я умру" , color=discord.Colour.dark_gray()))

# INFO COMMANDS

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['help'])
async def help(ctx:ApplicationContext, page:int=1): # Help command
    global COMMANDS

    helpbed = discord.Embed(title="Команды", description = "это вся помощь которая тебе нужна", color=discord.Colour.from_rgb(51, 168, 255))
    helpbed.set_thumbnail(url = client.user.avatar)
    helpbed.set_footer(text=f'() - обязательно, [] - необязательно, страница: {page}/{ceil(len(tuple(COMMANDS.keys()))/5)}, для большей информации - info.')

    # Page managment
    if page==1: view = ui.View(ui.Button(emoji='▶️', label='Следующая страница', style=ButtonStyle.blurple, custom_id=f'page {page+1}'))
    elif page==ceil(len(tuple(COMMANDS.keys()))/5): view = ui.View(ui.Button(emoji='◀️', label='Прошлая страница', style=ButtonStyle.blurple, custom_id=f'page {page-1}'))
    else: view = ui.View(ui.Button(emoji='◀️', label='Прошлая страница', style=ButtonStyle.blurple, custom_id=f'page {page-1}'), ui.Button(emoji='▶️', label='Следующая страница', style=ButtonStyle.blurple, custom_id=f'page {page+1}'))

    page -= 1
    if (pageitems := tuple(COMMANDS.keys())[page*5:page*5+5]) and page >= 0: # Pages
        for item in pageitems: helpbed.add_field(name=item, value=COMMANDS[item])

        await ctx.respond(embed=helpbed, view=view)

# Second help for buttons (slightly changed)
async def help2(ctx:discord.Interaction, page:int): # Help command
    global COMMANDS

    helpbed = discord.Embed(title="Команды", description = "это вся помощь которая тебе нужна", color=discord.Colour.from_rgb(51, 168, 255))
    helpbed.set_thumbnail(url = client.user.avatar)
    helpbed.set_footer(text=f'() - обязательно, [] - необязательно, страница: {page}/{ceil(len(tuple(COMMANDS.keys()))/5)}, для большей информации - info.')

    # Page managment
    if page==1: view = ui.View(ui.Button(emoji='▶️', label='Следующая страница', style=ButtonStyle.blurple, custom_id=f'page {page+1}'))
    elif page==ceil(len(tuple(COMMANDS.keys()))/5): view = ui.View(ui.Button(emoji='◀️', label='Прошлая страница', style=ButtonStyle.blurple, custom_id=f'page {page-1}'))
    else: view = ui.View(ui.Button(emoji='◀️', label='Прошлая страница', style=ButtonStyle.blurple, custom_id=f'page {page-1}'), ui.Button(emoji='▶️', label='Следующая страница', style=ButtonStyle.blurple, custom_id=f'page {page+1}'))

    page -= 1
    if (pageitems := tuple(COMMANDS.keys())[page*5:page*5+5]) and page >= 0: # Pages
        for item in pageitems: helpbed.add_field(name=item, value=COMMANDS[item])

        await ctx.edit_original_message(embed=helpbed, view=view)

@client.slash_command(guild_ids=GUILDS, description='Д-54 ис ху?')
async def info(ctx:ApplicationContext): # Info command
    global VERSION

    splashes = ('Донбасс 54 рекомендует!',
                'Спасибо за ваш интерес!',
                'Первым животным был мелвуш!',
                'Фан факт: литва сосат',
                'ИИ коминг сун?',
                '1.2 коминг сун?',
                '2.0 коминг сун?',
                '<:micro_yoba:7778468225710817>',
                f'Как барсик один раз сказал: "{rw.generate()}"!',
                f'Этот сплеш посвящается участнику по имени {ctx.author.name}!')
    infobed = discord.Embed(title='Информация о боте', description=random.choice(splashes), color=discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    infobed.add_field(name='Автор', value='G_cat#2267')
    infobed.add_field(name='Сделано для', value='Донбасса54')
    infobed.set_footer(text=f'Префикс бота - /. Версия бота {VERSION}')
    infobed.set_thumbnail(url = 'https://media.discordapp.net/attachments/764470796776767510/816730419314950184/e16a9c7a83dec0bc.png')
    await ctx.respond(embed=infobed)

# COMMANDS
# No comments here because most is self-explanatory

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['ping'])
async def ping(ctx:ApplicationContext): await ctx.respond(f'Pong!!! {round(client.latency * 1000)} ms')

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['logo'])
async def logo(ctx:ApplicationContext): await ctx.respond('https://cdn.discordapp.com/attachments/764470796776767510/883005037658374195/Donbass54_logo.jpg')

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['catboy'])
async def catboy(ctx : ApplicationContext, *, text : str): await ctx.respond(f'{text.replace("в", "w").replace("р", "w").replace("В", "W").replace("Р", "W")} {random.choice(("UwU", "OwO", "QwQ"))}')

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['avatar'])
async def avatar(ctx:ApplicationContext, member : discord.Member=None):
    if not member: member=ctx.author

    Avabed = discord.Embed(title=f'Ава {member.name}:', color=discord.Color.dark_gold())
    Avabed.set_image(url=member.avatar.url)

    await ctx.respond(embed=Avabed)

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['rate'])
async def rate(ctx:ApplicationContext, *, thing:str): await ctx.respond(f'{thing} - {random.randint(0,11)}/10')

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['goroskop'])
async def goroskop(ctx:ApplicationContext):
	goroskopi = ('прислушайся к голосу Вождя',
		     'зайди в Секас Воес',
		     'поиграй в Портал 2 с Кирюшей',
		     'надень мейд костюм',
		     'надуй жопу на стриме',
		     'выйди на дуэль с гикетом',
		     'оскорби литовца при помощи бота',
		     'оцени мою пипиську',
		     'потребуй деанон у Квареца',
		     'выйди с сервера литвы',
		     'ломай меня полностью',
		     'дрочи мой хуй себе в рот, я знаю тебе это нравится UwU OwO~',
		     'сделай себе чай и подожди стрима Квареца',
		     'добавь новую команду в бота',
		     'ставь лайк если жиза)))',
		     'не прислушивайся к советам')
	await ctx.respond(f'Кварец советует тебе сегодня: "{random.choice(goroskopi)}"')

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['hype'])
async def hype(ctx:ApplicationContext):
    pospogs = ('<:pog:764475422435180604>', '<:skelepog:805744262641483777>', '<:ReptiloPog:801355518379163658>', '<:isaac_pog:853295370737942598>')

    await ctx.send(f'{random.choice(pospogs)}{random.choice(pospogs)}{random.choice(pospogs)}')
    await ctx.delete()

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['hymn'])
async def hymn(ctx:ApplicationContext): await ctx.respond("https://www.youtube.com/watch?v=Z5NaC0L6lq0")

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['like'])
async def like(ctx:ApplicationContext, *, thing:str):
    await ctx.respond (f'<@{ctx.author.id}> обожает {thing}')

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['hate'])
async def hate(ctx:ApplicationContext, *, thing:str):
    await ctx.respond (f'<@{ctx.author.id}> ненавидит {thing}')

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['gm'])
async def gm(ctx:ApplicationContext):
    f = parse('https://www.lovethispic.com/rss/Morning%20Nights%20Days')
    await ctx.respond(f['entries'][random.randint(0, len(f['entries']))]['link'])

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['donbass'])
async def donbass(ctx:ApplicationContext):
    praise = ('гений ',
	     'молодец ',
	     'прекрасный ',
	     'красивый ',
	     'умный ',
	     'чёткий ',
	     'не-литовский ',
	     'ветеран ',
	     'патриот ',
	     'Виктор Слидовский ',
	     'гигант ',
	     'кетбой ',
	     'активный ',
	     'не-фурри ',
	     'Уксус147 ',
	     'мастер ',
	     'лучший ',
	     'хороший ',
	     'неплохой ',
	     'окейный ',
	     'высший ',
	     'крутой ',
	     'Swaggy ',
	     'надувная жопа ',
	     'победитель ',
	     'умница ',
	     'человек ',
	     'добрый ',
	     'фембой ',
	     'Герой Фронта ')
    dobasovei = ('кварец',
	      'ашон',
	      'гикет',
	      'вингалс',
	      'кирюша',
	      'шейдик',
	      'ебобо',
          'Д-54',
	      'донбассовец')
    await ctx.respond(random.choice(praise) + random.choice(dobasovei))

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['barsik'])
async def barsik(ctx:ApplicationContext): await ctx.respond(f'"{rw.generate()}"\n© Барсик')

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['emoji'])
async def emoji(ctx:ApplicationContext, emoji : discord.Emoji=None):
    if emoji:
        emobed = discord.Embed(title=emoji.name, color=discord.Colour.yellow())
        emobed.set_image(url = emoji.url)
        await ctx.respond(embed=emobed)
    else:
        await ctx.respond('Стандартные эмоджи скоро будут доступны')
        
@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['say'])
async def say(ctx:ApplicationContext, *, text:str): 
    await ctx.send(text)
    await ctx.delete()

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['tts'])
async def tts(ctx:ApplicationContext, *, text : str):
    lang = detect(text)
    if lang=='bg': lang='ru'

    speak(text.replace('\n', ' '), lang, save=True, file="tts.mp3")
    await ctx.respond(file=discord.File(r'tts.mp3'))

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['latest'])
async def latest(ctx:ApplicationContext, name : str):
    name = name.lower()
    channels = {'g_cat': 'https://www.youtube.com/channel/UCOH7EaAnk1HJhbJNPRCVC2g', 'quarez': 'https://www.youtube.com/channel/UC3nP9PKtwfyzJB6EY1t5oSA', 'd54': 'https://www.youtube.com/channel/UC5v5rdL6rGU70kXlxz3sjnw'}

    if name in channels.keys():
        chosen_channel = Channel(list(channels.values())[list(channels.keys()).index(name)])
        await ctx.respond(chosen_channel.video_urls[0])
    else:
        await ctx.respond('Незнакомый канал')

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['tarot'])
async def tarot(ctx:ApplicationContext):
    cards = (
            'The Fool',
            'The Magician',
            'The High Priestess',
            'The Empress',
            'The Emperor',
            'The Hierophant',
            'The Lovers',
            'The Chariot',
            'Justice',
            'The Hermit',
            'Wheel of Fortune',
            'Strength',
            'The Hanged Man',
            'Death',
            'Temperance',
            'The Devil',
            'The Tower',
            'The Star',
            'The Moon',
            'The Sun',
            'Judgement',
            'The World')
    
    await ctx.respond(f'{random.choice(cards)} ({random.choice(("обычная", "перевёрнутая"))})')

# @client.slash_command(guild_ids=GUILDS)
# async def fakeban(ctx:ApplicationContext, user : discord.User, *, reason:str='*нет причины*'):
#     await ctx.message.delete()
#     await ctx.respond(embed=discord.Embed(title=f'<:check:886696793423892530> {user.name}#{user.discriminator} был забанен! Причина: {reason}', color=discord.Colour.green()))

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['anekdot'])
async def anekdot(ctx:ApplicationContext):
    history = await client.get_channel(775834036735049748).history(limit=200).flatten()

    msg = random.choice(history)
    while len(msg.content) < 100: msg = random.choice(history)

    await ctx.respond(msg.content)

@client.slash_command(guild_ids=GUILDS, description=COMMANDS2['frog'])
async def frog(ctx:ApplicationContext): await ctx.respond(f'http://www.allaboutfrogs.org/funstuff/random/{"{:04d}".format(random.choice(range(1, 55)))}.jpg')

# RUN

client.run(getenv("FUNNY_KEY")) # Run client