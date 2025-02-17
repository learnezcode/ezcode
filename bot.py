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
import json

print("ezcode bot v0.3 @csoftware")

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
       keyboard = [[InlineKeyboardButton(text="🇷🇺 Русский", callback_data='lang_ru'),InlineKeyboardButton(text="🇬🇧 English", callback_data='lang_en'), InlineKeyboardButton(text='🇧🇾 Беларускi (β)', callback_data='lang_by')]]
    elif mu_type == 'main_en':
        keyboard = [[InlineKeyboardButton(text="✅ Official courses ✅", callback_data='off_courses')],[InlineKeyboardButton(text="🧑🏻‍💻 Courses from verified authors 🧑🏻‍💻", callback_data='ver_courses')],[InlineKeyboardButton(text="👨‍👨‍👦 Community courses 👨‍👨‍👦", callback_data='com_courses')], [InlineKeyboardButton(text='⚙️ Change language ⚙️', callback_data='lang_settings')]]
    elif mu_type == 'main_ru':
        keyboard = [[InlineKeyboardButton(text="✅ Официальные курсы ✅", callback_data='off_courses')],[InlineKeyboardButton(text="🧑🏻‍💻 Курсы от подтвержденных авторов 🧑🏻‍💻", callback_data='ver_courses')],[InlineKeyboardButton(text="👨‍👨‍👦 Курсы от сообщества 👨‍👨‍👦", callback_data='com_courses')], [InlineKeyboardButton(text='⚙️ Поменять язык ⚙️', callback_data='lang_settings')]]
    elif mu_type == 'main_by':
           keyboard = [[InlineKeyboardButton(text="✅ Афіцыйныя курсы ✅", callback_data='off_courses')],[InlineKeyboardButton(text="🧑🏻‍💻 Курсы ад пацверджаных аўтараў 🧑🏻‍💻", callback_data='ver_courses')],[InlineKeyboardButton(text="👨‍👨‍👦 Курсы ад супольнасці 👨‍👨‍👦", callback_data='com_courses')], [InlineKeyboardButton(text='⚙️ Памяняць мову ⚙️', callback_data='lang_settings')]]
    elif mu_type == 'courses_official':
        for course in courses:
            keyboard.append([InlineKeyboardButton(text=course['content'][0]['name'], callback_data=f"official_{course['id']}")])
    elif mu_type == 'course_official_steps':
        for parts in courses['content'][0]['content']:
            keyboard.append([InlineKeyboardButton(text=f"{parts['chapter']}. {parts['chapter-name']}", callback_data=f"off-{courses['id']}-{parts['chapter']}")])
    elif mu_type == 'back_off':
            keyboard.append([InlineKeyboardButton(text='🔙', callback_data=f'official_{courses}')])
    elif mu_type == 'back_ver':
                keyboard.append([InlineKeyboardButton(text='🔙', callback_data=f'verify_{courses}')])
    elif mu_type == 'courses_verify':
            for course in courses:
                keyboard.append([InlineKeyboardButton(text=course['content'][0]['name'], callback_data=f"verify_{course['id']}")])
    elif mu_type == 'course_verify_steps':
            for parts in courses['content'][0]['content']:
                keyboard.append([InlineKeyboardButton(text=f"{parts['chapter']}. {parts['chapter-name']}", callback_data=f"ver-{courses['id']}-{parts['chapter']}")])
    elif mu_type == 'back_verify':
                keyboard.append([InlineKeyboardButton(text='🔙', callback_data=f'verify_{courses}')])
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
               elif get_lang['language'] == 'by':
                   by_course = xata.records().get("courses_official", course_id, columns=["by.base64Content"])
                   decrypted_by = base64.b64decode(by_course['by']['base64Content']).decode("utf-8")
                   decrypted_by = ast.literal_eval(decrypted_by)
                   courses_list.append({'id': course_id, 'content': decrypted_by})

    return courses_list

