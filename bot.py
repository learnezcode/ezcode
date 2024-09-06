import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
from xata.client import XataClient
import table_init
import time
import base64
import ast
import textwrap
import re

print("ezcode bot v0.1 @csoftware")



bot = AsyncTeleBot(config.bot_token)
xata = XataClient(api_key=config.xata_key, db_url=config.xata_endpoint)
asyncio.run(table_init.init_db())

async def split_text(text, max_length=4096):
    parts = []
    while len(text) > max_length:
        split_point = text.rfind(' ', 0, max_length)

        if split_point == -1:
            split_point = max_length

        parts.append(text[:split_point].strip())
        text = text[split_point:].strip()
    if text:
        parts.append(text.strip())

    return parts

async def process_code_blocks(text):
    code_blocks = re.findall(r'```[\s\S]*?```', text)
    return code_blocks

async def remove_code_blocks(text, code_blocks):
    for code in code_blocks:
        text = text.replace(code, '')
    return text

async def split_message(message, max_length=4096):
    code_blocks = await process_code_blocks(message)
    clean_message = await remove_code_blocks(message, code_blocks)
    parts = await split_text(clean_message, max_length)
    final_parts = []
    for part in parts:
        print(part)
        final_parts.append(part)
        if code_blocks:
            final_parts.extend(code_blocks)
            code_blocks = []

    return final_parts

async def gen_markup(mu_type, courses=None):
    keyboard = []
    if mu_type == 'lang':
       keyboard = [[InlineKeyboardButton(text="🇷🇺 Русский", callback_data='lang_ru'),InlineKeyboardButton(text="🇬🇧English", callback_data='lang_en')]]
    elif mu_type == 'main_en':
        keyboard = [[InlineKeyboardButton(text="✅ Official courses ✅", callback_data='off_courses')],[InlineKeyboardButton(text="🧑🏻‍💻 Courses from verified authors 🧑🏻‍💻", callback_data='ver_courses')],[InlineKeyboardButton(text="👨‍👨‍👦 Community courses 👨‍👨‍👦", callback_data='com_courses')], [InlineKeyboardButton(text='⚙️ Change language ⚙️', callback_data='lang_settings')]]
    elif mu_type == 'main_ru':
        keyboard = [[InlineKeyboardButton(text="✅ Официальные курсы ✅", callback_data='off_courses')],[InlineKeyboardButton(text="🧑🏻‍💻 Курсы от подтвержденных авторов 🧑🏻‍💻", callback_data='ver_courses')],[InlineKeyboardButton(text="👨‍👨‍👦 Курсы от сообщества 👨‍👨‍👦", callback_data='com_courses')], [InlineKeyboardButton(text='⚙️ Поменять язык ⚙️', callback_data='lang_settings')]]
    elif mu_type == 'courses_official':
        for course in courses:
            keyboard.append([InlineKeyboardButton(text=course['content'][0]['name'], callback_data=f"official_{course['id']}")])
    elif mu_type == 'course_official_steps':
        for parts in courses['content'][0]['content']:
            keyboard.append([InlineKeyboardButton(text=f'{parts['chapter']}. {parts['chapter-name']}', callback_data=f"off-{courses['id']}-{parts['chapter']}")])
    markup = InlineKeyboardMarkup(keyboard)
    return markup

async def parse_official_courses(user_id):
    official_parse = xata.data().query("courses_official", {"columns": ["id"]})
    courses_list = []
    for i in range(0, len(official_parse['records'])):
               course_id = official_parse['records'][i]['id']
               get_lang = xata.records().get('users', user_id)
               if get_lang['language'] == 'ru':
                   ru_course = xata.records().get("courses_official", course_id, columns=["ru.base64Content"])
                   decrypted_ru = base64.b64decode(ru_course['ru']['base64Content']).decode("utf-8")
                   decrypted_ru = ast.literal_eval(decrypted_ru)
                   courses_list.append({'id': course_id, 'content': decrypted_ru})
               elif get_lang['language'] == 'en':
                   en_course = xata.records().get("courses_official", course_id, columns=["en.base64Content"])
                   decrypted_en = base64.b64decode(en_course['en']['base64Content']).decode("utf-8")
                   decrypted_en = ast.literal_eval(decrypted_en)
                   courses_list.append({'id': course_id, 'content': decrypted_en})
    return courses_list


async def escape_symbols(text):
    print('escape')
    symbols = r'_\\[\]\(\)~>#\+\-=|\{\}\.!'
    escaped_symbols = ''.join(f'\\{char}' for char in symbols)
    translation_table = str.maketrans({char: f'\\{char}' for char in symbols})
    return text.translate(translation_table)


