import requests
import config

class RequestException(Exception):
    pass

class KeyException(Exception):
    pass


url = 'https://api.openai.com/v1/chat/completions'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept': 'text/event-stream',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://platform.openai.com/',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {config.auth_key}',
    'OpenAI-Organization': config.organization,
    'OpenAI-Project': config.project,
    'Origin': 'https://platform.openai.com',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Priority': 'u=1',
    'TE': 'trailers',
}


def answer(params, proxy=None):
    data = {
        "messages": params,
        "temperature": 1,
        "max_tokens": 4096,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "seed": None,
        "model": "gpt-4o-mini",
        "response_format": {"type": "text"},
        "stream": False
        }
    try:
            if proxy==None:
                    gpt_req = requests.post(url, headers=headers, json=data)
            else:
                    gpt_req = requests.post(url, headers=headers, json=data, proxies=proxy)
            if gpt_req.status_code != 200:
                raise RequestException(gpt_req.text)
            return gpt_req.json()
    except Exception as e:
            raise RequestException(e)
