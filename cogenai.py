import yaml
from yaml import Loader, Dumper
import os.path
import google.generativeai as genai
import time

genai.configure(api_key='')
model = genai.GenerativeModel('gemini-1.5-pro')

def transform_to_gemini(messages_chatgpt):
    messages_gemini = []
    system_promt = ''
    for message in messages_chatgpt:
        if message['role'] == 'system':
            system_promt = message['content']
        elif message['role'] == 'user':
            messages_gemini.append({'role': 'user', 'parts': [message['content']]})
        elif message['role'] == 'assistant':
            messages_gemini.append({'role': 'model', 'parts': [message['content']]})
    if system_promt:
        messages_gemini[0]['parts'].insert(0, f"*{system_promt}*")

    return messages_gemini

def translator(text, lang):
    message_transtalor = [{'role': 'system', 'content': f'Act you as an translator to {lang} language. User gives you sentence, you need to translate full sentence, nothing else. Just translate full sentence. Dont translate programmic languages names'}, {'role': 'user', 'content': f'Translate this: {text}'}]
    response_translator = model.generate_content(transform_to_gemini(message_transtalor))
    print(response_translator.text)
    return response_translator.text


def generate_english(course_path):
    
    with open(course_path, 'r') as file:
        doc = file.read().replace('\n', f'\n')
    info = yaml.load(doc, Loader=Loader)
    print(f'Generating course\nName: {info['name']}\nDescription: {info['description']}')
    course = {'name': info['name'], 'desc': info['description'], 'lang': "en", 'content': []}
    message_list = [{"role": "system", "content": "You're an AI Programming teacher ezcode. You need to write text for course with chapters. User gives you chapter name and instructions for this chapter. Always write all variables on English. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"}, {"role": "user", "content": f"Chapter name: {info['course'][1]['chapter-name']}\nInstructions: {info['course'][1]['info']}. Write it on English. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"}]
    for i in range(0, len(info['course'])):

        if i == 0:
            print("Generating")
            response = model.generate_content(transform_to_gemini(message_list))
            print(response.text)
            course['content'].append({'chapter': i+1, 'chapter-name': info['course'][i+1]['chapter-name'], 'text': f"{response.text}"})    
            message_list.append({'role': 'assistant', 'content': response.text})
            print("Sleeping for 15 seconds")
            time.sleep(15)
        else:
            print("Generating")
            message_list.append({"role": "user", "content": f"Chapter name: {info['course'][i+1]['chapter-name']}\nInstructions: {info['course'][i+1]['info']}. Write it on English language. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"})
            response = model.generate_content(transform_to_gemini(message_list))
            print(response.text)
            course['content'].append({'chapter': i+1, 'chapter-name': info['course'][i+1]['chapter-name'], 'text': f"{response.text}"})
            message_list.append({'role': 'assistant', 'content': response.text})
            print("Sleeping for 15 seconds")
            time.sleep(15)
    return course

def generate_russian(course_path):
    
    with open(course_path, 'r') as file:
        doc = file.read().replace('\n', f'\n')
    info = yaml.load(doc, Loader=Loader)
    print(info['name'])
    name_t = translator(info['name'], 'Russian')
    desc_t = translator(info['description'], 'Russian')
    print(f'Generating course\nName: {name_t}\nDescription: {desc_t}')
    course = {'name': info['name'], 'desc': info['description'], 'lang': "en", 'content': []}
    message_list = [{"role": "system", "content": "You're an AI Programming teacher ezcode. You need to write text for course with chapters. User gives you chapter name and instructions for this chapter. Always write all variables on English. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"}, {"role": "user", "content": f"Chapter name: {info['course'][1]['chapter-name']}\nInstructions: {info['course'][1]['info']}. Write it on Russian. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"}]
    for i in range(0, len(info['course'])):

        if i == 0:
            print("Generating")
            response = model.generate_content(transform_to_gemini(message_list))
            print(response.text)
            course['content'].append({'chapter': i+1, 'chapter-name': translator(info['course'][i+1]['chapter-name'], 'Russian'), 'text': f"{response.text}"})    
            message_list.append({'role': 'assistant', 'content': response.text})
            print("Sleeping for 15 seconds")
            time.sleep(15)
        else:
            print("Generating")
            message_list.append({"role": "user", "content": f"Chapter name: {info['course'][i+1]['chapter-name']}\nInstructions: {info['course'][i+1]['info']}. Write it on Russian language. NEVER USE HEADING MARKDOWN, instead make text bold without heading markdown"})
            response = model.generate_content(transform_to_gemini(message_list))
            print(response.text)
            course['content'].append({'chapter': i+1, 'chapter-name': translator(info['course'][i+1]['chapter-name'], 'Russian'), 'text': f"{response.text}"})
            message_list.append({'role': 'assistant', 'content': response.text})
            print("Sleeping for 15 seconds")
            time.sleep(15)
    return course