async def parse_verified_courses(user_id):
    official_parse = xata.data().query("courses_verified", {"columns": ["id"]})
    courses_list = []
    for i in range(0, len(official_parse['records'])):
               course_id = official_parse['records'][i]['id']
               user_id_c = xata.records().get('courses_verified', course_id, columns=['user_id'])
               user_id_c = user_id_c['user_id']
               print(user_id_c)
               get_lang = xata.records().get('users', user_id)
               print(get_lang)
               if get_lang['language'] == 'ru':
                   ru_course = xata.records().get("courses_verified", course_id, columns=["ru.base64Content"])
                   decrypted_ru = base64.b64decode(ru_course['ru']['base64Content']).decode("utf-8")
                   decrypted_ru = ast.literal_eval(decrypted_ru)
                   courses_list.append({'id': course_id, 'content': decrypted_ru, 'user_id': user_id_c})
               elif get_lang['language'] == 'en':
                   en_course = xata.records().get("courses_verified", course_id, columns=["en.base64Content"])
                   decrypted_en = base64.b64decode(en_course['en']['base64Content']).decode("utf-8")
                   decrypted_en = ast.literal_eval(decrypted_en)
                   courses_list.append({'id': course_id, 'content': decrypted_en, 'user_id': user_id_c})
               elif get_lang['language'] == 'by':
                   by_course = xata.records().get("courses_verified", course_id, columns=["by.base64Content"])
                   decrypted_by = base64.b64decode(by_course['by']['base64Content']).decode("utf-8")
                   decrypted_by = ast.literal_eval(decrypted_by)
                   courses_list.append({'id': course_id, 'content': decrypted_by, 'user_id': user_id_c})

    return courses_list

async def escape_symbols(text):
    symbols = r'_\\[\]\(\)~>#\+\-=|\{\}\.!'
    escaped_symbols = ''.join(f'\\{char}' for char in symbols)
    translation_table = str.maketrans({char: f'\\{char}' for char in symbols})
    return text.translate(translation_table)
async def basic_text_process(text):
    symbols = r'^+=-_.,?!\\+$'
    escaped_symbols = ''.join(f'\\{char}' for char in symbols)
    translation_table = str.maketrans({char: f'\\{char}' for char in symbols})
    return text.translate(translation_table)

async def log_course_click(user_id, click_info):
    course_id = click_info
    if click_info.startswith("official_"):
        course_id = click_info[len("official_"):]
    elif click_info.startswith("verify_"):
        course_id = click_info[len("verify_"):]
    elif "-" in click_info:
        parts = click_info.split("-")
        if len(parts) >= 2 and parts[0] in ["off", "ver"]:
            course_id = parts[1]

    try:
        current = xata.records().get('users', user_id)
        clicks = []
        if "courses" in current and current["courses"]:
            try:
                clicks = json.loads(current["courses"])
            except Exception as e:
                clicks = []
        clicks.append({
            "course_id": course_id,
            "click": click_info,
            "timestamp": int(time.time())
        })
        xata.records().update('users', user_id, {"courses": json.dumps(clicks)})
    except Exception as e:
        print("Error logging course click for user", user_id, e)

@bot.message_handler(commands=['start'])
async def send_welcome(message):
        get_id = xata.records().get('users', message.from_user.id)
        print(get_id)
        try:
            if 'not found' in get_id['message']:
                text = '🇬🇧 Choose your language\n🇷🇺 Выберите ваш язык\n🇧🇾 Выберыце мову'
                await bot.send_photo(message.from_user.id,photo=open('./banner/banner-lang.png', 'rb'), caption=text, reply_markup=await gen_markup('lang'))
        except:
            if get_id['language'] == 'en':
                await bot.send_photo(message.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption='Welcome to ezcode - a source of free coding knowledges', reply_markup=await gen_markup('main_en'), timeout=1000000000)
            elif get_id['language'] == 'ru':
                await bot.send_photo(message.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption='Добро пожаловать в ezcode - источник бесплатных знаниий по программированию', reply_markup=await gen_markup('main_ru'),timeout=1000000000)
            elif get_id['language'] == 'by':
                await bot.send_photo(message.from_user.id,photo=open('./banner/banner-main.png', 'rb'), caption='Сардэчна запрашаем у ezcode - крыніца бясплатных ведаў па праграмаванні', reply_markup=await gen_markup('main_by'),timeout=1000000000)
