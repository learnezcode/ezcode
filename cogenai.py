import yaml
from yaml import Loader, Dumper
import os.path
import litemini
import time
import config

litemini.api_key=config.gemini_key

def transform_to_gemini(messages_chatgpt):
    messages_gemini = []
    main_prompt = ''
    for message in messages_chatgpt:
        if message['role'] == 'system':
            main_prompt = {"system_instruction": {"parts":{"text":message['content']}}}
        elif message['role'] == 'user':
            messages_gemini.append({'role': 'user', 'parts': [{'text': message['content']}]})
        elif message['role'] == 'assistant':
            messages_gemini.append({'role': 'model', 'parts': [{'text': message['content']}]})
    main_prompt["contents"] = messages_gemini
    return main_prompt

def translator(text, lang):
    while True:
        try:
            message_transtalor = [{'role': 'system', 'content': f'Act you as an translator to {lang} language. User gives you sentence, you need to translate full sentence, nothing else. Just translate full sentence. Dont translate programmic languages names'}, {'role': 'user', 'content': f'Translate this: {text}'}]
            response_translator = litemini.answer(params=transform_to_gemini(message_transtalor))
            break
        except:
            print("Error. Waiting for a minute")
            time.sleep(60)
    return response_translator['candidates'][0]['content']['parts'][0]['text']

def generate_english(course_path):

    with open(course_path, 'r') as file:
        doc = file.read().replace('\n', f'\n')
    info = yaml.load(doc, Loader=Loader)
    print(f'Generating course\nName: {info['name']}\nDescription: {info['description']}')
    course = {'name': info['name'], 'desc': info['description'], 'lang': "en", 'content': []}
    message_list = [{"role": "system", "content": "You're an AI Programming teacher ezcode. You need to write text for course with chapters. User gives you chapter name and instructions for this chapter. Always write all variables on English. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown."}, {"role": "user", "content": f"Course: {course['name']}. Description: {course['desc']}. Chapter name: {info['course'][1]['chapter-name']}\nInstructions: {info['course'][1]['info']}. Write it on English. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"}]
    print('Generating EN')
    for i in range(0, len(info['course'])):
        if i == 0:
            while True:
                    try:
                        response = litemini.answer(params=transform_to_gemini(message_list))
                        response_app = response['candidates'][0]['content']['parts'][0]['text']
                        course['content'].append({"chapter": i+1, "chapter-name": info['course'][i+1]['chapter-name'], "text": f"{response_app}"})
                        message_list.append({'role': 'assistant', 'content': response_app})
                        break
                    except:
                        print('Error. Waiting 1 minute')
                        time.sleep(60)
        else:
                message_list.append({"role": "user", "content": f"Chapter name: {info['course'][i+1]['chapter-name']}\nInstructions: {info['course'][i+1]['info']}. Write it on English language. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"})
                while True:
                    try:
                        response = litemini.answer(params=transform_to_gemini(message_list))
                        response_app = response['candidates'][0]['content']['parts'][0]['text']
                        course['content'].append({"chapter": i+1, "chapter-name": info['course'][i+1]['chapter-name'], "text": f"{response_app}"})
                        message_list.append({'role': 'assistant', 'content': response_app})
                        break
                    except:
                        print('Error. Waiting 1 minute')
                        time.sleep(60)
    print("Generation EN complete. Cooldown")
    time.sleep(120)
    return course

def generate_russian(course_path):

    with open(course_path, 'r') as file:
        doc = file.read().replace('\n', f'\n')
    info = yaml.load(doc, Loader=Loader)
    print(info['name'])
    name_t = translator(info['name'], 'Russian')
    desc_t = translator(info['description'], 'Russian')
    print(f'Generating course\nName: {name_t}\nDescription: {desc_t}')
    course = {'name': name_t, 'desc': desc_t, 'lang': "ru", 'content': []}
    message_list = [{"role": "system", "content": "You're an AI Programming teacher ezcode. You need to write text for course with chapters. User gives you chapter name and instructions for this chapter. Always write all variables on English. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"}, {"role": "user", "content": f"Course: {course['name']}. Description: {course['desc']}. Chapter name: {info['course'][1]['chapter-name']}\nInstructions: {info['course'][1]['info']}. Write it on Russian. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"}]
    print('Generating RU')
    for i in range(0, len(info['course'])):
        if i == 0:
            while True:
                    try:
                        response = litemini.answer(params=transform_to_gemini(message_list))
                        response_app = response['candidates'][0]['content']['parts'][0]['text']
                        course['content'].append({"chapter": i+1, "chapter-name": info['course'][i+1]['chapter-name'], "text": f"{response_app}"})
                        message_list.append({'role': 'assistant', 'content': response_app})
                        break
                    except:
                        print('Error. Waiting 1 minute')
                        time.sleep(1)
        else:
                message_list.append({"role": "user", "content": f"Chapter name: {info['course'][i+1]['chapter-name']}\nInstructions: {info['course'][i+1]['info']}. Write it on Russian language. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"})
                while True:
                    try:
                        response = litemini.answer(params=transform_to_gemini(message_list))
                        response_app = response['candidates'][0]['content']['parts'][0]['text']
                        course['content'].append({"chapter": i+1, "chapter-name": info['course'][i+1]['chapter-name'], "text": f"{response_app}"})
                        message_list.append({'role': 'assistant', 'content': response_app})
                        break;
                    except:
                        print('Error. Waiting 1 minute')
                        time.sleep(60)
    return course

def generate_course(file):
    eng = [generate_english(file)]
    with open(f'{file}.eng.gen.txt', 'w+') as f:
        f.write(str(eng))
    ru = [generate_russian(file)]
    with open(f'{file}.ru.gen.txt', 'w+') as f:
        f.write(str(ru))
    return eng, ru