@bot.message_handler(commands=['start'])
async def send_welcome(message):
        get_id = xata.records().get('users', message.from_user.id)
        print(get_id)
        try:
            if 'not found' in get_id['message']:
                text = '🇬🇧 Choose your language\n🇷🇺 Выберите ваш язык'
                await bot.send_photo(message.from_user.id,photo=open('./banner/banner-lang.png', 'rb'), caption=text, reply_markup=await gen_markup('lang'))
        except:
            if get_id['language'] == 'en':
                await bot.send_photo(message.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption='Welcome to ezcode - a source of free coding knowledges', reply_markup=await gen_markup('main_en'), timeout=1000000000)
            elif get_id['language'] == 'ru':
                await bot.send_photo(message.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption='Добро пожаловать в ezcode - источник бесплатных знаниий по программированию', reply_markup=await gen_markup('main_ru'),timeout=1000000000)

@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    if call.data == "lang_ru":
        xata.records().insert_with_id('users', call.from_user.id, {'language': 'ru', 'status': 'basic'})
        await bot.send_photo(call.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption='Добро пожаловать в ezcode', reply_markup=await gen_markup('main_ru'), timeout=1000000000)
    elif call.data == "lang_en":
        xata.records().insert_with_id('users', call.from_user.id, {'language': 'en', 'status': 'basic'})
        await bot.send_photo(call.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption='Welcome to ezcode', reply_markup=await gen_markup('main_en'), timeout=1000000000)
    elif call.data == 'lang_settings':
        text = '🇬🇧 Choose your language\n🇷🇺 Выберите ваш язык'
        await bot.send_photo(call.from_user.id,photo=open('./banner/banner-lang.png', 'rb'), caption=text, reply_markup=await gen_markup('lang'))
    elif call.data == 'off_courses':
        courses_off_list = await parse_official_courses(str(call.from_user.id))
        get_info = xata.records().get('users', call.from_user.id)
        if get_info['language'] == 'ru':
            await bot.send_photo(call.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption='*ezcode officials* \- курсы, разработанные администрацией ezcode\nМы уверены на 100% что они вас научат новым навыкам программирования\n\n*Выберите курс*', parse_mode='MarkdownV2', reply_markup=await gen_markup('courses_official', courses=courses_off_list), timeout=1000000000)
        elif get_info['language'] == 'en':
            await bot.send_photo(call.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption='*ezcode officials* \- courses developed by ezcode administration\nWe are 100% sure that they will teach you new programming skills\n\n*Choose a course*', parse_mode='MarkdownV2', reply_markup=await gen_markup('courses_official', courses=courses_off_list), timeout=1000000000)
    elif 'official_' in call.data:
            course_id = call.data
            course_id = course_id.replace('official_', '')
            courses_off_list = await parse_official_courses(str(call.from_user.id))
            course_info = []
            for course in courses_off_list:
                if course_id == course['id']:
                    course_info = course
            get_info = xata.records().get('users', call.from_user.id)
            if get_info['language'] == 'en':
                await bot.send_photo(call.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption=f"Name: {course_info['content'][0]['name']}\nDescription: {course_info['content'][0]['desc']}", reply_markup = await gen_markup('course_official_steps', course_info),timeout=1000000000)
            elif get_info['language'] == 'ru':
                await bot.send_photo(call.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption=f"Название: {course_info['content'][0]['name']}\nОписание: {course_info['content'][0]['desc']}", reply_markup = await gen_markup('course_official_steps', course_info), timeout=1000000000)
    elif call.data == 'ver_courses':
        get_info = xata.records().get('users', call.from_user.id)
        if get_info['language'] == 'en':
            await bot.send_photo(call.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption="generating...", timeout=1000000000)
        elif get_info['language'] == 'ru':
            await bot.send_photo(call.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption=f"генерируется...", timeout=1000000000)

    elif call.data == 'com_courses':
        get_info = xata.records().get('users', call.from_user.id)
        if get_info['language'] == 'en':
                await bot.send_photo(call.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption="Soon...\n\nIf you would like to write a course: https://github.com/learnezcode/ezcode-course\nPost on our platform: @contactlabsbot", timeout=1000000000)
        elif get_info['language'] == 'ru':
                await bot.send_photo(call.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption=f"Скоро будет доступно\n\nЕсли вы хотите написать курс: https://github.com/learnezcode/ezcode-course\nВыложить на нашей платформе: @contactlabsbot", timeout=1000000000)

    else:
        type, course_db, chapter_id = call.data.split('-')
        if type == 'off':
            courses_off_list = await parse_official_courses(str(call.from_user.id))
            course_info = []
            for course in courses_off_list:
                if course_db == course['id']:
                    course_info = course['content'][0]['content']
            get_info = xata.records().get('users', call.from_user.id)
            text_for = course_info[int(chapter_id)-1]['text']

            final_text = await escape_symbols(text_for)
            if len(final_text) >= 4096:
                final_text = await split_message(final_text)
                for text in final_text:
                    await bot.send_message(call.from_user.id, text, parse_mode='MarkdownV2')
                    time.sleep(1)
            else:
               await bot.send_message(call.from_user.id, final_text, parse_mode='MarkdownV2')
print('starting bot')
asyncio.run(bot.infinity_polling(True))
