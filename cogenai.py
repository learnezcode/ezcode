import yaml
from yaml import Loader, Dumper
import os.path
import litegpt
import time
import config

def transform_to_newgpt(messages_chatgpt):
    messages_newgpt = []
    for message in messages_chatgpt:
        if message['role'] == 'system':
            messages_newgpt.append({"role": "system", "content": [{"type": "text", "text": message['content']}]})
        elif message['role'] == 'user':
            messages_newgpt.append({'role': 'user', 'content': [{'type': 'text', 'text': message['content']}]})
        elif message['role'] == 'assistant':
            messages_newgpt.append({'role': 'assistant', 'content': [{'type': 'text', 'text': message['content']}]})
    return messages_newgpt

def translator(text, lang):
    while True:
        try:
            message_transtalor = [{'role': 'system', 'content': f'Act you as an translator to {lang} language. User gives you sentence, you need to translate full sentence, nothing else. Just translate full sentence. Dont translate programmic languages names'}, {'role': 'user', 'content': f'Translate this: {text}'}]
            response_translator = litegpt.answer(params=transform_to_newgpt(message_transtalor))
            break
        except:
            print("Error. Waiting for a minute")
            time.sleep(60)
    return response_translator['choices'][0]['message']['content']

def generate_english(course_path):

    with open(course_path, 'r') as file:
        doc = file.read().replace('\n', f'\n')
    info = yaml.load(doc, Loader=Loader)
    print(info)
    print(f'Generating course\nName: {info['name']}\nDescription: {info['description']}')
    course = {'name': info['name'], 'desc': info['description'], 'lang': "en", 'content': []}
    message_list = [{"role": "system", "content": "You're an AI Programming teacher ezcode. You need to write text for course with chapters. User gives you chapter name and instructions for this chapter. Always write all variables on English. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown."}, {"role": "user", "content": f"Course: {course['name']}. Description: {course['desc']}. Chapter name: {info['course'][1]['chapter-name']}\nInstructions: {info['course'][1]['info']}. Write it on English. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"}]
    print('Generating EN')
    for i in range(0, len(info['course'])):
        if i == 0:
            while True:
                    try:
                        response = litegpt.answer(params=transform_to_newgpt(message_list))
                        response_app = response['choices'][0]['message']['content']
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
                        response = litegpt.answer(params=transform_to_newgpt(message_list))
                        response_app = response['choices'][0]['message']['content']
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
                        response = litegpt.answer(params=transform_to_newgpt(message_list))
                        response_app = response['choices'][0]['message']['content']
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
                        response = litegpt.answer(params=transform_to_newgpt(message_list))
                        response_app = response['choices'][0]['message']['content']
                        course['content'].append({"chapter": i+1, "chapter-name": info['course'][i+1]['chapter-name'], "text": f"{response_app}"})
                        message_list.append({'role': 'assistant', 'content': response_app})
                        break;
                    except:
                        print('Error. Waiting 1 minute')
                        time.sleep(60)
    return course

def generate_belarussian(course_path):
    with open(course_path, 'r') as file:
        doc = file.read().replace('\n', f'\n')
    info = yaml.load(doc, Loader=Loader)
    print(info['name'])
    name_t = translator(info['name'], 'Belarussian')
    desc_t = translator(info['description'], 'Belarussian')
    print(f'Generating course\nName: {name_t}\nDescription: {desc_t}')
    course = {'name': name_t, 'desc': desc_t, 'lang': "by", 'content': []}
    message_list = [{"role": "system", "content": "You're an AI Programming teacher ezcode. You need to write text for course with chapters. User gives you chapter name and instructions for this chapter. Always write all variables on English. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"}, {"role": "user", "content": f"Course: {course['name']}. Description: {course['desc']}. Chapter name: {info['course'][1]['chapter-name']}\nInstructions: {info['course'][1]['info']}. Write it on Belarussian. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"}]
    print('Generating BY')
    for i in range(0, len(info['course'])):
        if i == 0:
            while True:
                    try:
                        response = litegpt.answer(params=transform_to_newgpt(message_list))
                        response_app = response['choices'][0]['message']['content']
                        course['content'].append({"chapter": i+1, "chapter-name": info['course'][i+1]['chapter-name'], "text": f"{response_app}"})
                        message_list.append({'role': 'assistant', 'content': response_app})
                        break
                    except:
                        print('Error. Waiting 1 minute')
                        time.sleep(1)
        else:
                message_list.append({"role": "user", "content": f"Chapter name: {info['course'][i+1]['chapter-name']}\nInstructions: {info['course'][i+1]['info']}. Write it on Belarussian language. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"})
                while True:
                    try:
                        response = litegpt.answer(params=transform_to_newgpt(message_list))
                        response_app = response['choices'][0]['message']['content']
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
    by = [generate_belarussian(file)]
    with open(f'{file}.by.gen.txt', 'w+') as f:
        f.write(str(by))
    return 'ok'