@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    if call.data.startswith("official_") or call.data.startswith("verify_") or (
        "-" in call.data and call.data.split("-")[0] in ["off", "ver"]
    ):
        await log_course_click(call.from_user.id, call.data)
    
    if call.data == "lang_ru":
        xata.records().insert_with_id('users', call.from_user.id, {'language': 'ru', 'status': 'basic'})
        await bot.send_photo(
            call.from_user.id,
            photo=open('./banner/banner-main.png', 'rb'),
            caption='Добро пожаловать в ezcode',
            reply_markup=await gen_markup('main_ru'),
            timeout=1000000000
        )
    elif call.data == "lang_en":
        xata.records().insert_with_id('users', call.from_user.id, {'language': 'en', 'status': 'basic'})
        await bot.send_photo(
            call.from_user.id,
            photo=open('./banner/banner-main.png', 'rb'),
            caption='Welcome to ezcode',
            reply_markup=await gen_markup('main_en'),
            timeout=1000000000
        )
    elif call.data == "lang_by":
        xata.records().insert_with_id('users', call.from_user.id, {'language': 'by', 'status': 'basic'})
        await bot.send_photo(
            call.from_user.id,
            photo=open('./banner/banner-main.png', 'rb'),
            caption='Сардэчна запрашаем у ezcode',
            reply_markup=await gen_markup('main_by'),
            timeout=1000000
        )
    elif call.data == 'lang_settings':
        text = '🇬🇧 Choose your language\n🇷🇺 Выберите ваш язык\n🇧🇾 Выберыце мову'
        await bot.send_photo(
            call.from_user.id,
            photo=open('./banner/banner-lang.png', 'rb'),
            caption=text,
            reply_markup=await gen_markup('lang')
        )
    elif call.data == 'off_courses':
        courses_off_list = await parse_official_courses(str(call.from_user.id))
        get_info = xata.records().get('users', call.from_user.id)
        if get_info['language'] == 'ru':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-main.png', 'rb'),
                caption='*ezcode officials* \\- курсы, разработанные администрацией ezcode\nМы уверены на 100% что они вас научат новым навыкам в программировании\n\n*Выберите курс*',
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('courses_official', courses=courses_off_list),
                timeout=1000000000
            )
        elif get_info['language'] == 'en':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-main.png', 'rb'),
                caption='*ezcode officials* \\- courses developed by ezcode administration\nWe are 100% sure that they will teach you new programming skills\n\n*Choose a course*',
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('courses_official', courses=courses_off_list),
                timeout=1000000000
            )
        elif get_info['language'] == 'by':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-main.png', 'rb'),
                caption='*ezcode officials* \\- курсы, распрацаваныя адміністрацыяй ezcode\nМы на 100% упэўнены, што яны навучаць вас новым праграмавальным навыкам\n\n*Выберыце курс*',
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('courses_official', courses=courses_off_list),
                timeout=1000000000
            )
    elif 'official_' in call.data:
        course_id = call.data.replace('official_', '')
        courses_off_list = await parse_official_courses(str(call.from_user.id))
        course_info = []
        for course in courses_off_list:
            if course_id == course['id']:
                course_info = course
        get_info = xata.records().get('users', call.from_user.id)
        if get_info['language'] == 'en':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-main.png', 'rb'),
                caption=f"Name: {await escape_symbols(course_info['content'][0]['name'])}\nDescription: {await escape_symbols(course_info['content'][0]['desc'])}",
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('course_official_steps', course_info),
                timeout=1000000000
            )
        elif get_info['language'] == 'ru':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-main.png', 'rb'),
                caption=f"Название: {await escape_symbols(course_info['content'][0]['name'])}\nОписание: {await escape_symbols(course_info['content'][0]['desc'])}",
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('course_official_steps', course_info),
                timeout=1000000000
            )
        elif get_info['language'] == 'by':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-main.png', 'rb'),
                caption=f"Назва: {await escape_symbols(course_info['content'][0]['name'])}\nАпiсанне: {await escape_symbols(course_info['content'][0]['desc'])}",
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('course_official_steps', course_info),
                timeout=1000000000
            )
    elif call.data == 'ver_courses':
        courses_ver_list = await parse_verified_courses(str(call.from_user.id))
        get_info = xata.records().get('users', call.from_user.id)
        if get_info['language'] == 'ru':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-verify.png', 'rb'),
                caption='*ezcode verified* \\- курсы, разработанные доверенными авторами для ezcode\n\n*Выберите курс*',
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('courses_verify', courses=courses_ver_list),
                timeout=1000000000
            )
        elif get_info['language'] == 'en':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-verify.png', 'rb'),
                caption='*ezcode verified* \\- courses developed by verfied authors especially for ezcode\n\n*Choose a course*',
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('courses_verify', courses=courses_ver_list),
                timeout=1000000000
            )
        elif get_info['language'] == 'by':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-verify.png', 'rb'),
                caption='*ezcode verified* \\- курсы, распрацаваныя верыфікаваныя аўтары для ezcode\n\n*Выберыце курс*',
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('courses_verify', courses=courses_ver_list),
                timeout=1000000000
            )
    elif 'verify_' in call.data:
        course_id = call.data.replace('verify_', '')
        courses_verify_list = await parse_verified_courses(str(call.from_user.id))
        course_info = []
        for course in courses_verify_list:
            if course_id == course['id']:
                course_info = course
        get_info = xata.records().get('users', call.from_user.id)
        if get_info['language'] == 'en':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-verify.png', 'rb'),
                caption=f"*Name:* {await escape_symbols(course_info['content'][0]['name'])}\n*Description:* {await escape_symbols(course_info['content'][0]['desc'])}\n\n*Author:* tg://user?id\\={str(course_info['user_id'])}",
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('course_verify_steps', course_info),
                timeout=1000000000
            )
        elif get_info['language'] == 'ru':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-verify.png', 'rb'),
                caption=f"*Название:* {await escape_symbols(course_info['content'][0]['name'])}\n*Описание:* {await escape_symbols(course_info['content'][0]['desc'])}\n*Автор:* tg://user?id\\={str(course_info['user_id'])}",
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('course_verify_steps', course_info),
                timeout=1000000000
            )
        elif get_info['language'] == 'by':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-verify.png', 'rb'),
                caption=f"*Назва:* {await escape_symbols(course_info['content'][0]['name'])}\n*Апiсанне:* {await escape_symbols(course_info['content'][0]['desc'])}\n*Аўтар:* tg://user?id\\={str(course_info['user_id'])}",
                parse_mode='MarkdownV2',
                reply_markup=await gen_markup('course_verify_steps', course_info),
                timeout=1000000000
            )
    elif call.data == 'com_courses':
        get_info = xata.records().get('users', call.from_user.id)
        if get_info['language'] == 'en':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-main.png', 'rb'),
                caption="Soon...\n\nIf you would like to write a course: https://github.com/learnezcode/ezcode-course\nPost on our platform: @contactlabsbot",
                timeout=1000000000
            )
        elif get_info['language'] == 'ru':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-main.png', 'rb'),
                caption="Скоро будет доступно\n\nЕсли вы хотите написать курс: https://github.com/learnezcode/ezcode-course\nВыложить на нашей платформе: @contactlabsbot",
                timeout=1000000000
            )
        elif get_info['language'] == 'by':
            await bot.send_photo(
                call.from_user.id,
                photo=open('./banner/banner-main.png', 'rb'),
                caption="Скора будзе даступна\nКалі вы хочаце напісаць курс: https://github.com/learnezcode/ezcode-course\nВыкласці на нашай платформе: @contactlabsbot"
            )
    else:
        type, course_db, chapter_id = call.data.split('-')
        if type == 'off':
            courses_off_list = await parse_official_courses(str(call.from_user.id))
            course_info = []
            for course in courses_off_list:
                if course_db == course['id']:
                    course_info = course['content'][0]['content']
            text_for = course_info[int(chapter_id)-1]['text']
            final_text = await escape_symbols(text_for)
            if len(final_text) >= 4096:
                final_text = await split_message(final_text)
                for text in final_text:
                    await bot.send_message(
                        call.from_user.id,
                        text,
                        parse_mode='MarkdownV2',
                        reply_markup=await gen_markup(f'back_{type}', course_db)
                    )
                    time.sleep(0.1)
            else:
                try:
                    await bot.send_message(
                        call.from_user.id,
                        final_text,
                        parse_mode='MarkdownV2',
                        reply_markup=await gen_markup(f'back_{type}', course_db)
                    )
                except:
                    await bot.send_message(
                        call.from_user.id,
                        f"{final_text}*",
                        parse_mode='MarkdownV2',
                        reply_markup=await gen_markup(f'back_{type}', course_db)
                    )
        elif type == 'ver':
            courses_ver_list = await parse_verified_courses(str(call.from_user.id))
            course_info = []
            for course in courses_ver_list:
                if course_db == course['id']:
                    course_info = course['content'][0]['content']
            text_for = course_info[int(chapter_id)-1]['text']
            final_text = await escape_symbols(text_for)
            if len(final_text) >= 4096:
                final_text = await split_message(final_text)
                for text in final_text:
                    await bot.send_message(
                        call.from_user.id,
                        text,
                        parse_mode='MarkdownV2',
                        reply_markup=await gen_markup(f'back_{type}', course_db)
                    )
                    time.sleep(1)
            else:
                try:
                    basic_pro = await basic_text_process(text_for)
                    await bot.send_message(
                        call.from_user.id,
                        basic_pro,
                        parse_mode="MarkdownV2",
                        reply_markup=await gen_markup(f'back_{type}', course_db)
                    )
                except Exception as e:
                    print(f'Error: {e}')
                    try:
                        await bot.send_message(
                            call.from_user.id,
                            final_text,
                            parse_mode='MarkdownV2',
                            reply_markup=await gen_markup(f'back_{type}', course_db)
                        )
                    except:
                        await bot.send_message(
                            call.from_user.id,
                            f"{final_text}*",
                            parse_mode='MarkdownV2',
                            reply_markup=await gen_markup(f'back_{type}', course_db)
                        )
 
print('starting bot')
asyncio.run(bot.infinity_polling(True))
