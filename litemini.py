import requests

class RequestException(Exception):
    pass

class KeyException(Exception):
    pass

api_key=''
headers = {
    "Content-Type": "application/json"
}

def answer(params, model='gemini-1.5-pro', proxy=None):
    if api_key == '':
        raise KeyException('No API Key declared. Use litemini.api_key to set a key')
    else:
        try:
            if proxy==None:
                    gemini_req = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}', headers=headers, json=params)
            else:
                    gemini_req = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}', headers=headers, json=params, proxies=proxy)
            if gemini_req.status_code != 200:
                raise RequestException(gemini_req.text)
            return gemini_req.json()
        except Exception as e:
            raise RequestException(e)
